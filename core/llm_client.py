import requests
from core.config import OLLAMA_MODEL, OLLAMA_URL, OLLAMA_TEMPERATURE
from core.prompts import TUTOR_SYSTEM_PROMPT

def perguntar(pergunta: str, historico: list) -> str:
    message_prompt = [
        {"role": "system", "content": TUTOR_SYSTEM_PROMPT}
    ]
    message_prompt.extend(normalizar_historico(historico))
    message_prompt.append({"role": "user", "content": pergunta})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": message_prompt,
        "temperature": OLLAMA_TEMPERATURE,
        "stream": False
    }

    try:
        resposta = requests.post(OLLAMA_URL, json=payload)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar ao Ollama. Verifique se o serviço está funcionando corretamente."
    except requests.exceptions.HTTPError as e:
        return f"Erro na requisição: {e}"
    except KeyError:
        return "Erro: resposta inesperada do Ollama."
    
def normalizar_historico(historico: list) -> list:
    normalizado = []
    for msg in historico:
        content = msg["content"]
        if isinstance(content, list):
            content = " ".join(
                item["text"] for item in content if item.get("type") == "text"
            )
        normalizado.append({"role": msg["role"], "content": content})
    return normalizado