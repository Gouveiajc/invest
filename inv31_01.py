'''
Programa de Impressão de Ativos
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv04
Módulo: inv31_01.py
'''

# ============================================================
# inv31_01.py - Impressão de Ativos em PDF
# ============================================================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from tkinter import ttk

# Importa query e funções auxiliares
import tkinter as tk
import inv00_0 
import inv23_01 

# ------------------------------------------------------------
# Função para desenhar cabeçalho em cada página
# ------------------------------------------------------------
def cabecalho(pdf, pagina):
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    pdf.setFont("Times-Bold", 12)
    pdf.drawString(30, 820, "RELATÓRIO DE ATIVOS")

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
    pdf.drawString(500, y, "Custo Médio")
    pdf.drawString(560, y, "% Alvo")

# ------------------------------------------------------------
# Função principal para gerar PDF
# ------------------------------------------------------------
def gerar_pdf_ativos():

    # Conexão com banco
    conn = inv00_0.conectar()

    # Buscar Dados
    dados = inv00_0.listar_ativos_inv02(conn)

    # Criação do PDF
    pdf = canvas.Canvas("ativos.pdf", pagesize=A4)
    pdf.setFont("Times-Roman", 5)

    pagina = 1
    cabecalho(pdf, pagina)

    y = 780

    # Busca Cotação do dólar (Ativos no Exterior) 
    cotacao_usd = inv23_01.obter_cotacao_moeda("USD")

    for row in dados:
        (
            codigo, descricao, tipo, desc_tipo, segmento, desc_segmento,
            valor_rs, valor_usd, ativo_exterior, custo_medio, pct
        ) = row

        if ativo_exterior == "S":
            valor_aquisicao = valor_usd * cotacao_usd
        else:
            valor_aquisicao = valor_rs

        pdf.drawString(30,  y, str(codigo))
        pdf.drawString(90,  y, str(descricao)[:25])
        pdf.drawString(250, y, f"{tipo} - {desc_tipo[:10]}")
        pdf.drawString(330, y, f"{segmento} - {desc_segmento[:10]}")
        pdf.drawRightString(480, y, f"{valor_aquisicao:,.2f}")
        pdf.drawRightString(540, y, f"{custo_medio:,.2f}")
        pdf.drawRightString(590, y, f"{pct:.2f}")

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
    