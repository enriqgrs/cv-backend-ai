from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from supabase import create_client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración (Usando tus datos confirmados)
SUPABASE_URL = "https://wuioytvfmkswexigetzg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1aW95dHZmbWtzd2V4aWdldHpnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTg1NTU2OSwiZXhwIjoyMDg3NDMxNTY5fQ.MK0_6nMW_NFb_PwgT37SfuLYTWQYdqnxxkmf8jtvLuQ" # La misma que usaste en ingesta.py
GEMINI_KEY = "AIzaSyAo_9eMl14FscNBP7w7MW4HRsHyZwAtJVg"

client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/ask")
async def ask_portfolio(request: ChatRequest):
    try:
        # 1. EL EMBEDDING QUE ESTÁ EN TU LISTA
        res_embed = client.models.embed_content(
            model='gemini-embedding-001', 
            contents=request.message,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        query_vector = res_embed.embeddings[0].values

        # 2. Buscar en Supabase
        rpc_res = supabase.rpc("buscar_en_cv", {
            "query_embedding": query_vector,
            "match_threshold": 0.3,
            "match_count": 5
        }).execute()

        contexto = "\n".join([item['res_content'] for item in rpc_res.data])
        
        # 3. Prompt
        prompt = f"Eres el asistente del portfolio de Enrique. Usa este contexto para responder brevemente: {contexto}. Pregunta: {request.message}"

        # 4. EL MODELO GENERATIVO QUE ESTÁ EN TU LISTA
        response = client.models.generate_content(
            model='gemini-2.5-flash', # <--- Usamos el modelo estrella que sí tienes
            contents=prompt
        )
        
        return {"answer": response.text}

    except Exception as e:
        print(f"Error técnico: {e}")
        return {"answer": f"Ups, ha ocurrido un error: {str(e)}"}
