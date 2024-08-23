import argparse 
import socket
import sys
import getpass
import sqlite3
import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

class AiHandler:
    def __init__(self) -> None:
        self.tasks = {}
        self.results = {}
        self.task_number = 0
        self.llm = Ollama(model="Llama3-8b")
        self.dbConn = sqlite3.connect(os.path.join("databases", "real_estate.db"))
        self.cur = self.dbConn.cursor()
        with open(os.path.join( "databases", "real_estate_ddl.sql"),"r") as file:
            self.schema = file.read()

        self.system_template_query = "Create a SQL-Query in Sqlite for the following Database based on the users question:\n{database}. You should put only the query out. No explanation. No indication that it is sql."
        self.prompt_template_query = ChatPromptTemplate.from_messages(
            [("system", self.system_template_query), ("user", "{text}")]
        )

        self.system_template_answer = "Answer the users question only based on the following data\n {table}. Answer truthfully."
        self.prompt_template_answer = ChatPromptTemplate.from_messages(
            [("system", self.system_template_answer), ("user", "{text}")]
        )
        self.chainQuery = self.prompt_template_query | self.llm
        self.chainPrompt = self.prompt_template_answer | self.llm
        self.chainTest = 

    def createQuery(self, prompt):
        query = self.chainQuery.invoke({"database": self.schema, "text": prompt})
        return query

    def createAnswer(self, query):
        table = self.cur.execute(query)
        return table

    def runTask(self, prompt):
        query = self.createQuery(self, prompt)


ai = AiHandler()
for row in ai.createAnswer("SELECT * FROM ApartmentDetails"):
    print(row)
