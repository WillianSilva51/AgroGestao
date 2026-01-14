import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (READ) ---
async def listar(filtro_nome=""):
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Fazemos um JOIN para "juntar" os dados de Pessoa e Produtor
            sql = """
                SELECT p.id_pessoa, p.nome, p.cpf, p.data_nascimento, pr.inscricao_estadual
                FROM Pessoa p
                JOIN Produtor pr USING (id_pessoa)
            """
            params = []
            
            # Lógica de Filtro (Requisito da Entrega)
            if filtro_nome:
                sql += " WHERE p.nome ILIKE %s"
                params.append(f"%{filtro_nome}%")
            
            sql += " ORDER BY p.nome"
            
            await cur.execute(sql, params)
            registros = await cur.fetchall()
            
            # Retorna DataFrame (se vazio, define colunas para não quebrar a tela)
            if not registros:
                return pd.DataFrame(columns=["id_pessoa", "nome", "cpf", "data_nascimento", "inscricao_estadual"])
            
            colunas = [desc[0] for desc in cur.description] if cur.description else []
            return pd.DataFrame(registros, columns=colunas)

# --- 2. INSERIR (CREATE) ---
async def inserir(nome, cpf, nascimento, inscricao):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("""
            WITH nova_pessoa AS (
                INSERT INTO Pessoa (nome, cpf, data_nascimento)
                VALUES (%s, %s, %s)
                RETURNING id_pessoa
            )
            INSERT INTO Produtor (id_pessoa, inscricao_estadual)
            SELECT id_pessoa, %s FROM nova_pessoa
        """, (nome, cpf, nascimento, inscricao))

# --- 3. ATUALIZAR (UPDATE) ---
async def atualizar(id_pessoa, nome, cpf, nascimento, inscricao):
    pool = await get_pool()
    async with pool.connection() as conn:
        # Atualiza Pessoa
        await conn.execute("""
            UPDATE Pessoa 
            SET nome=%s, cpf=%s, data_nascimento=%s 
            WHERE id_pessoa=%s
        """, (nome, cpf, nascimento, id_pessoa))
        
        # Atualiza Produtor
        await conn.execute("""
            UPDATE Produtor 
            SET inscricao_estadual=%s 
            WHERE id_pessoa=%s
        """, (inscricao, id_pessoa))

# --- 4. EXCLUIR (DELETE) ---
async def excluir(id_pessoa):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("DELETE FROM Produtor WHERE id_pessoa=%s", (id_pessoa,))
        await conn.execute("DELETE FROM Pessoa WHERE id_pessoa=%s", (id_pessoa,))

# --- 5. DADOS PARA O GRÁFICO ---
async def dados_grafico_idade():
    """Conta produtores por faixa etária (Exemplo de agregação)"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    CASE 
                        WHEN EXTRACT(YEAR FROM AGE(data_nascimento)) < 30 THEN 'Jovem (<30)'
                        WHEN EXTRACT(YEAR FROM AGE(data_nascimento)) BETWEEN 30 AND 50 THEN 'Adulto (30-50)'
                        ELSE 'Sênior (>50)'
                    END as faixa_etaria,
                    COUNT(*) as total
                FROM Pessoa p
                JOIN Produtor pr USING (id_pessoa)
                GROUP BY 1
            """)
            res = await cur.fetchall()
            return pd.DataFrame(res, columns=["faixa_etaria", "total"])