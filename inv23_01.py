"""Análise de Ativos 
Tabela INV02
Módulo: inv23_01.py
Fev/2026
"""

import tkinter as tk
from tkinter import ttk
import yfinance as yf
import inv00_0

COR_VERDE = "VERDE"
COR_AMARELO = "AMARELO"
COR_VERMELHO = "VERMELHO"

# ------------------------------------------------------------
# Função chamada pelo menu → monta o GRID
# ------------------------------------------------------------
def analisar_ativos():
    dados = obter_dados()

    if not dados:
        print("Nenhum dado encontrado.")
        return

    janela = tk.Toplevel()
    janela.title("Análise de Ativos")
    janela.geometry("1400x650")

    # ------------------------------------------------------------
    # BOTÃO DE RETORNO NO TOPO À DIREITA
    # ------------------------------------------------------------
    frame_topo = tk.Frame(janela)
    frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    janela.grid_columnconfigure(0, weight=1)

    botao_retorno = tk.Button(
        frame_topo,
        text="Retornar",
        font=("Arial", 12, "bold"),
        width=12,
        command=janela.destroy
    )
    botao_retorno.pack(side="right")

    # ------------------------------------------------------------
    # GRID (TREEVIEW)
    # ------------------------------------------------------------
    colunas = (
        "Codigo", "Descricao", "Segmento", "%Limite",
        "Moeda", "Cotacao", "Quantidade", "VlrOrig", "VlrBRL",
        "Total", "%Calc", "Status"
    )

    tree = ttk.Treeview(janela, columns=colunas, show="headings", height=25)

    # Cabeçalhos
    tree.heading("Codigo", text="Código")
    tree.heading("Descricao", text="Descrição")
    tree.heading("Segmento", text="Segmento")
    tree.heading("%Limite", text="% Limite")
    tree.heading("Moeda", text="Moeda")
    tree.heading("Cotacao", text="Cotação")
    tree.heading("Quantidade", text="Qtde")
    tree.heading("VlrOrig", text="Valor Orig.")
    tree.heading("VlrBRL", text="Valor (R$)")
    tree.heading("Total", text="Total (R$)")
    tree.heading("%Calc", text="% Calc.")
    tree.heading("Status", text="Status")

    # Larguras
    tree.column("Codigo", width=90)
    tree.column("Descricao", width=250)
    tree.column("Segmento", width=150)
    tree.column("%Limite", width=80, anchor="e")
    tree.column("Moeda", width=70, anchor="center")
    tree.column("Cotacao", width=90, anchor="e")
    tree.column("Quantidade", width=80, anchor="e")
    tree.column("VlrOrig", width=100, anchor="e")
    tree.column("VlrBRL", width=100, anchor="e")
    tree.column("Total", width=120, anchor="e")
    tree.column("%Calc", width=80, anchor="e")
    tree.column("Status", width=80, anchor="center")

    # Inserir dados
    for a in dados:
        cor = "black"
        if a["Status"] == "VERDE":
            cor = "green"
        elif a["Status"] == "AMARELO":
            cor = "orange"
        elif a["Status"] == "VERMELHO":
            cor = "red"

        tree.insert(
            "",
            tk.END,
            values=(
                a["CodigoAtivo"],
                a["DescricaoAtivo"],
                a.get("DescricaoSegmento", ""),
                f"{a.get('PercentualLimite', 0):.2f}",
                a["Moeda"],
                f"{a['Cotacao']:.4f}",
                a["Quantidade"],
                f"{a['ValorOriginal']:.2f}",
                f"{a['ValorUnitario']:.2f}",
                f"{a['TotalLocalizado']:.2f}",
                f"{a['PercentualCalculado']:.2f}",
                a["Status"]
            ),
            tags=(cor,)
        )

    # Cores
    tree.tag_configure("green", foreground="green")
    tree.tag_configure("orange", foreground="orange")
    tree.tag_configure("red", foreground="red")

    # Scrollbar
    scroll_y = ttk.Scrollbar(janela, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll_y.set)

    tree.grid(row=1, column=0, sticky="nsew")
    scroll_y.grid(row=1, column=1, sticky="ns")

    janela.grid_rowconfigure(1, weight=1)
    janela.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    analisar_ativos()

