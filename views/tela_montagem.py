import tkinter as tk
from tkinter import ttk, messagebox
from views.estilos import *
from models.modelos import Alimento, ItemRefeicao
from models.repositorio import buscar_alimentos, listar_grupos, salvar_cardapio


class TelaMontagem(tk.Frame):
    """Tela 3 — Montagem das refeições com adição de alimentos e validação."""

    def __init__(self, master, cardapio, voltar_cb, salvo_cb):
        super().__init__(master, bg=COR_FUNDO)
        self.cardapio = cardapio
        self.voltar_cb = voltar_cb
        self.salvo_cb = salvo_cb
        self._construir()

    def _construir(self):
        # Cabeçalho
        h = tk.Frame(self, bg=COR_PRIMARIA_DARK, pady=14)
        h.pack(fill="x")
        tk.Label(h, text="Montagem do cardápio", font=("Georgia", 16, "bold"),
                 fg="white", bg=COR_PRIMARIA_DARK).pack()
        tk.Label(h, text=f"{self.cardapio.nome}  •  {self.cardapio.kcal_total:.0f} kcal/dia",
                 font=FONTE_PEQUENA, fg="#A8D5BA", bg=COR_PRIMARIA_DARK).pack()

        # Rodapé (criar ANTES das refeições para evitar AttributeError)
        rodape = tk.Frame(self, bg=COR_FUNDO, pady=PAD_SM, padx=PAD * 2)
        rodape.pack(side="bottom", fill="x")

        tk.Button(
            rodape, text="← Voltar", font=FONTE_CORPO,
            bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
            cursor="hand2", command=self.voltar_cb,
        ).pack(side="left")

        self.btn_salvar = tk.Button(
            rodape, text="💾  Salvar cardápio completo", font=FONTE_CORPO_B,
            bg=COR_PRIMARIA, fg="white", relief="flat", padx=14, pady=6,
            cursor="hand2", command=self._salvar_completo,
            state="disabled",
        )
        self.btn_salvar.pack(side="right")

        self.lbl_status_geral = tk.Label(
            rodape, text="", font=FONTE_CORPO, bg=COR_FUNDO
        )
        self.lbl_status_geral.pack(side="right", padx=PAD)

        # Área rolável
        container = tk.Frame(self, bg=COR_FUNDO)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=COR_FUNDO, bd=0, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=COR_FUNDO, padx=PAD * 2, pady=PAD)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units"))

        # Renderiza cada refeição
        self._cards_refeicao = {}
        for refeicao in self.cardapio.refeicoes:
            self._renderizar_refeicao(refeicao)

        self._atualizar_status_geral()

    def _renderizar_refeicao(self, refeicao):
        card = tk.LabelFrame(
            self.scroll_frame,
            text=f"  {refeicao.nome}  •  {refeicao.kcal_refeicao:.1f} kcal  ({refeicao.percentual:.1f}%)",
            font=FONTE_CORPO_B,
            bg=COR_FUNDO_CARD,
            fg=COR_PRIMARIA_DARK,
            relief="groove",
            padx=PAD,
            pady=PAD_SM,
        )
        card.pack(fill="x", pady=(0, PAD))

        # ── Busca de alimentos ─────────────────────────────────────────────
        frame_busca = tk.Frame(card, bg=COR_FUNDO_CARD)
        frame_busca.pack(fill="x", pady=(0, PAD_SM))

        tk.Label(frame_busca, text="Buscar alimento:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left", padx=(0, PAD_SM))

        ent_busca = tk.Entry(frame_busca, font=FONTE_CORPO, width=22, relief="solid", bd=1)
        ent_busca.pack(side="left", padx=(0, PAD_SM))

        grupos = ["Todos os grupos"] + listar_grupos()
        var_grupo = tk.StringVar(value=grupos[0])
        cmb_grupo = ttk.Combobox(frame_busca, textvariable=var_grupo,
                                  values=grupos, width=20, state="readonly")
        cmb_grupo.pack(side="left", padx=(0, PAD_SM))

        tk.Label(frame_busca, text="Qtd (g):", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left", padx=(0, PAD_SM))
        ent_qtd = tk.Entry(frame_busca, font=FONTE_CORPO, width=7, relief="solid", bd=1)
        ent_qtd.pack(side="left", padx=(0, PAD_SM))

        # Lista de resultados
        frame_resultado = tk.Frame(card, bg=COR_FUNDO_CARD)
        frame_resultado.pack(fill="x", pady=(0, PAD_SM))

        lst_resultados = tk.Listbox(
            frame_resultado, font=FONTE_PEQUENA, height=4,
            relief="solid", bd=1, selectmode="single",
            bg=COR_FUNDO_CARD, fg=COR_TEXTO, activestyle="none",
            selectbackground=COR_PRIMARIA, selectforeground="white",
        )
        lst_resultados.pack(side="left", fill="x", expand=True)
        scr_lst = ttk.Scrollbar(frame_resultado, orient="vertical",
                                  command=lst_resultados.yview)
        lst_resultados.configure(yscrollcommand=scr_lst.set)
        scr_lst.pack(side="right", fill="y")

        alimentos_encontrados = []

        def _buscar(*_):
            nonlocal alimentos_encontrados
            termo = ent_busca.get().strip()
            grupo = var_grupo.get()
            grupo_filtro = "" if grupo == "Todos os grupos" else grupo
            alimentos_encontrados = buscar_alimentos(termo, grupo_filtro)
            lst_resultados.delete(0, "end")
            for a in alimentos_encontrados:
                lst_resultados.insert("end", f"{a.descricao}  [{a.grupo}]")

        ent_busca.bind("<KeyRelease>", _buscar)
        cmb_grupo.bind("<<ComboboxSelected>>", _buscar)
        
        # Carrega todos os alimentos ao iniciar
        _buscar()

        def _adicionar_alimento():
            sel = lst_resultados.curselection()
            if not sel:
                messagebox.showinfo("Atenção", "Selecione um alimento da lista.")
                return
            try:
                qtd = float(ent_qtd.get())
                if qtd <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Atenção", "Informe uma quantidade válida em gramas.")
                return

            alimento = alimentos_encontrados[sel[0]]
            item = ItemRefeicao(alimento=alimento, quantidade_g=qtd)
            refeicao.itens.append(item)
            _atualizar_tabela()
            ent_qtd.delete(0, "end")

        tk.Button(
            frame_busca, text="+ Adicionar", font=FONTE_CORPO,
            bg=COR_PRIMARIA, fg="white", relief="flat", padx=10, pady=3,
            cursor="hand2", command=_adicionar_alimento,
        ).pack(side="left")

        # ── Alimento personalizado ─────────────────────────────────────────
        def _adicionar_custom():
            dialog = tk.Toplevel(self)
            dialog.title("Adicionar Alimento Personalizado")
            dialog.geometry("420x360")
            dialog.resizable(False, False)
            dialog.transient(self)
            dialog.grab_set()
            dialog.configure(bg=COR_FUNDO)

            frame = tk.Frame(dialog, bg=COR_FUNDO_CARD, padx=PAD * 2, pady=PAD)
            frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)

            # Aviso: alimento fica só no cardápio, não no banco de dados
            aviso = tk.Label(
                frame,
                text="ℹ️  Este alimento ficará registrado apenas neste cardápio.\n"
                     "Ele não será salvo na base de dados do aplicativo.",
                font=FONTE_PEQUENA, bg=COR_AMARELO_LIGHT, fg=COR_TEXTO,
                pady=PAD_SM, padx=PAD_SM, justify="left", wraplength=360,
            )
            aviso.pack(fill="x", pady=(0, PAD))

            campos = {}
            for label, chave in [
                ("Nome:", "descricao"),
                ("Quantidade (g):", "quantidade"),
                ("Calorias (kcal/100g):", "calorias"),
                ("Proteínas (g/100g):", "proteinas"),
                ("Carboidratos (g/100g):", "carboidratos"),
                ("Lipídeos (g/100g):", "lipideos"),
            ]:
                f = tk.Frame(frame, bg=COR_FUNDO_CARD)
                f.pack(fill="x", pady=2)
                tk.Label(f, text=label, font=FONTE_CORPO, width=22, anchor="w",
                         bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left")
                ent = tk.Entry(f, font=FONTE_CORPO, relief="solid", bd=1)
                ent.pack(side="left", fill="x", expand=True)
                campos[chave] = ent

            def _confirmar():
                descricao = campos["descricao"].get().strip()
                if not descricao:
                    messagebox.showwarning("Atenção", "Informe a descrição.", parent=dialog)
                    return
                try:
                    qtd = float(campos["quantidade"].get())
                    calorias = float(campos["calorias"].get())
                    proteinas = float(campos["proteinas"].get())
                    carboidratos = float(campos["carboidratos"].get())
                    lipideos = float(campos["lipideos"].get())
                    if qtd <= 0:
                        raise ValueError("Quantidade deve ser maior que zero.")
                    if any(v < 0 for v in [calorias, proteinas, carboidratos, lipideos]):
                        raise ValueError("Valores nutricionais não podem ser negativos.")
                    if proteinas + carboidratos + lipideos > 100:
                        raise ValueError(
                            f"Soma de macros ({proteinas+carboidratos+lipideos:.1f}g) excede 100g por 100g."
                        )
                except ValueError as e:
                    messagebox.showwarning("Atenção", str(e), parent=dialog)
                    return

                alimento_custom = Alimento(
                    id=None, grupo="",
                    descricao=descricao,
                    calorias=calorias,
                    proteinas=proteinas,
                    lipideos=lipideos,
                    carboidratos=carboidratos,
                    fonte="custom",
                )
                refeicao.itens.append(ItemRefeicao(alimento=alimento_custom, quantidade_g=qtd))
                dialog.destroy()
                _atualizar_tabela()

            frame_btns = tk.Frame(frame, bg=COR_FUNDO_CARD)
            frame_btns.pack(fill="x", pady=(PAD, 0))
            tk.Button(frame_btns, text="Cancelar", font=FONTE_CORPO,
                      bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
                      cursor="hand2", command=dialog.destroy).pack(side="left")
            tk.Button(frame_btns, text="✓ Adicionar", font=FONTE_CORPO_B,
                      bg=COR_PRIMARIA, fg="white", relief="flat", padx=12, pady=6,
                      cursor="hand2", command=_confirmar).pack(side="right")
            campos["descricao"].focus()

        frame_link_custom = tk.Frame(card, bg=COR_FUNDO_CARD)
        frame_link_custom.pack(fill="x", pady=(0, PAD_SM))
        tk.Button(
            frame_link_custom,
            text="+ Adicionar alimento personalizado",
            font=FONTE_PEQUENA, bg=COR_FUNDO_CARD, fg=COR_ACENTO,
            relief="flat", padx=0, pady=1, cursor="hand2",
            command=_adicionar_custom, anchor="w",
        ).pack(side="left")

        # ── Tabela de alimentos ────────────────────────────────────────────
        style = ttk.Style()
        style.configure("Alim.Treeview", rowheight=28, font=FONTE_PEQUENA,
                         background=COR_FUNDO_CARD, fieldbackground=COR_FUNDO_CARD,
                         foreground=COR_TEXTO)
        style.configure("Alim.Treeview.Heading", font=FONTE_PEQUENA,
                         background=COR_PRIMARIA, foreground="white")

        # Frame para tabela com scroll próprio
        frame_tree = tk.Frame(card, bg=COR_FUNDO_CARD)
        frame_tree.pack(fill="x", pady=(0, PAD_SM))

        cols = ("alimento", "grupo", "qtd", "kcal", "prot", "carb", "lip")
        tree = ttk.Treeview(frame_tree, columns=cols, show="headings",
                             style="Alim.Treeview", height=5)
        for col, txt, w in [
            ("alimento", "Alimento",       220),
            ("grupo",    "Grupo",          140),
            ("qtd",      "Qtd (g)",         70),
            ("kcal",     "Kcal",            70),
            ("prot",     "Prot (g)",        80),
            ("carb",     "Carb (g)",        80),
            ("lip",      "Lip (g)",         80),
        ]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center" if col != "alimento" else "w")

        # Scrollbar para a tabela
        tree_scroll = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tree_scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        
        # Desabilita propagação do scroll para o canvas principal
        tree.bind("<Enter>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        tree.bind("<Leave>", lambda e: self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(-1*(e.delta//120), "units")))

        # ── Frame para edição inline ──────────────────────────────────────
        frame_edicao = tk.Frame(card, bg=COR_AMARELO_LIGHT, pady=PAD_SM, padx=PAD)
        # Não pack ainda - só mostra quando estiver editando
        
        lbl_editando = tk.Label(frame_edicao, text="", font=FONTE_CORPO_B,
                                bg=COR_AMARELO_LIGHT, fg=COR_TEXTO)
        lbl_editando.pack(side="left", padx=(0, PAD))
        
        tk.Label(frame_edicao, text="Nova quantidade:", font=FONTE_CORPO,
                 bg=COR_AMARELO_LIGHT, fg=COR_TEXTO).pack(side="left", padx=(0, PAD_SM))
        
        ent_edicao = tk.Entry(frame_edicao, font=FONTE_CORPO, width=10,
                              relief="solid", bd=2, bg="white")
        ent_edicao.pack(side="left", padx=(0, PAD_SM))
        
        tk.Label(frame_edicao, text="g", font=FONTE_CORPO,
                 bg=COR_AMARELO_LIGHT, fg=COR_TEXTO_MUTED).pack(side="left", padx=(0, PAD))
        
        idx_editando = [None]  # Usar lista para permitir modificação na closure
        
        def _salvar_edicao():
            if idx_editando[0] is None:
                return
            try:
                nova_qtd = float(ent_edicao.get())
                if nova_qtd <= 0:
                    raise ValueError
                refeicao.itens[idx_editando[0]].quantidade_g = nova_qtd
                _cancelar_edicao()
                _atualizar_tabela()
            except ValueError:
                messagebox.showwarning("Atenção", "Informe uma quantidade válida em gramas.")
        
        def _cancelar_edicao():
            idx_editando[0] = None
            frame_edicao.pack_forget()
            ent_edicao.delete(0, tk.END)
        
        tk.Button(frame_edicao, text="✓ Salvar", font=FONTE_CORPO,
                  bg=COR_VERDE, fg="white", relief="flat", padx=10, pady=3,
                  cursor="hand2", command=_salvar_edicao).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_edicao, text="✕ Cancelar", font=FONTE_CORPO,
                  bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=10, pady=3,
                  cursor="hand2", command=_cancelar_edicao).pack(side="left")
        
        ent_edicao.bind("<Return>", lambda e: _salvar_edicao())
        ent_edicao.bind("<Escape>", lambda e: _cancelar_edicao())

        # ── Totais + validação (NOVO: ranges ao lado) ──────────────────────
        ranges = refeicao.ranges_gramas
        
        frame_totais = tk.Frame(card, bg=COR_FUNDO_CARD, pady=8)
        frame_totais.pack(fill="x")

        # Kcal total (sem range, só informativo)
        f_kcal = tk.Frame(frame_totais, bg=COR_FUNDO_CARD)
        f_kcal.pack(side="left", padx=(0, PAD * 2))
        tk.Label(f_kcal, text="Total kcal:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).pack(anchor="w")
        lbl_kcal = tk.Label(f_kcal, text="0", font=FONTE_MONO,
                           bg=COR_FUNDO_CARD, fg=COR_TEXTO, width=10)
        lbl_kcal.pack(anchor="w")

        lbl_totais = {"kcal": lbl_kcal}

        # Macros com ranges ao lado
        for macro, (label_macro, pct_str, cor_macro) in RANGES_LABELS.items():
            r = ranges[macro]
            
            f = tk.Frame(frame_totais, bg=COR_FUNDO_CARD)
            f.pack(side="left", padx=(0, PAD * 2))
            
            # Label do macro
            tk.Label(f, text=f"{label_macro}:", font=FONTE_CORPO_B,
                     bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED).pack(anchor="w")
            
            # Frame para valor + range
            valor_range = tk.Frame(f, bg=COR_FUNDO_CARD)
            valor_range.pack(anchor="w")
            
            # Valor atual
            lbl = tk.Label(valor_range, text="0g", font=FONTE_MONO,
                           bg=COR_FUNDO_CARD, fg=COR_TEXTO, width=8)
            lbl.pack(side="left")
            
            # Range esperado (ao lado)
            tk.Label(valor_range, 
                     text=f"  [{r['min']:.1f}–{r['max']:.1f}g]", 
                     font=FONTE_PEQUENA,
                     bg=COR_FUNDO_CARD, 
                     fg=COR_TEXTO_MUTED).pack(side="left")
            
            lbl_totais[macro] = lbl

        # Status da refeição + botão salvar individual
        frame_acoes = tk.Frame(card, bg=COR_FUNDO_CARD, pady=PAD_SM)
        frame_acoes.pack(fill="x")

        lbl_status = tk.Label(frame_acoes, text="", font=FONTE_CORPO_B,
                               bg=COR_FUNDO_CARD, pady=4, padx=8)
        lbl_status.pack(side="left")

        btn_salvar_refeicao = tk.Button(
            frame_acoes, 
            text="💾 Salvar esta refeição", 
            font=FONTE_CORPO,
            bg=COR_VERDE, 
            fg="white", 
            relief="flat", 
            padx=12, 
            pady=5,
            cursor="hand2", 
            command=lambda: self._salvar_refeicao_individual(refeicao),
            state="disabled",
        )
        btn_salvar_refeicao.pack(side="right")

        # Botões de ação
        def _editar_item():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Atenção", "Selecione um alimento para editar.")
                return
            idx = tree.index(sel[0])
            item = refeicao.itens[idx]
            
            idx_editando[0] = idx
            lbl_editando.config(text=f"Editando: {item.alimento.descricao}")
            ent_edicao.delete(0, tk.END)
            ent_edicao.insert(0, str(item.quantidade_g))
            frame_edicao.pack(fill="x", pady=(0, PAD_SM), after=frame_tree)
            ent_edicao.focus()
            ent_edicao.select_range(0, tk.END)
        
        def _remover_item():
            sel = tree.selection()
            if not sel:
                return
            idx = tree.index(sel[0])
            refeicao.itens.pop(idx)
            _cancelar_edicao()
            _atualizar_tabela()

        tk.Button(
            frame_acoes, text="✏️ Editar quantidade", font=FONTE_PEQUENA,
            bg=COR_ACENTO, fg=COR_TEXTO, relief="flat", padx=8, pady=4,
            cursor="hand2", command=_editar_item,
        ).pack(side="right", padx=(0, PAD_SM))
        
        tk.Button(
            frame_acoes, text="🗑 Remover alimento", font=FONTE_PEQUENA,
            bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=8, pady=4,
            cursor="hand2", command=_remover_item,
        ).pack(side="right", padx=(0, PAD_SM))

        self._cards_refeicao[refeicao.nome] = {
            "tree": tree,
            "lbl_totais": lbl_totais,
            "lbl_status": lbl_status,
            "btn_salvar": btn_salvar_refeicao,
        }

        def _atualizar_tabela():
            for row in tree.get_children():
                tree.delete(row)
            tree.tag_configure("custom", background=COR_AMARELO_LIGHT)
            for item in refeicao.itens:
                m = item.macros
                is_custom = item.alimento.fonte == 'custom'
                tree.insert("", "end", values=(
                    f"{item.alimento.descricao} ✎" if is_custom else item.alimento.descricao,
                    "(personalizado)" if is_custom else item.alimento.grupo,
                    f"{item.quantidade_g:.1f}",
                    f"{m['calorias']:.1f}",
                    f"{m['proteinas']:.1f}",
                    f"{m['carboidratos']:.1f}",
                    f"{m['lipideos']:.1f}",
                ), tags=("custom",) if is_custom else ())

            totais = refeicao.totais
            validacao = refeicao.validacao

            lbl_totais["kcal"].config(text=f"{totais['calorias']:.1f}")

            for macro, chave in [("proteinas", "proteinas"),
                                   ("carboidratos", "carboidratos"),
                                   ("lipideos", "lipideos")]:
                ok = validacao[chave]
                cor = COR_VERDE if ok else COR_VERMELHO
                bg  = COR_VERDE_LIGHT if ok else COR_VERMELHO_LIGHT
                lbl_totais[macro].config(
                    text=f"{totais[macro]:.1f}g",
                    fg=cor, bg=bg,
                )

            if validacao["valida"]:
                lbl_status.config(
                    text="✔ Refeição válida!",
                    bg=COR_VERDE_LIGHT, fg=COR_VERDE,
                )
                btn_salvar_refeicao.config(state="normal")
            elif refeicao.itens:
                lbl_status.config(
                    text="✘ Macros fora do range",
                    bg=COR_VERMELHO_LIGHT, fg=COR_VERMELHO,
                )
                btn_salvar_refeicao.config(state="disabled")
            else:
                lbl_status.config(text="", bg=COR_FUNDO_CARD)
                btn_salvar_refeicao.config(state="disabled")

            self._atualizar_status_geral()

        _atualizar_tabela()
        self._cards_refeicao[refeicao.nome]["atualizar"] = _atualizar_tabela

    def _atualizar_status_geral(self):
        if self.cardapio.todas_validas:
            self.btn_salvar.config(state="normal")
            self.lbl_status_geral.config(
                text="✔ Todas as refeições estão válidas!",
                fg=COR_VERDE,
            )
        else:
            self.btn_salvar.config(state="disabled")
            validas = sum(1 for r in self.cardapio.refeicoes if r.validacao["valida"])
            total = len(self.cardapio.refeicoes)
            self.lbl_status_geral.config(
                text=f"{validas}/{total} refeições válidas",
                fg=COR_TEXTO_MUTED,
            )

    def _salvar_refeicao_individual(self, refeicao):
        """Salva apenas esta refeição específica."""
        if not refeicao.validacao["valida"]:
            messagebox.showwarning("Atenção", "Esta refeição ainda não está válida.")
            return
        
        # Salva o cardápio inteiro (necessário para manter consistência no banco)
        salvar_cardapio(self.cardapio)
        
        messagebox.showinfo(
            "Refeição salva!",
            f"A refeição '{refeicao.nome}' foi salva com sucesso!\n\n"
            f"Kcal: {refeicao.totais['calorias']:.1f}\n"
            f"Proteínas: {refeicao.totais['proteinas']:.1f}g\n"
            f"Carboidratos: {refeicao.totais['carboidratos']:.1f}g\n"
            f"Lipídeos: {refeicao.totais['lipideos']:.1f}g"
        )

    def _salvar_completo(self):
        """Salva o cardápio completo."""
        salvar_cardapio(self.cardapio)
        messagebox.showinfo(
            "Cardápio salvo!",
            f"O cardápio '{self.cardapio.nome}' foi salvo com sucesso!\n\n"
            f"Total do dia: {self.cardapio.kcal_total:.0f} kcal\n"
            f"Refeições: {len(self.cardapio.refeicoes)}"
        )
        self.salvo_cb()
