'''
Programa de Cadastro de Ativos
Alteração
JC Jan/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
Módulo: inv03_03.py
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
    janela.geometry("550x560")
    janela.transient(root)
    janela.grab_set()

    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # --- CAMPOS ---
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
    except:
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
    except:
        lista_segm = []
    finally:
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

    # NOVO CAMPO — Valoriza Ativo
    ttk.Label(frame, text="Valoriza Ativo:").grid(row=9, column=0, sticky="w", pady=5)
    lista_vlr = ["S - Sim", "N - Não"]
    combo_vlr = ttk.Combobox(frame, values=lista_vlr, state="readonly", width=30)
    combo_vlr.grid(row=9, column=1, sticky="w", pady=5)

    # Data Inclusão
    ttk.Label(frame, text="Data da Inclusão:").grid(row=10, column=0, sticky="w", pady=5)
    entry_data = ttk.Entry(frame, width=30)
    entry_data.grid(row=10, column=1, sticky="w", pady=5)

    # Percentual
    ttk.Label(frame, text="Percentual Investir:").grid(row=11, column=0, sticky="w", pady=5)
    entry_peri = ttk.Entry(frame, width=10)
    entry_peri.grid(row=11, column=1, sticky="w", pady=5)

    # Observação
    ttk.Label(frame, text="Observação:").grid(row=12, column=0, sticky="w", pady=5)
    entry_obs = ttk.Entry(frame, width=30)
    entry_obs.grid(row=12, column=1, sticky="w", pady=5)

    # -----------------------------
    # PREENCHIMENTO DOS CAMPOS
    # -----------------------------
    entry_codigo.config(state="normal")
    entry_codigo.insert(0, valores[0])
    entry_codigo.config(state="disabled")

    entry_descricao.insert(0, valores[1])
    combo_tipo.set(valores[2])
    combo_segm.set(valores[3])

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

    # NOVO CAMPO — preenchimento
    combo_vlr.set("S - Sim" if valores[9] == "S" else "N - Não")

    entry_data.insert(0, valores[10])
    entry_peri.insert(0, valores[11])
    entry_obs.insert(0, valores[12])

    # -----------------------------
    # SALVAR ALTERAÇÃO
    # -----------------------------
    def salvar():

        cod = valores[0]
        desc = entry_descricao.get().strip()
        perc = entry_peri.get().strip()
        obs = entry_obs.get().strip()

        tipo_sel = combo_tipo.get().strip()
        segm_sel = combo_segm.get().strip()
        atv_sel = combo_atv.get().strip()
        vlr_sel = combo_vlr.get().strip()
        if not segm_sel:
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return

        tipo_id = tipo_sel.split(" - ")[0]
        segm_id_novo = segm_sel.split(" - ")[0]
        segm_id_antigo = valores[3]
        atv_id = atv_sel.split(" - ")[0]
        vlr_id = vlr_sel.split(" - ")[0]

        try:
            perc_float = float(perc.replace(",", "."))
        except:
            messagebox.showwarning("Atenção", "Percentual inválido!", parent=janela)
            return

        perc_antigo = float(str(valores[11]).replace(",", "."))

        conn = inv00_0.conectar()

        try:
            if segm_id_novo == segm_id_antigo:
                soma_atual = inv00_0.soma_perc_inv02(conn, segm_id_novo)
                soma_sem_atual = soma_atual - perc_antigo
                nova_soma = soma_sem_atual + perc_float
            else:
                soma_atual_novo = inv00_0.soma_perc_inv02(conn, segm_id_novo)
                nova_soma = soma_atual_novo + perc_float

            if nova_soma > 100:
                msg = f"A soma dos percentuais ficará {nova_soma:.2f}%.\nDeseja continuar?"
                if not messagebox.askyesno("Confirmação", msg, parent=janela):
                    conn.close()
                    return

            # Atualiza no backend — AGORA COM O NOVO CAMPO
            inv00_0.atualizar_registro_inv02(conn, cod, desc, tipo_id, segm_id_novo, atv_id, vlr_id, perc_float, obs)

        finally:
            conn.close()

        # Atualiza o grid
        for item in tree.get_children():
            valores_tree = tree.item(item, "values")
            if valores_tree[0] == cod:
                tree.item(item, values=(
                    cod, desc, tipo_id, segm_id_novo, valores[4], valores[5],
                    valores[6], valores[7], valores[8], vlr_id, valores[10],
                    perc_float, obs
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

