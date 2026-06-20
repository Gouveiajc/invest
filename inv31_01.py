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
# Importa query e funções auxiliares
import threading
import tkinter as tk
import inv00_0
import inv00_1

# ============================================================
# Função principal chamada pelo Menu
# ============================================================
def gerar_pdf_ativos_geral(root):

    # Abre janela de aguarde
    aguarde = inv00_1.mostrar_aguarde(root)

    # Executa o processamento em thread separada
    threading.Thread(
        target=lambda: gerar_pdf_geral(root, aguarde),
        daemon=True
    ).start()

# ============================================================
# GERAÇÃO DO PDF 
# ============================================================
def gerar_pdf_geral(root,aguarde):

    conn = inv00_0.conectar()
    cotacao_usd = inv00_1.obter_cotacao_moeda("USD")

    rel, totais_tipo, totais_segmento, total_geral_rs, total_geral_us, total_geral_br = montar_dados_relatorio(conn, cotacao_usd)

    rel.sort(key=lambda x: (x["tipo"], x["segmento"], x["codigo"]))

    pdf = canvas.Canvas("ativos_geral.pdf", pagesize=A4)
    pagina = 1
    y = 790

    cabecalho(pdf, pagina)

    tipo_atual = None
    segmento_atual = None

    for item in rel:

        # QUEBRA DE TIPO
        if item["tipo"] != tipo_atual:
            y -= 5
            tipo_atual = item["tipo"]
            desc_tp_atual = item["desc_tipo"]
            perc_alvo_00 = item["perc_tp"]
            valor_tipo = totais_tipo[tipo_atual]
            perc_tipo = (valor_tipo / total_geral_rs) * 100

            pdf.setFont("Times-Bold", 8)
            pdf.drawString(30, y, f"TIPO {tipo_atual} {desc_tp_atual} -  Perc.Limite {perc_alvo_00}% - Total R$ {valor_tipo:,.2f} ({perc_tipo:.2f}%)")
            y -= 10

        # QUEBRA DE SEGMENTO
        if item["segmento"] != segmento_atual:
            segmento_atual = item["segmento"]
            desc_seg_atual = item["desc_seg"]
            perc_alvo_01 = item["perc_seg"]
            valor_seg = totais_segmento[tipo_atual][segmento_atual]
            perc_seg = (valor_seg / valor_tipo) * 100

            pdf.setFont("Times-Bold", 7)
            pdf.drawString(40, y, f"Segmento {segmento_atual} {desc_seg_atual} - Perc.Limite {perc_alvo_01}% - R$ {valor_seg:,.2f} ({perc_seg:.2f}%)")
            y -= 10

        #Calculo Valor Total Atual
        valor_atual_rs = item['qtde'] * item['valor_rs']
        valor_atual_us = item['qtde'] * item['valor_us']
        perc_seg_inv = (valor_atual_rs / valor_seg) * 100
        perc_total_inv = (valor_atual_rs / total_geral_rs) * 100

        # DETALHE DO ATIVO
        pdf.setFont("Times-Roman", 6)
        pdf.drawString(50, y, f"{item['codigo']}")
        desc = item['descricao']
        desc = (desc[:30] + "...") if len(desc) > 30 else desc  #Limitando Descrição em 30 Caracteres
        pdf.drawString(90, y, desc)
        pdf.drawRightString(240, y, f"{item['qtde']}")
        pdf.drawRightString(280, y, inv00_1.brstilo(item['valor_rs']) )
        pdf.drawRightString(310, y, inv00_1.brstilo(item['valor_us']) )
        pdf.drawRightString(360, y, inv00_1.brstilo(valor_atual_rs) )
        pdf.drawRightString(400, y, inv00_1.brstilo(valor_atual_us) )
        pdf.drawRightString(430, y, inv00_1.brstilo(item['perc_inv']) )
        pdf.drawRightString(460, y, inv00_1.brstilo(perc_seg_inv) )
        pdf.drawRightString(480, y, inv00_1.brstilo(perc_total_inv) )
        pdf.drawRightString(520, y, inv00_1.brstilo(item["custo_inicial"]) )
        pdf.drawRightString(550, y, inv00_1.brstilo(item["per_val"]) )

        y -= 8

        if y < 50:
            pdf.showPage()
            pagina += 1
            y = 780
            cabecalho(pdf, pagina)

    pdf.setFont("Times-Bold", 8)
    pdf.drawString(30, y - 20, f"TOTAL ATIVOS NACIONAL R$: {total_geral_br:,.2f}")
    pdf.drawString(30, y - 35, f"TOTAL ATIVOS EXTERIOR US$: {total_geral_us:,.2f}")
    pdf.drawString(30, y - 50, f"TOTAL GERAL R$: {total_geral_rs:,.2f}")

    pdf.save()
    conn.close()

    inv00_1.mensagem_sucesso("Relatório impresso com sucesso!",root,aguarde)

