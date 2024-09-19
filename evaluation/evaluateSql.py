"""
Evaluate SQL-Queries from a file for execution accuracy with a file where the gold queries are stored
"""
import sys, os
parent_directory = os.path.abspath('../..')
sys.path.append(parent_directory)
from ProjectBA.AiHandler import AiHandler # type: ignore
import json
import argparse

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

#checks table for equivalence, when every query is the same, then returns true, else false    
def tablesSame(table_predict, table_gold, sortList= True):
    table_predict_stripped = []
    table_gold_stripped = []
    if len(table_predict) != len(table_gold):
        return False
    
    for row in table_predict:
        table_predict_stripped.append(list(row.values()))
    for row in table_gold:
        table_gold_stripped.append(list(row.values()))
    if sortList:
        table_predict_stripped.sort()
        table_gold_stripped.sort()
    
    for rows in zip(table_predict_stripped, table_gold_stripped):
        #print(rows)
        if rows[0] != rows[1]:
            return False
    return True

#query DB and calls tableSame() for every table. If human_intervention is true, it will be able to check wrong queries manually.
#results will be wriiten in the same folder with the name "correct_queries.json"
def evaulateSQL(sql_queries_predict, sql_queries_gold, human_intervention, folder ):
    testSet = zip(sql_queries_predict, sql_queries_gold)
    i = 1

    tables_predict = []
    tables_gold = []

    for queries in testSet:
        tables_predict.append(AiHandler.queryDB(queries[0], FOLDER))
        tables_gold.append(AiHandler.queryDB(queries[1], FOLDER))

    tables = zip(tables_predict, tables_gold)
    i = 0
    correctList = []

    for table in tables:
        if(tablesSame(table[0], table[1])):
            print("Tables with id " + str(i) + " are the same" )
            correctList.append({"id": i, "correct": True})
        else:
            print("Tables with id " + str(i) + " are not the same" )
            print("Query(prediction): " + str(sql_queries_predict[i]))
            print("Query(gold): " + str(sql_queries_gold[i]))
            if(human_intervention):
                humanEval = ""
                while(humanEval != "YES" and  humanEval != "NO"):
                    humanEval = input("Are the two queries equivalent in regards of the question?: " + questions[i] + "\n Answer with 'YES' or 'NO'").upper()
                    if(humanEval == "YES"):
                        correctList.append({"id": i, "correct": True})
                    else:
                        correctList.append({"id": i, "correct": False})
            correctList.append({"id": i, "correct": False})

        i += 1    
    with open(os.path.join(".", folder ,"correct_queries.json"), "w") as file:
        toWrite = json.dumps(correctList, indent=2)
        file.write(toWrite)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Tool to create the dataset for testing the system")
    parser.add_argument("--gold", type = str, required= False, help = "Path to the gold queries", nargs='?', default="./testSuite/sql_queries_gold.txt")
    parser.add_argument("-f", type = str, required= True, help = "Path to folder")
    parser.add_argument("--human", type = bool, required= False, help = "If you want to be able to look on wrong quries and assest manualy if they are equivalent", nargs='?', default= False)
    args = parser.parse_args()
    HUMAN_INTERVENTION = args.human
    FOLDER = os.path.join(".","results",args.f)
    FILE_GOLD = args.gold
    sql_queries_predict, questions = readQueries(os.path.join(".", FOLDER, "sql_queries_predict.txt"))
    sql_queries_gold = readQueries(FILE_GOLD)[0]
    evaulateSQL(sql_queries_predict,sql_queries_gold, HUMAN_INTERVENTION, FOLDER)


