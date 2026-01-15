import pandas as pd
from src.database import get_pool

# --- 1. LISTAR (TRAZ TUDO DE UMA VEZ) ---
async def listar(filtro_nome=""):
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # LEFT JOIN: Traz dados de Produtor e Técnico se existirem
            sql = """
                SELECT 
                    p.id_pessoa,
                    p.nome,
                    p.cpf,
                    p.data_nascimento,
                    pr.inscricao_estadual,
                    t.crea,
                    CASE WHEN pr.id_pessoa IS NOT NULL THEN 1 ELSE 0 END as is_produtor,
                    CASE WHEN t.id_pessoa IS NOT NULL THEN 1 ELSE 0 END as is_tecnico
                FROM Pessoa p
                LEFT JOIN Produtor pr ON p.id_pessoa = pr.id_pessoa
                LEFT JOIN Tecnico t ON p.id_pessoa = t.id_pessoa
            """
            params = []
            if filtro_nome:
                sql += " WHERE p.nome ILIKE %s"
                params.append(f"%{filtro_nome}%")
            
            sql += " ORDER BY p.nome"
            
            await cur.execute(sql, params)
            res = await cur.fetchall()
            
            colunas = ["id", "Nome", "CPF", "Nascimento", "Inscrição Est.", "CREA", "É Produtor?", "É Técnico?"]
            if not res: return pd.DataFrame(columns=colunas)
            
            df = pd.DataFrame(res, columns=colunas)
            
            # Converte booleans para True/False visuais
            df["É Produtor?"] = df["É Produtor?"].apply(lambda x: "Sim" if x else "Não")
            df["É Técnico?"] = df["É Técnico?"].apply(lambda x: "Sim" if x else "Não")
            
            return df

# --- 2. SALVAR (INSERIR OU ATUALIZAR) ---
# Esta função é "inteligente": ela gerencia Pessoa, Produtor e Técnico
async def salvar(id_pessoa, nome, cpf, nascimento, 
                 is_produtor, inscricao, 
                 is_tecnico, crea):
    
    pool = await get_pool()
    async with pool.connection() as conn:
        # 1. Gerenciar a PESSOA (Pai)
        if id_pessoa: # Atualizar Pessoa
            await conn.execute("""
                UPDATE Pessoa SET nome=%s, cpf=%s, data_nascimento=%s WHERE id_pessoa=%s
            """, (nome, cpf, nascimento, id_pessoa))
            novo_id = id_pessoa
        else: # Inserir Pessoa
            cur = await conn.execute("""
                INSERT INTO Pessoa (nome, cpf, data_nascimento) VALUES (%s, %s, %s) RETURNING id_pessoa
            """, (nome, cpf, nascimento))
            row = await cur.fetchone()
            novo_id = row[0]

        # 2. Gerenciar PRODUTOR
        if is_produtor:
            # Upsert (Insere ou Atualiza se já existe)
            await conn.execute("""
                INSERT INTO Produtor (id_pessoa, inscricao_estadual) VALUES (%s, %s)
                ON CONFLICT (id_pessoa) DO UPDATE SET inscricao_estadual = EXCLUDED.inscricao_estadual
            """, (novo_id, inscricao))
        else:
            # Se desmarcou a caixa, remove o papel de produtor
            await conn.execute("DELETE FROM Produtor WHERE id_pessoa=%s", (novo_id,))

        # 3. Gerenciar TÉCNICO
        if is_tecnico:
            await conn.execute("""
                INSERT INTO Tecnico (id_pessoa, crea) VALUES (%s, %s)
                ON CONFLICT (id_pessoa) DO UPDATE SET crea = EXCLUDED.crea
            """, (novo_id, crea))
        else:
            await conn.execute("DELETE FROM Tecnico WHERE id_pessoa=%s", (novo_id,))

# --- 3. EXCLUIR ---
async def excluir(id_pessoa):
    pool = await get_pool()
    async with pool.connection() as conn:
        # Remove dos filhos primeiro
        await conn.execute("DELETE FROM Produtor WHERE id_pessoa=%s", (id_pessoa,))
        await conn.execute("DELETE FROM Tecnico WHERE id_pessoa=%s", (id_pessoa,))
        # Remove do pai
        await conn.execute("DELETE FROM Pessoa WHERE id_pessoa=%s", (id_pessoa,))

# --- 4. GRÁFICO (NOVO) ---
async def dados_grafico_papeis():
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # Conta quantos de cada tipo existem
            await cur.execute("""
                SELECT 'Produtores' as tipo, COUNT(*) as total FROM Produtor
                UNION ALL
                SELECT 'Técnicos' as tipo, COUNT(*) as total FROM Tecnico
            """)
            res = await cur.fetchall()
            return pd.DataFrame(res, columns=["Tipo", "Total"])