'''
Programa de Cadastro de Tipos de Ativo - Alteração
JC 01/2026
Ver 1
Banco de Dados inv.db
Tabela inv00

'''

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0

def alterar_registro(tree):
    """
    Função chamada pelo botão ALTERAR no grid.
    Recebe o Treeview, pega o item selecionado e abre a janela de edição.
    """
    item = tree.selection()
    if not item:
        messagebox.showwarning("Atenção", "Selecione um registro para alterar.")
        return

    valores = tree.item(item, "values")  # (INV00_01, INV00_02, INV00_03, INV00_20)
    abrir_janela_alteracao(tree.master, valores)


def abrir_janela_alteracao(root, valores):
    """
    Abre a janela para alterar um registro.
    valores = (codigo, descricao, percentual, segmento)
    """

    janela = tk.Toplevel(root)
    janela.title("Alteração de Tipo de Ativo")
    janela.geometry("550x350")
    janela.transient(root)
    janela.grab_set()

    # Centraliza a janela
    janela.update_idletasks()
    largura = 550
    altura = 350
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=5)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)
    entry_codigo.insert(0, valores[0])
    entry_codigo.config(state="disabled")  # Bloqueia edição do código

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)
    entry_descricao.insert(0, valores[1])

    ttk.Label(frame, text="Percentual (%):").grid(row=2, column=0, sticky="w", pady=5)
    entry_percentual = ttk.Entry(frame, width=5)
    entry_percentual.grid(row=2, column=1, sticky="w", pady=5)
    entry_percentual.insert(0, valores[2])

    ttk.Label(frame, text="Requer Segmento (S/N):").grid(row=3, column=0, sticky="w", pady=5)
    combo_segmento = ttk.Combobox(frame, values=["S", "N"], width=5, state="readonly")
    combo_segmento.grid(row=3, column=1, sticky="w", pady=5)
    combo_segmento.set(valores[3])

    # -----------------------------
    # FUNÇÃO SALVAR ALTERAÇÃO
    # -----------------------------
    def salvar():
        cod = valores[0]
        desc = entry_descricao.get().strip()
        perc = entry_percentual.get().strip()
        seg = combo_segmento.get().strip()

        # Validação do percentual
        try:
            perc_float = float(perc)
            if perc_float < 0:
                raise ValueError("Percentual negativo")
        except ValueError:
            messagebox.showwarning("Atenção", "Percentual inválido! Informe um número positivo.", parent=janela)
            return

        conn = inv00_0.conectar()
        total_atual = inv00_0.soma_perc(conn)

        # Ajusta soma considerando alteração
        soma_nova = total_atual - float(valores[2]) + perc_float

        if soma_nova != 100:
            # Janela de confirmação
            confirm_win = tk.Toplevel(janela)
            confirm_win.title("Confirmação")
            confirm_win.geometry("400x150")
            confirm_win.transient(janela)
            confirm_win.grab_set()

            msg = ttk.Label(confirm_win, text=f"A soma dos percentuais será {soma_nova:.2f}%, diferente de 100%.\nDeseja confirmar a alteração?", font=("Arial", 10))
            msg.pack(pady=20)

            frame_btn = ttk.Frame(confirm_win)
            frame_btn.pack(pady=10)

            def confirmar():
                inv00_0.alterar_registro(conn, cod, desc, perc_float, seg)
                conn.close()
                messagebox.showinfo("Sucesso", "Registro alterado com sucesso!", parent=janela)
                confirm_win.destroy()
                janela.destroy()

            def corrigir():
                confirm_win.destroy()
                # Não grava, retorna para edição

            ttk.Button(frame_btn, text="Confirmar", width=12, command=confirmar).pack(side="left", padx=10)
            ttk.Button(frame_btn, text="Não", width=12, command=corrigir).pack(side="right", padx=10)

        else:
            # Se soma = 100, grava direto
            inv00_0.alterar_registro(conn, cod, desc, perc_float, seg)
            conn.close()
            messagebox.showinfo("Sucesso", "Registro alterado com sucesso!", parent=janela)
            janela.destroy()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()
    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Cancelar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)
