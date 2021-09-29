"""
Main module for database connection.
Requires installation of SQLite ODBC Driver
Check for details using the following link:
http://www.ch-werner.de/sqliteodbc/
"""

import time
import json
import os
import logging
import numpy as np
import pandas as pd
import pyodbc

import config as c
from config import config

from utils.helpers import validate_data_for_sql_query

class DBConnector:
    def __init__(self, user=None, password=None, create_tables=True):
        self.user = user
        self.password = password
        self.connection = None
        self.tables = {
            "tournaments": "tournaments_common", "results": "tournaments_results", "bets": "tournaments_bets"
        }
        self._establish_connection()
        
        if create_tables:
            self._create_db_structure()
            
    def _establish_connection(self):
        """
        Create connection to DB if already not exists
        """
        if self.connection:
            self.connection.close()

        connection_str = "SERVER={server};DATABASE={database};Trusted_connection=yes".format(**config["db"])
        if "driver" in config["db"]:
            connection_str += ";DRIVER={driver}".format(**config["db"])
        if "port" in config["db"]:
            connection_str += ";PORT={port}".format(**config["db"])
        if self.user and self.password:
            connection_str += ";UID={user};PWD={password}".format(user=self.user, password=self.password)

        self.connection = pyodbc.connect(connection_str)
        self.connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        self.connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.connection.setencoding(encoding='utf-8')
        # self.connection.setdecoding(pyodbc.SQL_WMETADATA, encoding='utf-32le')

        self._check_connection()

    def _check_connection(self):
        """
        Check connection to DB. Raise exception if not exists
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.commit()
            # cursor.execute("PRAGMA encoding = 'UTF-8';")
            # cursor.commit()
            cursor.close()
            logging.info("Connection to database established")
        except Exception:
            raise ConnectionError("Exception during connecting to DB")

    def _execute_single_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        cursor.commit()
        cursor.close()

    def _execute_many_query(self, df, table, fast_executemany=True):
        """
        Save many row to table
        :param df: df with all fields to save
        :param table: tablename to save into
        :param fast_executemany: status if fast_executemany is needed
        :return:
        """
        # convert nans to None
        df = df.where(pd.notnull(df), None)
        columns = df.columns.tolist()
        values = df.values.tolist()
        query = "INSERT OR IGNORE INTO {} ({}) VALUES ({});".format(table, ", ".join(columns), ", ".join("?" * len(columns)))
        logging.info(columns)
        logging.info(values[0])
        logging.info(query)
        try:
            cursor = self.connection.cursor()
            #cursor.fast_executemany = fast_executemany
            t1 = time.time()
            cursor.executemany(query, values)
            cursor.commit()
            cursor.close()
            logging.info(
                "{} rows were saved to table {}. \nExecution took {} seconds".format(
                    df.shape[0], table, time.time() - t1))
        except Exception as e:
            logging.error("Exception during saving data to {} table. Error message: {}".format(table, e))
            raise Exception("Exception during saving data to {} table".format(table))

    def _create_table(self, table_name, fields):
        if not table_name:
            return False
        table_structure = ",\n".join(fields)
        table_structure = table_structure.format(**self.tables)
        query = "CREATE TABLE IF NOT EXISTS {0}\n({1});".format(table_name, table_structure, **self.tables)
        self._execute_single_query(query)
        cursor = self.connection.cursor()
        if cursor.tables(table=table_name, tableType='TABLE').fetchone():
            logging.info("DB initialisation: Table {} exists in DataBase".format(table_name))
        else:
            logging.error("DB initialisation: Table {} was not created".format(table_name))
            raise Exception("Not all tables were created")
        cursor.close()
        return True

    def _create_db_structure(self):
        """
        Create all tables based on schema file
        :param ebooks_schema: specified key of schema for ebooks static data as it's different for modeling and
        inference flow
        """
        schema_file = config["db"]["db_schema"]
        logging.info("DB schema: {schema}".format(schema=schema_file))

        if not os.path.exists(schema_file):
            raise Exception("DB initialisation: No db_schema specified")
        with open(schema_file, "r") as f:
            structure = json.load(f)

        self._create_table(self.tables.get("tournaments"), structure["tournaments_common"])
        self._create_table(self.tables.get("results"), structure["tournaments_results"])
        self._create_table(self.tables.get("bets"), structure["tournaments_bets"])
        logging.info("DB initialisation: all tables were created")

    def save_data(self, df, table, batch_size=2000):
        if not df.empty:
            for g, data in df.reset_index().groupby(np.arange(len(df)) // batch_size):
                logging.info("Save data for batch: {}/{}".format(g, len(df) // batch_size))
                self._execute_many_query(data, self.tables[table])
        else:
            logging.info("No data were found for saving to {}".format(self.tables[table]))

    def get_db_data(self, columns=c.VALID_FILTER_FIELDS+["Year"], rows=c.NROWS_PER_PAGE, page=1, sortby=["ATP", "Year"], sort_order='asc', search=None, **filters):
        """
        Get data from database
        :param columns:     an iterable of column names to retrieve from db, default is None
        :param rows:        number of rows displayed per page
        :param page:        page to be displayed
        :param sortby:      columns to be sorted by
        :param sort_order:  sorting order
        :param search:      phrase for global search
        :param filters:     filters for data visualization
        """
        columns = "*" if columns is None else ", ".join(columns)
        query = """
            SELECT {cols} FROM
            (SELECT * FROM {tournaments}
            LEFT JOIN {results}
            ON {tournaments}.ATP = {results}.ATP AND {tournaments}.Year = {results}.Year
            LEFT JOIN {bets}
            ON {results}.ATP = {bets}.ATP AND {results}.Year = {bets}.Year AND {results}.Winner = {bets}.Winner AND {results}.Loser = {bets}.Loser) as t
        """.format(cols=columns, **self.tables)
        
        query_with_filters = self.add_multiple_filters_to_query(query=query, table="t", search_value=search, **filters)
        query_with_filters_paginated = self.add_pagination_to_query("t", query_with_filters, sortby, rows, page, sort_order)

        data = pd.read_sql(query_with_filters_paginated, self.connection, coerce_float=True)
        data = data.T.groupby(level=0).first().T
        return data
    
    def delete_db_data(self, table, search=None, **filters):
        """
        Delete data from table
        :param table:       table to delete data from
        :param search:      phrase for global search
        :param filters:     filters for data visualization
        """
        table_name = self.tables[table]
        query = """
            DELETE FROM {}
        """.format(table_name)
        
        query_with_filters = self.add_multiple_filters_to_query(query=query, table=table_name, search_value=search, **filters)

        self._execute_single_query(query_with_filters)

    def add_multiple_filters_to_query(self, query, table="t", search_value=None, search_columns=c.SEARCH_FIELDS, **filters):
        """
        Add filters to query as WHERE clause: where [key1] in (values1) and [key2] in (values2) and ...
        :param query:                   input query
        :param table                    table containing data to filter out
        :param filters:                 data filters applied to an input table: WHERE filter1 AND/OR filter2 AND/OR ...
                                        Include numerical filters (=, <, <=, >, >=) 
        :param search:                  data to search globally across the table
        :param is_crm:                  True if query is applied to CRM data
        """
        query = query + "where 1=1"


        and_query = []
        if filters.get("and_filters"):
            and_values = {}
            and_filters = validate_data_for_sql_query(filters["and_filters"])
            for key, value in and_filters.items():
                and_values[key] = ', '.join("'{}'".format(v) for v in value)

            and_query = " and ".join("{}.{} in ({})".format(table,key,value) for key, value in and_values.items())
            
        or_query = []       
        if filters.get("or_filters"):
            or_filters = validate_data_for_sql_query(filters["or_filters"])           
            
            for key, value in or_filters.items():
                or_values = ', '.join("'{}'".format(v) for v in value)
                or_query.append("{}.{} in ({})".format(table,key,or_values))

        search_query = []
        if search_value:
            search_query.append(self.add_global_search_to_query(table=table, search_columns=search_columns, search_value=search_value))

        or_query_total = " or ".join(filter(None, [" or ".join(filter(None, or_query)), " or ".join(filter(None, search_query))]))

        query = " and ".join(filter(None, [query, and_query, "({})".format(or_query_total)])) if or_query_total else " and ".join(filter(None, [query, and_query]))

        return query

    def add_global_search_to_query(self, table, query=None, search_value=None, search_columns=None):
        """
        Add filters to query as WHERE clause: where [key1] like (values1) or [key2] like (values2) or ...
        :param query:   input query
        :param filters: filters for WHERE clause in query    
        """
        if search_value:
            value = validate_data_for_sql_query(search_value)
            columns = search_columns if search_columns else self.get_table_columns(table)
            search_conditions = ["{}.{} LIKE '%{}%'".format(table, col, value) for col in columns]
            query = "{}".format(" or ".join(search_conditions))
        return query

    def add_pagination_to_query(self, table, query, columns, rows=c.NROWS_PER_PAGE, page=1, order='asc'):
        """
        Add pagination to table by splitting it into chunks with same numbers of rows 
        :param query:   input query
        :param columns: columns to order by
        :param order: ascending of descending order
        :param rows: number of rows on each page
        :param page: page number 
        """

        offset = (page-1)*rows
        sorting_expression = "ORDER BY {}".format(', '.join(["{}.{} {}".format(table, col, order) for col in columns])) if columns else "ORDER BY(SELECT NULL)"
        paginated_query = query + """ {}
                                    LIMIT {} OFFSET {};
                                """.format(sorting_expression, rows, offset)
        return paginated_query 