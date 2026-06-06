import gradio as gr

def toggle_player(visivel: bool):
    novo_estado = not visivel
    seta = "\u276F" if novo_estado else "\u276E"
    return gr.Column(visible=novo_estado), gr.Button(value=seta), novo_estado