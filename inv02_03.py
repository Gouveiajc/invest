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
    item = tree.selection()
    if not item:
        messagebox.showwarning("Atenção", "Selecione um registro para alterar.")
        return

    # Esperado no Treeview:
    # (Inv02_00, Inv02_06, Inv02_02, Inv02_01, Inv02_05, Inv02_20)
    valores = tree.item(item, "values")
    abrir_janela_alteracao(tree.master, tree, valores)


def abrir_janela_alteracao(root, tree, valores):
    """
    valores = (
        Inv02_00,  # ID
        Inv02_06,  # Código Ativo
        Inv02_02,  # Descrição Ativo
        Inv02_01,  # Tipo Ativo
        Inv02_05,  # Segmento
        Inv02_20   # % Investir
    )
    """

    janela = tk.Toplevel(root)
    janela.title("Alteração de Ativos")
    janela.geometry("600x400")
    janela.transient(root)
    janela.grab_set()

    janela.update_idletasks()
    largura, altura = 600, 400
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

    frame = ttk.Frame(janela, padding=20)
    frame.pack(fill="both", expand=True)

    # -----------------------------
    # CAMPOS BÁSICOS
    # -----------------------------
    ttk.Label(frame, text="Código Ativo:").grid(row=0, column=0, sticky="w", pady=5)
    entry_codigo = ttk.Entry(frame, width=20)
    entry_codigo.grid(row=0, column=1, sticky="w", pady=5)
    entry_codigo.insert(0, valores[1])

    ttk.Label(frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
    entry_descricao = ttk.Entry(frame, width=40)
    entry_descricao.grid(row=1, column=1, sticky="w", pady=5)
    entry_descricao.insert(0, valores[2])

    # -----------------------------
    # TIPO ATIVO
    # -----------------------------
    ttk.Label(frame, text="Tipo Ativo:").grid(row=2, column=0, sticky="w", pady=5)

    conn = inv00_0.conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT INV00_01, INV00_02 FROM INV00 ORDER BY INV00_02")
    tipos = cursor.fetchall()
    conn.close()

    lista_tipos = [f"{t[0]} - {t[1]}" for t in tipos]

    combo_tipo = ttk.Combobox(frame, values=lista_tipos, width=30, state="readonly")
    combo_tipo.grid(row=2, column=1, sticky="w", pady=5)

    tipo_original = str(valores[3])
    for item in lista_tipos:
        if item.startswith(tipo_original + " "):
            combo_tipo.set(item)
            break

    # -----------------------------
    # SEGMENTO
    # -----------------------------
    ttk.Label(frame, text="Segmento:").grid(row=3, column=0, sticky="w", pady=5)

    def carregar_segmentos(tipo_id):
        conn_local = inv00_0.conectar()
        cur = conn_local.cursor()
        cur.execute("""
            SELECT INV01_01, INV01_02
              FROM INV01
             WHERE INV01_03 = ?
             ORDER BY INV01_02
        """, (tipo_id,))
        segs = cur.fetchall()
        conn_local.close()
        return [f"{s[0]} - {s[1]}" for s in segs]

    lista_segmentos = carregar_segmentos(tipo_original)

    combo_segmento = ttk.Combobox(frame, values=lista_segmentos, width=30, state="readonly")
    combo_segmento.grid(row=3, column=1, sticky="w", pady=5)

    seg_original = str(valores[4])
    for item in lista_segmentos:
        if item.startswith(seg_original + " "):
            combo_segmento.set(item)
            break

    def atualizar_segmentos(event):
        tipo_id = combo_tipo.get().split(" - ")[0].strip()
        novos = carregar_segmentos(tipo_id)
        combo_segmento["values"] = novos
        combo_segmento.set("")

    combo_tipo.bind("<<ComboboxSelected>>", atualizar_segmentos)

    # -----------------------------
    # PERCENTUAL
    # -----------------------------
    ttk.Label(frame, text="% Investir:").grid(row=4, column=0, sticky="w", pady=5)
    entry_percentual = ttk.Entry(frame, width=10)
    entry_percentual.grid(row=4, column=1, sticky="w", pady=5)
    entry_percentual.insert(0, valores[5])

    # -----------------------------
    # FUNÇÕES AUXILIARES
    # -----------------------------
    def soma_percentuais_segmento(conn_local, segmento_id, perc_original):
        soma_total = inv00_0.soma_percentuais_inv02_segmento(conn_local, segmento_id)

        # Garante que a variável existe antes do try
        perc_orig_float = 0.0

        try:
            perc_orig_float = float(str(perc_original).replace(",", "."))
        except ValueError:
            pass  # mantém 0.0

        return soma_total - perc_orig_float

    # -----------------------------
    # SALVAR
    # -----------------------------
    def salvar():
        id_reg = valores[0]
        cod = entry_codigo.get().strip()
        desc = entry_descricao.get().strip()
        perc_str = entry_percentual.get().strip()

        if not combo_tipo.get():
            messagebox.showwarning("Atenção", "Selecione um Tipo de Ativo.", parent=janela)
            return
        tipo_id = combo_tipo.get().split(" - ")[0].strip()

        if not combo_segmento.get():
            messagebox.showwarning("Atenção", "Selecione um Segmento.", parent=janela)
            return
        segmento_id = combo_segmento.get().split(" - ")[0].strip()

        ok, mensagem, campo = inv00_1.validar_campos_inv02(
            id_reg, cod, desc, tipo_id, segmento_id, perc_str
        ) if hasattr(inv00_1, "validar_campos_inv02") else (True, "", "")

        if not ok:
            messagebox.showwarning("Atenção", mensagem, parent=janela)
            return

        try:
            perc_float = float(perc_str.replace(",", "."))
        except ValueError:
            messagebox.showwarning("Atenção", "Percentual inválido.", parent=janela)
            return

        if perc_float < 0:
            messagebox.showwarning("Atenção", "Percentual não pode ser negativo.", parent=janela)
            return

        conn_local = inv00_0.conectar()

        try:
            soma_sem_atual = soma_percentuais_segmento(
                conn_local,
                segmento_id,
                valores[5]
            )
            nova_soma = soma_sem_atual + perc_float

            if nova_soma > 100:
                resposta = messagebox.askyesno(
                    "Atenção",
                    f"A soma dos percentuais dos ativos deste segmento ficará {nova_soma:.2f}%.\n"
                    f"Isto ultrapassa 100%.\n\n"
                    f"Deseja continuar mesmo assim?",
                    parent=janela
                )
                if not resposta:
                    return

            cur = conn_local.cursor()
            cur.execute("""
                UPDATE INV02
                   SET Inv02_06 = ?,
                       Inv02_02 = ?,
                       Inv02_01 = ?,
                       Inv02_05 = ?,
                       Inv02_20 = ?
                 WHERE Inv02_00 = ?
            """, (cod, desc, tipo_id, segmento_id, perc_float, id_reg))
            conn_local.commit()

            for item in tree.get_children():
                v = tree.item(item, "values")
                if str(v[0]) == str(id_reg):
                    tree.item(
                        item,
                        values=(id_reg, cod, desc, tipo_id, segmento_id, perc_float)
                    )
                    break

            messagebox.showinfo("Sucesso", "Registro alterado com sucesso!", parent=janela)
            janela.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}", parent=janela)
        finally:
            conn_local.close()

    # -----------------------------
    # BOTÕES
    # -----------------------------
    frame_botoes = ttk.Frame(janela, padding=10)
    frame_botoes.pack()

    ttk.Button(frame_botoes, text="Salvar", width=12, command=salvar).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botoes, text="Cancelar", width=12, command=janela.destroy).grid(row=0, column=1, padx=10)

    entry_codigo.focus()

