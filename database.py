
import mysql.connector

config = {
    "host": "localhost",
    "user": "Denilson",
    "password": "Denis2025**",
    "database": "fibrasil"
}

def executar_consulta(query, params=None, fetch=False, dictionary=False):
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=dictionary)
    cursor.execute(query, params or ())
    resultado = cursor.fetchall() if fetch else None
    conn.commit()
    cursor.close()
    conn.close()
    return resultado

def inserir_dados(colunas, valores):
    placeholders = ", ".join(["%s"] * len(colunas))
    colunas_str = ", ".join(colunas)
    query = f"INSERT INTO Fibrasil_TTK ({colunas_str}) VALUES ({placeholders})"
    executar_consulta(query, tuple(valores))
