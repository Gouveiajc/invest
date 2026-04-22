'''
Programa de Impressão de Ativos
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv04
Módulo: inv31_02.py
'''

# ============================================================
# inv31_02.py - Impressão de Ativos Exterior em PDF
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from tkinter import ttk

# Importa query e funções auxiliares
import tkinter as tk
import inv00_0
import inv00_1
import inv23_01 

# ------------------------------------------------------------
# Função para desenhar cabeçalho em cada página
# ------------------------------------------------------------
def cabecalho(pdf, pagina):
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    pdf.setFont("Times-Bold", 12)
    pdf.drawString(30, 820, "RELATÓRIO DE ATIVOS EXTERIOR")

    # Data + Página
    pdf.setFont("Times-Roman", 9)
    pdf.drawString(420, 820, f"Data: {data_hoje}")
    pdf.drawString(500, 820, f"Página {pagina}")

    # Cabeçalho das colunas
    pdf.setFont("Times-Bold", 9)
    y = 800
    pdf.drawString(30,  y, "Código")
    pdf.drawString(90,  y, "Descrição")
    pdf.drawString(250, y, "Tipo")
    pdf.drawString(330, y, "Segmento")
    pdf.drawString(420, y, "Aquisição (R$)")
    pdf.drawString(490, y, "Custo Médio (R$)")
    pdf.drawString(560, y, "% Alvo")

# ------------------------------------------------------------
# Função principal para gerar PDF
# ------------------------------------------------------------
def gerar_pdf_ativos_ext():

    # Conexão com banco
    conn = inv00_0.conectar()

    # Buscar Dados
    dados = inv00_0.listar_ativos_inv02(conn,'S')

    # Criação do PDF
    pdf = canvas.Canvas("ativos_ext.pdf", pagesize=A4)
    pdf.setFont("Times-Roman", 5)

    pagina = 1
    cabecalho(pdf, pagina)

    y = 780

    # Busca Cotação do dólar (Ativos no Exterior) 
    cotacao_usd = inv00_1.obter_cotacao_moeda("USD")

    for row in dados:
        (
            codigo, descricao, tipo, desc_tipo, segmento, desc_segmento,qtde,
            valor_rs, valor_usd, custo_medio, pct
        ) = row

        valor_rs = valor_usd * cotacao_usd
 
        pdf.drawString(30,  y, str(codigo))
        pdf.drawString(90,  y, str(descricao)[:25])
        pdf.drawString(250, y, f"{tipo} - {desc_tipo[:10]}")
        pdf.drawString(330, y, f"{segmento} - {desc_segmento[:10]}")
    #    pdf.drawRightString(480, y, f"{valor_rs:,.2f}")
    #    pdf.drawRightString(540, y, f"{custo_medio:,.2f}")
    #    pdf.drawRightString(590, y, f"{pct:.2f}")
        pdf.drawRightString(480, y, inv00_1.brstilo(valor_rs))
        pdf.drawRightString(540, y, inv00_1.brstilo(custo_medio))
        pdf.drawRightString(590, y, inv00_1.brstilo(pct))


        y -= 18

        if y < 50:
            pdf.showPage()
            pagina += 1
            cabecalho(pdf, pagina)
            y = 780

    pdf.save()
    conn.close()

    mensagem_sucesso("Relatório impresso com sucesso!")


def mensagem_sucesso(texto):
    janela = tk.Toplevel()
    janela.title("Informação")
    janela.geometry("300x120")
    janela.resizable(False, False)

    janela.update_idletasks()
    largura = 300
    altura = 120
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

    janela.grab_set()

    lbl = ttk.Label(janela, text=texto, font=("Arial", 11))
    lbl.pack(pady=15)

    btn = ttk.Button(janela, text="OK", command=janela.destroy)
    btn.pack(pady=5)
'''
# Execução direta
if __name__ == "__main__":
    gerar_pdf_ativos()
'''
    