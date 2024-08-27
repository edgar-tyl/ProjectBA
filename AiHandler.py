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
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from operator import itemgetter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
class AiHandler:
    def __init__(self) -> None:
        self.tasks = {}
        self.results = {}
        self.task_number = 0
        self.llm = Ollama(model="Llama3-8b")
        self.db = SQLDatabase.from_uri("sqlite:///ProjectBA/databases/real_estate.db")
        
        #print(self.db.dialect)
        #print(self.db.get_usable_table_names())
        #print(self.db.run("SELECT * FROM ApartmentDetails"))
        #https://python.langchain.com/v0.1/docs/use_cases/sql/quickstart/
        
        self.template_query = '''Create a SQLite3 Query of the users question. It must be pure SQlite and no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all
        {table_info}. If not stated otherwise use only the top {top_k} results.

        Question: {input}'''

        self.template_answer =     """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
        Use the following format for answering the quesstion:
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        Answer: """
        self.prompt_query = PromptTemplate.from_template(self.template_query)
        self.prompt_answer = PromptTemplate.from_template(self.template_answer) 
        self.answer = self.prompt_answer | self.llm | StrOutputParser()       
        execute_query = QuerySQLDataBaseTool(db=self.db)
        write_query = create_sql_query_chain(self.llm, self.db, self.prompt_query)
        self.chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
                )
                | self.answer
            )
        
    def runTask(self, prompt):
        answer = self.chain.invoke({"question": "{prompt}".format(prompt = prompt)})
        return answer
    
    def format_document_list(self, items):
        return "\n".join([f"{item.page_content}\n" for item in items])
    

    def createRetrievalChain(self,prompt):
        embeddings = OllamaEmbeddings(model = "nomic-embed-text")

        vector_store = Chroma(
            collection_name="sql_examples_collection",
            embedding_function=embeddings,
            persist_directory=(os.path.join(".","ProjectBA","databases","chroma_langchain_db")),  # Where to save data locally, remove if not neccesary
        )
        retriever = vector_store.as_retriever(search_kwargs={'k': 3})
        template_queryRAG = '''Create a SQLite3 Query of the users question. It must be pure SQlite and no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all
        {table_info}. 
        Question: {input}
        
        Here are a few example queries, which may help you to answer the question:
        {examples}
        '''
        
        template_answerRAG = '''Answer the users question with the given  sql table and the sql query.
        Query: {query}
        Data extracted from Table: {table}. 
        Question: {input}'''

        prompt_queryRAG = PromptTemplate.from_template(template_queryRAG)
        prompt_answerRAG = PromptTemplate.from_template(template_answerRAG)

        toolkit = QuerySQLDataBaseTool(db=self.db, llm=self.llm)
        examples = self.format_document_list(retriever.invoke(prompt))
        chainQuery = prompt_queryRAG | self.llm | StrOutputParser()
        sql_query = chainQuery.invoke({"table_info": self.db.get_context(),"input":prompt, "examples": examples})
        table = toolkit.invoke(sql_query)
        chainAnswer = prompt_answerRAG | self.llm | StrOutputParser()
        answer = chainAnswer.invoke({"query": sql_query,"table": table, "input":prompt})
        
        fullAnswer = f'''
        Question: {prompt}\n
        Query: {sql_query}\n
        Table: {table}
        Answer: {answer}
        '''
        
        return fullAnswer
        
