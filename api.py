import flask
from flask import abort, request, send_file, Response
import os
import json
import logging

import numpy as np
import pandas as pd

import config as constants
from config import config

from utils.db.connector import DBConnector
from utils.loader.loader import TennisDataLoader

from utils.preprocess import Preprocessor
from utils.preprocess import TOURNAMENTS_PREPROCESS, RESULTS_PREPROCESS, BETS_PREPROCESS

from utils.logging.helpers import log_initialize
from utils.helpers import validate_input_json

# initialize logging
log_initialize(
    file_path=config["logging"]["log_path_api"],
    file_mode=constants.LOG_FILE_MODE,
    log_level=constants.LOG_LEVEL,
    log_format_str=constants.LOG_FORMAT,
    days_keep=30
)

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The requested link does not exist.</p>", 404

@app.route('/api/get/data/<int:year>', methods=['GET'])
def get_data(year):

    db_connector = DBConnector()
    
    search_value = request.args.get("search")

    nrows = constants.NROWS_PER_PAGE

    filters = {}
    filters["and_filters"] = {}

    filters["and_filters"]["Year"] = [year]
    for c in constants.VALID_FILTER_FIELDS:
        if c in request.args:
            filters["and_filters"][c] = request.args.get(c)

    if not request.args.get("page"):
        page = 1
        nrows = 100000000
    else:
        page = int(request.args.get("page"))

    print("Start loading backend data from database \n"\
                    "Page number: {} \n" \
                    "Rows to fetch: {} \n" \
                    "Applying OR filters: {} \n" \
                    "Applying AND filters: {} \n" \
                    "Applying search for {}".format(page, nrows, filters.get("or_filters"), filters.get("and_filters"), search_value))

    data = db_connector.get_db_data(page=page, rows=nrows, search=search_value, **filters)

    data.to_csv("test.csv", index=False)

    return data.to_json(orient="records", force_ascii=False)

@app.route('/api/get/data/<int:year>/download', methods=['GET'])
def download_data(year):

    db_connector = DBConnector()
    
    search_value = request.args.get("search")

    nrows = constants.NROWS_PER_PAGE

    filters = {}
    filters["and_filters"] = {}

    filters["and_filters"]["Year"] = [year]
    for c in constants.VALID_FILTER_FIELDS:
        if c in request.args:
            filters["and_filters"][c] = request.args.get(c)

    if not request.args.get("page"):
        page = 1
        nrows = 100000000
    else:
        page = int(request.args.get("page"))

    print("Start loading backend data from database \n"\
                    "Page number: {} \n" \
                    "Rows to fetch: {} \n" \
                    "Applying OR filters: {} \n" \
                    "Applying AND filters: {} \n" \
                    "Applying search for {}".format(page, nrows, filters.get("or_filters"), filters.get("and_filters"), search_value))

    data = db_connector.get_db_data(page=page, rows=nrows, search=search_value, **filters)

    os.makedirs("data/files/downloaded", exist_ok=True)
    path = "data/files/downloaded/{}.json".format(year)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data.to_json(orient="records", force_ascii=False), f, ensure_ascii=False, indent=4)

    return send_file(path, as_attachment=True)

