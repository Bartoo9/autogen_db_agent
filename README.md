## AutoGen Sakila Chat — AI-to-Database Query Tool

# Overview 

This project demonstrates how to use **[Microsoft AutoGen](https://microsoft.github.io/autogen/stable/index.html)** to build a simple **AI chat interface** that can answer natural-language questions using real data from the **Sakila database**.

It is designed as a technical prototype for demonstrating **AI + SQL + multi-agent system** interaction — where a Large Language Model (LLM) can translate prompts into safe SQL queries, execute them against a given database (in this case Sakila db), and return structured results in natural language.

# Agent Runtime 

User (prompt) -> LLM Agent (SQL query) -> DB Executor (result) -> Interpreter (response) -> Logger Agent

# Quick usage

1) Clone the repository 

```bash
git clone https://github.com/Bartoo9/autogen_db_agent.git
cd autogen_db_agent
```

2) .venv and dependencies 

python -m venv .venv
(Linux) source .venv/bin/activate
pip install -r requirements.txt

3) Local PostgreSQL instance (Sakila example)

**[Sakila](https://github.com/sakiladb/postgres?tab=readme-ov-file)**

4) Environment variables config

Set db connection strings and LLM credentials

example: 
DB_HOST=your_host
DB_PORT=your_port
...
OPEN_AI_API_KEY=sk-..
GEMINI_API_KEY=...

5) run the main entry point 



