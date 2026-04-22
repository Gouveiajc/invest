"""
Programa de Analise de Ativos
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv04
Módulo: inv23_01.py
"""
# inv23_01.py
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import inv00_0
import inv00_1

COR_VERDE = "VERDE"
COR_AMARELO = "AMARELO"
COR_VERMELHO = "VERMELHO"

# ============================================================
# JANELA DE AGUARDE
# ============================================================
def executar_analise(root):
    aguarde = mostrar_aguarde(root)
    root.after(100, lambda: processar_analise(root, aguarde))


def processar_analise(root, aguarde):
    tipos, segmentos, ativos = obter_dados()
    aguarde.destroy()
    abrir_grids(tipos, segmentos, ativos)


def mostrar_aguarde(root):
    janela = tk.Toplevel(root)
    janela.title("Aguarde")
    janela.resizable(False, False)

    centralizar_janela(janela, 300, 150)

    tk.Label(
        janela,
        text="Pesquisando dados...\nPor favor, aguarde.",
        font=("Arial", 12),
        pady=10
    ).pack()

    # --- BARRA DE PROGRESSO ANIMADA ---
    barra = ttk.Progressbar(janela, mode="indeterminate", length=250)
    barra.pack(pady=10)
    barra.start(10)   # velocidade da animação (ms)
    
    janela.update()
    return janela


def centralizar_janela(janela, largura, altura):
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    janela.geometry(f"{largura}x{altura}+{x}+{y}")


# ============================================================
# AJUSTE DE TICKER
# ============================================================
def ajustar_ticker(ticker, exterior):
    if not ticker:
        return ""

    ticker = ticker.strip().upper()

    if exterior == "S":
        return ticker

    if ticker.endswith(".SA"):
        return ticker

    return ticker + ".SA"

# ============================================================
# STATUS
# ============================================================
def calcular_status(percentual, limite):
    if limite <= 0:
        return ""

    if percentual <= limite * 0.85:
        return COR_VERDE
    elif percentual <= limite * 0.95:
        return COR_AMARELO
    else:
        return COR_VERMELHO


# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================
def obter_dados():
    linhas = inv00_0.buscar_ativos_pagadores()
    if not linhas:
        return [], [], []

    ativos = []

    # -----------------------------
    # Preparar lista de tickers
    # -----------------------------
    tickers = []
    for r in linhas:
        if r["Inv02_22"] == "S":
            tickers.append(ajustar_ticker(r["Inv02_06"], r["Inv02_17"]))

    cotacoes = inv00_1.obter_cotacoes_em_lote(tickers)

    # -----------------------------
    # Processar ativos
    # -----------------------------
    for r in linhas:
        qtd = r["Inv02_07"]
        if qtd <= 0:
            continue

        exterior = r["Inv02_17"]
        usa_cotacao = r["Inv02_22"] == "S"

        custo_brl = float(r["Inv02_09"])
        custo_usd = float(r["Inv02_10"])

        ticker = ajustar_ticker(r["Inv02_06"], exterior)
        preco_original = cotacoes.get(ticker, 0.0)

        moeda = "USD" if exterior == "S" else "BRL"
        cotacao_moeda = inv00_1.obter_cotacao_moeda(moeda)

        # -----------------------------
        # Cálculo do valor
        # -----------------------------
        if usa_cotacao and preco_original > 0:
            valor_unit_brl = preco_original * cotacao_moeda
            total_brl = valor_unit_brl * qtd
        else:
            if exterior == "S":
                total_brl = custo_usd * qtd * cotacao_moeda
            else:
                total_brl = custo_brl * qtd

            valor_unit_brl = total_brl / qtd if qtd else 0.0

        ativo = {
            "CodigoAtivo": r["Inv02_06"],
            "DescricaoAtivo": r["Inv02_02"],
            "DescricaoSegmento": r["Inv01_02"],
            "CodigoSegmento": r["Inv01_05"],
            "CodigoTipo": r["Inv02_01"],
            "DescricaoTipo": r["Inv00_02"],

            "PercentualLimiteAtivo": float(r["Inv02_20"]),
            "PercentualLimiteSegmento": float(r["Inv01_20"]),
            "PercentualLimiteTipo": float(r["Inv00_20"]),

            "Moeda": moeda,
            "Cotacao": preco_original,                 # cotação real
            "CotacaoBRL": valor_unit_brl,              # cotação convertida
            "Quantidade": qtd,

            "ValorOriginal": preco_original,
            "ValorUnitario": valor_unit_brl,
            "ValorTotalCotacao": preco_original * qtd, # NOVO
            "TotalLocalizado": total_brl,

            "AtivoExterior": exterior,
        }

        ativos.append(ativo)

    # -----------------------------
    # Total geral
    # -----------------------------
    total_geral = sum(a["TotalLocalizado"] for a in ativos)

    # -----------------------------
    # TIPOS
    # -----------------------------
    tipos = {}
    for a in ativos:
        cod_tipo = a["CodigoTipo"]
        if cod_tipo not in tipos:
            tipos[cod_tipo] = {
                "Codigo": cod_tipo,
                "Descricao": a["DescricaoTipo"],
                "Total": 0.0,
                "PercentualLimite": a["PercentualLimiteTipo"],
            }
        tipos[cod_tipo]["Total"] += a["TotalLocalizado"]

    for t in tipos.values():
        t["PercentualCalculado"] = (t["Total"] / total_geral) * 100
        t["Status"] = calcular_status(t["PercentualCalculado"], t["PercentualLimite"])

    # -----------------------------
    # SEGMENTOS
    # -----------------------------
    segmentos = {}
    for a in ativos:
        seg = a["CodigoSegmento"]
        if seg not in segmentos:
            segmentos[seg] = {
                "Codigo": seg,
                "Descricao": a["DescricaoSegmento"],
                "CodigoTipo": a["CodigoTipo"],
                "Total": 0.0,
                "PercentualLimite": a["PercentualLimiteSegmento"],
            }
        segmentos[seg]["Total"] += a["TotalLocalizado"]

    for s in segmentos.values():
        total_tipo = tipos[s["CodigoTipo"]]["Total"]
        s["PercentualCalculado"] = (s["Total"] / total_tipo) * 100 if total_tipo > 0 else 0
        s["Status"] = calcular_status(s["PercentualCalculado"], s["PercentualLimite"])

    # -----------------------------
    # ATIVOS (% dentro do segmento)
    # -----------------------------
    for a in ativos:
        total_segmento = segmentos[a["CodigoSegmento"]]["Total"]
        a["PercentualCalculado"] = (a["TotalLocalizado"] / total_segmento) * 100 if total_segmento > 0 else 0
        a["Status"] = calcular_status(a["PercentualCalculado"], a["PercentualLimiteAtivo"])

    return list(tipos.values()), list(segmentos.values()), ativos


