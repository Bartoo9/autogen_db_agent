import os
import asyncio
import asyncpg
from dotenv import load_dotenv

# .env file
load_dotenv()

# variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

async def get_connection():
    """ Create and run a postgres connection """
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# async def test_connection():
#     conn = await get_connection()
#     print("connection successful")
#     await conn.close()

async def execute_query(query: str):
    conn = await get_connection()

    try:
        rows = await conn.fetch(query) # returns a list of records
        return [dict(row) for row in rows]  # convert to dict
    finally:
        await conn.close()

async def test_query():
    query = 'SELECT * FROM actor LIMIT 5;'
    results = await execute_query(query)

    for row in results:
        print(row)

if __name__ == "__main__":
    asyncio.run(test_query())