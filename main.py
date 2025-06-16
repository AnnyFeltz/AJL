from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Conexão com banco de dados (Server02)
db = mysql.connector.connect(
    host="10.20.21.144",  # IP da sua VM com MySQL
    user="root_AJL",
    password="AJL",
    database="api_db"
)

class Usuario(BaseModel):
    nome: str
    email: str
    senha: str

@app.post("/register")
def registrar_usuario(usuario: Usuario):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
            (usuario.nome, usuario.email, usuario.senha)
        )
        db.commit()
        return {"mensagem": "Usuário registrado com sucesso!"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=str(err))
