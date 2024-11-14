import sqlite3

def init_db():
    conn = sqlite3.connect("prediagnosticos.db")
    cursor = conn.cursor()
    
    # Crear la tabla sin la columna `ruta_imagen`
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediagnosticos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            diagnostico TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Base de datos inicializada sin la columna `ruta_imagen`.")

if __name__ == "__main__":
    init_db()
