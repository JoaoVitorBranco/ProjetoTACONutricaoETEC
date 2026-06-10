"""
importar_taco.py
----------------
Execute este script UMA VEZ para popular o banco com os dados da tabela TACO.
Uso: python importar_taco.py caminho/para/taco.xlsx
"""

import sys
import os

# Garante que importa o módulo database do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from database.db import get_connection, inicializar_banco


COLUNAS = {
    "Grupo": "grupo",
    "Descrição do Alimento": "descricao",
    "Energia(kcal)": "calorias",
    "Proteína(g)": "proteinas",
    "Lipídeos(g)": "lipideos",
    "Carboidrato(g)": "carboidratos",
}


def importar(caminho_excel: str):
    print(f"Lendo arquivo: {caminho_excel}")

    df = pd.read_excel(caminho_excel, usecols=list(COLUNAS.keys()))
    df.rename(columns=COLUNAS, inplace=True)

    # Trata valores vazios como 0
    for col in ["calorias", "proteinas", "lipideos", "carboidratos"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Remove linhas sem descrição
    df.dropna(subset=["descricao"], inplace=True)
    df["descricao"] = df["descricao"].str.strip()
    df["grupo"] = df["grupo"].fillna("Sem grupo").str.strip()

    inicializar_banco()
    conn = get_connection()
    cursor = conn.cursor()

    # Remove alimentos TACO anteriores para evitar duplicatas em re-importação
    cursor.execute("DELETE FROM alimentos WHERE fonte = 'taco'")

    inseridos = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO alimentos (grupo, descricao, calorias, proteinas, lipideos, carboidratos, fonte)
            VALUES (?, ?, ?, ?, ?, ?, 'taco')
        """, (
            row["grupo"],
            row["descricao"],
            round(float(row["calorias"]), 2),
            round(float(row["proteinas"]), 2),
            round(float(row["lipideos"]), 2),
            round(float(row["carboidratos"]), 2),
        ))
        inseridos += 1

    conn.commit()
    conn.close()
    print(f"Importação concluída! {inseridos} alimentos inseridos.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python importar_taco.py caminho/para/taco.xlsx")
        sys.exit(1)
    importar(sys.argv[1])
