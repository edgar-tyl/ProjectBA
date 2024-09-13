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
    def __init__(self) -> None:
        self.tasks = {}
        self.results = {}
        self.task_number = 0

        self.llm = Ollama(model="Llama3-8b")
        if os.path.basename(os.getcwd()) == "ProjectBA":
            self.retriever = self.createRetriever("nomic-embed-text", "sql_examples_collection",os.path.join(".","databases","chroma_langchain_db"), 3 )
            self.db = SQLDatabase.from_uri("sqlite:///databases/real_estate.db")
        else:
            self.retriever = self.createRetriever("nomic-embed-text", "sql_examples_collection",os.path.join(".","ProjectBA","databases","chroma_langchain_db"), 3 )
            self.db = SQLDatabase.from_uri("sqlite:///ProjectBA/databases/real_estate.db")
        
        
        
        self.chainQuery = self.createSQLChain(self.llm)
        self.chainAnswer = self.createAnswerChain(self.llm)
        
    def runTask(self, prompt):
        examples = self.retrieveDocuments(prompt, self.retriever)

        sql_query = self.createSQLQuery(self.chainQuery, self.db, prompt, examples)
        table = self.queryDB(sql_query)
        while((table == None) or (self.validateQuery(sql_query) == False)):
            sql_query = self.createSQLQuery(self.chainQuery, self.db, prompt, examples)
            print(sql_query)
            table = self.queryDB(sql_query)
        
        answer = self.getAnswer(self.chainAnswer, sql_query, table, prompt)
        fullAnswer = f'''
        Question: {prompt}\n
        Examples: {examples}\n
        Query: {sql_query}\n
        Table: {table}\n
        Answer: {answer}
        '''
        return fullAnswer
    
    def format_document_list(self, items):
        return "\n".join([f"{item.page_content}\n" for item in items])
    
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

    @staticmethod
    def queryDB(sql_query):
        if os.path.basename(os.getcwd()) != "ProjectBA":
            con = sqlite3.connect(os.path.join(".","ProjectBA","databases","real_estate.db"))
        else:
            con = sqlite3.connect(os.path.join(".","databases","real_estate.db"))
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
    
    def createRetriever(self, model , collection_name, directory, amount):
        embeddings = OllamaEmbeddings(model = model)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=(directory),  
        )
        retriever = vector_store.as_retriever(search_kwargs={'k': amount})
        return retriever
    
    def retrieveDocuments(self, prompt, retriever):
        examples = self.format_document_list(retriever.invoke(prompt))
        return examples
    
    def createSQLChain(self, llm):
        template_queryRAG = '''Create a SQLite3 Query of the users question. It must be pure SQlite and add no indications that it is SQL. Do not explain that it is sql. And do not explain anything at all. U are not allowed to alter the database at all.
        Do not use qoutation marks to indicate that it is SQL. The sql statement must be executable immediatly. U only have read acces to the database. Limit the query to 10 results, unless it is stated otherwise in the question.
        DDL: {table_info}. 
        Question: {input}
        
        Here are a few example queries witch answer the question of a user, which may help you to generate a query:
        {examples}
        '''
        prompt_queryRAG = PromptTemplate.from_template(template_queryRAG)
        chainQuery = prompt_queryRAG | llm | StrOutputParser()
        return chainQuery
    
    def createAnswerChain(self, llm):
        template_answerRAG = '''Explain the data to the users question with the given sql table in JSON format in regards of the users question. The table was created with the given sqlite SELECT-Statement. 
        Only use data from the extracted table and do not make data up. You only need to explain the data to the users. There is no need to restate the data again for the user.
        Data extracted from Table: {table}.
        Query:{query} 
        Question: {input}'''
        prompt_answerRAG = PromptTemplate.from_template(template_answerRAG)
        chainAnswer = prompt_answerRAG | llm | StrOutputParser()
        return chainAnswer
    
    def createSQLQuery(self, chainQuery, db, prompt, examples):
        sql_query = chainQuery.invoke({"table_info": db.get_context(),"input":prompt, "examples": examples})           
        return sql_query
    
    def getSQLTable(self, sql_query):
        table = self.queryDB(sql_query)
        return table
    
    def getAnswer(self, chainAnswer, sql_query, table, prompt):
        answer = chainAnswer.invoke({"query": sql_query,"table": table, "input":prompt})
        return answer
    