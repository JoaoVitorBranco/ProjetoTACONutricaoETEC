import tkinter as tk
from tkinter import ttk, messagebox
from views.estilos import *
from models.modelos import Cardapio, Refeicao


class TelaConfiguracaoCardapio(tk.Frame):
    """
    Tela 2 — O aluno informa o nome do cardápio, as kcal totais do dia
    e cria as refeições com seus percentuais. Avança para a Tela 3 quando
    a soma dos percentuais for exatamente 100%.
    """

    def __init__(self, master, avancar_cb, voltar_cb, cardapio_existente=None, kcal_inicial=None):
        super().__init__(master, bg=COR_FUNDO)
        self.avancar_cb = avancar_cb
        self.voltar_cb = voltar_cb
        self.cardapio = cardapio_existente
        self.kcal_inicial = kcal_inicial
        self._linhas_refeicao = []   # lista de dicts com widgets de cada linha
        self._construir()
        if cardapio_existente:
            self._preencher_existente()
        elif kcal_inicial:
            # Pré-preenche com kcal calculada
            self.entrada_kcal.insert(0, str(int(kcal_inicial)))

    # ── Construção da interface ───────────────────────────────────────────────

    def _construir(self):
        # Cabeçalho
        self._cabecalho("Configurar cardápio", "Defina as refeições e a distribuição de calorias")

        corpo = tk.Frame(self, bg=COR_FUNDO, padx=PAD * 2, pady=PAD)
        corpo.pack(fill="both", expand=True)

        # ── Nome e kcal ───────────────────────────────────────────────────
        frame_dados = tk.LabelFrame(
            corpo, text=" Dados gerais ", font=FONTE_CORPO_B,
            bg=COR_FUNDO_CARD, fg=COR_PRIMARIA, relief="groove", padx=PAD, pady=PAD
        )
        frame_dados.pack(fill="x", pady=(0, PAD))

        grade = tk.Frame(frame_dados, bg=COR_FUNDO_CARD)
        grade.pack(fill="x")

        tk.Label(grade, text="Nome do cardápio:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).grid(row=0, column=0, sticky="w", padx=(0, PAD_SM))
        self.entrada_nome = tk.Entry(grade, font=FONTE_CORPO, width=30,
                                     relief="solid", bd=1)
        self.entrada_nome.grid(row=0, column=1, sticky="w", padx=(0, PAD * 2))

        tk.Label(grade, text="Kcal totais do dia:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).grid(row=0, column=2, sticky="w", padx=(0, PAD_SM))
        self.entrada_kcal = tk.Entry(grade, font=FONTE_CORPO, width=10,
                                     relief="solid", bd=1)
        self.entrada_kcal.grid(row=0, column=3, sticky="w")
        tk.Label(grade, text="kcal", font=FONTE_CORPO,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).grid(row=0, column=4, padx=(4, 0))

        # ── Refeições ─────────────────────────────────────────────────────
        frame_ref = tk.LabelFrame(
            corpo, text=" Refeições ", font=FONTE_CORPO_B,
            bg=COR_FUNDO_CARD, fg=COR_PRIMARIA, relief="groove", padx=PAD, pady=PAD
        )
        frame_ref.pack(fill="both", expand=True, pady=(0, PAD))

        # Cabeçalho da tabela
        cabecalho = tk.Frame(frame_ref, bg=COR_PRIMARIA)
        cabecalho.pack(fill="x")
        for texto, peso in [("Nome da refeição", 3), ("% das kcal diárias", 2), ("Kcal calculadas", 2), ("", 1)]:
            tk.Label(
                cabecalho, text=texto, font=FONTE_CORPO_B,
                bg=COR_PRIMARIA, fg="white", pady=6
            ).pack(side="left", expand=True, fill="x")

        # Container das linhas
        self.frame_linhas = tk.Frame(frame_ref, bg=COR_FUNDO_CARD)
        self.frame_linhas.pack(fill="both", expand=True, pady=(PAD_SM, 0))

        # Linha de soma + botão adicionar
        rodape = tk.Frame(frame_ref, bg=COR_FUNDO_CARD)
        rodape.pack(fill="x", pady=(PAD_SM, 0))

        tk.Button(
            rodape, text="+ Adicionar refeição", font=FONTE_CORPO,
            bg=COR_PRIMARIA, fg="white", relief="flat", padx=10, pady=4,
            cursor="hand2", command=self._adicionar_linha,
        ).pack(side="left")

        soma_frame = tk.Frame(rodape, bg=COR_FUNDO_CARD)
        soma_frame.pack(side="right")
        tk.Label(soma_frame, text="Soma dos percentuais:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left", padx=(0, 4))
        self.lbl_soma = tk.Label(soma_frame, text="0%", font=FONTE_CORPO_B,
                                  bg=COR_FUNDO_CARD, fg=COR_VERMELHO, width=6)
        self.lbl_soma.pack(side="left")

        # ── Rodapé navegação ──────────────────────────────────────────────
        self._rodape_navegacao(corpo)

        # Adiciona 3 linhas vazias por padrão
        for _ in range(3):
            self._adicionar_linha()

    def _cabecalho(self, titulo, subtitulo):
        h = tk.Frame(self, bg=COR_PRIMARIA_DARK, pady=14)
        h.pack(fill="x")
        tk.Label(h, text=titulo, font=("Georgia", 16, "bold"),
                 fg="white", bg=COR_PRIMARIA_DARK).pack()
        tk.Label(h, text=subtitulo, font=FONTE_PEQUENA,
                 fg="#A8D5BA", bg=COR_PRIMARIA_DARK).pack()

    def _rodape_navegacao(self, pai):
        rodape = tk.Frame(pai, bg=COR_FUNDO, pady=PAD_SM)
        rodape.pack(fill="x", side="bottom")

        tk.Button(
            rodape, text="← Voltar", font=FONTE_CORPO,
            bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
            cursor="hand2", command=self.voltar_cb,
        ).pack(side="left")

        self.btn_avancar = tk.Button(
            rodape, text="Avançar para montagem →", font=FONTE_CORPO_B,
            bg=COR_PRIMARIA, fg="white", relief="flat", padx=14, pady=6,
            cursor="hand2", command=self._avancar,
            state="disabled",
        )
        self.btn_avancar.pack(side="right")

    # ── Linhas de refeição ────────────────────────────────────────────────────

    def _adicionar_linha(self, nome="", percentual=""):
        linha = tk.Frame(self.frame_linhas, bg=COR_FUNDO_CARD, pady=3)
        linha.pack(fill="x")

        ent_nome = tk.Entry(linha, font=FONTE_CORPO, width=22, relief="solid", bd=1)
        ent_nome.insert(0, nome)
        ent_nome.pack(side="left", padx=(0, PAD_SM))

        ent_pct = tk.Entry(linha, font=FONTE_CORPO, width=8, relief="solid", bd=1)
        ent_pct.insert(0, str(percentual))
        ent_pct.pack(side="left", padx=(0, 4))
        tk.Label(linha, text="%", font=FONTE_CORPO, bg=COR_FUNDO_CARD,
                 fg=COR_TEXTO_MUTED).pack(side="left", padx=(0, PAD_SM))

        lbl_kcal = tk.Label(linha, text="—", font=FONTE_MONO, width=12,
                             bg=COR_AMARELO_LIGHT, fg=COR_TEXTO, relief="flat")
        lbl_kcal.pack(side="left", padx=(0, PAD_SM))

        btn_rem = tk.Button(
            linha, text="✕", font=FONTE_PEQUENA,
            bg=COR_VERMELHO, fg="white", relief="flat", padx=6,
            cursor="hand2",
        )
        btn_rem.pack(side="left")

        dados = {"frame": linha, "nome": ent_nome, "pct": ent_pct, "kcal_lbl": lbl_kcal}
        self._linhas_refeicao.append(dados)

        btn_rem.config(command=lambda d=dados: self._remover_linha(d))
        ent_pct.bind("<KeyRelease>", lambda e: self._atualizar_soma())

        self._atualizar_soma()

    def _remover_linha(self, dados):
        dados["frame"].destroy()
        self._linhas_refeicao.remove(dados)
        self._atualizar_soma()

    def _atualizar_soma(self):
        soma = 0.0
        try:
            kcal_dia = float(self.entrada_kcal.get())
        except ValueError:
            kcal_dia = 0

        for d in self._linhas_refeicao:
            try:
                pct = float(d["pct"].get())
                soma += pct
                kcal_ref = kcal_dia * pct / 100
                d["kcal_lbl"].config(text=f"{kcal_ref:.1f} kcal")
            except ValueError:
                d["kcal_lbl"].config(text="—")

        self.lbl_soma.config(
            text=f"{soma:.1f}%",
            fg=COR_VERDE if abs(soma - 100) < 0.01 else COR_VERMELHO,
        )
        pode_avancar = abs(soma - 100) < 0.01 and len(self._linhas_refeicao) > 0
        self.btn_avancar.config(state="normal" if pode_avancar else "disabled")

    def _preencher_existente(self):
        self.entrada_nome.insert(0, self.cardapio.nome)
        self.entrada_kcal.insert(0, str(self.cardapio.kcal_total))

        # Remove linhas vazias padrão
        for d in self._linhas_refeicao[:]:
            d["frame"].destroy()
        self._linhas_refeicao.clear()

        for ref in self.cardapio.refeicoes:
            self._adicionar_linha(ref.nome, ref.percentual)

    # ── Avançar ───────────────────────────────────────────────────────────────

    def _avancar(self):
        nome = self.entrada_nome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "Informe o nome do cardápio.")
            return

        try:
            kcal = float(self.entrada_kcal.get())
            if kcal <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Informe um valor válido de kcal.")
            return

        refeicoes = []
        for i, d in enumerate(self._linhas_refeicao):
            nome_ref = d["nome"].get().strip()
            if not nome_ref:
                messagebox.showwarning("Atenção", f"Informe o nome da refeição {i+1}.")
                return
            try:
                pct = float(d["pct"].get())
            except ValueError:
                messagebox.showwarning("Atenção", f"Percentual inválido na refeição '{nome_ref}'.")
                return
            refeicoes.append(Refeicao(nome=nome_ref, percentual=pct, kcal_diaria=kcal, ordem=i))

        cardapio = self.cardapio or Cardapio(nome=nome, kcal_total=kcal)
        cardapio.nome = nome
        cardapio.kcal_total = kcal

        # Preserva itens das refeições se estiver editando
        if self.cardapio:
            nomes_antigos = {r.nome: r for r in self.cardapio.refeicoes}
            for ref in refeicoes:
                if ref.nome in nomes_antigos:
                    ref.itens = nomes_antigos[ref.nome].itens
                    ref.id = nomes_antigos[ref.nome].id

        cardapio.refeicoes = refeicoes
        self.avancar_cb(cardapio)
