"""
Configuration parser and logging initializer
"""

import os
import logging
import configparser
import numpy as np
import pandas as pd
from pathlib import Path

# load configuration file
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), "config.ini"))

# logging constants
LOG_FILE_MODE = config["logging"]["mode"]
LOG_LEVEL = getattr(logging, config["logging"]["level"].upper())
LOG_FORMAT = "%(asctime)s\t[%(levelname)s]\t%(message)s"

TOURNAMENTS_FIELDS = ["ATP", "Date",
    "Tournament", "Location",
    "Series", "Court", "Surface"
]

RESULTS_FIELDS = ["ATP", "Date", "Winner", "Loser",
    "Round", "BestOf",
    "WRank", "LRank", "WPts", "LPts", 
    "W1", "L1", "W2", "L2", 
    "W3", "L3", "W4", "L4", "W5", "L5",
    "Wsets", "Lsets", 
    "Comment"
]

BETS_FIELDS = ["ATP", "Date", "Winner", "Loser",
    "B365W", "B365L", "EXW", "EXL", 
    "LBW", "LBL", "PSW", "PSL", 
    "SJW", "SJL", "MaxW", "MaxL", "AvgW", "AvgL"
]

RENAME_MAP = {"Best of" : "BestOf"}

NROWS_PER_PAGE = 100

SEARCH_FIELDS = ["Tournament", "Location", "Year",
    "Series", "Court", "Surface", 
    "Winner", "Loser", "Round", "Comment"
]

VALID_FILTER_FIELDS = [
    "ATP", "Date",
    "Tournament", "Location",
    "Series", "Court", "Surface",
    "Winner", "Loser",
    "Round", "BestOf",
    "WRank", "LRank", "WPts", "LPts", 
    "W1", "L1", "W2", "L2", 
    "W3", "L3", "W4", "L4", "W5", "L5",
    "Wsets", "Lsets", 
    "Comment",
    "B365W", "B365L", "EXW", "EXL", 
    "LBW", "LBL", "PSW", "PSL", 
    "SJW", "SJL", "MaxW", "MaxL", "AvgW", "AvgL"
]