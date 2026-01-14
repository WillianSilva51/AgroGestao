import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (JOIN COM NOMES REAIS) ---
async def listar():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            sql = """
                SELECT 
                    pl.id_plantio,
                    s.descricao_safra || ' (' || s.ano_agricola || ')' as safra_fmt,
                    c.nome_cultura || ' - ' || c.variedade as cultura_fmt,
                    prop.nome_propriedade,
                    pl.data_plantio,
                    pl.area_plantada_hectares
                FROM Plantio pl
                JOIN Safra s ON pl.id_safra = s.id_safra
                JOIN Cultivo c ON pl.id_cultivo = c.id_cultivo
                JOIN Propriedade prop ON pl.id_propriedade = prop.id_propriedade
                ORDER BY pl.data_plantio DESC
            """
            await cur.execute(sql)
            res = await cur.fetchall()
            
            colunas = ["id", "Safra", "Cultura", "Propriedade", "Data Plantio", "Área (ha)"]
            if not res: return pd.DataFrame(columns=colunas)
            
            df = pd.DataFrame(res, columns=colunas)
            
            df["Área (ha)"] = df["Área (ha)"].astype(float)
            
            return df

# --- 2. AUXILIARES (PARA OS SELECTS) ---
async def get_opcoes_safra():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Concatena descricao e ano para ficar bonito no menu
            await cur.execute("SELECT descricao_safra || ' ' || ano_agricola, id_safra FROM Safra ORDER BY ano_agricola DESC")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

async def get_opcoes_cultivo():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Mostra Cultura + Variedade
            await cur.execute("SELECT nome_cultura || ' (' || variedade || ')', id_cultivo FROM Cultivo ORDER BY nome_cultura")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

async def get_opcoes_propriedade():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT nome_propriedade, id_propriedade FROM Propriedade ORDER BY nome_propriedade")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

# --- 3. CRUD (INSERIR, ATUALIZAR, EXCLUIR) ---
async def inserir(id_safra, id_cultivo, id_prop, data_plantio, area):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("""
            INSERT INTO Plantio (id_safra, id_cultivo, id_propriedade, data_plantio, area_plantada_hectares)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_safra, id_cultivo, id_prop, data_plantio, area))

async def atualizar(id_plantio, id_safra, id_cultivo, id_prop, data_plantio, area):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("""
            UPDATE Plantio 
            SET id_safra=%s, id_cultivo=%s, id_propriedade=%s, 
                data_plantio=%s, area_plantada_hectares=%s
            WHERE id_plantio=%s
        """, (id_safra, id_cultivo, id_prop, data_plantio, area, id_plantio))

async def excluir(id_plantio):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("DELETE FROM Plantio WHERE id_plantio=%s", (id_plantio,))

# --- 4. GRÁFICO ---
async def dados_grafico_cultura():
    """Conta hectares plantados por tipo de cultura"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT c.nome_cultura, SUM(pl.area_plantada_hectares) as total_ha
                FROM Plantio pl
                JOIN Cultivo c ON pl.id_cultivo = c.id_cultivo
                GROUP BY c.nome_cultura
            """)
            res = await cur.fetchall()
            return pd.DataFrame(res, columns=["Cultura", "Total Hectares"])