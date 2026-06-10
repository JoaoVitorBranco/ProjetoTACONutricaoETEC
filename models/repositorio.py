from typing import List, Optional
from database.db import get_connection
from models.modelos import Alimento, Cardapio, Refeicao, ItemRefeicao


# ── Alimentos ─────────────────────────────────────────────────────────────────

def buscar_alimentos(termo: str = "", grupo: str = "") -> List[Alimento]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM alimentos WHERE 1=1"
    params = []
    if termo:
        query += " AND descricao LIKE ?"
        params.append(f"%{termo}%")
    if grupo:
        query += " AND grupo = ?"
        params.append(grupo)
    query += " ORDER BY grupo, descricao"
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return [_row_to_alimento(r) for r in rows]


def listar_grupos() -> List[str]:
    """Retorna lista de todos os grupos (tabela grupos + grupos em alimentos)."""
    conn = get_connection()
    
    # Grupos da tabela grupos
    grupos_tabela = conn.execute("SELECT DISTINCT nome FROM grupos ORDER BY nome").fetchall()
    grupos_set = set(r["nome"] for r in grupos_tabela)
    
    # Grupos que existem em alimentos
    grupos_alimentos = conn.execute("SELECT DISTINCT grupo FROM alimentos ORDER BY grupo").fetchall()
    for r in grupos_alimentos:
        grupos_set.add(r["grupo"])
    
    conn.close()
    return sorted(list(grupos_set))


def buscar_alimento_por_id(alimento_id: int) -> Optional[Alimento]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM alimentos WHERE id = ?", (alimento_id,)).fetchone()
    conn.close()
    return _row_to_alimento(row) if row else None


def _row_to_alimento(row) -> Alimento:
    return Alimento(
        id=row["id"],
        grupo=row["grupo"],
        descricao=row["descricao"],
        calorias=row["calorias"],
        proteinas=row["proteinas"],
        lipideos=row["lipideos"],
        carboidratos=row["carboidratos"],
        fonte=row["fonte"],
    )


# ── Cardápios ─────────────────────────────────────────────────────────────────

