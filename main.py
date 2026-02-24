from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
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
# El código leerá los valores de los "Secrets" de Hugging Face de forma segura
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Si usas la llave de Google en tu código, hazlo así:
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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
