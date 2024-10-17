#Script to format the previous created JSON-Data to "question ||| sql" to use in canonicaliser.py

import json
import json
import argparse
import canonicaliser
parser = argparse.ArgumentParser(description = "Tool to create the dataset for testing the system")
parser.add_argument("-i", type = str, required= False, help = "Path to the input json file", nargs='?', default="./testSuite/sql_test.json")
parser.add_argument("-o", type = str, required= False, help = "Path to the output file", nargs='?', default="./testSuite/sql_queries_gold.txt")
parser.add_argument("--ddl", type = str, required= False, help = "Path to ddl", nargs='?', default="../databases/real_estate_ddl.sql")
args = parser.parse_args()

FILEPATH_INPUT = args.i
FILEPATH_OUTPUT = args.o
DDL = args.ddl
with open(FILEPATH_INPUT) as data_file: 
    data = json.load(data_file)
    queryLine = []
    for item in data:
        sql_query = item["sql"]
        sentence = item["question"]
        queryLine.append(sentence + " ||| " + sql_query + "\n")

with open(FILEPATH_OUTPUT, "w") as data_file:
    data_file.writelines(queryLine)

canonicaliser.standarise_file(FILEPATH_OUTPUT,DDL, log=True, overwrite=True, skip= ["standardise_aliases"], nonjson=True)