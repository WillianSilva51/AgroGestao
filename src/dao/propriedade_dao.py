import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (COM JOIN EM MUNICÍPIO) ---
async def listar(filtro_nome=""):
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            sql = """
                SELECT 
                    p.id_propriedade,
                    p.nome_propriedade,
                    p.registro_imovel,
                    m.nome_municipio || ' - ' || m.uf as localizacao,
                    p.area_total_hectares,
                    p.logradouro,
                    p.numero,
                    p.cep,
                    p.id_municipio
                FROM Propriedade p
                JOIN Municipio m ON p.id_municipio = m.id_municipio
            """
            params = []
            if filtro_nome:
                sql += " WHERE p.nome_propriedade ILIKE %s"
                params.append(f"%{filtro_nome}%")
            
            sql += " ORDER BY p.nome_propriedade"
            
            await cur.execute(sql, params)
            res = await cur.fetchall()
            
            # Nomes amigáveis para a tabela
            colunas = ["id", "Nome", "Registro", "Localização", "Área (ha)", "Logradouro", "Num", "CEP", "id_mun_oculto"]
            
            if not res: return pd.DataFrame(columns=colunas)
            
            df = pd.DataFrame(res, columns=colunas)
            
            # CORREÇÃO DO ERRO DECIMAL (CRUCIAL!)
            df["Área (ha)"] = df["Área (ha)"].astype(float)
            
            return df

# --- 2. AUXILIAR (MENU DE MUNICÍPIOS) ---
async def get_opcoes_municipio():
    """Retorna dicionário {'Quixadá - CE': 1, ...}"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT nome_municipio || ' - ' || uf, id_municipio FROM Municipio ORDER BY nome_municipio")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

# --- 3. CRUD (INSERIR, ATUALIZAR, EXCLUIR) ---
async def inserir(nome, registro, area, logradouro, numero, cep, id_municipio):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("""
            INSERT INTO Propriedade (nome_propriedade, registro_imovel, area_total_hectares, 
                                     logradouro, numero, cep, id_municipio)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, registro, area, logradouro, numero, cep, id_municipio))

async def atualizar(id_prop, nome, registro, area, logradouro, numero, cep, id_municipio):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("""
            UPDATE Propriedade 
            SET nome_propriedade=%s, registro_imovel=%s, area_total_hectares=%s,
                logradouro=%s, numero=%s, cep=%s, id_municipio=%s
            WHERE id_propriedade=%s
        """, (nome, registro, area, logradouro, numero, cep, id_municipio, id_prop))

async def excluir(id_prop):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("DELETE FROM Propriedade WHERE id_propriedade=%s", (id_prop,))

# --- 4. GRÁFICO (AGREGAÇÃO) ---
async def dados_grafico_municipio():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT m.nome_municipio, SUM(p.area_total_hectares) as total_area
                FROM Propriedade p
                JOIN Municipio m ON p.id_municipio = m.id_municipio
                GROUP BY m.nome_municipio
                ORDER BY total_area DESC
                LIMIT 5
            """)
            res = await cur.fetchall()
            df = pd.DataFrame(res, columns=["Município", "Total Hectares"])
            
            # CORREÇÃO DECIMAL
            if not df.empty:
                df["Total Hectares"] = df["Total Hectares"].astype(float)
            
            return df