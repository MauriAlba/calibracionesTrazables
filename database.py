import sqlite3

DB_NAME = "calibraciones.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def crear_base():
    conn = get_connection()
    cursor = conn.cursor()

    # Instrumentos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instrumentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        tipo TEXT,
        ubicacion TEXT,
        descripcion TEXT
    )
    """)

    # Calibraciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calibraciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instrumento_id INTEGER,
        fecha TEXT,
        responsable TEXT,
        observaciones TEXT,
        FOREIGN KEY (instrumento_id) REFERENCES instrumentos(id)
    )
    """)

    # Mediciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        calibracion_id INTEGER,
        valor_patron REAL,
        valor_medido REAL,
        error REAL,
        FOREIGN KEY (calibracion_id) REFERENCES calibraciones(id)
    )
    """)

    conn.commit()
    conn.close()