# ------------------------------------------------------------
# Busca cotação de moedas
# ------------------------------------------------------------
def obter_cotacao_moeda(moeda):
    pares = {
        "USD": "USDBRL=X",
        "EUR": "EURBRL=X",
        "CAD": "CADBRL=X",
        "GBP": "GBPBRL=X",
        "JPY": "JPYBRL=X"
    }

    if moeda not in pares:
        return 1.0  # BRL ou moeda desconhecida → sem conversão

    try:
        t = yf.Ticker(pares[moeda])
        info = t.fast_info

        # Compatível com versões antigas e novas
        preco = (
            info.get("last_price")
            or info.get("lastPrice")
            or info.get("regularMarketPrice")
            or 1.0
        )
        return float(preco)

    except:
        return 1.0

# ------------------------------------------------------------
# Ajusta ticker conforme ativo nacional ou exterior
# ------------------------------------------------------------
def ajustar_ticker(ticker: str, ativo_exterior: str) -> str:
    if not ticker or ticker == "0":
        return ""
    if ativo_exterior and ativo_exterior.upper() == "S":
        return ticker
    return ticker + ".SA"

# ------------------------------------------------------------
# Busca o preço atual no Yahoo Finance
# ------------------------------------------------------------
def obter_preco_atual(ticker: str):
    try:
        if not ticker:
            return 0.0, "BRL"

        t = yf.Ticker(ticker)

        # força carregar o fast_info
        info = dict(t.fast_info)

        preco = (
            info.get("last_price")
            or info.get("lastPrice")
            or info.get("regularMarketPrice")
            or 0.0
        )

        moeda = info.get("currency", "BRL")

        return float(preco), moeda

    except Exception as e:
        print("Erro obter_preco_atual:", e)
        return 0.0, "BRL"

# ------------------------------------------------------------
# Calcula status (cores)
# ------------------------------------------------------------
def calcular_status(percentual_calculado: float, percentual_limite: float) -> str:
    if percentual_limite <= 0:
        return ""

    limite_80 = percentual_limite * 0.80
    limite_95 = percentual_limite * 0.95

    if percentual_calculado <= limite_80:
        return COR_VERDE
    elif percentual_calculado <= limite_95:
        return COR_AMARELO
    else:
        return COR_VERMELHO


# ------------------------------------------------------------
# Monta toda a análise e devolve lista de dicionários
# ------------------------------------------------------------
def obter_dados():
    ativos = inv00_0.buscar_ativos_para_pesquisa()

    if not ativos:
        return []

    for a in ativos:
        ativo_exterior = (a.get("AtivoExterior") or "").strip().upper()
        ticker_ajustado = ajustar_ticker(a["CodigoAtivo"], ativo_exterior)

        preco_original, moeda = obter_preco_atual(ticker_ajustado)
        cotacao = obter_cotacao_moeda(moeda)

        preco_convertido = preco_original * cotacao

        a["TickerAjustado"] = ticker_ajustado
        a["Moeda"] = moeda
        a["Cotacao"] = cotacao
        a["ValorOriginal"] = preco_original
        a["ValorUnitario"] = preco_convertido
        a["TotalLocalizado"] = preco_convertido * a["Quantidade"]

    total_geral = sum(a["TotalLocalizado"] for a in ativos)

    if total_geral == 0:
        return []

    for a in ativos:
        a["PercentualCalculado"] = (a["TotalLocalizado"] / total_geral) * 100
        limite = a.get("PercentualLimite", 0) or 0
        a["Status"] = calcular_status(a["PercentualCalculado"], limite)

    return ativos

