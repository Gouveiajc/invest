

import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0
import datetime


def abrir_janela_inv03(root, tree):
    """
    Abre a janela de confirmação para exclusão do registro selecionado.
    """

    janela = tk.Toplevel(root)
    janela.title("Exclusão de Movimento")
    janela.geometry("400x180")
    janela.grab_set()
    janela.bind("<Escape>", lambda e: janela.destroy())

    frame = ttk.Frame(janela, padding=15)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Confirma a exclusão do movimento selecionado?",
              font=("Arial", 11)).pack(pady=20)

    ttk.Button(frame, text="Excluir", width=15,
               command=lambda: excluir_registro(janela, tree)).pack(pady=5)

    ttk.Button(frame, text="Cancelar", width=15,
               command=janela.destroy).pack(pady=5)



def excluir_registro(janela, tree):

    # -----------------------------------------
    # 1) Verifica se há item selecionado
    # -----------------------------------------
    selecionado = tree.selection()
    if not selecionado:
        messagebox.showwarning("Atenção", "Nenhum registro selecionado.", parent=janela)
        return

    item = tree.item(selecionado)
    valores = item["values"]

    if not valores:
        messagebox.showerror("Erro", "Não foi possível obter os dados do registro.", parent=janela)
        return

    # -----------------------------------------
    # 2) Função auxiliar para evitar ValueError
    # -----------------------------------------
    def conv_float(v):
        """
        Converte texto para float, mesmo que o valor seja '', ' ', None ou não numérico.
        """
        try:
            if v in (None, "", " "):
                return 0.0
            return float(str(v).replace(",", "."))
        except:
            return 0.0

    # -----------------------------------------
    # 3) Extrair informações do registro
    # -----------------------------------------
    id_registro    = valores[0]          # PK da tabela INV03
    codigo_ativo   = valores[1]
    tipo_mov       = valores[2]          # C / D / V
    quantidade     = conv_float(valores[3])
    vlr_unitario   = conv_float(valores[4])
    vlr_total_rs   = conv_float(valores[5])
    cotacao_us     = conv_float(valores[6]) if len(valores) > 6 else 0
    vlr_unit_us    = conv_float(valores[7]) if len(valores) > 7 else 0
    vlr_total_us   = conv_float(valores[8]) if len(valores) > 8 else 0
    data_inclusao  = valores[9]

    # -----------------------------------------
    # 4) Verificar se a data do movimento = data atual
    # -----------------------------------------
    hoje = datetime.date.today().strftime("%d/%m/%Y")

    if str(data_inclusao) != hoje:
        messagebox.showwarning(
            "Atenção",
            "Somente movimentos incluídos HOJE podem ser excluídos.",
            parent=janela
        )
        return

    # -----------------------------------------
    # 5) Reverter posição e excluir registro
    # -----------------------------------------
    conn = inv00_0.conectar()

    # Reverter impacto na INV02
    inv00_0.reverter_posicao_inv02(
        conn,
        codigo_ativo=codigo_ativo,
        tipo_mov=tipo_mov,
        quantidade=quantidade,
        total_rs=vlr_total_rs,
        total_us=vlr_total_us
    )

    # Excluir registro na INV03
    inv00_0.excluir_registro_inv03(conn, id_registro)

    conn.close()

    # -----------------------------------------
    # 6) Recarregar os registros na tela
    # -----------------------------------------
    for item in tree.get_children():
        tree.delete(item)

    conn = inv00_0.conectar()
    registros = inv00_0.listar_registros_inv03(conn)
    conn.close()

    for reg in registros:
        tree.insert("", tk.END, values=reg)

    messagebox.showinfo("Sucesso", "Registro excluído com sucesso!", parent=janela)
    janela.destroy()