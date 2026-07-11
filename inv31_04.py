'''
Programa de Impressão de Movimentação de Ativos
Tela Inicial 
JC Jun/2026
Ver 1
Banco de Dados inv.db
Tabela inv02 e inv03
Módulo: inv31_04.py

'''
import sqlite3
from tkinter import Tk, Button, messagebox, Toplevel
from tkinter import ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import inv00_0
import inv00_1

# ---------------------------------------------------------
# Janela principal: lista ativos e mostra botões
# ---------------------------------------------------------
def gerar_pdf_movim(root):

    conn = inv00_0.conectar()
    dados = inv00_0.listar_ativos_inv02_geral(conn)

    # JAMAIS criar outro Tk() — sempre Toplevel
    janela = Toplevel(root)
    janela.title("Impressão de Movimento de Ativos")
    janela.geometry("1000x600")
    janela.grab_set()  # mantém interação dentro da janela

    colunas = (
        "Codigo", "Descricao", "Quantidade", "CustoMedio",
        "Tipo", "DescTipo", "Segmento", "DescSeg"
    )

    idx = {
        "Codigo": 0,
        "Descricao": 1,
        "Tipo": 2,
        "DescTipo": 3,
        "Segmento": 5,
        "DescSeg": 6,
        "Quantidade": 8,
        "CustoMedio": 11
    }

    tree = ttk.Treeview(janela, columns=colunas, show="headings", height=20)

    # Configuração das colunas
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="w")

    # Inserir dados no grid
    for linha in dados:
        tree.insert("", "end", values=[linha[idx[col]] for col in colunas])

    tree.pack(pady=10, fill="both", expand=True)

    # ---------------------------------------------------------
    # Botão IMPRIMIR
    # ---------------------------------------------------------
    def imprimir():
        item = tree.focus()
        pagina = 1

        if not item:
            messagebox.showwarning("Aviso", "Selecione um ativo para imprimir.")
            tree.focus_set()
            return

        valores = tree.item(item)["values"]
        codigo = valores[0]

        movimentos = inv00_0.buscar_movimentos_ativo(conn, codigo)

        if not movimentos:
            messagebox.showinfo("Aviso", "Este ativo não possui movimentos.")
            tree.focus_set()
            tree.selection_set(item)
            return

        gerar_pdf_movimento(codigo, movimentos, valores, pagina)

        tree.focus_set()
        tree.selection_set(item)

    # ---------------------------------------------------------
    # Botão RETORNAR AO MENU
    # ---------------------------------------------------------
    def retornar():
        janela.destroy()

    botoes = ttk.Frame(janela)
    botoes.pack(pady=10)

    btn_imprimir = Button(botoes, text="Imprimir", width=15, command=imprimir)
    btn_imprimir.grid(row=0, column=0, padx=10)

    btn_retornar = Button(botoes, text="Retornar", width=15, command=retornar)
    btn_retornar.grid(row=0, column=1, padx=10)


# ---------------------------------------------------------
# Função que gera o PDF
# ---------------------------------------------------------
def gerar_pdf_movimento(codigo, movimentos, valores, pagina):

    nome_pdf = f"ativo_movimento_{codigo}.pdf"
    pdf = canvas.Canvas(nome_pdf, pagesize=A4)

    data_hoje = datetime.now().strftime("%d/%m/%Y")

    y = 800
    pdf.setFont("Times-Bold", 14)
    pdf.drawString(50, y, f"Movimentação do Ativo {codigo}")

    pdf.setFont("Times-Roman", 10)
    pdf.drawString(420, y, f"Data: {data_hoje}")
    pdf.drawString(500, y, f"Página {pagina}")

    y -= 15

    texto = valores[1]
    limite = 20
    if len(texto) > limite:
        texto = texto[:limite - 1] + "…"

    pdf.drawString(50, y, texto)
    pdf.drawString(200, y, "Quantidade: ")
    pdf.drawString(260, y, valores[2])

    pdf.setFont("Times-Bold", 10)
    y -= 15
    pdf.drawString(50,  y, "Data")
    pdf.drawString(120, y, "Movimentação")
    pdf.drawString(230, y, "Quantidade")
    pdf.drawString(320, y, "Vlr Unitário")
    pdf.drawString(410, y, "Vlr Total")

    pdf.line(50, y-2, 550, y-2)

    pdf.setFont("Times-Roman", 10)
    y -= 15

    ntot_mov = 0
    nval_mov = 0

    for mov in movimentos:
        cod, desc, tipo, qtd, vlr_unit, vlr_tot, data = mov

        if tipo == "V":
            qtd = -abs(qtd)

        mov_desc = {
            "B": "Bonificação",
            "C": "Compra",
            "V": "Venda",
            "D": "Desdobramento"
        }.get(tipo, tipo)

        pdf.drawString(50, y, inv00_1.iso_compacto_para_br(data))
        pdf.drawString(120, y, mov_desc)
        pdf.drawRightString(280, y, f"{qtd}")
        pdf.drawRightString(370, y, f"{vlr_unit:,.2f}")
        pdf.drawRightString(460, y, f"{vlr_tot:,.2f}")

        y -= 15
        ntot_mov += qtd
        nval_mov += vlr_tot

        if y < 50:
            pagina += 1
            pdf.showPage()
            pdf.setFont("Times-Roman", 10)
            y = 800

    pdf.setFont("Times-Bold", 10)        
    pdf.drawString(120, y, "Total Movimento: ")    
    pdf.drawRightString(280, y, f"{ntot_mov}")
    pdf.drawRightString(460, y, f"{nval_mov:,.2f}")

    if ntot_mov != float(valores[2]):
        y -= 20
        pdf.setFont("Times-Bold", 12)
        pdf.drawString(100, y, f"Atenção: Quantidade diferente da quantidade do movimento ")

    pdf.save()

    messagebox.showinfo("PDF Gerado", f"Arquivo criado: {nome_pdf}")
