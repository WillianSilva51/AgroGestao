import os
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv

load_dotenv()

if "DATABASE_URL" not in os.environ:
    raise EnvironmentError(
        "DATABASE_URL not found in environment variables. Please ensure DATABASE_URL is set "
        "in your .env file or environment variables."
    )

DATABASE_URL = os.environ["DATABASE_URL"]

_pool = None

async def get_pool():
    """
    Singleton: Cria e retorna uma pool de conexões assíncronas ao banco de dados PostgreSQL.
    Se o banco cair, a pool tentará se reconectar automaticamente.
    """
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(conninfo=DATABASE_URL, open=False, )
        await _pool.open()
    return _pool

async def close_pool():
    """
    Fecha a pool de conexões ao banco de dados.
    """
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None