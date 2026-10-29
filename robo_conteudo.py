import os
import random
import time
import requests
from datetime import datetime
from google import genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
B_CLIENT_ID = os.environ.get("B_CLIENT_ID")
B_CLIENT_SECRET = os.environ.get("B_CLIENT_SECRET")
B_REFRESH_TOKEN = os.environ.get("B_REFRESH_TOKEN")

client = genai.Client(api_key=GEMINI_API_KEY)

CATEGORIAS = ['Futebol', 'Poliesportivos', 'Motor e Combate', 'Especiais e Análises']
TAGS_IMAGEM = ['soccer', 'athletes', 'adrenaline sports', 'sports insights']

def obter_imagem_dinamica(index):
    termo = TAGS_IMAGEM[index % len(TAGS_IMAGEM)]
    timestamp = int(time.time())
    rand_id = random.randint(10, 100)
    return f"https://picsum.photos/seed/{termo}{timestamp}{rand_id}/800/450"

def obter_novo_access_token():
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": B_CLIENT_ID,
        "client_secret": B_CLIENT_SECRET,
        "refresh_token": B_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def gerar_artigo():
    cat_escolhida = random.choice(CATEGORIAS)
    idx = CATEGORIAS.index(cat_escolhida)

    prompt = f"""
    Você é um jornalista sênior especializado no nicho de '{cat_escolhida}' para o portal 'Arena Esportiva'.
    Escreva um artigo jornalístico relevante, inédito e atualizado sobre as principais tendências ou novidades recentes desse tema.

    ESTRUTURA OBRIGATÓRIA (HTML):
    [TITULO] Título chamativo e otimizado para SEO [/TITULO]
    [CONTEUDO]
    <p><b>Introdução direta focada no impacto...</b></p>
    <h3>Análise Completa e Detalhes</h3>
    <p>Explicação detalhada dos fatos com linguagem profissional...</p>
    <h3>O que Esperar para o Futuro</h3>
    <p>Perspectivas e próximos passos...</p>
    <br><hr>
    <p><small><i><b>Disclaimer:</b> Conteúdo informativo e educacional.</i></small></p>
    [/CONTEUDO]
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    texto = response.text

    titulo = texto.split("[TITULO]")[1].split("[/TITULO]")[0].strip()
    conteudo = texto.split("[CONTEUDO]")[1].split("[/CONTEUDO]")[0].strip()

    imagem_url = obter_imagem_dinamica(idx)
    html_final = f'<p><img src="{imagem_url}" alt="Destaque" style="width:100%; max-height:450px; object-fit:cover; border-radius:8px; margin-bottom:15px;"/></p>\n' + conteudo

    return titulo, html_final, cat_escolhida

def publicar():
    access_token = obter_novo_access_token()
    if not access_token: return

    titulo, conteudo, etiqueta = gerar_artigo()
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    payload = {"kind": "blogger#post", "title": titulo, "content": conteudo, "labels": [etiqueta, "Arena Esportiva"]}

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        print(f"✅ Publicado: [{etiqueta}] {titulo}")
    else:
        print(f"❌ Erro: {res.text}")

if __name__ == "__main__":
    publicar()