def listar_cardapios() -> List[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, nome, kcal_total, data_criacao FROM cardapios ORDER BY data_criacao DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def carregar_cardapio(cardapio_id: int) -> Optional[Cardapio]:
    conn = get_connection()

    row = conn.execute("SELECT * FROM cardapios WHERE id = ?", (cardapio_id,)).fetchone()
    if not row:
        conn.close()
        return None

    cardapio = Cardapio(
        id=row["id"],
        nome=row["nome"],
        kcal_total=row["kcal_total"],
        data_criacao=row["data_criacao"],
    )

    ref_rows = conn.execute(
        "SELECT * FROM refeicoes WHERE cardapio_id = ? ORDER BY ordem", (cardapio_id,)
    ).fetchall()

    for ref_row in ref_rows:
        refeicao = Refeicao(
            id=ref_row["id"],
            nome=ref_row["nome"],
            percentual=ref_row["percentual"],
            kcal_diaria=cardapio.kcal_total,
            ordem=ref_row["ordem"],
        )

        item_rows = conn.execute("""
            SELECT ra.id, ra.quantidade_g, a.*
            FROM refeicao_alimentos ra
            JOIN alimentos a ON a.id = ra.alimento_id
            WHERE ra.refeicao_id = ?
        """, (refeicao.id,)).fetchall()

        for item_row in item_rows:
            alimento = Alimento(
                id=item_row["id"],
                grupo=item_row["grupo"],
                descricao=item_row["descricao"],
                calorias=item_row["calorias"],
                proteinas=item_row["proteinas"],
                lipideos=item_row["lipideos"],
                carboidratos=item_row["carboidratos"],
                fonte=item_row["fonte"],
            )
            refeicao.itens.append(ItemRefeicao(
                id=item_row["id"],
                alimento=alimento,
                quantidade_g=item_row["quantidade_g"],
            ))

        cardapio.refeicoes.append(refeicao)

    conn.close()
    return cardapio


def salvar_cardapio(cardapio: Cardapio) -> int:
    """Insere ou atualiza o cardápio. Retorna o id."""
    conn = get_connection()
    cursor = conn.cursor()

    if cardapio.id is None:
        cursor.execute(
            "INSERT INTO cardapios (nome, kcal_total) VALUES (?, ?)",
            (cardapio.nome, cardapio.kcal_total),
        )
        cardapio.id = cursor.lastrowid
    else:
        cursor.execute(
            "UPDATE cardapios SET nome = ?, kcal_total = ? WHERE id = ?",
            (cardapio.nome, cardapio.kcal_total, cardapio.id),
        )
        cursor.execute("DELETE FROM refeicoes WHERE cardapio_id = ?", (cardapio.id,))

    for ordem, refeicao in enumerate(cardapio.refeicoes):
        cursor.execute(
            "INSERT INTO refeicoes (cardapio_id, nome, percentual, ordem) VALUES (?, ?, ?, ?)",
            (cardapio.id, refeicao.nome, refeicao.percentual, ordem),
        )
        refeicao_id = cursor.lastrowid

        for item in refeicao.itens:
            cursor.execute(
                "INSERT INTO refeicao_alimentos (refeicao_id, alimento_id, quantidade_g) VALUES (?, ?, ?)",
                (refeicao_id, item.alimento.id, item.quantidade_g),
            )

    conn.commit()
    conn.close()
    return cardapio.id


def excluir_cardapio(cardapio_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM cardapios WHERE id = ?", (cardapio_id,))
    conn.commit()
    conn.close()


# ── Gerenciamento de Alimentos e Grupos ──────────────────────────────────────

def adicionar_alimento(grupo: str, descricao: str, calorias: float, 
                       proteinas: float, lipideos: float, carboidratos: float) -> int:
    """Adiciona um novo alimento com fonte 'usuario'. Retorna o id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alimentos (grupo, descricao, calorias, proteinas, lipideos, carboidratos, fonte)
        VALUES (?, ?, ?, ?, ?, ?, 'usuario')
    """, (grupo, descricao, calorias, proteinas, lipideos, carboidratos))
    alimento_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alimento_id


def editar_alimento(alimento_id: int, grupo: str, descricao: str, 
                    calorias: float, proteinas: float, lipideos: float, carboidratos: float):
    """Edita um alimento existente (apenas se fonte = 'usuario')."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se é alimento do usuário
    row = cursor.execute("SELECT fonte FROM alimentos WHERE id = ?", (alimento_id,)).fetchone()
    if not row or row["fonte"] != "usuario":
        conn.close()
        raise ValueError("Apenas alimentos criados pelo usuário podem ser editados.")
    
    cursor.execute("""
        UPDATE alimentos 
        SET grupo = ?, descricao = ?, calorias = ?, proteinas = ?, lipideos = ?, carboidratos = ?
        WHERE id = ?
    """, (grupo, descricao, calorias, proteinas, lipideos, carboidratos, alimento_id))
    
    conn.commit()
    conn.close()


def excluir_alimento(alimento_id: int):
    """Exclui um alimento (apenas se fonte = 'usuario')."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se é alimento do usuário
    row = cursor.execute("SELECT fonte FROM alimentos WHERE id = ?", (alimento_id,)).fetchone()
    if not row or row["fonte"] != "usuario":
        conn.close()
        raise ValueError("Apenas alimentos criados pelo usuário podem ser excluídos.")
    
    cursor.execute("DELETE FROM alimentos WHERE id = ?", (alimento_id,))
    conn.commit()
    conn.close()


def criar_grupo(nome_grupo: str):
    """Cria um novo grupo na tabela grupos."""
    nome_grupo = nome_grupo.strip()
    if not nome_grupo:
        raise ValueError("O nome do grupo não pode estar vazio.")
    
    # Verifica se já existe (case-insensitive)
    grupos_existentes = listar_grupos()
    if nome_grupo.lower() in [g.lower() for g in grupos_existentes]:
        raise ValueError(f"O grupo '{nome_grupo}' já existe.")
    
    # Insere na tabela grupos
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO grupos (nome, fonte) VALUES (?, 'usuario')", (nome_grupo,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
    
    return nome_grupo


def excluir_grupo(nome_grupo: str):
    """Exclui um grupo da tabela grupos se não tiver alimentos associados."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se o grupo existe na tabela grupos
    grupo_row = cursor.execute("SELECT fonte FROM grupos WHERE nome = ?", (nome_grupo,)).fetchone()
    
    if not grupo_row:
        # Grupo só existe em alimentos (TACO), não pode excluir
        conn.close()
        raise ValueError(f"O grupo '{nome_grupo}' é da base TACO e não pode ser excluído.")
    
    if grupo_row["fonte"] != "usuario":
        conn.close()
        raise ValueError(f"O grupo '{nome_grupo}' é do sistema e não pode ser excluído.")
    
    # Verifica se há alimentos no grupo
    count = cursor.execute(
        "SELECT COUNT(*) as total FROM alimentos WHERE grupo = ?", 
        (nome_grupo,)
    ).fetchone()["total"]
    
    if count > 0:
        conn.close()
        raise ValueError(
            f"Não é possível excluir o grupo '{nome_grupo}' pois existem {count} "
            f"alimento(s) associado(s). Remova ou reclassifique os alimentos primeiro."
        )
    
    # Remove da tabela grupos
    cursor.execute("DELETE FROM grupos WHERE nome = ?", (nome_grupo,))
    conn.commit()
    conn.close()
    return True


def contar_alimentos_por_grupo(nome_grupo: str) -> dict:
    """Retorna contagem de alimentos de um grupo separado por fonte."""
    conn = get_connection()
    cursor = conn.cursor()
    
    total = cursor.execute(
        "SELECT COUNT(*) as n FROM alimentos WHERE grupo = ?",
        (nome_grupo,)
    ).fetchone()["n"]
    
    taco = cursor.execute(
        "SELECT COUNT(*) as n FROM alimentos WHERE grupo = ? AND fonte = 'taco'",
        (nome_grupo,)
    ).fetchone()["n"]
    
    usuario = total - taco
    
    conn.close()
    return {"total": total, "taco": taco, "usuario": usuario}


# ── Exportar / Importar ──────────────────────────────────────────────────────

def exportar_alimentos_para_excel(caminho_arquivo: str) -> int:
    """Exporta todos os alimentos para um arquivo Excel. Retorna quantidade exportada."""
    import pandas as pd
    
    conn = get_connection()
    
    # Query todos os alimentos (SEM a coluna fonte)
    query = """
        SELECT grupo, descricao, calorias, proteinas, carboidratos, lipideos
        FROM alimentos
        ORDER BY grupo, descricao
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Renomear colunas para ficar mais legível
    df.rename(columns={
        'grupo': 'Grupo',
        'descricao': 'Descrição',
        'calorias': 'Calorias (kcal)',
        'proteinas': 'Proteínas (g)',
        'carboidratos': 'Carboidratos (g)',
        'lipideos': 'Lipídeos (g)',
    }, inplace=True)
    
    # Salvar
    df.to_excel(caminho_arquivo, index=False, engine='openpyxl')
    
    return len(df)


def importar_alimentos_de_excel(caminho_arquivo: str) -> dict:
    """
    Importa alimentos de um arquivo Excel.
    Valida a fonte (TACO vs usuário) comparando com a TACO embutida.
    Retorna dict com estatísticas: {criados, atualizados, erros, detalhes_erros}
    """
    import pandas as pd
    import os
    import sys
    
    # Lê o Excel do usuário
    try:
        df = pd.read_excel(caminho_arquivo, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo Excel: {str(e)}")
    
    # Valida colunas (SEM fonte)
    colunas_esperadas = ['Grupo', 'Descrição', 'Calorias (kcal)', 'Proteínas (g)', 
                         'Carboidratos (g)', 'Lipídeos (g)']
    
    for col in colunas_esperadas:
        if col not in df.columns:
            raise ValueError(f"Coluna '{col}' não encontrada no arquivo Excel.")
    
    # Carrega TACO embutida para validação de fonte
    if getattr(sys, 'frozen', False):
        # Executável
        base_path = sys._MEIPASS
    else:
        # Desenvolvimento
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    caminho_taco = os.path.join(base_path, "taco", "Taco.xlsx")
    
    # Lê TACO para criar conjunto de alimentos TACO
    alimentos_taco = set()
    try:
        df_taco = pd.read_excel(caminho_taco, usecols=["Grupo", "Descrição do Alimento"])
        for _, row in df_taco.iterrows():
            grupo = str(row['Grupo']).strip().lower()
            desc = str(row['Descrição do Alimento']).strip().lower()
            if grupo != 'nan' and desc != 'nan':
                alimentos_taco.add((grupo, desc))
    except:
        # Se não conseguir ler TACO, continua sem validação de fonte
        pass
    
    conn = get_connection()
    cursor = conn.cursor()
    
    criados = 0
    atualizados = 0
    erros = 0
    detalhes_erros = []
    
    for idx, row in df.iterrows():
        linha = idx + 2  # +2 porque Excel começa em 1 e tem cabeçalho
        
        try:
            # Validações
            grupo = str(row['Grupo']).strip()
            descricao = str(row['Descrição']).strip()
            
            if not grupo or grupo == 'nan':
                raise ValueError("Grupo vazio")
            if not descricao or descricao == 'nan':
                raise ValueError("Descrição vazia")
            
            calorias = float(row['Calorias (kcal)'])
            proteinas = float(row['Proteínas (g)'])
            carboidratos = float(row['Carboidratos (g)'])
            lipideos = float(row['Lipídeos (g)'])
            
            if any(v < 0 for v in [calorias, proteinas, carboidratos, lipideos]):
                raise ValueError("Valores negativos")
            
            # Determina fonte: verifica se está na TACO embutida
            chave = (grupo.lower(), descricao.lower())
            fonte = 'taco' if chave in alimentos_taco else 'usuario'
            
            # Cria grupo se não existir
            grupos_existentes = listar_grupos()
            if grupo not in grupos_existentes:
                try:
                    criar_grupo(grupo)
                except:
                    pass  # Grupo já existe ou foi criado por outra linha
            
            # Verifica se alimento já existe (grupo + descrição, case-insensitive)
            existe = cursor.execute("""
                SELECT id, fonte FROM alimentos 
                WHERE LOWER(grupo) = LOWER(?) AND LOWER(descricao) = LOWER(?)
            """, (grupo, descricao)).fetchone()
            
            if existe:
                # Atualiza (mantém a fonte original)
                cursor.execute("""
                    UPDATE alimentos
                    SET calorias = ?, proteinas = ?, lipideos = ?, carboidratos = ?
                    WHERE id = ?
                """, (calorias, proteinas, lipideos, carboidratos, existe['id']))
                atualizados += 1
            else:
                # Cria novo com fonte determinada
                cursor.execute("""
                    INSERT INTO alimentos (grupo, descricao, calorias, proteinas, lipideos, carboidratos, fonte)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (grupo, descricao, calorias, proteinas, lipideos, carboidratos, fonte))
                criados += 1
        
        except Exception as e:
            erros += 1
            detalhes_erros.append(f"Linha {linha}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    return {
        'criados': criados,
        'atualizados': atualizados,
        'erros': erros,
        'detalhes_erros': detalhes_erros
    }


def restaurar_base_taco() -> int:
    """
    Restaura alimentos da base TACO aos valores originais usando TACO embutida.
    Sobrescreve apenas alimentos com fonte='taco'.
    Retorna quantidade de alimentos restaurados.
    """
    import pandas as pd
    import os
    import sys
    
    # Localiza TACO embutida
    if getattr(sys, 'frozen', False):
        # Executável
        base_path = sys._MEIPASS
    else:
        # Desenvolvimento
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    caminho_taco = os.path.join(base_path, "taco", "Taco.xlsx")
    
    if not os.path.exists(caminho_taco):
        raise ValueError(f"Arquivo TACO não encontrado em: {caminho_taco}")
    
    # Lê o Excel da TACO
    try:
        df = pd.read_excel(caminho_taco, usecols=[
            "Grupo", "Descrição do Alimento", "Energia(kcal)", 
            "Proteína(g)", "Lipídeos(g)", "Carboidrato(g)"
        ])
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo TACO: {str(e)}")
    
    # Renomeia colunas
    df.rename(columns={
        "Grupo": "grupo",
        "Descrição do Alimento": "descricao",
        "Energia(kcal)": "calorias",
        "Proteína(g)": "proteinas",
        "Lipídeos(g)": "lipideos",
        "Carboidrato(g)": "carboidratos",
    }, inplace=True)
    
    # Trata valores vazios como 0
    for col in ["calorias", "proteinas", "lipideos", "carboidratos"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    
    # Remove linhas sem descrição
    df.dropna(subset=["descricao"], inplace=True)
    df["descricao"] = df["descricao"].str.strip()
    df["grupo"] = df["grupo"].fillna("Sem grupo").str.strip()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    restaurados = 0
    
    for _, row in df.iterrows():
        # Verifica se o alimento existe com fonte='taco'
        existe = cursor.execute("""
            SELECT id FROM alimentos
            WHERE LOWER(grupo) = LOWER(?) AND LOWER(descricao) = LOWER(?) AND fonte = 'taco'
        """, (row['grupo'], row['descricao'])).fetchone()
        
        if existe:
            # Atualiza valores
            cursor.execute("""
                UPDATE alimentos
                SET calorias = ?, proteinas = ?, lipideos = ?, carboidratos = ?
                WHERE id = ?
            """, (
                round(float(row['calorias']), 2),
                round(float(row['proteinas']), 2),
                round(float(row['lipideos']), 2),
                round(float(row['carboidratos']), 2),
                existe['id']
            ))
            restaurados += 1
        else:
            # Alimento TACO não existe (pode ter sido deletado) - recria
            cursor.execute("""
                INSERT INTO alimentos (grupo, descricao, calorias, proteinas, lipideos, carboidratos, fonte)
                VALUES (?, ?, ?, ?, ?, ?, 'taco')
            """, (
                row['grupo'],
                row['descricao'],
                round(float(row['calorias']), 2),
                round(float(row['proteinas']), 2),
                round(float(row['lipideos']), 2),
                round(float(row['carboidratos']), 2),
            ))
            restaurados += 1
    
    conn.commit()
    conn.close()
    
    return restaurados
