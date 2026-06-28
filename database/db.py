import sqlite3
import os
import sys


def get_db_path():
    """Retorna o caminho do banco de dados na pasta AppData do usuário."""
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
        db_dir = os.path.join(app_data, "CardapioNutricional")
    else:
        db_dir = os.path.join(os.path.expanduser("~"), ".cardapio_nutricional")

    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "cardapio.db")


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_banco():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS alimentos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            grupo       TEXT    NOT NULL,
            descricao   TEXT    NOT NULL,
            calorias    REAL    NOT NULL DEFAULT 0,
            proteinas   REAL    NOT NULL DEFAULT 0,
            lipideos    REAL    NOT NULL DEFAULT 0,
            carboidratos REAL   NOT NULL DEFAULT 0,
            fonte       TEXT    NOT NULL DEFAULT 'taco'
        );

        CREATE TABLE IF NOT EXISTS grupos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL UNIQUE,
            fonte       TEXT    NOT NULL DEFAULT 'usuario'
        );

        CREATE TABLE IF NOT EXISTS cardapios (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nome          TEXT    NOT NULL,
            kcal_total    REAL    NOT NULL,
            data_criacao  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS refeicoes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cardapio_id INTEGER NOT NULL REFERENCES cardapios(id) ON DELETE CASCADE,
            nome        TEXT    NOT NULL,
            percentual  REAL    NOT NULL,
            ordem       INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS refeicao_alimentos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            refeicao_id INTEGER NOT NULL REFERENCES refeicoes(id) ON DELETE CASCADE,
            alimento_id INTEGER NOT NULL REFERENCES alimentos(id),
            quantidade_g REAL   NOT NULL
        );

        CREATE TABLE IF NOT EXISTS refeicao_alimentos_custom (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            refeicao_id  INTEGER NOT NULL REFERENCES refeicoes(id) ON DELETE CASCADE,
            descricao    TEXT    NOT NULL,
            quantidade_g REAL    NOT NULL,
            calorias     REAL    NOT NULL DEFAULT 0,
            proteinas    REAL    NOT NULL DEFAULT 0,
            lipideos     REAL    NOT NULL DEFAULT 0,
            carboidratos REAL    NOT NULL DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()
