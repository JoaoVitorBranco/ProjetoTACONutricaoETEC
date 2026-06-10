"""
Paleta de cores e estilos do app.
Tema: verde-escuro clínico + branco + acentos âmbar — remete a nutrição e saúde.
"""

# ── Cores ─────────────────────────────────────────────────────────────────────
COR_FUNDO         = "#F7F8F5"
COR_FUNDO_CARD    = "#FFFFFF"
COR_PRIMARIA      = "#2D6A4F"   # verde-escuro
COR_PRIMARIA_DARK = "#1B4332"
COR_ACENTO        = "#D4A017"   # âmbar
COR_TEXTO         = "#1A1A2E"
COR_TEXTO_MUTED   = "#6B7280"
COR_BORDA         = "#E0E5DC"
COR_VERDE         = "#52B788"   # validação OK
COR_VERMELHO      = "#E63946"   # validação ERRO
COR_AMARELO_LIGHT = "#FFF8E1"
COR_VERDE_LIGHT   = "#E8F5E9"
COR_VERMELHO_LIGHT= "#FFEBEE"

# ── Fontes ────────────────────────────────────────────────────────────────────
FONTE_TITULO  = ("Georgia", 18, "bold")
FONTE_SUBTIT  = ("Georgia", 13, "bold")
FONTE_CORPO   = ("Segoe UI", 10)
FONTE_CORPO_B = ("Segoe UI", 10, "bold")
FONTE_PEQUENA = ("Segoe UI", 9)
FONTE_MONO    = ("Consolas", 10)

# ── Espaçamentos ──────────────────────────────────────────────────────────────
PAD = 16
PAD_SM = 8

# ── Ranges fixos do sistema ───────────────────────────────────────────────────
RANGES_LABELS = {
    "carboidratos": ("Carboidratos", "45–60%", COR_ACENTO),
    "proteinas":    ("Proteínas",    "10–20%", "#5B8DB8"),
    "lipideos":     ("Lipídeos",     "20–30%", "#9B72CF"),
}
