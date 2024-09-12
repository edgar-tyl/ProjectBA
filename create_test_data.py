import sqlite3
import argparse 
import json
from AiHandler import AiHandler

parser = argparse.ArgumentParser(description = "Tool to create the dataset for testing the system")
parser.add_argument("-i", type = str, required= False, help = "Path to the input json file", nargs='?', default="databases/sql_test.json")
parser.add_argument("-o", type = str, required= False, help = "Path to the output json file", nargs='?', default="databases/sql_test_with_table.json")
parser.add_argument("-d", type = str, required= False, help = "Path to the database", nargs='?', default="databases/real_estate.db")
args = parser.parse_args()
print(args)

FILEPATH_INPUT = args.i
FILEPATH_OUTPUT = args.o
DATABASE = args.d
con = sqlite3.connect(DATABASE)
cur = con.cursor()

def queryDB(sql_query):
        try:
            cur.execute(sql_query)
        except sqlite3.OperationalError:
            print("Error: SQL could not be executed")
            return None
        #https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3 from user logi-kal
        headers = list(map(lambda attr : attr[0], cur.description))
        print(headers)
        results = [{header:row[i] for i, header in enumerate(headers)} for row in cur]
        return results

with open(FILEPATH_INPUT) as data_file:    
            data = json.load(data_file)
            finalList = []
            for item in data:
                sql_query = item['sql']
                table = AiHandler.queryDB(sql_query)
                item["table"] = table
                finalList.append(item) 
            with open(FILEPATH_OUTPUT, "w") as output:
                  json.dump(finalList, output)