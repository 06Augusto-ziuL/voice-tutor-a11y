CSS = """

/* ── Variáveis de tema ── */
:root, :root.dark, :root .dark {
    --body-background-fill: #0d0f1a !important;
    --background-fill-primary: #0d0f1a !important;
    --background-fill-secondary: #12152b !important;
    --block-background-fill: #12152b !important;
    --color-accent: #7c3aed !important;
    --border-color-primary: #2a2d4a !important;
}

body {
    height: 100vh;
    width: 100%;
    padding: 20px;
}

/* ── Layout ── */
.row {
    height: 100%;
    align-items: stretch !important;
}

#coluna_player.hide {
    opacity: 0 !important;
    flex-grow: 0 !important;
    min-width: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
}

.column {
    transition: flex-grow 0.3s ease, width 0.3s ease !important;
}

/* ── Botão toggle ── */
#btn_toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 100;
    background: #1e2035 !important;
    border: 1px solid #2a2d4a !important;
    border-radius: 10px !important;
    width: 2rem !important;
    height: 2rem !important;
    padding: 0 !important;
}

#btn_toggle:hover {
    background-color: #141624
}

/* ── Botão enviar ── */
[data-testid="submit-button"] {
    background-color: #7c3aed !important;
    border-color: #7c3aed !important;
    border-radius: 5px important;
}

[data-testid="submit-button"]:hover {
    background-color: #6d28d9 !important;
}

/* ── Botões de sugestão ── */
button.example {
    background-color: #1e2035 !important;
    border-color: #2a2d4a !important;
    color: #e2e8f0 !important;
}

button.example:hover {
    background-color: #2a2d4a !important;
    border-color: #7c3aed !important;
}

/* ── Input de texto ── */
[data-testid="textbox"] {
    background-color: #12152b !important;
    color: #e2e8f0 !important;
}

/* ── Descrição centralizada ── */
div.prose > .md p {
    text-align: center !important;
}

#coluna_player {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;
    transition: flex-grow 0.3s ease, opacity 0.3s ease !important;
    opacity: 1;
    border: 3px solid #7c3aed;
    border-radius: 10px;
    padding: 10px;
}

[data-testid="waveform-Ouvir resposta"] {
    border: 1px solid #2a2d4a !important;
    border-radius: 8px !important;
}
"""