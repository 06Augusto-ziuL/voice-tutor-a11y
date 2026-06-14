from faster_whisper import WhisperModel
from core.config import STT_MODEL

_modelo = WhisperModel(STT_MODEL, device="cpu", compute_type="int8")

def transcrever(caminho_audio: str) -> str:
    segmentos, _ = _modelo.transcribe(
        caminho_audio,
        language="pt",
        initial_prompt="Um aluno está fazendo perguntas sobre matérias escolares em português do Brasil.",
        vad_filter=True,
        vad_parameters=dict(
            threshold=0.3,
            min_speech_duration_ms=100,
            min_silence_duration_ms=500,
            speech_pad_ms=400,
        )
    )
    return "".join(seg.text for seg in segmentos).strip()