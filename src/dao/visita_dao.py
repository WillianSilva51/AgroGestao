import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (O JOIN DUPLO ACONTECE AQUI) ---
async def listar(filtro_obs=""):
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Nota: Juntamos Visita -> Tecnico -> Pessoa (para pegar o nome)
            # E juntamos Visita -> Propriedade
            sql = """
                SELECT 
                    v.id_visita,
                    pes.nome || ' (CREA: ' || t.crea || ')' as tecnico_fmt,
                    prop.nome_propriedade,
                    v.data_visita,
                    v.observacoes,
                    v.id_tecnico,     -- Oculto (para edição)
                    v.id_propriedade  -- Oculto (para edição)
                FROM Visita_tecnica v
                JOIN Tecnico t ON v.id_tecnico = t.id_pessoa
                JOIN Pessoa pes ON t.id_pessoa = pes.id_pessoa
                JOIN Propriedade prop ON v.id_propriedade = prop.id_propriedade
            """
            params = []
            if filtro_obs:
                sql += " WHERE v.observacoes ILIKE %s"
                params.append(f"%{filtro_obs}%")
            
            sql += " ORDER BY v.data_visita DESC"
            
            await cur.execute(sql, params)
            res = await cur.fetchall()
            
            colunas = ["id", "Técnico", "Propriedade", "Data", "Observações", "id_tec_oculto", "id_prop_oculto"]
            if not res: return pd.DataFrame(columns=colunas)
            
            return pd.DataFrame(res, columns=colunas)

# --- 2. AUXILIARES (PARA OS SELECTS) ---
async def get_opcoes_tecnico():
    """Busca apenas pessoas que são TÉCNICOS"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT p.nome || ' - ' || t.crea, t.id_pessoa 
                FROM Tecnico t
                JOIN Pessoa p ON t.id_pessoa = p.id_pessoa
                ORDER BY p.nome
            """)
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

async def get_opcoes_propriedade():
    """Reutiliza a lógica de propriedades"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT nome_propriedade, id_propriedade FROM Propriedade ORDER BY nome_propriedade")
            res = await cur.fetchall()
            return {row[0]: row[1] for row in res}

# --- 3. CRUD ---
async def salvar(id_visita, id_tecnico, id_propriedade, data, obs):
    pool = await get_pool()
    async with pool.connection() as conn:
        if id_visita: # Atualizar
            await conn.execute("""
                UPDATE Visita_tecnica 
                SET id_tecnico=%s, id_propriedade=%s, data_visita=%s, observacoes=%s
                WHERE id_visita=%s
            """, (id_tecnico, id_propriedade, data, obs, id_visita))
        else: # Inserir
            await conn.execute("""
                INSERT INTO Visita_tecnica (id_tecnico, id_propriedade, data_visita, observacoes)
                VALUES (%s, %s, %s, %s)
            """, (id_tecnico, id_propriedade, data, obs))

async def excluir(id_visita):
    pool = await get_pool()
    async with pool.connection() as conn:
        await conn.execute("DELETE FROM Visita_tecnica WHERE id_visita=%s", (id_visita,))

# --- 4. GRÁFICO ---
async def dados_grafico_visitas():
    """Conta quantas visitas cada técnico fez"""
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT p.nome, COUNT(*) as total
                FROM Visita_tecnica v
                JOIN Pessoa p ON v.id_tecnico = p.id_pessoa
                GROUP BY p.nome
            """)
            res = await cur.fetchall()
            return pd.DataFrame(res, columns=["Técnico", "Total Visitas"])