# ============================================================
# NOVA FUNÇÃO — CÁLCULOS CORRIGIDOS (inv23_01)
# ============================================================
def montar_dados_relatorio(conn, cotacao_usd):

    linhas = inv00_0.buscar_ativos()
    if not linhas:
        return [], {}, {}, 0, 0

    rel = []
    total_geral_rs = 0
    total_geral_us = 0
    total_geral_br = 0

    totais_tipo = {}
    totais_segmento = {}

    # 1) Monta lista de tickers
    tickers = []
    for r in linhas:
        if r["Inv02_22"] == "S":  # usa cotação
            tickers.append(inv00_1.ajustar_ticker(r["Inv02_06"], r["Inv02_17"]))

    # 2) Obtém cotações em lote
    cotacoes = inv00_1.obter_cotacoes_em_lote(tickers)

    # 3) Processa cada ativo
    for r in linhas:

        codigo = r["Inv02_06"]
        descricao = r["Inv02_02"]
        tipo = r["Inv02_01"]
        desc_tipo = r["Inv00_02"]
        perc_tp = float(r["Inv00_20"])

        segmento = r["Inv01_05"]
        desc_segmento = r["Inv01_02"]
        perc_seg = float(r["Inv01_20"])

        qtde = r["Inv02_07"]
        if qtde <= 0:
            continue

        exterior = r["Inv02_17"]  # S/N
        usa_cotacao = r["Inv02_22"] == "S"

        custo_brl = float(r["Inv02_09"])
        custo_usd = float(r["Inv02_10"])

        ticker = inv00_1.ajustar_ticker(codigo, exterior)
        preco_original = cotacoes.get(ticker, 0.0)

        moeda = "USD" if exterior == "S" else "BRL"
        cotacao_moeda = inv00_1.obter_cotacao_moeda(moeda)

        # 4) Cálculo correto do valor (mesma lógica da inv23_01)
        if usa_cotacao and preco_original > 0:
            valor_unit_brl = preco_original * cotacao_moeda
            valor_unit_usd = preco_original if exterior == "S" else 0
            custo_aquis = custo_usd if exterior == "S" else custo_brl
        else:
            if exterior == "S":
                custo_aquis = custo_usd
                valor_unit_brl = (custo_usd * cotacao_moeda) / qtde
                valor_unit_usd = custo_usd / qtde
            else:
                custo_aquis = custo_brl
                valor_unit_brl = custo_brl
                valor_unit_usd = 0

        total_brl = valor_unit_brl * qtde
        total_usd = valor_unit_usd  * qtde if exterior == "S" else 0
        
        # Calcula Valorização
        if exterior == "S":
            valoriza = inv00_1.valoriza(total_usd,custo_aquis)
        else:
            valoriza = inv00_1.valoriza(total_brl,custo_aquis)

        # 5) Totais gerais
        total_geral_rs += total_brl
        total_geral_us += total_usd
        total_geral_br += total_brl if exterior == "N" else 0

        # 6) Totais por tipo
        if tipo not in totais_tipo:
            totais_tipo[tipo] = 0
        totais_tipo[tipo] += total_brl

        # 7) Totais por segmento
        if tipo not in totais_segmento:
            totais_segmento[tipo] = {}
        if segmento not in totais_segmento[tipo]:
            totais_segmento[tipo][segmento] = 0
        totais_segmento[tipo][segmento] += total_brl

        # 8) Guarda item para o PDF
        rel.append({
            "tipo": tipo,
            "desc_tipo": desc_tipo,
            "perc_tp": perc_tp,
            "segmento": segmento,
            "desc_seg": desc_segmento,
            "perc_seg": perc_seg,
            "codigo": codigo,
            "descricao": descricao,
            "qtde": qtde,
            "valor_rs": valor_unit_brl,
            "valor_us": valor_unit_usd,
            "perc_inv": float(r["Inv02_20"]),
            "custo_inicial": custo_aquis,
            "per_val": valoriza,
        })

    return rel, totais_tipo, totais_segmento, total_geral_rs, total_geral_us, total_geral_br

def cabecalho(pdf, pagina):
    y = 820 
    pdf.setFont("Times-Bold", 11)
    pdf.drawString(30, y, "RELATÓRIO DE ATIVOS - GERAL")

    data = datetime.now().strftime("%d/%m/%Y")
    pdf.setFont("Times-Roman", 7)
    pdf.drawString(450, y, f"Data: {data}")
    pdf.drawString(520, y, f"Pág: {pagina}")

    y -= 14
    pdf.setFont("Times-Bold", 7)
    pdf.drawString(260, y, "Un.")
    pdf.drawString(300, y, "Un.")
    pdf.drawString(340, y, "Vlr")
    pdf.drawString(380, y, "Vlr")
    pdf.drawString(420, y, "%")
    pdf.drawString(450, y, "%")
    pdf.drawString(470, y, "%")
    pdf.drawString(500, y, "Vlr")
    pdf.drawString(530, y, "%")

    y -= 6
    pdf.setFont("Times-Bold", 7)
    pdf.drawString(50, y, "Código")
    pdf.drawString(120, y, "Descrição")
    pdf.drawString(230, y, "Qtd")
    pdf.drawString(250, y, "Atual R$")
    pdf.drawString(290, y, "Atual US$")
    pdf.drawString(330, y, "Atual R$")
    pdf.drawString(370, y, "Total US$")
    pdf.drawString(410, y, "Investir")
    pdf.drawString(440, y, "Segm.")
    pdf.drawString(460, y, "Investido")
    pdf.drawString(490, y, "Investido")
    pdf.drawString(520, y, "Valorização")

    pdf.line(30, 795, 570, 795)
