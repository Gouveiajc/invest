'''
Programa de Cadastro de Tipos de Ativo - Alteração
JC 01/2026
Ver 1
Banco de Dados inv.db
Tabela inv01
'''
import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0
import inv00_1

def alterar_registro(tree):
    """
    Função chamada pelo botão ALTERAR no grid.
    Recebe o Treeview, pega o item selecionado e abre a janela de edição.
    """
    item = tree.selection()
    if not item:
        messagebox.showwarning("Atenção", "Selecione um registro para alterar.")
        return

    valores = tree.item(item, "values")  # (codigo, descricao, tipo, percentual)
    abrir_janela_alteracao(tree.master, tree, valores)


def abrir_janela_alteracao(root, tree, valores):
    """
    Abre a janela para alterar um registro da tabela INV01.
    valores = (codigo, descricao, tipo_id, percentual)
    """

    janela = tk.Toplevel(root)
    janela.title("Alteração de Segmentos")
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
    entry_codigo = ttk.Entry(frame, width=10)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)
    entry_codigo.insert(0, valores[0])
    entry_codigo.config(state="disabled")

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)
    entry_descricao.insert(0, valores[1])

    # Carrega tipos de ativos
    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)

    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV00_01, INV00_02 FROM INV00 ORDER BY INV00_02")
        tipos = cursor.fetchall()
        lista_tipos = [f"{t[0]} - {t[1]}" for t in tipos]
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar tipos: {e}")
        lista_tipos = []
    finally:
        conn.close()

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, width=30, state="readonly")
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    # Seleciona o tipo atual
    tipo_original = str(valores[2])
    for item in lista_tipos:
        if item.startswith(tipo_original):
            combo_tipo.set(item)
            break

    ttk.Label(frame, text="Percentual (%):").grid(row=3, column=0, sticky="w", pady=5)
    entry_percentual = ttk.Entry(frame, width=10)
    entry_percentual.grid(row=3, column=1, sticky="w", pady=5)
    entry_percentual.insert(0, str(valores[3]))

    # -----------------------------
    # FUNÇÃO SALVAR ALTERAÇÃO
    # -----------------------------
    def salvar():
        cod = valores[0]
        desc = entry_descricao.get().strip()
        perc = entry_percentual.get().strip()

        tipo_selecionado = combo_tipo.get()
        if not tipo_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_selecionado.split(" - ")[0]

        # Validação geral
        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, tipo_id, perc)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        try:
            perc_float = float(perc.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Percentual inválido!", parent=janela)
            return

        conn = inv00_0.conectar()

        # Soma atual sem o registro original
        soma_atual = inv00_0.soma_perc_inv01(conn, tipo_id) - float(valores[3])
        nova_soma = soma_atual + perc_float

        # Se ultrapassar 100%, confirmar
        if nova_soma > 100:
            msg = f"A soma dos percentuais ficará {nova_soma:.2f}%.\nDeseja continuar?"
            if not messagebox.askyesno("Confirmação", msg, parent=janela):
                conn.close()
                return

        # Atualiza registro
        inv00_0.atualizar_registro_inv01(conn, cod, desc, tipo_id, perc_float)
        conn.close()

        # Atualiza Treeview
        for item in tree.get_children():
            valores_tree = tree.item(item, "values")
            if valores_tree[0] == cod:
                tree.item(item, values=(cod, desc, tipo_id, perc_float))
                break

        messagebox.showinfo("Sucesso", "Registro alterado com sucesso!", parent=janela)
        janela.destroy()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Cancelar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_descricao.focus()
