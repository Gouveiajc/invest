'''
Programa de Cadastro de Ativo - Alteração
JC 02/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
'''
import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0
import inv00_1

def alterar_registro(tree):
    item = tree.selection()
    if not item:
        messagebox.showwarning("Atenção", "Selecione um registro para alterar.")
        return

    item_id = item[0]
    valores = tree.item(item_id, "values")

    abrir_janela_alteracao(tree.master, tree, valores)


def abrir_janela_alteracao(root, tree, valores):

    janela = tk.Toplevel(root)
    janela.title("Alteração de Ativos")
    janela.geometry("550x490")
    janela.transient(root)
    janela.grab_set()

    janela.update_idletasks()
    largura = 550
    altura = 490
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # CAMPOS
    ttk.Label(frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=10, state="disabled")
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=30)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)

    # Tipo Ativo
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

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, state="readonly", width=30)
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    # Segmento
    ttk.Label(frame, text="Segmento:").grid(row=3, column=0, sticky="w", pady=5)

    try:
        conn = inv00_0.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT INV01_05, INV01_02 FROM INV01 ORDER BY INV01_02")
        segm = cursor.fetchall()
        lista_segm = [f"{s[0]} - {s[1]}" for s in segm]
    except Exception as f:
        messagebox.showerror("Erro", f"Erro ao carregar Segmentos: {f}")
        lista_segm = []
    finally:
        if conn:
            conn.close()

    combo_segm = ttk.Combobox(frame, values=lista_segm, state="readonly", width=30)
    combo_segm.grid(row=3, column=1, sticky="w", pady=5)

    # Quantidade
    ttk.Label(frame, text="Quantidade Ativo:").grid(row=4, column=0, sticky="w", pady=5)
    entry_qtd = ttk.Entry(frame, width=30, state="disabled")
    entry_qtd.grid(row=4, column=1, sticky="w", pady=5)

    # Custo Médio
    ttk.Label(frame, text="Custo Médio Ativo:").grid(row=5, column=0, sticky="w", pady=5)
    entry_cusm = ttk.Entry(frame, width=30, state="disabled")
    entry_cusm.grid(row=5, column=1, sticky="w", pady=5)

    # Custo Aquisição
    ttk.Label(frame, text="Custo Aquisição:").grid(row=6, column=0, sticky="w", pady=5)
    entry_cusa = ttk.Entry(frame, width=30, state="disabled")
    entry_cusa.grid(row=6, column=1, sticky="w", pady=5)

    # Ativo Exterior
    ttk.Label(frame, text="Ativo Exterior:").grid(row=7, column=0, sticky="w", pady=5)
    lista_atv = ["S - Sim", "N - Não"]
    combo_atv = ttk.Combobox(frame, values=lista_atv, state="readonly", width=30)
    combo_atv.grid(row=7, column=1, sticky="w", pady=5)

    # Custo US$
    ttk.Label(frame, text="Custo Aquisição US$:").grid(row=8, column=0, sticky="w", pady=5)
    entry_cusus = ttk.Entry(frame, width=30, state="disabled")
    entry_cusus.grid(row=8, column=1, sticky="w", pady=5)

    # Data Inclusão
    ttk.Label(frame, text="Data da Inclusão:").grid(row=9, column=0, sticky="w", pady=5)
    entry_data = ttk.Entry(frame, width=30)
    entry_data.grid(row=9, column=1, sticky="w", pady=5)

    # Percentual
    ttk.Label(frame, text="Percentual Investir:").grid(row=10, column=0, sticky="w", pady=5)
    entry_peri = ttk.Entry(frame, width=10)
    entry_peri.grid(row=10, column=1, sticky="w", pady=5)

    # Observação
    ttk.Label(frame, text="Observação:").grid(row=11, column=0, sticky="w", pady=5)
    entry_obs = ttk.Entry(frame, width=30)
    entry_obs.grid(row=11, column=1, sticky="w", pady=5)

    # -----------------------------
    # PREENCHIMENTO DOS CAMPOS
    # -----------------------------

    entry_codigo.config(state="normal")
    entry_codigo.insert(0, valores[0])
    entry_codigo.config(state="disabled")

    entry_descricao.insert(0, valores[1])
    combo_tipo.set(valores[2])
    combo_segm.set(valores[3])

    # Campos desabilitados → habilita → preenche → desabilita
    entry_qtd.config(state="normal")
    entry_qtd.insert(0, valores[4])
    entry_qtd.config(state="disabled")

    entry_cusm.config(state="normal")
    entry_cusm.insert(0, valores[5])
    entry_cusm.config(state="disabled")

    entry_cusa.config(state="normal")
    entry_cusa.insert(0, valores[6])
    entry_cusa.config(state="disabled")

    combo_atv.set("S - Sim" if valores[7] == "S" else "N - Não")

    entry_cusus.config(state="normal")
    entry_cusus.insert(0, valores[8])
    entry_cusus.config(state="disabled")

    entry_data.insert(0, valores[9])
    entry_peri.insert(0, valores[10])
    entry_obs.insert(0, valores[11])

    # -----------------------------
    # SALVAR
    # -----------------------------
    def salvar():
        cod = valores[0]              # código do registro original
        desc = entry_descricao.get().strip()
        perc = entry_peri.get().strip()
        obs = entry_obs.get().strip()

        # Tipo selecionado na tela (novo tipo)
        tipo_selecionado = combo_tipo.get()
        if not tipo_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id_novo = tipo_selecionado.split(" - ")[0]

        # Tipo original (que estava no grid antes de abrir a tela)
        # ajuste o índice conforme sua tupla 'valores'
        tipo_id_antigo = valores[3]   # EXEMPLO: se o tipo original estiver na posição 3

        ok, mensagem, campo = inv00_1.validar_campos_inv01(cod, desc, tipo_id_novo, perc)
        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        try:
            perc_float = float(perc.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Percentual inválido!", parent=janela)
            return

        # Percentual antigo (que estava gravado antes da alteração)
        try:
            perc_antigo = float(str(valores[10]).replace(",", "."))
        except Exception:
            perc_antigo = 0.0  # fallback para não quebrar

        conn = inv00_0.conectar()

        try:
            # Se o tipo NÃO mudou:
            if tipo_id_novo == tipo_id_antigo:
                # soma de todos os percentuais daquele tipo, incluindo o atual
                soma_atual = inv00_0.soma_perc_inv02(conn, tipo_id_novo)
                # remove o percentual antigo desse registro
                soma_sem_atual = soma_atual - perc_antigo
                nova_soma = soma_sem_atual + perc_float
            else:
                # tipo mudou: não faz sentido subtrair o percentual antigo
                # da soma do novo tipo; o antigo já pertence a outro grupo
                soma_atual_novo_tipo = inv00_0.soma_perc_inv02(conn, tipo_id_novo)
                nova_soma = soma_atual_novo_tipo + perc_float

            if nova_soma > 100:
                msg = f"A soma dos percentuais para o tipo {tipo_id_novo} ficará {nova_soma:.2f}%.\nDeseja continuar?"
                if not messagebox.askyesno("Confirmação", msg, parent=janela):
                    conn.close()
                    return

            # Atualiza o registro
            inv00_0.atualizar_registro_inv02(conn, cod, desc, tipo_id_novo, perc_float,obs)

        finally:
            conn.close()


        # Atualiza o grid
        for item in tree.get_children():
            valores_tree = tree.item(item, "values")
            if valores_tree[0] == cod:
                tree.item(item, values=(
                    cod, desc, tipo_id_novo, valores[3], valores[4], valores[5],
                    valores[6], valores[7], valores[8], valores[9],
                    perc_float, valores[11]
                ))
                break

        messagebox.showinfo("Sucesso", "Registro alterado com sucesso!", parent=janela)
        janela.destroy()

    # BOTÕES
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Cancelar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_descricao.focus()

    '''
    def salvar():
        cod = valores[0]
        desc = entry_descricao.get().strip()
        perc = entry_peri.get().strip()

        tipo_selecionado = combo_tipo.get()
        if not tipo_selecionado:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_selecionado.split(" - ")[0]

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

        soma_atual = inv00_0.soma_perc_inv01(conn, tipo_id) - float(valores[10])
        nova_soma = soma_atual + perc_float

        if nova_soma > 100:
            msg = f"A soma dos percentuais ficará {nova_soma:.2f}%.\nDeseja continuar?"
            if not messagebox.askyesno("Confirmação", msg, parent=janela):
                conn.close()
                return

        inv00_0.atualizar_registro_inv01(conn, cod, desc, tipo_id, perc_float)
        conn.close()
'''
