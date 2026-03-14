'''
Programa de Cadastro de Tipos de Ativo
Inclusão
JC Jan/2026
Ver 1
Banco de Dados inv.db
Tabela inv00
Módulo inv01_02.py
'''
import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0


def abrir_janela(root, atualizar_grid_callback=None):

    janela = tk.Toplevel(root)
    janela.title("Inclusão de Tipo de Ativo")
    janela.geometry("450x300")
    janela.grab_set()

    # -----------------------------
    # CAMPOS
    # -----------------------------
    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=10)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Percentual (%):").grid(row=2, column=0, sticky="w", pady=5)
    entry_percentual = ttk.Entry(frame, width=10)
    entry_percentual.grid(row=2, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Requer Segmento (S/N):").grid(row=3, column=0, sticky="w", pady=5)
    combo_segmento = ttk.Combobox(frame, values=["S", "N"], width=5, state="readonly")
    combo_segmento.grid(row=3, column=1, sticky="w", pady=5)
    combo_segmento.set("N")

    # -----------------------------
    # FUNÇÃO SALVAR
    # -----------------------------
    def salvar():
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        perc = entry_percentual.get().strip()
        seg = combo_segmento.get().strip()

        # Validação
        if not cod or not desc or not perc:
            messagebox.showwarning("Atenção", "Preencha todos os campos!", parent=janela)
            return

        try:
            perc_float = float(perc)
            if perc_float < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Percentual inválido!", parent=janela)
            return

        conn = inv00_0.conectar()

        # 🔍 Soma atual dos percentuais
        soma_atual = inv00_0.soma_perc(conn)
        soma_nova = soma_atual + perc_float

        # ⚠️ Se ultrapassar 100%, perguntar ao usuário
        if soma_nova > 100:
            msg = (
                f"O total dos percentuais {soma_nova:.2f}%.\n"
                "Excedeu o limite de 100%.\n\n"
                "Deseja continuar mesmo assim?"
            )
            continuar = messagebox.askyesno("Atenção", msg, parent=janela)
            if not continuar:
                conn.close()
                return

        # Gravação
        inv00_0.inserir_registro(conn, cod, desc, seg, perc_float)
        conn.close()

        if atualizar_grid_callback:
            atualizar_grid_callback()

        messagebox.showinfo("Sucesso", "Registro incluído com sucesso!", parent=janela)
        janela.destroy()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Cancelar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)


