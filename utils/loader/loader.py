"""
Basic Loader for downloading data from http://tennis-data.co.uk
"""
import os
import shutil
import logging
import requests
from zipfile import ZipFile
import pandas as pd

import config as c
from config import config

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def load_data(filename, data=None):
    """
        Load data from file based on its base name.
        Supports CSV, JSON, XLS and XLSX formats
        :param basename: an input file base name
        :param data: an input dataframe
        :return: dataframe object
        """
    if data is None:
        if os.path.exists(filename):
            logging.info("Loading data from file: {}".format(filename))
            try:
                data = pd.read_csv(filename)
            except Exception:
                try:
                    data = pd.read_json(filename)
                except Exception:
                    try:
                        data = pd.read_excel(filename)
                    except Exception as e:
                        logging.info("Failed to open {} due to exception: {}".format(filename, e))
                        raise Exception(e)
        else:
            logging.info("File not found")
            
    return data

class TennisDataLoader(object):

    def __init__(self, url, db_connector, auth=None):
        self.url = url
        self.auth = auth
        self.session = self.create_session(retries=3)
        self.db_connector = db_connector
        
    def create_session(self, retries=3):
        """
        Create session object with auth and specified number of retries
        :param retries: allowed number of retries
        :return: session object
        """
        session = requests.Session()
        if self.auth:
            session.auth = self.auth
        retries = Retry(total=retries, backoff_factor=0.2, status_forcelist=[500])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session
    
    def single_api_call(self, url, params=None, timeout=600, filename=None):
        """
        Single get request with specified timeout
        :return: responce as json object with data and its time if any was received
        """
        if not params:
            params = {}
            
        try:
            with self.session.get(url, params=params, timeout=timeout, stream=True) as r:
                    r.raise_for_status()
                    with open(filename, "wb") as f:
                        shutil.copyfileobj(r.raw, f, length=16*1024*1024)
            logging.info("Downloaded: {}".format(filename))
            responce_time = r.elapsed.total_seconds()
        except Exception as e:
            msg = "Exception on API call to tennis-data: {}".format(type(e))
            logging.error(msg)
            raise Exception(msg)
            
        return True
    
    def download_by_year(self, url, year, path, data=None):
        """
        Download yearly file or load if already downloaded
        """
        if data is None:
            url = url.format(year=year)
            
            filename = os.path.join(path, url[url.rindex('/')+1:])
                
            os.makedirs(path, exist_ok=True)
            
            self.single_api_call(url=url, filename=filename)

            # Accepted file formats
            formats = (".csv", ".json", ".xlsx", ".xls")

            extracted_file = None
            
            # Check if file was downloaded correctly
            if not os.path.exists(filename):
                logging.info("Failed to download data")
                raise Exception("Failed to download data")
            else:
                with ZipFile(filename, 'r') as zipf:
                    # Check if any files in zip have correct file format
                    # If not raise exception
                    files = [f for f in zipf.namelist() if f.endswith(formats)]
                    if len(files) == 0:
                        logging.info("No valid data file detected")
                        raise Exception("No valid data file detected")
                    # Extract only files with correct format
                    # There should be one correct file per zip but if there's many
                    # pick the last one assuming that data is the same across the files
                    for f in files:
                        zipf.extract(f, path=path)
                        extracted_file = f
                        logging.info("Extracted: {}".format(f))  
                os.remove(filename)
            logging.info("Unpacked: {}".format(filename))  
            
            extracted_file_path = os.path.join(path, extracted_file)

            logging.info("Using file {}".format(extracted_file_path))
            data = load_data(extracted_file_path)
            
            if data is None:
                logging.error("Failed to load data from file")
                raise Exception("Failed to load data from file")

        return data

    @staticmethod
    def save_data_to_csv(data, filename, **kwargs):
        """
        Save df to csv
        :param data: df to save
        :param filename: path to file
        :param kwargs: additional arguments for DataFrame.to_csv method
        """
        dirname = os.path.dirname(filename)
        os.makedirs(dirname, exist_ok=True)
        data.to_csv(filename, **kwargs)
    
    def save_tournament_data(self, yearly_data, primary_keys, filename, data=None):
        """
        Save downloaded static tournaments data
        :param yearly_data: dataFrame with static tournaments fields (atp, year, location, etc.)
        :param filename: CSV file to save data to and load data from
        :data: dataframe to be save in file and database
        """
        logging.info("Start working with tournament data")
        if data is None:
            data = yearly_data[c.TOURNAMENTS_FIELDS + ["Year"]]

        data = data.drop_duplicates(subset=primary_keys)

        self.save_data_to_csv(data, filename, index=False)

        data = data.set_index(primary_keys)

        self.db_connector.save_data(df=data, table="tournaments")
        logging.info("Tournaments data successfully loaded in database")

    def save_results_data(self, yearly_data, primary_keys, filename, data=None):
        """
        Save downloaded data with tournament results in each round
        :param yearly_data: dataFrame with static tournaments fields (atp, year, location, etc.)
        :param filename: CSV file to save data to and load data from
        :data: dataframe to be save in file and database
        """
        logging.info("Start working with results data")
        if data is None:
            data = yearly_data[c.RESULTS_FIELDS + ["Year"]]

        data = data.drop_duplicates(subset=primary_keys)

        self.save_data_to_csv(data, filename, index=False)

        data = data.set_index(primary_keys)

        self.db_connector.save_data(df=data, table="results")
        logging.info("Results data successfully loaded in database")

    def save_bets_data(self, yearly_data, primary_keys, filename, data=None):
        """
        Save downloaded data with bets on each tournament result in each round
        :param yearly_data: dataFrame with static tournaments fields (atp, year, location, etc.)
        :param filename: CSV file to save data to and load data from
        :data: dataframe to be save in file and database
        """
        logging.info("Start working with bets data")
        if data is None:
            data = yearly_data[c.BETS_FIELDS + ["Year"]]

        data = data.drop_duplicates(subset=primary_keys)

        self.save_data_to_csv(data, filename, index=False)

        data = data.set_index(primary_keys)

        self.db_connector.save_data(df=data, table="bets")
        logging.info("Bets data successfully loaded in database")

