'''
Programa de Impressão de Ativos Nacionais
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
Módulo: inv31_02.py
'''

# ============================================================
# inv31_01.py - Impressão de Ativos Nacionais em PDF
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from tkinter import ttk
# Importa query e funções auxiliares
import threading
import tkinter as tk
import tkinter as tk
import inv00_0 
import inv00_1

# ============================================================
# Função principal chamada pelo Menu
# ============================================================
def gerar_pdf_ativos_nac(root):

    # Abre janela de aguarde
    aguarde = inv00_1.mostrar_aguarde(root)

    # Executa o processamento em thread separada
    threading.Thread(
        target=lambda: gerar_pdf_nac(root, aguarde),
        daemon=True
    ).start()

# ------------------------------------------------------------
# Função principal para gerar PDF
# ------------------------------------------------------------
def gerar_pdf_nac(root,aguarde):

    # Conexão com banco
    conn = inv00_0.conectar()

    # Buscar Dados
    dados = inv00_0.listar_ativos_inv02(conn,'N')

    # Criação do PDF
    pdf = canvas.Canvas("ativos_nac.pdf", pagesize=A4)
    pdf.setFont("Times-Roman", 5)

    pagina = 1
    cabecalho(pdf, pagina)

    y = 780
    total_aquisicao = 0

    for row in dados:
        (
            codigo, descricao, tipo, desc_tipo, segmento, desc_segmento,qtde,
            valor_rs, valor_usd, custo_medio, pct
        ) = row

        total_aquisicao += valor_rs

        pdf.drawString(30,  y, str(codigo))
        pdf.drawString(70,  y, str(descricao)[:25])
        pdf.drawString(210, y, f"{tipo} - {desc_tipo[:10]}")
        pdf.drawString(290, y, f"{segmento} - {desc_segmento[:10]}")
        pdf.drawRightString(390, y, inv00_1.brstilo(qtde))
        pdf.drawRightString(450, y, inv00_1.brstilo(valor_rs))
        pdf.drawRightString(500, y, inv00_1.brstilo(custo_medio))
        pdf.drawRightString(550, y, inv00_1.brstilo(pct))

        y -= 12

        if y < 50:
            pdf.showPage()
            pagina += 1
            cabecalho(pdf, pagina)
            y = 780

    #Imprime Total
    pdf.setFont("Times-Bold",9)
    pdf.drawRightString(400, y - 10, "Total: ")
    pdf.drawRightString(460, y - 10, inv00_1.brstilo(total_aquisicao))
        
    pdf.save()
    conn.close()

    inv00_1.mensagem_sucesso("Relatório impresso com sucesso!",root,aguarde)

    # ------------------------------------------------------------
# Função para desenhar cabeçalho em cada página
# ------------------------------------------------------------
def cabecalho(pdf, pagina):
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    pdf.setFont("Times-Bold", 12)
    pdf.drawString(30, 820, "RELATÓRIO DE ATIVOS NACIONAIS")

    # Data + Página
    pdf.setFont("Times-Roman", 9)
    pdf.drawString(420, 820, f"Data: {data_hoje}")
    pdf.drawString(500, 820, f"Página {pagina}")

    # Cabeçalho das colunas
    pdf.setFont("Times-Bold", 7)
    y = 800
    pdf.drawString(30,  y, "Código")
    pdf.drawString(70,  y, "Descrição")
    pdf.drawString(230, y, "Tipo")
    pdf.drawString(310, y, "Segmento")
    pdf.drawString(370, y, "Qtde")
    pdf.drawString(410, y, "Aquisição (R$)")
    pdf.drawString(470, y, "Custo Médio (R$)")
    pdf.drawString(530, y, "% Alvo")
