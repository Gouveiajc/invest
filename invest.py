'''
Programa de Controle de Investimentos
JC 01/2026
Ver. 1
'''

import tkinter as tk
from tkinter import Menu
import inv01_01
import inv02_01
import inv03_01
import inv21_01
import inv21_05


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Controle de Aplicação")
        self.root.attributes("-fullscreen", True)

        # Atalho para sair do modo fullscreen
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        # Captura do clique no X
        self.root.protocol("WM_DELETE_WINDOW", self.sair)

        self.criar_menu()

    # -----------------------------
    #       MENU PRINCIPAL
    # -----------------------------
    def criar_menu(self):
        menu_bar = Menu(self.root)

        # MENU CADASTRO
        menu_cadastro = Menu(menu_bar, tearoff=0)
        menu_cadastro.add_command(
            label="Tipo Ativos",
            command=lambda: inv01_01.abrir_lista(self.root)
        )
        #menu_cadastro = Menu(menu_bar, tearoff=0)
        menu_cadastro.add_command(
            label="Segmentos", 
            command=lambda: inv02_01.abrir_lista(self.root)
        )
        menu_cadastro.add_command(
            label="Ativos", 
            command=lambda: inv03_01.abrir_lista(self.root)
            )
        
        menu_bar.add_cascade(label="Cadastro", menu=menu_cadastro)
        
        # MENU MANUTENÇÃO
        menu_manutencao = Menu(menu_bar, tearoff=0)
        menu_manutencao.add_command(
            label="Movimento", 
            command=lambda: inv21_01.abrir_lista(self.root)
            )
        
        menu_manutencao.add_command(
            label="Consolidar", 
            command=lambda: inv21_05.conciliar_ativos()
            )
        menu_bar.add_cascade(label="Manutenção", menu=menu_manutencao)

        # MENU IMPRESSÃO
        menu_impressao = Menu(menu_bar, tearoff=0)
        menu_impressao.add_command(label="Impressão de Dados", command=self.impressao)
        menu_bar.add_cascade(label="Impressão", menu=menu_impressao)

        # MENU SAIR
        menu_bar.add_command(label="Sair", command=self.sair)

        self.root.config(menu=menu_bar)

    # -----------------------------
    #       FUNÇÕES DO MENU
    # -----------------------------
    def cadastrar_classe(self):
        print("Cadastro de Classe de Ativos selecionado")

    def cadastrar_ativos(self):
        print("Cadastro de Ativos selecionado")

    def manutencao(self):
        print("Menu Manutenção selecionado")

    def impressao(self):
        print("Menu Impressão selecionado")

    def sair(self):
        self.root.quit()


# -----------------------------
#       INICIAR APLICAÇÃO
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
