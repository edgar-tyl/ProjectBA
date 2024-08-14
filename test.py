import argparse 
import socket
import sys

parser = argparse.ArgumentParser(description = "Tool to test the LLM")
parser.add_argument("--ip", type = str, required= True, help = "The IP-address of the service you are connecting to")
parser.add_argument("-p", type = int, required = True, help = "The open port of the service")
args = parser.parse_args()
IP = args.ip
PORT = args.p

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((IP, PORT))
    while True:
        try:
            query = input("Enter your Query: ")
            s.sendall(query.encode('utf-8'))
            data = s.recv(2048)
            print(data.decode('utf-8'))
        except KeyboardInterrupt:
            s.close()
            print("Socket closed")
            sys.exit(0)

