"""
Module to create sql queries for later evaluation in evalauteSql.py
Resulting queries are saved in folder results/YYYY-MM-DD Time
Uses canonicaliser.py from https://github.com/jkkummerfeld/text2sql-data/tree/master/tools from Jonathan Kummerfeld et al. to standardise queries
"""
import canonicaliser
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
parent_directory = os.path.abspath('../..')
sys.path.append(parent_directory)
from ProjectBA.AiHandler import AiHandler  # type: ignore

FOLDER = "../"

#read queries from a file which saves queries like this : "question ||| sql"
#line break determines new QA-tuple
def readQueries(file):
    with open(file) as data_file:
        sql_queries = []
        questions = []
        for line in data_file:
            question, sql_query = line.split(" ||| ")
            sql_queries.append(sql_query.replace("\n", " "))
            questions.append(question)
        return sql_queries, questions

#create the queries standarise them with canonicaliser and saves them in a file
def create_queries(file_input, dir_output, ddl, RAG, HYDE, RERANK):
    outputName = "/sql_queries_predict.txt"
    ai = AiHandler(FOLDER, RAG, HYDE, RERANK)
    Path(dir_output).mkdir(parents=True, exist_ok=True)
    sql_queries_gold, questions = readQueries(file_input)

    with open(dir_output + outputName, "w") as file:
        print("Save queries in: " + file.name)

        for prompt in questions:
            examples = None
            promptForRetrieve = prompt
            if ai.RAG:
                if ai.hyDE:
                    promptForRetrieve = "question: " + prompt + "\n" + "sql: " + ai.createSQLQuery(ai.chainHyDE, ai.db, promptForRetrieve, None)
                    print("hyde: " + promptForRetrieve)
                if ai.reRank:
                    examples = ai.retrieveDocuments(promptForRetrieve, ai.compresion_retriever)
                else:
                    examples = ai.retrieveDocuments(promptForRetrieve, ai.retriever)
            sql_query_predict = ai.createSQLQuery(ai.chainQuery, ai.db, prompt, examples)
            table_temp = ai.queryDB(sql_query_predict, FOLDER)
            while((table_temp == None) or (ai.validateQuery(sql_query_predict) == False)):
                sql_query_predict = ai.createSQLQuery(ai.chainQuery, ai.db, prompt, examples)
                table_temp = ai.queryDB(sql_query_predict, FOLDER)           
            file.writelines(prompt + " ||| " + sql_query_predict.replace("\n", " ") + "\n")

    with open(dir_output + "/meta.txt", "w") as file:
        output = "RAG: " + str(RAG) + "\nHyDE: " + str(HYDE) + "\nReRank: " + str(RERANK) 
        file.write(output)
    #exclude aliases because it causes errors, sql not executable anymore. Not needed for later evaluation because coloumn names arent respected anyway
    canonicaliser.standarise_file(dir_output + outputName, ddl, log=True, overwrite=True, skip= ['standardise_aliases'], nonjson=True)
    
    sql_queries_predict  = readQueries(dir_output + outputName)[0]


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description = "Tool for testing sql-generation via execution accuracy")
    parser.add_argument("-i", type = str, required= False, help = "Path to the input file", nargs='?', default="./testSuite/sql_queries_gold.txt")
    parser.add_argument("--ddl", type = str, required= False, help = "Path to ddl", nargs='?', default="../databases/real_estate_ddl.sql")
    parser.add_argument("--folder", type = str, required= False, help = "Path to folder")
    parser.add_argument("--rag",  required= False, help = "Wheter to use rag or not", action="store_true")
    parser.add_argument("--hyde",  required= False, help = "Wheter to use HyDe or not", action="store_true")
    parser.add_argument("--rerank",  required= False, help = "Wheter to use ReRank or not", action="store_true")
    args = parser.parse_args()
    FOLDER_NAME = args.folder
    FILEPATH_INPUT = args.i
    DDL = args.ddl
    RAG = args.rag
    HYDE = args.hyde
    RERANK = args.rerank
    
    
    create_queries(FILEPATH_INPUT,FOLDER_NAME, DDL, RAG, HYDE, RERANK)

