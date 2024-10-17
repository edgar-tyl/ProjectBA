# ProjectBA

A web application for asking a LLM questions with the help of a database

## Description

This Project was written for a Bachelor thesis. It is an app created with Flask in Python. When entering the prompt, the LLM tries to create a SQL query.
The query will be executed afterwards. An answer is created based on the data received from the previous step.

## Getting Started

### Dependencies

* All libriaries in the requirments.txt
* Ollama and the LLMs(llama3.1:8b-instruct-q8_0, nomic-embed-text v1.5)
* Browser (Tested on Mozilla Firefox)
* (soft) Working backend for Ollama for faster LLM inference (ex. For NVIDIA users: CUDA-Toolkit)

### Installing

The installation guide is created with a Debian-based distro in mind. You may adjust some steps for your own distro or operating system.

Install Ollama in your enviroment with
```
curl -fsSL https://ollama.com/install.sh | sh
```

Pull the LLM from Ollama with
```
ollama pull llama3.1:8b-instruct-q8_0
```
and
```
ollama pull nomic-embed-text
```
You should see the LLM names "llama3.1:8b-instruct-q8_0" and "nomic-embed-text" when running
```
ollama list
```
The names must match exactly for running the app. Sometimes ":latest" is written behind the name. This does not matter.

Clone the repository wiht the following command:
```
git clone https://github.com/edgar-tyl/ProjectBA.git
```
Pip install the requirments from the requirments.txt with
```
pip install -r requirements.txt
```
### Executing program

* For launching the app run the command below in the directory where the app directory is located.
```
flask run
```

* For testint the app run the python module evaluate.py with the wanted options.

## Author

Edgar Melcher

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

* [text2sql-data] https://github.com/jkkummerfeld/text2sql-data
* [README-template.md] https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc
