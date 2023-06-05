# Smolex: A code retrieval ChatGPT Plugin

**Experimental: Smolex is very experimental, mostly thrown together to serve my own needs!**

### Motivation

Sometimes I have a chat with ChatGPT about a piece of code and want to provide it with more context about my codebase.
So far I did manually craft a context to provide to ChatGPT, but this is tedious when also considering the token limit.

Smolex is an experimental plugin for ChatGPT that allows ChatGPT to lookup code context in a codebase and use that as
context for the conversation. This allows for more natural conversations about code.

### How to use it

```
...

Me: Look up the correct class interface for the notebook repo and update your suggestion accordingly.
ChatGPT (usig Smolex): I have updated the suggestion using NotebookRepository...

...
```

### How it works

We create embeddings for all code in the codebase and store them locally. We also AST parse all code and store that in a
local SQLite database. When a user asks a question, we try to look up the requested code in the database and either
return the entire code or a summary of the code ("interface"). In case we have no match in the database, we use the
vector store to find the code (or interface) that might be most relevant to the question.

## Setup

### Install dependencies

```
pip install -r requirements.txt
```

### Run API server

```
# update config.py with your codebase path

export OPENAI_API_KEY=<your key>
python ./main.py
```

### Install plugin

- Plugin Store -> Develop your own plugin -> localhost:5003

### Re-index codebase (as needed)

```
python ./index.py
```