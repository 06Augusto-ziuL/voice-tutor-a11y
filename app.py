import gradio as gr
from core.llm_client import perguntar
from core.tts_engine import sintetizar_voz

def responder(pergunta: str, historico:list):
    resposta = perguntar(pergunta, historico)
    audio = sintetizar_voz(resposta)
    return resposta, audio

tema = gr.themes.Default(
    primary_hue="purple",
    neutral_hue="gray"
)

with gr.Blocks() as app:
    audio_output = gr.Audio(label="Ouvir resposta", autoplay=True)
    
    gr.ChatInterface(
        fn=responder,
        title="\U0001F393 Papoi - Tutor Escolar Acessível por Voz",
        additional_outputs=[audio_output]
    )

if __name__ == "__main__":
    app.launch()