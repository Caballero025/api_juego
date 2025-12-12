# main.py - VERSIÓN CORREGIDA
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORTANTE
import psycopg2
from pydantic import BaseModel
from typing import List
import os
import uvicorn  # <--- Para poder ejecutar directamente

app = FastAPI()

# Configuración CORS para Godot HTML5
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica tus dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/")
def root():
    return {"message": "API del juego funcionando"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ... el resto de tus endpoints se mantienen igual ...
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

# ... todos tus otros endpoints ...

if __name__ == "__main__":
    # ESCUCHAR EN 0.0.0.0 para Kubernetes
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)