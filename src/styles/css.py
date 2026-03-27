def load_css():
    return """
    <style>
    html, body, [class*="css"]  {
        font-size: 15px;
    }

    h1 {
        font-size: 32px;
    }

    h2 {
        font-size: 24px;
    }

    h3 {
        font-size: 20px;
    }

    div[data-testid="stCaptionContainer"] p {
        font-size: 16px !important;
        color: grey !important;
    }

    .block-container {
        padding-top: 2rem;
    }
    </style>
    """