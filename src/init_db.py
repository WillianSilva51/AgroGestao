import asyncio
import os

from click import confirm
from src.database import get_pool
from psycopg import sql

async def init_db():
    print("Iniciando a inicialização do banco de dados...")
    
    caminho_sql = os.path.join("database", "init.sql")
    
    if not os.path.exists(caminho_sql):
        print(f"Erro: Arquivo não encontrado em {caminho_sql}")
        return
    
    with open(caminho_sql, "r", encoding="utf-8") as arquivo_sql:
        comandos_sql = arquivo_sql.read()
        
    try:
        pool = await get_pool()
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql.SQL(comandos_sql))
                print("Banco de dados inicializado com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")        
        
if __name__ == "__main__":
    confirmacao = confirm("Tem certeza que deseja inicializar o banco de dados? Isso pode apagar dados existentes.", default=False)
    
    if not confirmacao:
        print("Inicialização do banco de dados cancelada.")
        exit(0)
    # Roda a função async
    asyncio.run(init_db())