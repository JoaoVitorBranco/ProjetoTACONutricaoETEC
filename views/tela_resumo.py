import tkinter as tk
from tkinter import ttk
from views.estilos import *


class TelaResumoCardapio(tk.Toplevel):
    def __init__(self, master, cardapio):
        super().__init__(master)
        self.cardapio = cardapio
        self.title(f"Resumo — {cardapio.nome}")
        self.geometry("720x580")
        self.minsize(640, 480)
        self.configure(bg=COR_FUNDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self.focus_set()

    def _construir(self):
        # Cabeçalho
        h = tk.Frame(self, bg=COR_PRIMARIA_DARK, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="📊  Resumo do Cardápio", font=("Georgia", 16, "bold"),
                 fg="white", bg=COR_PRIMARIA_DARK).pack()
        tk.Label(h, text=f"{self.cardapio.nome}  •  {self.cardapio.kcal_total:.0f} kcal/dia",
                 font=FONTE_PEQUENA, fg="#A8D5BA", bg=COR_PRIMARIA_DARK).pack()

        # Rodapé fixo
        rodape = tk.Frame(self, bg=COR_FUNDO, pady=PAD_SM, padx=PAD * 2)
        rodape.pack(side="bottom", fill="x")
        tk.Button(
            rodape, text="Fechar", font=FONTE_CORPO,
            bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=14, pady=6,
            cursor="hand2", command=self.destroy,
        ).pack(side="right")

        # Área rolável
        container = tk.Frame(self, bg=COR_FUNDO)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=COR_FUNDO, bd=0, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        sf = tk.Frame(canvas, bg=COR_FUNDO, padx=PAD * 2, pady=PAD)

        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._secao_totais(sf)
        self._secao_refeicoes(sf)

    # ── Seção: Totais do dia ───────────────────────────────────────────────────

    def _secao_totais(self, pai):
        total_kcal = sum(r.totais["calorias"]     for r in self.cardapio.refeicoes)
        total_prot = sum(r.totais["proteinas"]    for r in self.cardapio.refeicoes)
        total_carb = sum(r.totais["carboidratos"] for r in self.cardapio.refeicoes)
        total_lip  = sum(r.totais["lipideos"]     for r in self.cardapio.refeicoes)

        frame = tk.LabelFrame(
            pai, text=" Totais do dia ", font=FONTE_CORPO_B,
            bg=COR_FUNDO_CARD, fg=COR_PRIMARIA, relief="groove", padx=PAD, pady=PAD,
        )
        frame.pack(fill="x", pady=(0, PAD))

        # Linha de kcal
        kcal_pct = (total_kcal / self.cardapio.kcal_total * 100) if self.cardapio.kcal_total else 0
        kcal_ok  = 95 <= kcal_pct <= 105
        kcal_cor = COR_VERDE if kcal_ok else COR_VERMELHO

        f_kcal = tk.Frame(frame, bg=COR_FUNDO_CARD)
        f_kcal.pack(fill="x", pady=(0, PAD))
        tk.Label(f_kcal, text="Kcal consumidas:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).pack(side="left")
        tk.Label(f_kcal, text=f"  {total_kcal:.1f} kcal  ({kcal_pct:.1f}% do alvo)",
                 font=FONTE_MONO, bg=COR_FUNDO_CARD, fg=kcal_cor).pack(side="left")
        tk.Label(f_kcal, text=f"   / alvo: {self.cardapio.kcal_total:.0f} kcal",
                 font=FONTE_CORPO, bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).pack(side="left")

        # Cards de macros
        f_macros = tk.Frame(frame, bg=COR_FUNDO_CARD)
        f_macros.pack(fill="x")

        macros = [
            ("Proteínas",     total_prot, 4, 0.10, 0.20),
            ("Carboidratos",  total_carb, 4, 0.45, 0.60),
            ("Lipídeos",      total_lip,  9, 0.20, 0.30),
        ]

        for nome, gramas, kcal_g, pmin, pmax in macros:
            kcal_macro = gramas * kcal_g
            pct_real = (kcal_macro / total_kcal * 100) if total_kcal else 0
            ok = pmin * 100 <= pct_real <= pmax * 100
            cor   = COR_VERDE    if ok else COR_VERMELHO
            bg_c  = COR_VERDE_LIGHT if ok else COR_VERMELHO_LIGHT

            card = tk.Frame(f_macros, bg=bg_c, relief="flat", padx=PAD, pady=PAD_SM)
            card.pack(side="left", expand=True, fill="both", padx=(0, PAD_SM))

            tk.Label(card, text=nome, font=FONTE_CORPO_B,
                     bg=bg_c, fg=COR_TEXTO_MUTED).pack(anchor="w")
            tk.Label(card, text=f"{gramas:.1f} g", font=("Consolas", 14, "bold"),
                     bg=bg_c, fg=cor).pack(anchor="w")
            tk.Label(card, text=f"{pct_real:.1f}% das kcal",
                     font=FONTE_PEQUENA, bg=bg_c, fg=cor).pack(anchor="w")
            tk.Label(card, text=f"[{pmin*100:.0f}–{pmax*100:.0f}%]",
                     font=FONTE_PEQUENA, bg=bg_c, fg=COR_TEXTO_MUTED).pack(anchor="w")

    # ── Seção: Por refeição ────────────────────────────────────────────────────

    def _secao_refeicoes(self, pai):
        frame = tk.LabelFrame(
            pai, text=" Por refeição ", font=FONTE_CORPO_B,
            bg=COR_FUNDO_CARD, fg=COR_PRIMARIA, relief="groove", padx=PAD, pady=PAD,
        )
        frame.pack(fill="x", pady=(0, PAD))

        style = ttk.Style()
        style.configure("Resumo.Treeview", rowheight=30, font=FONTE_PEQUENA,
                         background=COR_FUNDO_CARD, fieldbackground=COR_FUNDO_CARD,
                         foreground=COR_TEXTO)
        style.configure("Resumo.Treeview.Heading", font=FONTE_PEQUENA,
                         background=COR_PRIMARIA, foreground="white", relief="flat")

        cols = ("refeicao", "pct", "kcal", "prot", "carb", "lip", "status")
        tree = ttk.Treeview(
            frame, columns=cols, show="headings",
            style="Resumo.Treeview",
            height=len(self.cardapio.refeicoes),
        )

        for col, txt, w, anchor in [
            ("refeicao", "Refeição",    190, "w"),
            ("pct",      "% kcal",       65, "center"),
            ("kcal",     "Kcal",         80, "center"),
            ("prot",     "Prot (g)",      80, "center"),
            ("carb",     "Carb (g)",      80, "center"),
            ("lip",      "Lip (g)",       80, "center"),
            ("status",   "Status",        70, "center"),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor=anchor)

        tree.tag_configure("valida",   background=COR_VERDE_LIGHT)
        tree.tag_configure("invalida", background=COR_VERMELHO_LIGHT)
        tree.tag_configure("vazia",    background=COR_FUNDO_CARD)

        for ref in self.cardapio.refeicoes:
            t = ref.totais
            v = ref.validacao
            if not ref.itens:
                status = "—"
                tag = "vazia"
            elif v["valida"]:
                status = "✔"
                tag = "valida"
            else:
                status = "✘"
                tag = "invalida"

            tree.insert("", "end", values=(
                ref.nome,
                f"{ref.percentual:.1f}%",
                f"{t['calorias']:.1f}",
                f"{t['proteinas']:.1f}",
                f"{t['carboidratos']:.1f}",
                f"{t['lipideos']:.1f}",
                status,
            ), tags=(tag,))

        tree.pack(fill="x")
