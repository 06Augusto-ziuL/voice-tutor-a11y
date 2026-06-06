from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_MODEL = "qwen2.5:3b"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_TEMPERATURE = 1

STT_MODEL = "base"

PIPER_MODEL = BASE_DIR / "assets" / "piper_model" / "pt_BR-faber-medium.onnx"
PIPER_CONFIG = BASE_DIR / "assets" / "piper_model" / "pt_BR-faber-medium.onnx.json"

AUDIO_OUTPUT = BASE_DIR / "assets" / "output.wav"