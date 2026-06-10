import tkinter as tk
from tkinter import ttk, messagebox
from views.estilos import *
from models.repositorio import listar_cardapios, excluir_cardapio, carregar_cardapio


class TelaHome(tk.Frame):
    def __init__(self, master, abrir_cardapio_cb, novo_cardapio_cb):
        super().__init__(master, bg=COR_FUNDO)
        self.abrir_cardapio_cb = abrir_cardapio_cb
        self.novo_cardapio_cb = novo_cardapio_cb
        self._construir()

    def _construir(self):
        # ── Cabeçalho ──────────────────────────────────────────────────────
        header = tk.Frame(self, bg=COR_PRIMARIA_DARK, pady=20)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🥗  Cardápio Nutricional",
            font=("Georgia", 22, "bold"),
            fg="white",
            bg=COR_PRIMARIA_DARK,
        ).pack()
        tk.Label(
            header,
            text="Ferramenta de apoio ao técnico em nutrição",
            font=FONTE_PEQUENA,
            fg="#A8D5BA",
            bg=COR_PRIMARIA_DARK,
        ).pack()

        # ── Área principal ─────────────────────────────────────────────────
        corpo = tk.Frame(self, bg=COR_FUNDO, padx=PAD * 2, pady=PAD)
        corpo.pack(fill="both", expand=True)

        # Título + botão novo
        topo = tk.Frame(corpo, bg=COR_FUNDO)
        topo.pack(fill="x", pady=(PAD, PAD_SM))

        tk.Label(
            topo,
            text="Meus cardápios",
            font=FONTE_TITULO,
            fg=COR_TEXTO,
            bg=COR_FUNDO,
        ).pack(side="left")

        tk.Button(
            topo,
            text="+ Novo cardápio",
            font=FONTE_CORPO_B,
            bg=COR_PRIMARIA,
            fg="white",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.novo_cardapio_cb,
            activebackground=COR_PRIMARIA_DARK,
            activeforeground="white",
        ).pack(side="right")

        # ── Tabela ─────────────────────────────────────────────────────────
        frame_tabela = tk.Frame(corpo, bg=COR_FUNDO)
        frame_tabela.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background=COR_FUNDO_CARD,
            fieldbackground=COR_FUNDO_CARD,
            foreground=COR_TEXTO,
            rowheight=36,
            font=FONTE_CORPO,
            borderwidth=0,
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=COR_PRIMARIA,
            foreground="white",
            font=FONTE_CORPO_B,
            relief="flat",
        )
        style.map("Custom.Treeview", background=[("selected", COR_PRIMARIA)])

        cols = ("nome", "kcal", "refeicoes", "data")
        self.tree = ttk.Treeview(
            frame_tabela,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
        )
        self.tree.heading("nome",      text="Nome do cardápio")
        self.tree.heading("kcal",      text="Kcal/dia")
        self.tree.heading("refeicoes", text="Refeições")
        self.tree.heading("data",      text="Criado em")

        self.tree.column("nome",      width=280, anchor="w")
        self.tree.column("kcal",      width=100, anchor="center")
        self.tree.column("refeicoes", width=100, anchor="center")
        self.tree.column("data",      width=160, anchor="center")

        scroll = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", lambda e: self._abrir_selecionado())

        # ── Botões de ação ─────────────────────────────────────────────────
        acoes = tk.Frame(corpo, bg=COR_FUNDO, pady=PAD_SM)
        acoes.pack(fill="x")

        tk.Button(
            acoes,
            text="✏️  Editar",
            font=FONTE_CORPO,
            bg=COR_ACENTO,
            fg=COR_TEXTO,
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._abrir_selecionado,
        ).pack(side="left", padx=(0, PAD_SM))

        tk.Button(
            acoes,
            text="🗑️  Excluir",
            font=FONTE_CORPO,
            bg=COR_VERMELHO,
            fg="white",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._excluir_selecionado,
        ).pack(side="left")

        self.lbl_vazio = tk.Label(
            corpo,
            text="Nenhum cardápio encontrado. Clique em '+ Novo cardápio' para começar.",
            font=FONTE_CORPO,
            fg=COR_TEXTO_MUTED,
            bg=COR_FUNDO,
        )

        self.carregar_lista()

    def carregar_lista(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        cardapios = listar_cardapios()

        if not cardapios:
            self.lbl_vazio.pack(pady=PAD)
        else:
            self.lbl_vazio.pack_forget()
            for c in cardapios:
                cardapio_obj = carregar_cardapio(c["id"])
                n_refeicoes = len(cardapio_obj.refeicoes) if cardapio_obj else "—"
                data = c["data_criacao"][:16] if c["data_criacao"] else "—"
                self.tree.insert("", "end", iid=str(c["id"]), values=(
                    c["nome"],
                    f"{c['kcal_total']:.0f} kcal",
                    n_refeicoes,
                    data,
                ))

    def _abrir_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione um cardápio para abrir.")
            return
        self.abrir_cardapio_cb(int(sel[0]))

    def _excluir_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione um cardápio para excluir.")
            return
        nome = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmar", f"Excluir o cardápio '{nome}'?"):
            excluir_cardapio(int(sel[0]))
            self.carregar_lista()