@app.route('/api/upload/data', methods=['GET', 'POST'])
def upload_data():
    if not request.get_json():
        abort(400, {'message': 'No JSON file provided'})

    payload = request.get_json()

    if not 'ATP' in payload or not 'Year' in payload:
        abort(400, {'message': 'No ATP and Year fields provided'})

    if not validate_input_json(payload):
        abort(400, {'message': 'Invalid input data format'})
    else:
        logging.info("Input data successfully validated")

    try:
        db_connector = DBConnector()
        loader = TennisDataLoader(url=config["tennis"]["base_url"], db_connector=db_connector)

        pd_payload = {k:[v] for k,v in payload.items()}

        data = pd.DataFrame.from_dict(pd_payload)

        print("Preprocessing data before loading in database")
        data_preprocessor = Preprocessor(TOURNAMENTS_PREPROCESS+RESULTS_PREPROCESS+BETS_PREPROCESS)
        data = data_preprocessor.calculate(data)

        year = int(payload.get("Year"))

        data = data.rename(columns=constants.RENAME_MAP)

        loader.save_tournament_data(yearly_data=data, filename=config["data"]["tournaments_data"].format(year=year), primary_keys=["ATP", "Year"])
        loader.save_results_data(yearly_data=data, filename=config["data"]["results_data"].format(year=year), primary_keys=["ATP", "Year", "Winner", "Loser"])
        loader.save_bets_data(yearly_data=data, filename=config["data"]["bets_data"].format(year=year), primary_keys=["ATP", "Year", "Winner", "Loser"])
    except Exception as e:
        # In case of failed execution return message with exception content
        logging.error("Data uploading failed with exception {}".format(e))
        return Response("Failed to load data for year {} due to exception: {}".format(year, e), status=400)

    return Response("Data for year {} successfully uploaded".format(year), status=200)

@app.route('/api/import/data/<int:year>', methods=['GET', 'POST'])
def import_data(year):

    try:
        logging.info("Start loading data for year {}".format(year))

        db_connector = DBConnector()
        loader = TennisDataLoader(url=config["tennis"]["base_url"], db_connector=db_connector)

        logging.info("Downloading data from {}".format(config["tennis"]["base_url"]))
        yearly_data = loader.download_by_year(url=config["tennis"]["url_year"], year=year, path=config["tennis"]["base_dir"])

        logging.info("Preprocessing data before loading in database")
        results_preprocessor = Preprocessor(TOURNAMENTS_PREPROCESS+RESULTS_PREPROCESS+BETS_PREPROCESS)
        yearly_data = results_preprocessor.calculate(yearly_data)

        yearly_data = yearly_data.rename(columns=constants.RENAME_MAP)
        yearly_data["Year"] = int(year)

        loader.save_tournament_data(yearly_data=yearly_data, filename=config["data"]["tournaments_data"].format(year=year), primary_keys=["ATP", "Year"])
        loader.save_results_data(yearly_data=yearly_data, filename=config["data"]["results_data"].format(year=year), primary_keys=["ATP", "Year", "Winner", "Loser"])
        loader.save_bets_data(yearly_data=yearly_data, filename=config["data"]["bets_data"].format(year=year), primary_keys=["ATP", "Year", "Winner", "Loser"])

    except Exception as e:
        # In case of failed execution return message with exception content
        logging.error("Data import failed with exception {}".format(e))
        return Response("Failed to import data for year {} due to exception: {}".format(year, e), status=400)

    return Response("Data for year {} successfully imported".format(year), status=200)

@app.route('/api/delete/data', methods=['GET', 'POST'])
def delete_data():

    try:
        db_connector = DBConnector()
        
        search_value = request.args.get("search")

        filters = {}
        filters["tournaments"] = {}
        filters["results"] = {}
        filters["bets"] = {}
        filters["tournaments"]["and_filters"] = {}
        filters["results"]["and_filters"] = {}
        filters["bets"]["and_filters"] = {}

        if not request.args:
            return Response("No data is specified to be deleted.")

        for c in constants.TOURNAMENTS_FIELDS:
            if c in request.args:
                filters["tournaments"]["and_filters"][c] = request.args.get(c)

        for c in constants.RESULTS_FIELDS:
            if c in request.args:
                filters["results"]["and_filters"][c] = request.args.get(c)

        for c in constants.BETS_FIELDS:
            if c in request.args:
                filters["bets"]["and_filters"][c] = request.args.get(c)

        db_connector.delete_db_data(table="tournaments", search=search_value, **filters["tournaments"])
        db_connector.delete_db_data(table="results", search=search_value, **filters["results"])
        db_connector.delete_db_data(table="bets", search=search_value, **filters["bets"])

    except Exception as e:
        # In case of failed execution return message with exception content
        logging.error("Data deletion failed with exception {}".format(e))
        return Response("Failed to delete data from database due to exception: {}".format(e), status=400)

    return Response("Successfully deleted data from database", status=200)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()