import re
import json
import logging
from dateutil.parser import parse

def replace_symbols(values, to_replace, with_replace):
    if isinstance(values, str):
        return values.replace(to_replace, with_replace)
    elif isinstance(values, type([])):
        return [replace_symbols(v, to_replace, with_replace) for v in values]
    elif isinstance(values, type({})):
        return {k:replace_symbols(v, to_replace, with_replace) for k,v in values.items()}
    else:
        return values

def validate_data_for_sql_query(data):

    # Replace special URL and SQL symbols
    data = replace_symbols(data, "'", "''")
    data = replace_symbols(data, "amp26", "&")
    data = replace_symbols(data, "hash23", "#")
    data = replace_symbols(data, "%", "[%]")

    return data

def validate_input_json(data):

    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.
        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
         """
        try: 
            parse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    def is_float(string):
        """
        Return whether the string can be converted to float.
        :param string: str, string to check for float
        """
        try:
            float(string)
            return True
        except ValueError:
            return False
                
    numeric_fields = ["ATP", "Best of", "WRank", "LRank", "WPts", "LPts", "W1", "L1", "W2", "L2",  "W3", "L3", "W4", "L4", "W5", "L5", "Wsets", "Lsets"]

    for f in numeric_fields:
        val = data.get(f)
        if val and not isinstance(val, int) and not val.isnumeric():
            return False

    decimal_fields = ["B365W", "B365L", "EXW", "EXL", "LBW", "LBL", "PSW", "PSL", "SJW", "SJL", "MaxW", "MaxL", "AvgW", "AvgL"]

    for f in decimal_fields:
        val = data.get(f)
        if val and not isinstance(val, float) and not is_float(val):
            return False

    date = data.get("date")
    if date and not is_date(date):
        return False
    
    return True