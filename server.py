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
"""
if not os.environ.get("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = getpass.getpass()
if not os.environ["LANGCHAIN_TRACING_V2"] == "true":
    os.environ["LANGCHAIN_TRACING_V2"] == "true"
print("Hello")
"""

parser = argparse.ArgumentParser(description = "Tool to test the LLM")
parser.add_argument("--ip", type = str, required= True, help = "The IP-address used for binding")
parser.add_argument("-p", type = int, required = True, help = "The port used for binding")
args = parser.parse_args()
IP = args.ip
PORT = args.p

llm = Ollama(model="Llama3-8b")
with open(os.path.join("databases", "real_estate_ddl.sql"),"r") as file:
     schema = file.read()

system_template = "Create a SQL-Query in Sqlite for the following Database based on the users question:\n{database}. Do not explain the queries."
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)
chain = prompt_template | llm
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((IP, PORT))
    s.listen()
    try:
        while True:       
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(2048)
                    if not data:
                        break
                    
                    result = chain.invoke({"database": schema, "text": data.decode("utf-8")})
                    print(result)
                    conn.sendall(result.encode("utf-8"))
    except KeyboardInterrupt:
            print ("Server closing")
            s.close()
            print("Socket closed")
            sys.exit(0)
