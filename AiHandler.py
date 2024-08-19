import argparse 
import socket
import sys
import getpass
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
        with open(os.path.join("ProjectBA", "databases", "real_estate_ddl.sql"),"r") as file:
            self.schema = file.read()

        self.system_template = "Create a SQL-Query in Sqlite for the following Database based on the users question:\n{database}. Do not explain the queries."
        self.prompt_template = ChatPromptTemplate.from_messages(
            [("system", self.system_template), ("user", "{text}")]
        )
        self.chain = self.prompt_template | self.llm

    def runTask(self, prompt):
        result = self.chain.invoke({"database": self.schema, "text": prompt})
        return result