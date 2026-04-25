'''
Programa de Impressão de Ativos Geral
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv02
Módulo: inv31_01.py
'''

# ============================================================
# inv31_01.py - Impressão de Ativos Geral Por Tipo e Segmento
# ============================================================
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import inv00_0
import inv00_1

def cabecalho(pdf, pagina):
    pdf.setFont("Times-Bold", 11)
    pdf.drawString(30, 820, "RELATÓRIO DE ATIVOS - INV02")

    data = datetime.now().strftime("%d/%m/%Y")
    pdf.setFont("Times-Roman", 7)
    pdf.drawString(450, 820, f"Data: {data}")
    pdf.drawString(520, 820, f"Pág: {pagina}")

    pdf.setFont("Times-Bold", 7)
    pdf.drawString(30, 800, "Código")
    pdf.drawString(90, 800, "Descrição")
    pdf.drawString(260, 800, "Qtd")
    pdf.drawString(300, 800, "Valor Atual R$")
    pdf.drawString(380, 800, "Valor Atual US$")
    pdf.drawString(460, 800, "% Investir")

    pdf.line(30, 795, 570, 795)

def montar_dados_relatorio(conn, cotacao_usd):

    dados = inv00_0.listar_ativos_inv02_geral(conn)

    rel = []
    total_geral_rs = 0
    total_geral_us = 0

    totais_tipo = {}
    totais_segmento = {}

    for row in dados:

        (
            codigo,
            descricao,
            tipo,
            desc_tipo,
            segmento,
            desc_segmento,
            qtde,
            valor_aquis_rs,
            valor_aquis_us,
            custo_medio,
            perc_inv,
            usa_valor_atual,
            ativo_ext
        ) = row

        # Valor Atual R$
        if usa_valor_atual == 'S':
            valor_rs = inv00_1.obter_valor_atual(codigo)
        else:
            valor_rs = valor_aquis_rs

        # Valor Atual US$
        if ativo_ext == 'S':
            valor_us = valor_rs / cotacao_usd
        else:
            valor_us = 0

        # Totais gerais
        total_geral_rs += valor_rs
        total_geral_us += valor_us

        # Totais por Tipo
        if tipo not in totais_tipo:
            totais_tipo[tipo] = 0
        totais_tipo[tipo] += valor_rs

        # Totais por Segmento
        if tipo not in totais_segmento:
            totais_segmento[tipo] = {}
        if segmento not in totais_segmento[tipo]:
            totais_segmento[tipo][segmento] = 0
        totais_segmento[tipo][segmento] += valor_rs

        # Guarda item
        rel.append({
            "tipo": tipo,
            "segmento": segmento,
            "codigo": codigo,
            "descricao": descricao,
            "qtde": qtde,
            "valor_rs": valor_rs,
            "valor_us": valor_us,
            "perc_inv": perc_inv
        })

    return rel, totais_tipo, totais_segmento, total_geral_rs, total_geral_us

def gerar_pdf_ativos_geral():

    conn = inv00_0.conectar()
    cotacao_usd = inv00_1.obter_cotacao_moeda("USD")

    rel, totais_tipo, totais_segmento, total_geral_rs, total_geral_us = montar_dados_relatorio(conn, cotacao_usd)

    rel.sort(key=lambda x: (x["tipo"], x["segmento"], x["codigo"]))

    pdf = canvas.Canvas("ativos_geral.pdf", pagesize=A4)
    pagina = 1
    y = 780

    cabecalho(pdf, pagina)

    tipo_atual = None
    segmento_atual = None

    for item in rel:

        # QUEBRA DE TIPO
        if item["tipo"] != tipo_atual:
            tipo_atual = item["tipo"]
            valor_tipo = totais_tipo[tipo_atual]
            perc_tipo = (valor_tipo / total_geral_rs) * 100

            pdf.setFont("Times-Bold", 8)
            pdf.drawString(30, y, f"TIPO {tipo_atual} - Total R$ {valor_tipo:,.2f} ({perc_tipo:.2f}%)")
            y -= 12

        # QUEBRA DE SEGMENTO
        if item["segmento"] != segmento_atual:
            segmento_atual = item["segmento"]
            valor_seg = totais_segmento[tipo_atual][segmento_atual]
            perc_seg = (valor_seg / valor_tipo) * 100

            pdf.setFont("Times-Bold", 7)
            pdf.drawString(40, y, f"Segmento {segmento_atual} - R$ {valor_seg:,.2f} ({perc_seg:.2f}%)")
            y -= 10

        # DETALHE DO ATIVO
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(50, y, f"{item['codigo']}")
        pdf.drawString(90, y, f"{item['descricao'][:40]}")
        pdf.drawRightString(310, y, f"{item['qtde']}")
        pdf.drawRightString(380, y, f"{item['valor_rs']:,.2f}")
        pdf.drawRightString(460, y, f"{item['valor_us']:,.2f}")
        pdf.drawRightString(540, y, f"{item['perc_inv']:,.2f}%")

        y -= 8

        if y < 50:
            pdf.showPage()
            pagina += 1
            y = 780
            cabecalho(pdf, pagina)

    pdf.setFont("Times-Bold", 8)
    pdf.drawString(30, y - 20, f"TOTAL GERAL R$: {total_geral_rs:,.2f}")
    pdf.drawString(30, y - 35, f"TOTAL ATIVOS EXTERIOR US$: {total_geral_us:,.2f}")

    pdf.save()
    conn.close()

    inv00_1.mensagem_sucesso("Relatório impresso com sucesso!")

