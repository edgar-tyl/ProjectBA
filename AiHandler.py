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
        
        
    def runTask(self, prompt):
        answer = self.chain.invoke({"question": "{prompt}".format(prompt = prompt)})
        return answer
    
    def format_document_list(self, items):
        return "\n".join([f"{item.page_content}\n" for item in items])
    

    
    def queryDB(self, sql_query):
        con = sqlite3.connect("./ProjectBA/databases/real_estate.db")
        cur = con.cursor()
        cur.execute(sql_query)
        #https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
        headers = list(map(lambda attr : attr[0], cur.description))
        print(headers)
        results = [{header:row[i] for i, header in enumerate(headers)} for row in cur]
        return results
    
    def createRetriever(self, model , collection_name, directory, amount):
        embeddings = OllamaEmbeddings(model = model)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=(directory),  # Where to save data locally, remove if not neccesary
        )
        retriever = vector_store.as_retriever(search_kwargs={'k': amount})
        return retriever
    

    def createRetrievalChain(self,prompt):

        retriever = self.createRetriever("nomic-embed-text", "sql_examples_collection",os.path.join(".","ProjectBA","databases","chroma_langchain_db"), 3 )
        template_queryRAG = '''Create a SQLite3 Query of the users question. It must be pure SQlite and no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all. U are not allowed to alter the database at all.
        Do not use qoutation marks to indicate that it is SQL. The sql statement must be executable immediatly.
        {table_info}. 
        Question: {input}
        
        Here are a few example queries, which may help you to answer the question:
        {examples}
        '''
        
        template_answerRAG = '''Answer the users question with the given sql table in JSON format. Only use data from the extracted table and do not make data up.
        Data extracted from Table: {table}.
        Query:{query} 
        Question: {input}'''
        prompt_queryRAG = PromptTemplate.from_template(template_queryRAG)
        prompt_answerRAG = PromptTemplate.from_template(template_answerRAG)

        examples = self.format_document_list(retriever.invoke(prompt))
        chainQuery = prompt_queryRAG | self.llm | StrOutputParser()
        sql_query = chainQuery.invoke({"table_info": self.db.get_context(),"input":prompt, "examples": examples})
        print(sql_query)
        table = self.queryDB(sql_query)
        chainAnswer = prompt_answerRAG | self.llm | StrOutputParser()
        answer = chainAnswer.invoke({"query": sql_query,"table": table, "input":prompt})
        
        fullAnswer = f'''
        Question: {prompt}\n
        Query: {sql_query}\n
        Table: {table}\n
        Answer: {answer}
        '''
        
        return fullAnswer
        
