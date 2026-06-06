CSS = """
:root, :root.dark, :root .dark {
    --body-background-fill: #0d0f1a !important;
    --background-fill-primary: #0d0f1a !important;
    --background-fill-secondary: #12152b !important;
    --block-background-fill: #12152b !important;
    --color-accent: #7c3aed !important;
    --border-color-primary: #2a2d4a !important;
    --border-color-accent: #7c3aed !important;
}

[data-testid="submit-button"] {
    background-color: #7c3aed !important;
    border-color: #7c3aed !important;
}

[data-testid="submit-button"]:hover {
    background-color: #6d28d9 !important;
}

button.example {
    background-color: #1e2035 !important;
    border-color: #2a2d4a !important;
    color: #e2e8f0 !important;
}

button.example:hover {
    background-color: #2a2d4a !important;
    border-color: #7c3aed !important;
}

.md p {
    text-align: center !important;
}

.placeholder {
    text-align: center !important;
    width: 100% !important;
}

[data-testid="textbox"] {
    background-color: #12152b !important;
    color: #e2e8f0 !important;
}
"""