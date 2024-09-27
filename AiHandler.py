"""
Class which contains the retriever, the llm and the means to query the db
Used by blueprint chat from 'chat.py'
"""

import sqlite3
import sqlglot
import os
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.utilities.sql_database import SQLDatabase

class AiHandler:
    def __init__(self, folder, RAG = False) -> None:
        #folder from which AiHandler is started
        self.folder = folder
        #Ollama is used for inference, must be same name as stated here in Ollama 
        self.llm = Ollama(model="llama3.1:8b-instruct-q8_0")
        self.retriever = self.createRetriever("nomic-embed-text", "sql_examples_collection",os.path.join(".",folder,"databases","chroma_langchain_db"), 3 )
        self.db = SQLDatabase.from_uri("sqlite:///" + folder + "/databases/real_estate.db")
        self.RAG = RAG
        self.chainQuery = self.createSQLChain(self.llm, RAG)
        self.chainAnswer = self.createAnswerChain(self.llm)

    #Basic implementation of RAG. Retriever collects examples. Afterwards query will be created with the help of these examples. Afterwards query DB for table
    #Table is used in last answer generation. Afterwards returns formatted answer    
    def runTask(self, prompt):
        examples = None
        if self.RAG:
            examples = self.retrieveDocuments(prompt, self.retriever)
        print(examples)
        sql_query = self.createSQLQuery(self.chainQuery, self.db, prompt, examples)
        table = self.queryDB(sql_query, self.folder)
        while((table == None) or (self.validateQuery(sql_query) == False)):
            sql_query = self.createSQLQuery(self.chainQuery, self.db, prompt, examples)
            print(sql_query)
            table = self.queryDB(sql_query, self.folder)
        
        answer = self.getAnswer(self.chainAnswer, sql_query, table, prompt)
        fullAnswer = f'''
        Question: {prompt}\n
        Examples: {examples}\n
        Query: {sql_query}\n
        Table: {table}\n
        Answer: {answer}
        '''
        return fullAnswer
    #only retrieve the page cpntent from documents
    def format_document_list(self, items):
        return "\n".join([f"{item.page_content}\n" for item in items])
    
    #Basic SQL Validator. Only select statements are allowed. Afterwards parse into sqglot-Parser for syntax validation
    def validateQuery(self, sql_query : str):
        sql_query = sql_query.replace("```", "")
        if "SELECT" != sql_query[:6]:
            print("Error: Not a SELECT statement")
            return False
        print("Results: ")
        try:
            sqlglot.parse(sql_query, read="sqlite")
        except sqlglot.errors.ParseError:
            print("Error: Invalid SQL-expression")
            return False
        print("Valid SQL")
        return True

    #Queries DB and format it as a list of dict. LLM understands data better with the labels instead of only the raw data
    @staticmethod
    def queryDB(sql_query, folder):
        con = sqlite3.connect(os.path.join(".", folder ,"databases","real_estate.db"))
        cur = con.cursor()
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
    #creates retriever with langchain from Chroma
    def createRetriever(self, model , collection_name, directory, amount):
        embeddings = OllamaEmbeddings(model = model)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=(directory),  
        )
        retriever = vector_store.as_retriever(search_kwargs={'k': amount})
        return retriever
    #uses retriever to retrieve relevant documents. Only list of page content is returned
    def retrieveDocuments(self, prompt, retriever):
        examples = self.format_document_list(retriever.invoke(prompt))
        return examples
    
    #simple chain with single prompt template for creating sql-queries with the help of examples and the ddl of the database
    def createSQLChain(self, llm, RAG):
        if(RAG):
            template_queryRAG = '''Create a SQLite3 Query of the users question. It must be pure SQlite and add no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all. U are not allowed to alter the database at all.
            Do not use qoutation marks to indicate that it is SQL. The sql statement must be executable immediatly. U only have read acces to the database.
            DDL: {table_info}. 
            Question: {input}

            Here are a few example queries witch answer the question of a user, which may help you to generate a query:
            {examples}
            '''
        else:
            template_queryRAG = '''Create a SQLite3 Query of the users question. It must be pure SQlite and add no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all. U are not allowed to alter the database at all.
            Do not use qoutation marks to indicate that it is SQL. The sql statement must be executable immediatly. U only have read acces to the database.
            DDL: {table_info}. 
            Question: {input}

            '''
        prompt_queryRAG = PromptTemplate.from_template(template_queryRAG)
        chainQuery = prompt_queryRAG | llm | StrOutputParser()
        return chainQuery
    
    #simple chain with single prompt template for creating sql-queries
    def createAnswerChain(self, llm):
        template_answerRAG = '''Explain the data to the users question with the given sql table in JSON format in regards of the users question. The table was created with the given sqlite SELECT-Statement. 
        Only use data from the extracted table and do not make data up. You only need to explain the data to the users. There is no need to restate the data again for the user.
        Data extracted from Table: {table}.
        Query:{query} 
        Question: {input}'''
        prompt_answerRAG = PromptTemplate.from_template(template_answerRAG)
        chainAnswer = prompt_answerRAG | llm | StrOutputParser()
        return chainAnswer
    
    def createSQLQuery(self, chainQuery, db, prompt, examples=None):
        if examples is not None:
            sql_query = chainQuery.invoke({"table_info": db.get_context(),"input":prompt, "examples": examples})
        else :
            sql_query = chainQuery.invoke({"table_info": db.get_context(),"input":prompt})           
        return sql_query
    
    def getSQLTable(self, sql_query):
        table = self.queryDB(sql_query)
        return table
    
    def getAnswer(self, chainAnswer, sql_query, table, prompt):
        answer = chainAnswer.invoke({"query": sql_query,"table": table, "input":prompt})
        return answer
    