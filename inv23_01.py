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

    barra = ttk.Progressbar(janela, mode="indeterminate", length=250)
    barra.pack(pady=10)
    barra.start(10)
    
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

    tickers = []
    for r in linhas:
        if r["Inv02_22"] == "S":
            tickers.append(inv00_1.ajustar_ticker(r["Inv02_06"], r["Inv02_17"]))

    cotacoes = inv00_1.obter_cotacoes_em_lote(tickers)

    for r in linhas:
        qtd = r["Inv02_07"]
        if qtd <= 0:
            continue

        exterior = r["Inv02_17"]
        usa_cotacao = r["Inv02_22"] == "S"

        custo_brl = float(r["Inv02_09"])
        custo_usd = float(r["Inv02_10"])

        ticker = inv00_1.ajustar_ticker(r["Inv02_06"], exterior)
        preco_original = cotacoes.get(ticker, 0.0)

        moeda = "USD" if exterior == "S" else "BRL"
        cotacao_moeda = inv00_1.obter_cotacao_moeda(moeda)

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
            "Cotacao": preco_original,
            "CotacaoBRL": valor_unit_brl,
            "Quantidade": qtd,

            "ValorOriginal": preco_original,
            "ValorUnitario": valor_unit_brl,
            "ValorTotalCotacao": preco_original * qtd,
            "TotalLocalizado": total_brl,

            "AtivoExterior": exterior,
        }

        ativos.append(ativo)

    total_geral = sum(a["TotalLocalizado"] for a in ativos)

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

    cols_tipos = ("Codigo", "Descricao", "Total", "%Limite",  "%Calc", "Status")
    tree_tipos = ttk.Treeview(frame_tipos, columns=cols_tipos, show="headings")

    tree_tipos.heading("Codigo", text="Codigo")
    tree_tipos.column("Codigo", width=80, anchor="center")

    tree_tipos.heading("Descricao", text="Descricao")
    tree_tipos.column("Descricao", width=250, anchor="w")

    tree_tipos.heading("Total", text="Total")
    tree_tipos.column("Total", width=120, anchor="e")

    tree_tipos.heading("%Limite", text="%Limite")
    tree_tipos.column("%Limite", width=80, anchor="center")

    tree_tipos.heading("%Calc", text="%Calc")
    tree_tipos.column("%Calc", width=80, anchor="center")

    tree_tipos.heading("Status", text="Status")
    tree_tipos.column("Status", width=90, anchor="center")

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
                inv00_1.brstilo(t['Total'] ),
                inv00_1.brstilo(t['PercentualLimite'] ),
                inv00_1.brstilo(t['PercentualCalculado'] ),
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

    cols_seg = ("Codigo", "Descricao", "Total", "%Limite",  "%Calc", "Status")
    tree_seg = ttk.Treeview(frame_seg, columns=cols_seg, show="headings")

    tree_seg.heading("Codigo", text="Codigo")
    tree_seg.column("Codigo", width=80, anchor="center")

    tree_seg.heading("Descricao", text="Descricao")
    tree_seg.column("Descricao", width=250, anchor="w")

    tree_seg.heading("Total", text="Total")
    tree_seg.column("Total", width=120, anchor="e")

    tree_seg.heading("%Limite", text="%Limite")
    tree_seg.column("%Limite", width=80, anchor="center")

    tree_seg.heading("%Calc", text="%Calc")
    tree_seg.column("%Calc", width=80, anchor="center")

    tree_seg.heading("Status", text="Status")
    tree_seg.column("Status", width=90, anchor="center")

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
                inv00_1.brstilo(s['Total'] ),
                inv00_1.brstilo(s['PercentualLimite'] ),
                inv00_1.brstilo(s['PercentualCalculado'] ),
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
        "Codigo", "Descricao", "Segmento", "%Limite", "%Calc",
        "Moeda", "Cotacao", "Quantidade", "ValorTotal", 
        "VlrBRL", "TotalBRL", "Status"
    )

    tree = ttk.Treeview(frame_ativos, columns=colunas, show="headings")

    tree.heading("Codigo", text="Codigo")
    tree.column("Codigo", width=90, anchor="center")

    tree.heading("Descricao", text="Descricao")
    tree.column("Descricao", width=250, anchor="w")

    tree.heading("Segmento", text="Segmento")
    tree.column("Segmento", width=180, anchor="w")

    tree.heading("%Limite", text="%Limite")
    tree.column("%Limite", width=80, anchor="center")

    tree.heading("%Calc", text="%Calc")
    tree.column("%Calc", width=80, anchor="center")

    tree.heading("Moeda", text="Moeda")
    tree.column("Moeda", width=70, anchor="center")

    tree.heading("Cotacao", text="Cotacao")
    tree.column("Cotacao", width=100, anchor="e")

    tree.heading("Quantidade", text="Quantidade")
    tree.column("Quantidade", width=100, anchor="e")

    tree.heading("ValorTotal", text="ValorTotal")
    tree.column("ValorTotal", width=120, anchor="e")

    tree.heading("VlrBRL", text="VlrBRL")
    tree.column("VlrBRL", width=120, anchor="e")

    tree.heading("TotalBRL", text="TotalBRL")
    tree.column("TotalBRL", width=140, anchor="e")

    tree.heading("Status", text="Status")
    tree.column("Status", width=90, anchor="center")

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
                inv00_1.brstilo(a["PercentualLimiteAtivo"] ),
                inv00_1.brstilo(a['PercentualCalculado'] ),
                a["Moeda"],
                inv00_1.brstilo(a['Cotacao'] ),
                a["Quantidade"],
                inv00_1.brstilo(a['ValorTotalCotacao'] ),
                inv00_1.brstilo(a['ValorUnitario'] ),
                inv00_1.brstilo(a['TotalLocalizado'] ),
                status
            ),
            tags=(status,)
        )

    tree.pack(fill="both", expand=True)


