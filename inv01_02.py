'''
Programa de Cadastro de Tipos de Ativo
JC 01/2026
Ver 1
Banco de Dados inv.db
Tabela inv00

'''

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import inv00_0
import inv00_1


def abrir_janela(root):

    # Evita abrir mais de uma janela de inclusão
    for widget in root.winfo_children():
        if isinstance(widget, tk.Toplevel) and widget.title() == "Inclusão de Tipos de Ativos":
            widget.lift()
            widget.focus_force()
            return

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Tipos de Ativos")
    janela.geometry("550x350")

    # Mantém a janela acima do root
    janela.transient(root)
    janela.grab_set()

    # Atalho ESC
    janela.bind("<Escape>", lambda e: janela.destroy())

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)
    
    frame.columnconfigure(1, weight=0)

    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=5)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame,width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Percentual (%):").grid(row=2, column=0, sticky="w", pady=5)
    entry_percentual = ttk.Entry(frame, width=5)
    entry_percentual.grid(row=2, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Requer Segmento (S/N):").grid(row=3, column=0, sticky="w", pady=5)
    combo_segmento = ttk.Combobox(frame, values=["S", "N"], width=5, state="readonly")
    combo_segmento.grid(row=3, column=1, sticky="w", pady=5)
    combo_segmento.set("N")

    # -----------------------------
    # FUNÇÃO PARA DEVOLVER FOCO À TELA DE INCLUSÃO
    # -----------------------------
    def devolver_foco():
        try:
            janela.lift()
            janela.focus_force()
        except:
            pass

    # -----------------------------
    # FUNÇÃO SALVAR
    # -----------------------------
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        perc = entry_percentual.get().strip()
        seg = combo_segmento.get().strip()

        # 1) VALIDAR CAMPOS
        ok, mensagem, campo = inv00_1.validar_campos(cod, desc, perc, seg)

        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            janela.after(10, devolver_foco)
            return

        # 2) VERIFICAR DUPLICIDADE
        conn = inv00_0.conectar()
        if inv00_0.existe_codigo(conn, cod):
            conn.close()
            messagebox.showwarning("Atenção", f"O código {cod} já está cadastrado.", parent=janela)
            janela.after(10, devolver_foco)
            return

        # 3) VERIFICAR SOMA DOS PERCENTUAIS
        total_atual = inv00_0.soma_perc(conn)
        novo_total = total_atual + float(perc)

        if novo_total > 100:
            # Cria janela de confirmação
            confirm_win = tk.Toplevel(janela)
            confirm_win.title("Confirmação")
            confirm_win.geometry("400x150")
            confirm_win.transient(janela)
            confirm_win.grab_set()

            msg = ttk.Label(confirm_win, text=f"A soma dos percentuais será {novo_total:.2f}%, maior que 100%.\nDeseja confirmar a inclusão?", font=("Arial", 10))
            msg.pack(pady=20)

            # Botões
            frame_btn = ttk.Frame(confirm_win)
            frame_btn.pack(pady=10)

            def confirmar():
                inv00_0.inserir_registro(conn, cod, desc, perc, seg)
                conn.close()
                messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)
                confirm_win.destroy()
                # Limpa campos
                entry_codigo.delete(0, tk.END)
                entry_descricao.delete(0, tk.END)
                entry_percentual.delete(0, tk.END)
                combo_segmento.set("N")
                entry_codigo.focus()

            def corrigir():
                confirm_win.destroy()
                conn.close()  # Não grava, retorna para edição

            ttk.Button(frame_btn, text="Confirmar", width=12, command=confirmar).pack(side="left", padx=10)
            ttk.Button(frame_btn, text="Corrigir", width=12, command=corrigir).pack(side="right", padx=10)

        else:
            # Se não ultrapassar, insere normalmente
            inv00_0.inserir_registro(conn, cod, desc, perc, seg)
            conn.close()
            messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)

            # Limpa campos
            entry_codigo.delete(0, tk.END)
            entry_descricao.delete(0, tk.END)
            entry_percentual.delete(0, tk.END)
            combo_segmento.set("N")
            entry_codigo.focus()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Retornar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()
    janela.lift()
    janela.focus_force()
