'''
Programa de Impressão de Ativos Exterior
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
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
import threading
import tkinter as tk
import inv00_0
import inv00_1

# ============================================================
# Função principal chamada pelo Menu
# ============================================================
def gerar_pdf_ativos_ext(root):

    # Abre janela de aguarde
    aguarde = inv00_1.mostrar_aguarde(root)

    # Executa o processamento em thread separada
    threading.Thread(
        target=lambda: gerar_pdf_ext(root, aguarde),
        daemon=True
    ).start()

# ============================================================
# Função interna que realmente gera o PDF
# ============================================================
def gerar_pdf_ext(root, aguarde):

    # Conexão com banco
    conn = inv00_0.conectar()

    # Buscar Dados
    dados = inv00_0.listar_ativos_inv02(conn, 'S')

    # Criação do PDF
    pdf = canvas.Canvas("ativos_ext.pdf", pagesize=A4)
    pdf.setFont("Times-Roman", 5)

    pagina = 1
    cabecalho(pdf, pagina)

    y = 790
    
    total_rs = 0
    total_us = 0
    
    # Busca Cotação do dólar (Ativos no Exterior) 
    cotacao_usd = inv00_1.obter_cotacao_moeda("USD")

    for row in dados:
        (
            codigo, descricao, tipo, desc_tipo, segmento, desc_segmento, qtde,
            valor_rs, valor_usd, custo_medio, pct
        ) = row

        valor_rs = valor_usd * cotacao_usd
        total_rs += valor_rs
        total_us += valor_usd

        pdf.setFont("Times-Bold", 7)
        pdf.drawString(30,  y, str(codigo))
        pdf.drawString(70,  y, str(descricao)[:22])
        pdf.drawString(180, y, f"{tipo} - {desc_tipo[:12]}")
        pdf.drawString(260, y, f"{segmento} - {desc_segmento[:12]}")
        pdf.drawRightString(370, y,inv00_1.brstilo6(qtde))
        pdf.drawRightString(410, y, inv00_1.brstilo(valor_usd))
        pdf.drawRightString(470, y, inv00_1.brstilo(valor_rs))
        pdf.drawRightString(520, y, inv00_1.brstilo(custo_medio))
        pdf.drawRightString(560, y, inv00_1.brstilo(pct))

        y -= 8

        if y < 50:
            pdf.showPage()
            pagina += 1
            cabecalho(pdf, pagina)
            y = 780

    # Imprime Total
    pdf.setFont("Times-Bold", 9)
    pdf.drawRightString(330, y - 10, "Total US$/R$: ")
    pdf.drawRightString(410, y - 10, inv00_1.brstilo(total_us))    
    pdf.drawRightString(470, y - 10, inv00_1.brstilo(total_rs))    

    pdf.save()
    conn.close()

     # Mensagem final
    inv00_1.mensagem_sucesso("Relatório impresso com sucesso!",root,aguarde)

# ============================================================
# Função para desenhar cabeçalho em cada página
# ============================================================
def cabecalho(pdf, pagina):
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    pdf.setFont("Times-Bold", 12)
    pdf.drawString(30, 820, "RELATÓRIO DE ATIVOS EXTERIOR")

    # Data + Página
    pdf.setFont("Times-Roman", 9)
    pdf.drawString(420, 820, f"Data: {data_hoje}")
    pdf.drawString(500, 820, f"Página {pagina}")

    # Cabeçalho das colunas
    pdf.setFont("Times-Bold", 7)
    y = 800
 
    pdf.drawString(30,  y, "Código")
    pdf.drawString(70,  y, "Descrição")
    pdf.drawString(210, y, "Tipo")
    pdf.drawString(290, y, "Segmento")
    pdf.drawString(350, y, "Qtde")
    pdf.drawString(380, y, "Aquisição (US$)")
    pdf.drawString(430, y, "Aquisição (R$)")
    pdf.drawString(480, y, "Custo Médio (R$)")
    pdf.drawString(540, y, "% Alvo")
   