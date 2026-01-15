import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (COM FILTRO DE SAFRA) ---
async def listar(filtro_safra=""):
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
            """
            params = []
            
            # Lógica de Filtro: Busca por Nome da Safra OU Ano Agrícola
            if filtro_safra:
                sql += " WHERE s.descricao_safra ILIKE %s OR s.ano_agricola ILIKE %s"
                params.append(f"%{filtro_safra}%")
                params.append(f"%{filtro_safra}%")
            
            sql += " ORDER BY pl.data_plantio DESC"
            
            await cur.execute(sql, params)
            res = await cur.fetchall()
            
            colunas = ["id", "Safra", "Cultura", "Propriedade", "Data Plantio", "Área (ha)"]
            if not res: return pd.DataFrame(columns=colunas)
            
            df = pd.DataFrame(res, columns=colunas)
            # Converte Decimal para Float (Correção do erro de serialização)
            df["Área (ha)"] = df["Área (ha)"].astype(float)
            
            return df

# --- 2. AUXILIARES (PARA OS SELECTS) ---
async def get_opcoes_safra():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT descricao_safra || ' ' || ano_agricola, id_safra FROM Safra ORDER BY ano_agricola DESC")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

async def get_opcoes_cultivo():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
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
            df = pd.DataFrame(res, columns=["Cultura", "Total Hectares"])
            
            if not df.empty:
                df["Total Hectares"] = df["Total Hectares"].astype(float)
                
            return df