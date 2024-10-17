#Read JSON file. Queries DB for each sql statement in json file. Afterwards create file with tables. Not used in later iterations, can be ignored.
import sqlite3
import argparse 
import json
import os
import sys
parent_directory = os.path.abspath('../')
sys.path.append(parent_directory)
from app.AiHandler import AiHandler  # type: ignore


parser = argparse.ArgumentParser(description = "Tool to create the dataset for testing the system")
parser.add_argument("-i", type = str, required= False, help = "Path to the input json file", nargs='?', default=".evaluation//testSuite/sql_test.json")
parser.add_argument("-o", type = str, required= False, help = "Path to the output json file", nargs='?', default="./evaluation/testSuite/sql_test_with_table.json")
parser.add_argument("-d", type = str, required= False, help = "Path to the database", nargs='?', default="./databases/real_estate.db")
args = parser.parse_args()
print(args)

FILEPATH_INPUT = args.i
FILEPATH_OUTPUT = args.o
DATABASE = args.d
FOLDER = "../"

with open(FILEPATH_INPUT) as data_file:    
            data = json.load(data_file)
            finalList = []
            for item in data:
                sql_query = item['sql']
                table = AiHandler.queryDB(sql_query,)
                item["table"] = table
                finalList.append(item) 
            with open(FILEPATH_OUTPUT, "w") as output:
                  json.dump(finalList, output, indent=2)
