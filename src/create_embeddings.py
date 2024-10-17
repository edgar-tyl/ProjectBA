#Creates embeddings from JSON file with questions, sql and id elements . Uses ChromaDB
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from langchain_core.documents import Document
import json

class Embedder:

    def __init__(self):
        self.embeddings = OllamaEmbeddings(model = "nomic-embed-text")

        self.vector_store = Chroma(
            collection_name="sql_examples_collection",
            embedding_function=self.embeddings,
            persist_directory=(os.path.join(".","databases","chroma_langchain_db")), 
        )

    @staticmethod
    def getListFromJSON(filepath):
        with open(filepath) as data_file:    
            data = json.load(data_file)
            docList = []
            for item in data:
                docList.append(Document(
                    page_content= "question: " + item.get("question") + "\n" + "sql: " + item.get("sql"),
                    id= item.get("id")
            ))
        
        print(docList[:1])

        return docList
    
    def createEmbeddings(self, docList):
        listId =[str(item) for item in range(0, len(docList))]
        self.vector_store.add_documents(documents=docList, ids=listId)

    def similarity(self, text):
        results = self.vector_store.similarity_search(
            text,
            k=3
        )
        return results

       

ai = Embedder()
List = ai.getListFromJSON(os.path.join(".","databases","sql_examples.json"))
ai.createEmbeddings(List)
