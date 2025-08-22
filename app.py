import os, json, traceback
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

PERPLEXITY_KEY = os.getenv('PERPLEXITY_API_KEY', '').strip()
APPS_SCRIPT_WEBHOOK_URL = os.getenv('APPS_SCRIPT_WEBHOOK_URL', '').strip()

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
templates = Jinja2Templates(directory=TEMPLATES_DIR)

from rag_query import query_knowledge_base
from logger import log_escalation

try:
    from ollama import Ollama
    ollama_client = Ollama()
except Exception:
    ollama_client = None

ESCALATION_KEYWORDS = [
    'not satisfied', 'talk to human', 'speak to human', 'connect me with support',
    'i want to talk to a human', 'escalate', 'complaint', 'human agent', 'human support'
]

INDEX_TOP_K = 4

INDEX_HTML_PATH = os.path.join(TEMPLATES_DIR, 'index.html')
if os.path.exists(INDEX_HTML_PATH):
    INDEX_HTML = open(INDEX_HTML_PATH, 'r', encoding='utf-8').read()
else:
    INDEX_HTML = '<h3>Place an index.html inside templates/</h3>'

@app.get('/', response_class=HTMLResponse)
async def home(request: Request):
    return HTMLResponse(INDEX_HTML)

def call_perplexity_chat(prompt, model='sonar-pro'):
    import requests
    url = 'https://api.perplexity.ai/chat/completions'
    headers = {
        'Authorization': f'Bearer {PERPLEXITY_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}]}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    r.raise_for_status()
    return r.json()

@app.post('/ask')
async def ask(request: Request):
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = {'question': form.get('question', ''), 'name': form.get('name', ''), 'email': form.get('email', '')}
    question = (data.get('question') or '').strip()
    name = data.get('name') or 'Guest'
    email = data.get('email') or 'N/A'
    if not question:
        return JSONResponse({'error': 'question required'}, status_code=400)

    low = question.lower()
    if any(k in low for k in ESCALATION_KEYWORDS):
        ok = log_escalation(question, name=name, email=email)
        reply = 'I have logged your request — a human support agent will contact you shortly.'
        return JSONResponse({'answer': reply, 'escalated': True, 'logged': ok})

    docs = query_knowledge_base(question, n_results=INDEX_TOP_K)
    context_text = '\n\n'.join(docs)
    prompt = f"Context:\n{context_text}\n\nQuestion: {question}\n\nAnswer concisely based only on the context. If context lacks answer, say you don't know and offer escalation."

    if PERPLEXITY_KEY:
        try:
            resp = call_perplexity_chat(prompt)
            choices = resp.get('choices') or resp.get('result') or []
            if isinstance(choices, list) and len(choices)>0:
                msg = choices[0].get('message') or choices[0].get('text') or choices[0]
                if isinstance(msg, dict):
                    answer = msg.get('content') or msg.get('text') or json.dumps(msg)
                else:
                    answer = str(msg)
            else:
                answer = resp.get('answer') or resp.get('output_text') or json.dumps(resp)
            return JSONResponse({'answer': answer, 'sources': docs, 'used': 'perplexity'})
        except Exception:
            traceback.print_exc()

    if ollama_client is not None:
        try:
            out = ollama_client.generate('llama3.1:8b', prompt)
            if isinstance(out, dict):
                ans = out.get('text') or json.dumps(out)
            else:
                ans = str(out)
            return JSONResponse({'answer': ans, 'sources': docs, 'used': 'ollama'})
        except Exception:
            traceback.print_exc()

    fallback = '\n\n'.join(docs[:3]) or "I couldn't find information in the knowledge base."
    return JSONResponse({'answer': fallback, 'sources': docs, 'used': 'context_fallback'})

@app.post('/escalate')
async def escalate(payload: dict):
    name = payload.get('name') or 'Guest'
    email = payload.get('email') or 'N/A'
    question = payload.get('question') or ''
    ok = log_escalation(question, name=name, email=email)
    return JSONResponse({'ok': ok})