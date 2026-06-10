import tkinter as tk
from tkinter import ttk, messagebox
from views.estilos import *
from models.repositorio import (
    buscar_alimentos, listar_grupos, adicionar_alimento, 
    editar_alimento, excluir_alimento, criar_grupo, 
    excluir_grupo, contar_alimentos_por_grupo
)


class TelaGerenciarAlimentos(tk.Toplevel):
    """Janela para gerenciar alimentos e grupos alimentares."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gerenciar Alimentos")
        self.geometry("1000x600")
        self.minsize(900, 500)
        self.configure(bg=COR_FUNDO)
        
        # Centralizar
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (500)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (300)
        self.geometry(f"1000x600+{x}+{y}")
        
        self._construir()
        self._carregar_alimentos()
    
    def _construir(self):
        # Cabeçalho
        header = tk.Frame(self, bg=COR_PRIMARIA_DARK, pady=14)
        header.pack(fill="x")
        
        tk.Label(header, text="🥗 Gerenciar Alimentos", 
                 font=("Georgia", 16, "bold"),
                 fg="white", bg=COR_PRIMARIA_DARK).pack()
        tk.Label(header, text="Adicione, edite e organize seus alimentos personalizados",
                 font=FONTE_PEQUENA, fg="#A8D5BA", bg=COR_PRIMARIA_DARK).pack()
        
        # Área principal
        corpo = tk.Frame(self, bg=COR_FUNDO, padx=PAD * 2, pady=PAD)
        corpo.pack(fill="both", expand=True)
        
        # Barra de busca e filtros
        frame_busca = tk.Frame(corpo, bg=COR_FUNDO)
        frame_busca.pack(fill="x", pady=(0, PAD))
        
        tk.Label(frame_busca, text="Buscar:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left", padx=(0, PAD_SM))
        
        self.ent_busca = tk.Entry(frame_busca, font=FONTE_CORPO, width=25,
                                   relief="solid", bd=1)
        self.ent_busca.pack(side="left", padx=(0, PAD))
        self.ent_busca.bind("<KeyRelease>", lambda e: self._carregar_alimentos())
        
        tk.Label(frame_busca, text="Grupo:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left", padx=(0, PAD_SM))
        
        self.var_grupo = tk.StringVar(value="Todos")
        self.cmb_grupo = ttk.Combobox(frame_busca, textvariable=self.var_grupo,
                                       width=20, state="readonly")
        self.cmb_grupo.pack(side="left")
        self.cmb_grupo.bind("<<ComboboxSelected>>", lambda e: self._carregar_alimentos())
        self._atualizar_combo_grupos()
        
        # Botões de ação principais
        frame_btns = tk.Frame(corpo, bg=COR_FUNDO)
        frame_btns.pack(fill="x", pady=(0, PAD))
        
        tk.Button(frame_btns, text="📁 Adicionar Grupo", font=FONTE_CORPO_B,
                  bg=COR_ACENTO, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._adicionar_grupo).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_btns, text="+ Adicionar Alimento", font=FONTE_CORPO_B,
                  bg=COR_PRIMARIA, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._adicionar_alimento).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_btns, text="📤 Exportar", font=FONTE_CORPO,
                  bg=COR_VERDE, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._exportar_alimentos).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_btns, text="📥 Importar", font=FONTE_CORPO,
                  bg=COR_VERDE, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._importar_alimentos).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_btns, text="🔄 Restaurar TACO", font=FONTE_CORPO,
                  bg="#FF9800", fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=self._restaurar_taco).pack(side="left")
        
        # Tabela de alimentos
        frame_tabela = tk.Frame(corpo, bg=COR_FUNDO)
        frame_tabela.pack(fill="both", expand=True, pady=(0, PAD))
        
        style = ttk.Style()
        style.configure("Gerenc.Treeview", rowheight=30, font=FONTE_CORPO,
                         background=COR_FUNDO_CARD, fieldbackground=COR_FUNDO_CARD,
                         foreground=COR_TEXTO)
        style.configure("Gerenc.Treeview.Heading", font=FONTE_CORPO_B,
                         background=COR_PRIMARIA, foreground="white")
        
        cols = ("descricao", "grupo", "calorias", "proteinas", "carboidratos", "lipideos", "fonte")
        self.tree = ttk.Treeview(frame_tabela, columns=cols, show="headings",
                                  style="Gerenc.Treeview", selectmode="browse")
        
        for col, txt, w in [
            ("descricao", "Descrição", 250),
            ("grupo", "Grupo", 150),
            ("calorias", "Kcal", 70),
            ("proteinas", "Prot (g)", 80),
            ("carboidratos", "Carb (g)", 80),
            ("lipideos", "Lip (g)", 80),
            ("fonte", "Fonte", 80),
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="center" if col != "descricao" else "w")
        
        scroll = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        
        # Ações com alimentos selecionados
        frame_acoes = tk.Frame(corpo, bg=COR_FUNDO)
        frame_acoes.pack(fill="x")
        
        tk.Label(frame_acoes, text="Ações:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left", padx=(0, PAD))
        
        tk.Button(frame_acoes, text="✏️ Editar Alimento", font=FONTE_CORPO,
                  bg=COR_VERDE, fg="white", relief="flat", padx=12, pady=5,
                  cursor="hand2", command=self._editar_alimento).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_acoes, text="🗑 Excluir Alimento", font=FONTE_CORPO,
                  bg=COR_VERMELHO, fg="white", relief="flat", padx=12, pady=5,
                  cursor="hand2", command=self._excluir_alimento).pack(side="left", padx=(0, PAD_SM))
        
        tk.Button(frame_acoes, text="🗑 Excluir Grupo", font=FONTE_CORPO,
                  bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=5,
                  cursor="hand2", command=self._excluir_grupo).pack(side="left")
    
    def _atualizar_combo_grupos(self):
        """Atualiza a lista de grupos no combobox."""
        grupos = ["Todos"] + listar_grupos()
        self.cmb_grupo['values'] = grupos
    
    def _carregar_alimentos(self):
        """Carrega alimentos na tabela com base nos filtros."""
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Busca com filtros
        termo = self.ent_busca.get().strip()
        grupo = self.var_grupo.get()
        grupo_filtro = "" if grupo == "Todos" else grupo
        
        alimentos = buscar_alimentos(termo, grupo_filtro)
        
        for a in alimentos:
            # Destaca alimentos do usuário em negrito
            tags = ("usuario",) if a.fonte == "usuario" else ()
            self.tree.insert("", "end", iid=str(a.id), values=(
                a.descricao,
                a.grupo,
                f"{a.calorias:.1f}",
                f"{a.proteinas:.1f}",
                f"{a.carboidratos:.1f}",
                f"{a.lipideos:.1f}",
                a.fonte.upper()
            ), tags=tags)
        
        # Estilo para alimentos do usuário
        self.tree.tag_configure("usuario", font=FONTE_CORPO_B, foreground=COR_PRIMARIA)
    
    # ── Adicionar Grupo ───────────────────────────────────────────────────────
    
    def _adicionar_grupo(self):
        """Abre diálogo para criar novo grupo."""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Novo Grupo")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=COR_FUNDO)
        
        # Centralizar
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 125
        dialog.geometry(f"500x250+{x}+{y}")
        
        frame = tk.Frame(dialog, bg=COR_FUNDO_CARD, padx=PAD * 2, pady=PAD * 2)
        frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        
        tk.Label(frame, text="Nome do grupo:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(anchor="w", pady=(0, 8))
        
        ent_nome = tk.Entry(frame, font=FONTE_CORPO, relief="solid", bd=1)
        ent_nome.pack(fill="x", pady=(0, PAD_SM))
        ent_nome.focus()
        
        tk.Label(frame, text="Exemplos: Suplementos, Alimentos Industrializados, Receitas Caseiras",
                 font=FONTE_PEQUENA, bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED,
                 wraplength=440, justify="left").pack(anchor="w", pady=(0, PAD * 2))
        
        def _salvar():
            nome = ent_nome.get().strip()
            try:
                criar_grupo(nome)
                messagebox.showinfo("Sucesso", f"Grupo '{nome}' criado com sucesso!", parent=dialog)
                self._atualizar_combo_grupos()
                dialog.destroy()
            except ValueError as e:
                messagebox.showwarning("Atenção", str(e), parent=dialog)
        
        frame_btns = tk.Frame(frame, bg=COR_FUNDO_CARD)
        frame_btns.pack(fill="x", pady=(PAD, 0))
        
        tk.Button(frame_btns, text="Cancelar", font=FONTE_CORPO,
                  bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=14, pady=7,
                  cursor="hand2", command=dialog.destroy).pack(side="left")
        
        tk.Button(frame_btns, text="💾 Salvar Grupo", font=FONTE_CORPO_B,
                  bg=COR_PRIMARIA, fg="white", relief="flat", padx=14, pady=7,
                  cursor="hand2", command=_salvar).pack(side="right")
        
        ent_nome.bind("<Return>", lambda e: _salvar())
    
    # ── Adicionar Alimento ────────────────────────────────────────────────────
    
    def _adicionar_alimento(self):
        """Abre diálogo para adicionar novo alimento."""
        self._form_alimento(modo="adicionar")
    
    def _editar_alimento(self):
        """Edita o alimento selecionado."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione um alimento para editar.")
            return
        
        alimento_id = int(sel[0])
        self._form_alimento(modo="editar", alimento_id=alimento_id)
    
    def _form_alimento(self, modo="adicionar", alimento_id=None):
        """Formulário para adicionar ou editar alimento."""
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Alimento" if modo == "adicionar" else "Editar Alimento")
        dialog.geometry("450x420")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=COR_FUNDO)
        
        # Centralizar
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 225
        y = self.winfo_y() + (self.winfo_height() // 2) - 210
        dialog.geometry(f"450x420+{x}+{y}")
        
        frame = tk.Frame(dialog, bg=COR_FUNDO_CARD, padx=PAD * 2, pady=PAD * 2)
        frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        
        # Se editar, carrega dados
        alimento_atual = None
        if modo == "editar":
            from models.repositorio import buscar_alimento_por_id
            alimento_atual = buscar_alimento_por_id(alimento_id)
            if not alimento_atual:
                messagebox.showerror("Erro", "Alimento não encontrado.")
                dialog.destroy()
                return
            if alimento_atual.fonte != "usuario":
                messagebox.showwarning("Atenção", "Alimentos da base TACO não podem ser editados.")
                dialog.destroy()
                return
        
        # Descrição
        tk.Label(frame, text="Descrição do alimento:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(anchor="w", pady=(0, 4))
        ent_descricao = tk.Entry(frame, font=FONTE_CORPO, relief="solid", bd=1)
        ent_descricao.pack(fill="x", pady=(0, PAD))
        if alimento_atual:
            ent_descricao.insert(0, alimento_atual.descricao)
        
        # Grupo
        tk.Label(frame, text="Grupo alimentar:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(anchor="w", pady=(0, 4))
        var_grupo = tk.StringVar()
        cmb_grupo = ttk.Combobox(frame, textvariable=var_grupo, state="readonly")
        cmb_grupo['values'] = listar_grupos()
        cmb_grupo.pack(fill="x", pady=(0, PAD))
        if alimento_atual:
            var_grupo.set(alimento_atual.grupo)
        
        # Valores nutricionais
        tk.Label(frame, text="Valores nutricionais (por 100g):", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(anchor="w", pady=(PAD_SM, 4))
        
        campos = {}
        for label, chave in [
            ("Calorias (kcal):", "calorias"),
            ("Proteínas (g):", "proteinas"),
            ("Carboidratos (g):", "carboidratos"),
            ("Lipídeos (g):", "lipideos"),
        ]:
            f = tk.Frame(frame, bg=COR_FUNDO_CARD)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=FONTE_CORPO, width=18, anchor="w",
                     bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(side="left")
            ent = tk.Entry(f, font=FONTE_CORPO, width=12, relief="solid", bd=1)
            ent.pack(side="left")
            if alimento_atual:
                ent.insert(0, str(getattr(alimento_atual, chave)))
            campos[chave] = ent
        
        def _salvar():
            descricao = ent_descricao.get().strip()
            grupo = var_grupo.get()
            
            if not descricao:
                messagebox.showwarning("Atenção", "Informe a descrição do alimento.", parent=dialog)
                return
            if not grupo:
                messagebox.showwarning("Atenção", "Selecione um grupo.", parent=dialog)
                return
            
            try:
                calorias = float(campos["calorias"].get())
                proteinas = float(campos["proteinas"].get())
                carboidratos = float(campos["carboidratos"].get())
                lipideos = float(campos["lipideos"].get())
                
                if any(v < 0 for v in [calorias, proteinas, carboidratos, lipideos]):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Atenção", "Informe valores numéricos válidos >= 0.", parent=dialog)
                return
            
            try:
                if modo == "adicionar":
                    adicionar_alimento(grupo, descricao, calorias, proteinas, lipideos, carboidratos)
                    messagebox.showinfo("Sucesso", f"Alimento '{descricao}' adicionado!", parent=dialog)
                else:
                    editar_alimento(alimento_id, grupo, descricao, calorias, proteinas, lipideos, carboidratos)
                    messagebox.showinfo("Sucesso", f"Alimento '{descricao}' atualizado!", parent=dialog)
                
                self._carregar_alimentos()
                self._atualizar_combo_grupos()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", str(e), parent=dialog)
        
        frame_btns = tk.Frame(frame, bg=COR_FUNDO_CARD)
        frame_btns.pack(fill="x", pady=(PAD, 0))
        
        tk.Button(frame_btns, text="Cancelar", font=FONTE_CORPO,
                  bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=dialog.destroy).pack(side="left")
        
        tk.Button(frame_btns, text="💾 Salvar Alimento", font=FONTE_CORPO_B,
                  bg=COR_PRIMARIA, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=_salvar).pack(side="right")
    
    # ── Excluir ───────────────────────────────────────────────────────────────
    
    def _excluir_alimento(self):
        """Exclui o alimento selecionado."""
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Atenção", "Selecione um alimento para excluir.")
            return
        
        alimento_id = int(sel[0])
        valores = self.tree.item(sel[0])["values"]
        nome = valores[0]
        fonte = valores[6]
        
        if fonte == "TACO":
            messagebox.showwarning("Atenção", "Alimentos da base TACO não podem ser excluídos.")
            return
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir '{nome}'?\n\nEsta ação não pode ser desfeita."):
            try:
                excluir_alimento(alimento_id)
                messagebox.showinfo("Sucesso", f"Alimento '{nome}' excluído!")
                self._carregar_alimentos()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
    
    def _excluir_grupo(self):
        """Exclui um grupo (se possível)."""
        grupos = [g for g in listar_grupos() if g != "Todos"]
        
        if not grupos:
            messagebox.showinfo("Atenção", "Não há grupos disponíveis para excluir.")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Excluir Grupo")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=COR_FUNDO)
        
        # Centralizar
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 200
        y = self.winfo_y() + (self.winfo_height() // 2) - 90
        dialog.geometry(f"400x180+{x}+{y}")
        
        frame = tk.Frame(dialog, bg=COR_FUNDO_CARD, padx=PAD * 2, pady=PAD * 2)
        frame.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        
        tk.Label(frame, text="Selecione o grupo para excluir:", font=FONTE_CORPO_B,
                 bg=COR_FUNDO_CARD, fg=COR_TEXTO).pack(anchor="w", pady=(0, 4))
        
        var_grupo = tk.StringVar()
        cmb_grupo = ttk.Combobox(frame, textvariable=var_grupo, values=grupos, state="readonly")
        cmb_grupo.pack(fill="x", pady=(0, PAD))
        
        lbl_info = tk.Label(frame, text="", font=FONTE_PEQUENA,
                            bg=COR_FUNDO_CARD, fg=COR_TEXTO_MUTED, wraplength=350)
        lbl_info.pack(anchor="w", pady=(0, PAD))
        
        def _atualizar_info(*args):
            grupo = var_grupo.get()
            if grupo:
                info = contar_alimentos_por_grupo(grupo)
                lbl_info.config(
                    text=f"Alimentos neste grupo: {info['total']} "
                         f"(TACO: {info['taco']}, Usuário: {info['usuario']})"
                )
        
        var_grupo.trace("w", _atualizar_info)
        
        def _excluir():
            grupo = var_grupo.get()
            if not grupo:
                messagebox.showwarning("Atenção", "Selecione um grupo.", parent=dialog)
                return
            
            if messagebox.askyesno("Confirmar", 
                                    f"Tem certeza que deseja excluir o grupo '{grupo}'?",
                                    parent=dialog):
                try:
                    excluir_grupo(grupo)
                    messagebox.showinfo("Sucesso", f"Grupo '{grupo}' excluído!", parent=dialog)
                    self._atualizar_combo_grupos()
                    self._carregar_alimentos()
                    dialog.destroy()
                except ValueError as e:
                    messagebox.showwarning("Atenção", str(e), parent=dialog)
        
        frame_btns = tk.Frame(frame, bg=COR_FUNDO_CARD)
        frame_btns.pack(fill="x")
        
        tk.Button(frame_btns, text="Cancelar", font=FONTE_CORPO,
                  bg=COR_BORDA, fg=COR_TEXTO, relief="flat", padx=12, pady=6,
                  cursor="hand2", command=dialog.destroy).pack(side="left")
        
        tk.Button(frame_btns, text="🗑 Excluir Grupo", font=FONTE_CORPO_B,
                  bg=COR_VERMELHO, fg="white", relief="flat", padx=12, pady=6,
                  cursor="hand2", command=_excluir).pack(side="right")
    
    # ── Exportar / Importar / Restaurar ───────────────────────────────────────
    
    def _exportar_alimentos(self):
        """Exporta todos os alimentos para Excel."""
        from tkinter import filedialog
        from datetime import datetime
        from models.repositorio import exportar_alimentos_para_excel
        
        # Sugere nome de arquivo
        data_hoje = datetime.now().strftime("%Y%m%d")
        nome_sugerido = f"alimentos_cardapio_nutricional_{data_hoje}.xlsx"
        
        caminho = filedialog.asksaveasfilename(
            title="Exportar Alimentos",
            defaultextension=".xlsx",
            initialfile=nome_sugerido,
            filetypes=[("Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
        
        try:
            total = exportar_alimentos_para_excel(caminho)
            messagebox.showinfo(
                "Exportação Concluída",
                f"✅ {total} alimentos exportados com sucesso!\n\nArquivo salvo em:\n{caminho}"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar:\n{str(e)}")
    
    def _importar_alimentos(self):
        """Importa alimentos de um arquivo Excel."""
        from tkinter import filedialog
        from models.repositorio import importar_alimentos_de_excel
        
        caminho = filedialog.askopenfilename(
            title="Importar Alimentos",
            filetypes=[("Excel", "*.xlsx"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
        
        # Confirmação
        if not messagebox.askyesno(
            "Confirmar Importação",
            "A importação irá:\n\n"
            "• Criar novos alimentos\n"
            "• Atualizar alimentos existentes (TACO e usuário)\n"
            "• Criar novos grupos automaticamente\n\n"
            "Deseja continuar?"
        ):
            return
        
        try:
            resultado = importar_alimentos_de_excel(caminho)
            
            # Monta mensagem de resultado
            msg = f"✅ Importação concluída!\n\n"
            msg += f"📝 Alimentos criados: {resultado['criados']}\n"
            msg += f"✏️ Alimentos atualizados: {resultado['atualizados']}\n"
            msg += f"❌ Erros: {resultado['erros']}\n"
            
            if resultado['detalhes_erros']:
                msg += f"\n⚠️ Detalhes dos erros:\n"
                msg += "\n".join(resultado['detalhes_erros'][:5])  # Primeiros 5
                if len(resultado['detalhes_erros']) > 5:
                    msg += f"\n... e mais {len(resultado['detalhes_erros']) - 5} erros."
            
            messagebox.showinfo("Importação Concluída", msg)
            
            self._carregar_alimentos()
            self._atualizar_combo_grupos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar:\n{str(e)}")
    
    def _restaurar_taco(self):
        """Restaura a base TACO aos valores originais usando TACO embutida."""
        from models.repositorio import restaurar_base_taco
        
        # Aviso
        if not messagebox.askyesno(
            "Restaurar Base TACO",
            "⚠️ Esta ação irá restaurar todos os alimentos da base TACO\n"
            "aos valores originais da tabela TACO embutida no aplicativo.\n\n"
            "✅ Seus alimentos personalizados NÃO serão afetados.\n"
            "✅ Apenas alimentos com fonte 'TACO' serão restaurados.\n\n"
            "Deseja continuar?"
        ):
            return
        
        try:
            restaurados = restaurar_base_taco()
            messagebox.showinfo(
                "Restauração Concluída",
                f"✅ Base TACO restaurada com sucesso!\n\n"
                f"📊 {restaurados} alimentos da TACO foram restaurados aos valores originais.\n\n"
                f"✅ Seus alimentos personalizados foram preservados."
            )
            
            self._carregar_alimentos()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao restaurar TACO:\n{str(e)}")
