import canonicaliser
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
parent_directory = os.path.abspath('../..')
sys.path.append(parent_directory)
from ProjectBA.AiHandler import AiHandler  # type: ignore



def readQueries(file):
    with open(file) as data_file:
        sql_queries = []
        questions = []
        for line in data_file:
            question, sql_query = line.split(" ||| ")
            sql_queries.append(sql_query.replace("\n", " "))
            questions.append(question)
        return sql_queries, questions

def create_queries(file_input, dir_output, ddl):
    outputName = "/sql_queries_predict.txt"
    ai = AiHandler()
    Path(dir_output).mkdir(parents=True, exist_ok=True)
    sql_queries_gold, questions = readQueries(file_input)

    with open(dir_output + outputName, "w") as file:
        print(file.name)

        for prompt in questions:
            examples = ai.retrieveDocuments(prompt, ai.retriever)
            sql_query_predict = ai.createSQLQuery(ai.chainQuery, ai.db, prompt, examples)
            print(sql_query_predict)
            table_temp = ai.queryDB(sql_query_predict)
            while((table_temp == None) or (ai.validateQuery(sql_query_predict) == False)):
                sql_query_predict = ai.createSQLQuery(ai.chainQuery, ai.db, prompt, examples)
                table_temp = ai.queryDB(sql_query_predict)           
            file.writelines(prompt + " ||| " + sql_query_predict.replace("\n", " ") + "\n")

    canonicaliser.standarise_file(file_input, ddl, log=True, overwrite=True, skip= ["standardise_aliases"], nonjson=True)

    sql_queries_predict  = readQueries(dir_output + outputName)[0]

    sql_tables_gold = []
    sql_tables_predict = []
    for query in sql_queries_gold: 
        sql_tables_gold.append(AiHandler.queryDB(query))
    for query in sql_queries_predict: 
        sql_tables_predict.append(AiHandler.queryDB(query))


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = "Tool for testing sql-generation via execution accuracy")
    parser.add_argument("-i", type = str, required= False, help = "Path to the input file", nargs='?', default="./testSuite/sql_queries_gold.txt")
    parser.add_argument("--ddl", type = str, required= False, help = "Path to ddl", nargs='?', default="../databases/real_estate_ddl.sql")
    parser.add_argument("--folder", type = str, required= False, help = "Path to folder")
    args = parser.parse_args()
    FOLDER_NAME = args.folder
    FILEPATH_INPUT = args.i
    DDL = args.ddl
    
    
    create_queries(FILEPATH_INPUT,FOLDER_NAME, DDL)

