"""
Combines all evaluation module in a single module. No need to call every single module manually 
"""

import datetime
import create_queries
import evaluateSql
import os
import argparse
parser = argparse.ArgumentParser(description = "Tool to create the dataset for testing the system")
parser.add_argument("--rag", required= False, help = "If you want to test with RAG", action='store_true')
parser.add_argument("--hyde",  required= False, help = "Wheter to use HyDe or not", action="store_true")
parser.add_argument("--rerank",  required= False, help = "Wheter to use ReRank or not", action="store_true")
parser.add_argument("--human", required= False, help = "If you want to test with Human intervention", action='store_true')
args = parser.parse_args()
RAG = args.rag
HYDE = args.hyde
RERANK = args.rerank
HUMAN = args.human
folderName = os.path.join(".", "results", str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
FILE_GOLD = os.path.join(".","testSuite", "sql_queries_gold.txt")
#For evaluating SQl-Generation of the LLM
create_queries.create_queries("./testSuite/sql_queries_gold.txt", folderName, "../databases/real_estate_ddl.sql", RAG, HYDE, RERANK)
sql_queries_predict, questions = evaluateSql.readQueries(os.path.join(".", folderName, "sql_queries_predict.txt"))
sql_queries_gold = evaluateSql.readQueries(FILE_GOLD)[0]
evaluateSql.evaulateSQL(sql_queries_predict, sql_queries_gold, questions, HUMAN, "../", folderName, )