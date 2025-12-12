# main.py - VERSIÓN PARA KUBERNETES CON API INTERNA
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from pydantic import BaseModel
from typing import List
import os
import uvicorn

# Crear router con prefijo /api
router = APIRouter(prefix="/api")

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

# ========== ENDPOINTS CON PREFIJO /api ==========

@router.get("/")
def root():
    return {"message": "API del juego funcionando"}

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/guardar_usuario")
def guardar_usuario(data: Usuario):
    print("Recibido:", data)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuario (nombre) VALUES (%s)", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "message": "Usuario guardado correctamente"}

@router.get("/usuarios", response_model=List[UsuarioOut])
def obtener_usuarios():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM usuario ORDER BY id DESC")
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"nombre": fila[0]} for fila in filas]

@router.post("/eliminar_usuario")
def eliminar_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuario WHERE nombre = %s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "message": "Usuario eliminado"}

@router.post("/login_usuario")
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

@router.post("/ping_usuario")
def ping_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE usuarios_online SET last_seen=NOW() WHERE nombre=%s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}

@router.get("/usuarios_online", response_model=List[UsuarioOut])
def obtener_usuarios_online():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT nombre, score FROM usuarios_online WHERE last_seen > NOW() - INTERVAL '5 seconds'")
    filas = cur.fetchall()
    print("Filas obtenidas:", filas)
    cur.close()
    conn.close()
    return [{"nombre": f[0], "score": f[1]} for f in filas]

@router.post("/logout_usuario")
def logout_usuario(data: Usuario):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios_online WHERE nombre=%s", (data.nombre,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok"}

@router.post("/actualizar_score")
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

# ========== CREAR APLICACIÓN ==========
app = FastAPI()

# Configuración CORS SEGURA (solo tu dominio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://caballero026.me",  # Tu dominio principal
        "http://localhost:8000",    # Desarrollo local
        "http://localhost",         # Desarrollo
        "https://localhost",        # Desarrollo con HTTPS
        "http://127.0.0.1:8000",   # Desarrollo alternativo
        "*"                         # Temporal para pruebas, QUITAR en producción
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Incluir router con prefijo /api
app.include_router(router)

# También mantener endpoints sin prefijo para compatibilidad (opcional)
@app.get("/")
def root_no_prefijo():
    return {"message": "API del juego (sin prefijo) - Usa /api/..."}

@app.get("/health")
def health_no_prefijo():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)