import gradio as gr
from core.llm_client import perguntar
from core.tts_engine import sintetizar_voz

def responder_texto(pergunta: str):
    if not pergunta.strip():
        return "Por favor, digite uma pergunta.", None
    
    resposta = perguntar(pergunta)
    audio = sintetizar_voz(resposta)
    return resposta, audio

def responder_voz(audio):
    #Aguardando implementação do stt_engine
    return "STT ainda não implementado.", None, None

with gr.Blocks(title="Papoi - Tutor Escolar") as app:
    gr.Markdown("# \U0001F393 Papoi - Tutor Escolar Acessível por Voz")

    with gr.Tabs():
        with gr.TabItem("Texto"):
            with gr.Row():
                entrada_texto = gr.Textbox(
                    label="Sua pergunta",
                    placeholder="Digite sua pergunta aqui...",
                    lines=3
                )
            with gr.Row():
                botao_perguntar = gr.Button("Perguntar", variant="primary")
            with gr.Row():
                saida_texto = gr.Textbox(label="Resposta", lines=6)
                saida_audio = gr.Audio(label="Ouvir resposta", autoplay=True)
            botao_perguntar.click(
                fn=responder_texto,
                inputs=entrada_texto,
                outputs=[saida_texto, saida_audio]
            )
        with gr.TabItem("Voz"):
            gr.Markdown("### Fale sua pergunta")
            with gr.Row():
                entrada_voz = gr.Audio(
                    label= "Microfone",
                    sources=["microphone"],
                    type="filepath"
                )
            with gr.Row():
                transcricao = gr.Textbox(label="Transcrição", interactive=False)
            with gr.Row():
                botao_confirmar = gr.Button("Confirmar e enviar", variant="primary")
            with gr.Row():
                saida_texto_voz = gr.Textbox(label="Resposta", lines=6)
                saida_audio_voz = gr.Audio(label="Ouvir resposta", autoplay=True)
            botao_confirmar.click(
                fn=responder_voz,
                inputs=entrada_voz,
                outputs=[transcricao, saida_texto_voz, saida_audio_voz]
            )

if __name__ == "__main__":
    app.launch()