# ============================================================
# GRIDS
# ============================================================
def abrir_grids(tipos, segmentos, ativos):
    if not ativos:
        messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
        return

    janela = tk.Toplevel()
    janela.title("Análise de Ativos")
    janela.geometry("1500x700")

    # --- BOTÃO RETORNAR NO TOPO DIREITO ---
    top_frame = tk.Frame(janela)
    top_frame.pack(fill="x")

    btn_retornar = tk.Button(top_frame, text="Retornar", font=("Arial", 12), command=janela.destroy)
    btn_retornar.pack(side="right", padx=10, pady=10)

    notebook = ttk.Notebook(janela)
    notebook.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # GRID TIPOS
    # --------------------------------------------------------
    frame_tipos = ttk.Frame(notebook)
    notebook.add(frame_tipos, text="Tipos")

    cols_tipos = ("Codigo", "Descricao", "%Limite", "Total", "%Calc", "Status")
    tree_tipos = ttk.Treeview(frame_tipos, columns=cols_tipos, show="headings")

    for c in cols_tipos:
        tree_tipos.heading(c, text=c)

    # Configurar cores
    tree_tipos.tag_configure("VERDE", foreground="green")
    tree_tipos.tag_configure("AMARELO", foreground="orange")
    tree_tipos.tag_configure("VERMELHO", foreground="red")

    for t in tipos:
        status = t["Status"]
        tree_tipos.insert(
            "",
            tk.END,
            values=(
                t["Codigo"],
                t["Descricao"],
                f"{t['PercentualLimite']:.2f}",
                f"{t['Total']:.2f}",
                f"{t['PercentualCalculado']:.2f}",
                status,
            ),
            tags=(status,)
        )

    tree_tipos.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # GRID SEGMENTOS
    # --------------------------------------------------------
    frame_seg = ttk.Frame(notebook)
    notebook.add(frame_seg, text="Segmentos")

    cols_seg = ("Codigo", "Descricao", "%Limite", "Total", "%Calc", "Status")
    tree_seg = ttk.Treeview(frame_seg, columns=cols_seg, show="headings")

    for c in cols_seg:
        tree_seg.heading(c, text=c)

    tree_seg.tag_configure("VERDE", foreground="green")
    tree_seg.tag_configure("AMARELO", foreground="orange")
    tree_seg.tag_configure("VERMELHO", foreground="red")

    for s in segmentos:
        status = s["Status"]
        tree_seg.insert(
            "",
            tk.END,
            values=(
                s["Codigo"],
                s["Descricao"],
                f"{s['PercentualLimite']:.2f}",
                f"{s['Total']:.2f}",
                f"{s['PercentualCalculado']:.2f}",
                status,
            ),
            tags=(status,)
        )

    tree_seg.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # GRID ATIVOS
    # --------------------------------------------------------
    frame_ativos = ttk.Frame(notebook)
    notebook.add(frame_ativos, text="Ativos")

    colunas = (
        "Codigo", "Descricao", "Segmento", "%Limite",
        "Moeda", "Cotacao", "Quantidade",
        "ValorTotal", "VlrBRL", "TotalBRL",
        "%Calc", "Status"
    )

    tree = ttk.Treeview(frame_ativos, columns=colunas, show="headings")

    for c in colunas:
        tree.heading(c, text=c)

    tree.tag_configure("VERDE", foreground="green")
    tree.tag_configure("AMARELO", foreground="orange")
    tree.tag_configure("VERMELHO", foreground="red")

    for a in ativos:
        status = a["Status"]
        tree.insert(
            "",
            tk.END,
            values=(
                a["CodigoAtivo"],
                a["DescricaoAtivo"],
                a["DescricaoSegmento"],
                f"{a['PercentualLimiteAtivo']:.2f}",
                a["Moeda"],
                f"{a['Cotacao']:.4f}",
                a["Quantidade"],
                f"{a['ValorTotalCotacao']:.2f}",
                f"{a['ValorUnitario']:.2f}",
                f"{a['TotalLocalizado']:.2f}",
                f"{a['PercentualCalculado']:.2f}",
                status
            ),
            tags=(status,)
        )

    tree.pack(fill="both", expand=True)

