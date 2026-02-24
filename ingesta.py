# cv/ingesta.py
from google import genai  # <--- CAMBIO IMPORTANTE
from google.genai import types
from supabase import create_client
from github import Github
# Configuración usando los datos de tus capturas
# URL de image_d4d3de.png y Service Role Key de image_d4bd19.png
SUPABASE_URL = "https://wuioytvfmkswexigetzg.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1aW95dHZmbWtzd2V4aWdldHpnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTg1NTU2OSwiZXhwIjoyMDg3NDMxNTY5fQ.MK0_6nMW_NFb_PwgT37SfuLYTWQYdqnxxkmf8jtvLuQ" # La que sacamos de API Settings
GEMINI_KEY = "AIzaSyAo_9eMl14FscNBP7w7MW4HRsHyZwAtJVg"
client = genai.Client(api_key=GEMINI_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generar_vector(texto):
    """Genera el embedding usando gemini-embedding-001 con 768 dimensiones"""
    # Forzamos 768 dimensiones para que coincida con tu tabla de Supabase
    res = client.models.embed_content(
        model='gemini-embedding-001',
        contents=texto,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )
    return res.embeddings[0].values

def guardar_en_supabase(texto, fuente):
    try:
        vector = generar_vector(texto)
        supabase.table("curriculum").insert({
            "content": texto, 
            "embedding": vector
        }).execute()
        print(f"✅ Guardado: {fuente}")
    except Exception as e:
        print(f"❌ Error en {fuente}: {e}")

def inyectar_github(usuario_gh):
    print(f"\n--- 🐙 Iniciando GitHub: {usuario_gh} ---")
    g = Github()
    try:
        user = g.get_user(usuario_gh)
        for repo in user.get_repos():
            if repo.fork: continue
            info = f"PROYECTO GITHUB: {repo.name}. Desc: {repo.description}. Link: {repo.html_url}"
            guardar_en_supabase(info, f"Repo: {repo.name}")
    except Exception as e:
        print(f"❌ Error GitHub: {e}")

# --- EJECUCIÓN ---
mi_cv = """
[ENRIQUE]
Perfil: Estudiante de 21 años en 3o de Ingeniería Informática (especialidad en Computación) en la Universidad de Zaragoza. Interesado por la resolución de problemas complejos mediante algoritmos eficientes y el desarrollo de sistemas inteligentes mediante el diseño de arquitecturas de Deep Learning, modelos probabilísticos y programación concurrente.
Experiencia: Profesor Particular - Preparación de pruebas de acceso EVAU [2025].
Educacion: Universidad de Zaragoza: [2022-Actualmente] Ingeniería Informática (Computación) Centrado en el diseño de algoritmos avanzados e inteligencia artificial. Integrando áreas como robótica, visión artificial y aprendizaje automático para desarrollar sistemas inteligentes en diversos sectores tecnológicos. Colegio Sagrado Corazón La Mina: [2020-2022] Bachillerato Científico-Tecnológico.
Hard skills: Lenguajes de Programación: C++ (Avanzado), Java, Python (Numpy, TensorFlow, Keras), C, JavaScript, Haskell, Ada, Ensamblador. IA y Data Science: Deep Learning (CNN), Inferencia Probabilística (HMM/Partículas), Regresión Robusta y Clasificación Naive Bayes. Bases de Datos: SQL, PostgreSQL (Diseño y administración). Herramientas y Sistemas: Docker, Git/GitHub, Linux, Sistemas Empotrados, HTML/CSS. Algoritmia: Optimización de búsqueda, heurísticas, poda Alfa-Beta y estructuras de datos eficientes.
Idiomas: Español: Nativo. Inglés: Nivel B2.
Soft Skills: Trabajo en equipos multidisciplinares. Comunicación técnica adaptativa. Pensamiento analítico y crítico. Responsabilidad y liderazgo. Proactividad y aprendizaje autónomo. Resiliencia y gestión del error.

"""

print("--- 📄 Iniciando Ingesta de CV ---")
for parrafo in mi_cv.split("\n\n"):
    if parrafo.strip():
        guardar_en_supabase(parrafo, "CV")

# Ejecutamos la carga de tus repositorios
inyectar_github("enriqgrs")

print("\n--- 🚀 PROCESO COMPLETADO ---")
