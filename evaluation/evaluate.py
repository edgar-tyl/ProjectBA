import datetime
import create_queries
import evaluateSql
import os
folderName = os.path.join(".", "results", str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
FILE_GOLD = os.path.join(".","testSuite", "sql_queries_gold.txt")
create_queries.create_queries("./testSuite/sql_queries_gold.txt", folderName, "../databases/real_estate_ddl.sql")
sql_queries_predict, questions = evaluateSql.readQueries(os.path.join(".", folderName, "sql_queries_predict.txt"))
sql_queries_gold = evaluateSql.readQueries(FILE_GOLD)[0]
evaluateSql.evaulateSQL(sql_queries_predict, sql_queries_gold, False, folderName)