from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import json
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hash/{text}")
def get_hash(text: str):
    hash_obj = hashlib.sha256(text.encode())
    return {
        "request": text,
        "result": hash_obj.hexdigest()
    }

@app.get("/api/about")
def get_about():
    file_path = os.path.join(os.path.dirname(__file__), 'about.json')
    try:
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            return {"project_name": "CargoPay", "status": "about.json not found"}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Ошибка чтения about.json: {str(e)}"}
