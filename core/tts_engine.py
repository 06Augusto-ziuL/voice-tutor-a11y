import subprocess
from core.config import PIPER_MODEL, PIPER_CONFIG, PIPER_LENGTH_SCALE, PIPER_SENTENCE_SILENCE,AUDIO_OUTPUT

def sintetizar_voz(texto: str) -> str:
    comando = [
        "piper",
        "-m", str(PIPER_MODEL),
        "-c", str(PIPER_CONFIG),
        "-f", str(AUDIO_OUTPUT),
        "--length-scale", PIPER_LENGTH_SCALE,
        "--sentence-silence", PIPER_SENTENCE_SILENCE
    ]

    try:
        processo = subprocess.run(
            comando,
            input=texto,
            text=True,
            capture_output=True
        )

        if processo.returncode != 0:
            raise RuntimeError(f"Piper retornou erro: {processo.stderr}")
        
        return str(AUDIO_OUTPUT)
    
    except FileNotFoundError:
        return "Erro: executável do Piper não encontrado."
    except RuntimeError as e:
        return f"Erro na síntese: {e}"
    