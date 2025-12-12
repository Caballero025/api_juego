from fastapi import FastAPI
import psycopg2
from pydantic import BaseModel
from typing import List
app = FastAPI()

class Usuario(BaseModel):
    nombre: str
    
class UsuarioOut(BaseModel):
    nombre: str
    score: int

class ScoreUpdate(BaseModel):
    nombre: str
    score: int

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME", "juego"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "12345678")
    )
@app.post("/guardar_usuario")
def guardar_usuario(data: Usuario):
    print("Recibido:", data)
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO usuario (nombre) VALUES (%s)", (data.nombre,))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "message": "Usuario guardado correctamente"}

@app.get("/usuarios", response_model=List[UsuarioOut])
def obtener_usuarios():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuario ORDER BY id DESC")  # último primero
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"nombre": fila[0]} for fila in filas]

@app.post("/eliminar_usuario")
def eliminar_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuario WHERE nombre = %s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "message": "Usuario eliminado"}


@app.post("/login_usuario")
def login_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios_online (nombre, conectado, last_seen)
        VALUES (%s, TRUE, NOW())
        ON CONFLICT (nombre) DO UPDATE SET conectado=TRUE, last_seen=NOW()
    """, (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}

# Hacer ping para mantener en línea
@app.post("/ping_usuario")
def ping_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios_online SET last_seen=NOW() WHERE nombre=%s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}

@app.get("/usuarios_online", response_model=List[UsuarioOut])
def obtener_usuarios_online():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nombre, score FROM usuarios_online WHERE last_seen > NOW() - INTERVAL '5 seconds'")
    filas = cur.fetchall()
    print("Filas obtenidas:", filas)  # <--- esto imprimirá en la consola del servidor
    cur.close()
    conn.close()
    return [{"nombre": f[0], "score": f[1]} for f in filas]

# Salir del juego
@app.post("/logout_usuario")
def logout_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios_online WHERE nombre=%s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}


@app.post("/actualizar_score")
def actualizar_score(data: ScoreUpdate):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE usuarios_online SET score = %s, last_ping = NOW() WHERE nombre = %s",
        (data.score, data.nombre)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}