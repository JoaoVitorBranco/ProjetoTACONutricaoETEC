import tkinter as tk
import sys
import os

# Windows: força ícone correto na barra de tarefas (evita pena padrão do Python)
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ETEC.CardapioNutricional.1")
except Exception:
    pass

# Garante que os módulos locais são encontrados (necessário para PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database.db import inicializar_banco, get_connection
from views.tela_home import TelaHome
from views.tela_configuracao import TelaConfiguracaoCardapio
from views.tela_montagem import TelaMontagem
from models.repositorio import carregar_cardapio


def _popular_taco_se_vazio():
    """Na primeira execução, importa automaticamente os alimentos da tabela TACO."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM alimentos").fetchone()[0]
    conn.close()
    if count == 0:
        try:
            from models.repositorio import restaurar_base_taco
            restaurar_base_taco()
        except Exception:
            pass  # Segue sem dados; usuário pode importar manualmente depois


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cardápio Nutricional — Técnico em Nutrição")
        self.geometry("960x680")
        self.minsize(800, 560)
        self.configure(bg="#F7F8F5")

        # Ícone da janela
        try:
            base = sys._MEIPASS if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            self.iconbitmap(os.path.join(base, "logo.ico"))
        except Exception:
            pass

        # Inicializa banco e popula TACO na primeira execução
        inicializar_banco()
        _popular_taco_se_vazio()

        # Criar menu
        self._criar_menu()

        self._tela_atual = None
        self._ir_para_home()

    def _criar_menu(self):
        """Cria a barra de menu superior."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menu Ferramentas
        menu_ferramentas = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas)
        menu_ferramentas.add_command(label="Gerenciar Alimentos", command=self._abrir_gerenciar_alimentos)

    def _abrir_gerenciar_alimentos(self):
        """Abre a janela de gerenciamento de alimentos."""
        from views.tela_gerenciar_alimentos import TelaGerenciarAlimentos
        TelaGerenciarAlimentos(self)

    # ── Navegação ─────────────────────────────────────────────────────────────

    def _limpar(self):
        if self._tela_atual:
            self._tela_atual.destroy()
            self._tela_atual = None

    def _ir_para_home(self):
        self._limpar()
        tela = TelaHome(
            master=self,
            abrir_cardapio_cb=self._abrir_cardapio,
            novo_cardapio_cb=self._novo_cardapio,
        )
        tela.pack(fill="both", expand=True)
        self._tela_atual = tela

    def _novo_cardapio(self):
        """Novo cardápio - Modo 1 (inserção direta)"""
        self._limpar()
        tela = TelaConfiguracaoCardapio(
            master=self,
            avancar_cb=self._ir_para_montagem,
            voltar_cb=self._ir_para_home,
        )
        tela.pack(fill="both", expand=True)
        self._tela_atual = tela

    def _abrir_cardapio(self, cardapio_id: int):
        cardapio = carregar_cardapio(cardapio_id)
        if not cardapio:
            return
        self._limpar()
        tela = TelaConfiguracaoCardapio(
            master=self,
            avancar_cb=self._ir_para_montagem,
            voltar_cb=self._ir_para_home,
            cardapio_existente=cardapio,
        )
        tela.pack(fill="both", expand=True)
        self._tela_atual = tela

    def _ir_para_montagem(self, cardapio):
        self._limpar()
        tela = TelaMontagem(
            master=self,
            cardapio=cardapio,
            voltar_cb=lambda: self._retornar_configuracao(cardapio),
            salvo_cb=self._ir_para_home,
        )
        tela.pack(fill="both", expand=True)
        self._tela_atual = tela

    def _retornar_configuracao(self, cardapio):
        self._limpar()
        tela = TelaConfiguracaoCardapio(
            master=self,
            avancar_cb=self._ir_para_montagem,
            voltar_cb=self._ir_para_home,
            cardapio_existente=cardapio,
        )
        tela.pack(fill="both", expand=True)
        self._tela_atual = tela


if __name__ == "__main__":
    app = App()
    app.mainloop()
