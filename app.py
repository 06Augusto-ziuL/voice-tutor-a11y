import gradio as gr
from core.llm_client import perguntar
from core.tts_engine import sintetizar_voz
from ui.styles import CSS
from ui.ui import toggle_player

def responder(pergunta: str, historico: list):
    resposta = perguntar(pergunta, historico)
    audio = sintetizar_voz(resposta)
    return resposta, audio, gr.Column(visible=True), gr.Button(value="\u276F"), True

tema = gr.themes.Default(
    primary_hue="purple",
    neutral_hue="gray"
)

with gr.Blocks() as app:
    with gr.Row():
        with gr.Column(scale=2, elem_id="coluna_chat") as coluna_chat:
            pass
        with gr.Column(scale=1, visible=False, elem_id="coluna_player") as coluna_player:
            audio_output = gr.Audio(label="Ouvir resposta", autoplay=True, waveform_options=gr.WaveformOptions(
                waveform_color="#7c3aed",
                waveform_progress_color="#a855f7"
            ))

        with coluna_chat:
            estado_player = gr.State(False)

            btn_toggle = gr.Button("\u276E", elem_id="btn_toggle", size="sm")


            gr.ChatInterface(
                fn=responder,
                title="&#127891; Papoi - Tutor Escolar Acessível por Voz",
                description="Seu tutor escolar inteligente, sempre pronto para ajudar.",
                chatbot=gr.Chatbot(
                    placeholder="""<div style='text-align:center'>
                <p style='font-size:3rem'>&#127891;</p>
                <h2>Olá! &#x1F44B</h2>
                <p>Sou o Papoi, seu tutor escolar por voz.</p>
                <p>Como posso te ajudar hoje?</p>
                </div>""",
                    show_label=False,
                    render_markdown=True
                ),
                examples=[
                    "Explicar um conteúdo",
                    "Resolver exercício",
                    "Revisar texto",
                    "Tirar dúvida"
                ],
                additional_outputs=[audio_output, coluna_player, btn_toggle, estado_player]
            )

            btn_toggle.click(
                fn=toggle_player,
                inputs=[estado_player],
                outputs=[coluna_player, btn_toggle, estado_player]
            )

if __name__ == "__main__":
    app.launch(theme=None, css=CSS)