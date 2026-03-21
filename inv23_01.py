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

    centralizar_janela(janela, 300, 120)

    tk.Label(
        janela,
        text="Pesquisando dados...\nPor favor, aguarde.",
        font=("Arial", 12),
        pady=20
    ).pack()

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
# BUSCA DE COTAÇÕES EM LOTE
# ============================================================
def obter_cotacoes_em_lote(lista_tickers):
    if not lista_tickers:
        return {}

    dados = yf.download(lista_tickers, period="1d", group_by="ticker", progress=False)

    cotacoes = {}

    for t in lista_tickers:
        try:
            if len(lista_tickers) == 1:
                preco = float(dados["Close"].iloc[-1])
            else:
                preco = float(dados[t]["Close"].iloc[-1])
            cotacoes[t] = preco
        except:
            cotacoes[t] = 0.0

    return cotacoes


# ============================================================
# COTAÇÃO DE MOEDA
# ============================================================
def obter_cotacao_moeda(moeda):
    pares = {
        "USD": "USDBRL=X",
        "EUR": "EURBRL=X",
        "CAD": "CADBRL=X",
        "GBP": "GBPBRL=X",
        "JPY": "JPYBRL=X"
    }

    if moeda not in pares:
        return 1.0

    try:
        t = yf.Ticker(pares[moeda])
        info = dict(t.fast_info or {})
        preco = info.get("last_price") or info.get("regularMarketPrice")

        if preco:
            return float(preco)

        hist = t.history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])

    except:
        pass

    return 1.0

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

    cotacoes = obter_cotacoes_em_lote(tickers)

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
        cotacao_moeda = obter_cotacao_moeda(moeda)

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

'''
ANTERIOR
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import inv00_0

COR_VERDE = "VERDE"
COR_AMARELO = "AMARELO"
COR_VERMELHO = "VERMELHO"

# ------------------------------------------------------------
# Função que mostra "aguarde" e executa a análise
# ------------------------------------------------------------
def executar_analise(root):
    aguarde = mostrar_aguarde(root)
    tipos, segmentos, ativos = obter_dados()
    aguarde.destroy()
    abrir_grids(tipos, segmentos, ativos)

# ------------------------------------------------------------
# Janela de "Aguarde"
# ------------------------------------------------------------
def mostrar_aguarde(root):
    janela = tk.Toplevel(root)
    janela.title("Aguarde")
    janela.resizable(False, False)

    centralizar_janela(janela, 300, 120)

    tk.Label(
        janela,
        text="Pesquisando dados...\nPor favor, aguarde.",
        font=("Arial", 12),
        pady=20
    ).pack()

    janela.update()
    return janela

# ------------------------------------------------------------
# Centralizar Janela de "Aguarde"
# ------------------------------------------------------------
def centralizar_janela(janela, largura, altura):
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)

    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# ------------------------------------------------------------
# Monta os 3 GRIDs
# ------------------------------------------------------------
def abrir_grids(tipos, segmentos, ativos):
    if not ativos:
        messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
        return

    janela = tk.Toplevel()
    janela.title("Análise de Ativos")
    janela.geometry("1400x650")

    frame_topo = tk.Frame(janela)
    frame_topo.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
    janela.grid_columnconfigure(0, weight=1)

    tk.Button(
        frame_topo,
        text="Retornar",
        font=("Arial", 12, "bold"),
        width=12,
        command=janela.destroy
    ).pack(side="right")

    notebook = ttk.Notebook(janela)
    notebook.grid(row=1, column=0, sticky="nsew")
    janela.grid_rowconfigure(1, weight=1)

    # --------------------------------------------------------
    # GRID TIPOS
    # --------------------------------------------------------
    frame_tipos = ttk.Frame(notebook)
    notebook.add(frame_tipos, text="Tipos")

    cols_tipos = ("Codigo", "Descricao", "%Limite", "Total", "%Calc", "Status")
    tree_tipos = ttk.Treeview(frame_tipos, columns=cols_tipos, show="headings", height=20)

    for c in cols_tipos:
        tree_tipos.heading(c, text=c)

    tree_tipos.column("Codigo", width=100)
    tree_tipos.column("Descricao", width=200)
    tree_tipos.column("%Limite", width=80, anchor="e")
    tree_tipos.column("Total", width=120, anchor="e")
    tree_tipos.column("%Calc", width=80, anchor="e")
    tree_tipos.column("Status", width=80, anchor="center")

    for t in tipos:
        cor = "black"
        if t["Status"] == COR_VERDE:
            cor = "green"
        elif t["Status"] == COR_AMARELO:
            cor = "orange"
        elif t["Status"] == COR_VERMELHO:
            cor = "red"

        tree_tipos.insert(
            "",
            tk.END,
            values=(
                t["Codigo"],
                t["Descricao"],
                f"{t['PercentualLimite']:.2f}",
                f"{t['Total']:.2f}",
                f"{t['PercentualCalculado']:.2f}",
                t["Status"],
            ),
            tags=(cor,)
        )

    tree_tipos.tag_configure("green", foreground="green")
    tree_tipos.tag_configure("orange", foreground="orange")
    tree_tipos.tag_configure("red", foreground="red")

    scroll_tipos = ttk.Scrollbar(frame_tipos, orient="vertical", command=tree_tipos.yview)
    tree_tipos.configure(yscroll=scroll_tipos.set)
    tree_tipos.pack(side="left", fill="both", expand=True)
    scroll_tipos.pack(side="right", fill="y")

    # --------------------------------------------------------
    # GRID SEGMENTOS
    # --------------------------------------------------------
    frame_seg = ttk.Frame(notebook)
    notebook.add(frame_seg, text="Segmentos")

    cols_seg = ("Codigo", "Descricao", "%Limite", "Total", "%Calc", "Status")
    tree_seg = ttk.Treeview(frame_seg, columns=cols_seg, show="headings", height=20)

    for c in cols_seg:
        tree_seg.heading(c, text=c)

    tree_seg.column("Codigo", width=120)
    tree_seg.column("Descricao", width=250)
    tree_seg.column("%Limite", width=80, anchor="e")
    tree_seg.column("Total", width=120, anchor="e")
    tree_seg.column("%Calc", width=80, anchor="e")
    tree_seg.column("Status", width=80, anchor="center")

    for s in segmentos:
        cor = "black"
        if s["Status"] == COR_VERDE:
            cor = "green"
        elif s["Status"] == COR_AMARELO:
            cor = "orange"
        elif s["Status"] == COR_VERMELHO:
            cor = "red"

        tree_seg.insert(
            "",
            tk.END,
            values=(
                s["Codigo"],
                s["Descricao"],
                f"{s['PercentualLimite']:.2f}",
                f"{s['Total']:.2f}",
                f"{s['PercentualCalculado']:.2f}",
                s["Status"],
            ),
            tags=(cor,)
        )

    tree_seg.tag_configure("green", foreground="green")
    tree_seg.tag_configure("orange", foreground="orange")
    tree_seg.tag_configure("red", foreground="red")

    scroll_seg = ttk.Scrollbar(frame_seg, orient="vertical", command=tree_seg.yview)
    tree_seg.configure(yscroll=scroll_seg.set)
    tree_seg.pack(side="left", fill="both", expand=True)
    scroll_seg.pack(side="right", fill="y")

    # --------------------------------------------------------
    # GRID ATIVOS
    # --------------------------------------------------------
    frame_ativos = ttk.Frame(notebook)
    notebook.add(frame_ativos, text="Ativos")

    colunas = (
        "Codigo", "Descricao", "Segmento", "%Limite",
        "Moeda", "Cotacao", "Quantidade", "VlrOrig", "VlrBRL",
        "Total", "%Calc", "Status"
    )

    tree = ttk.Treeview(frame_ativos, columns=colunas, show="headings", height=20)

    for c in colunas:
        tree.heading(c, text=c)

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

    for a in ativos:
        cor = "black"
        if a["Status"] == COR_VERDE:
            cor = "green"
        elif a["Status"] == COR_AMARELO:
            cor = "orange"
        elif a["Status"] == COR_VERMELHO:
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

    tree.tag_configure("green", foreground="green")
    tree.tag_configure("orange", foreground="orange")
    tree.tag_configure("red", foreground="red")

    scroll_y = ttk.Scrollbar(frame_ativos, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scroll_y.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

# ------------------------------------------------------------
# Conversão de moedas
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
        return 1.0

    try:
        t = yf.Ticker(pares[moeda])
        info = dict(t.fast_info or {})

        preco = (
            info.get("last_price")
            or info.get("lastPrice")
            or info.get("regularMarketPrice")
        )

        if preco:
            return float(preco)

        hist = t.history(period="5d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])

        return 1.0

    except:
        return 1.0


# ------------------------------------------------------------
# Ajuste de ticker nacional / exterior
# ------------------------------------------------------------
def ajustar_ticker(ticker: str, ativo_exterior: str) -> str:
    if not ticker or ticker == "0":
        return ""

    ticker = ticker.strip().upper()

    if ativo_exterior and ativo_exterior.upper() == "S":
        return ticker

    if not ticker.endswith(".SA"):
        return ticker + ".SA"

    return ticker


# ------------------------------------------------------------
# Preço atual com fallback
# ------------------------------------------------------------
def obter_preco_atual(ticker: str):
    try:
        if not ticker:
            return 0.0, "BRL"

        t = yf.Ticker(ticker)

        info = dict(t.fast_info or {})
        preco = (
            info.get("last_price")
            or info.get("lastPrice")
            or info.get("regularMarketPrice")
        )
        moeda = info.get("currency")

        if not preco:
            hist = t.history(period="5d")
            if not hist.empty:
                preco = float(hist["Close"].iloc[-1])
                moeda = info.get("currency", "BRL")

        if not preco:
            preco = 0.0
        if not moeda:
            moeda = "BRL"

        return float(preco), moeda

    except Exception as e:
        print("Erro obter_preco_atual:", e)
        return 0.0, "BRL"


# ------------------------------------------------------------
# Cores conforme percentual
# ------------------------------------------------------------
def calcular_status(percentual_calculado: float, percentual_limite: float) -> str:
    if percentual_limite <= 0:
        return ""

    limite_85 = percentual_limite * 0.85
    limite_95 = percentual_limite * 0.95

    if percentual_calculado <= limite_85:
        return COR_VERDE
    elif percentual_calculado <= limite_95:
        return COR_AMARELO
    else:
        return COR_VERMELHO


# ------------------------------------------------------------
# Monta toda a análise
# ------------------------------------------------------------
def obter_dados():
    linhas = inv00_0.buscar_ativos_pagadores()
    if not linhas:
        return [], [], []

    ativos = []

    for r in linhas:
        r = dict(r)  
        qtd = r.get("Quantidade") or 0

        if qtd <= 0:
            continue

        ativo_exterior = (r.get("AtivoExterior") or "").strip().upper()
        usa_cotacao = (r.get("UsaCotacao") or "").strip().upper() == "S"

        custo_brl = float(r.get("CustoBRL") or 0.0)
        custo_usd = float(r.get("CustoUSD") or 0.0)

        ticker_ajustado = ""
        preco_original = 0.0
        moeda = "BRL"
        cotacao_moeda = 1.0
        valor_unit_brl = 0.0
        total_brl = 0.0

        if usa_cotacao:
            ticker_ajustado = ajustar_ticker(r["CodigoAtivo"], ativo_exterior)
            preco_original, moeda = obter_preco_atual(ticker_ajustado)

            if preco_original > 0:
                cotacao_moeda = obter_cotacao_moeda(moeda)
                valor_unit_brl = preco_original * cotacao_moeda
                total_brl = valor_unit_brl * qtd
            else:
                if ativo_exterior == "S" and custo_usd > 0:
                    cotacao_moeda = obter_cotacao_moeda("USD")
                    total_brl = custo_usd * cotacao_moeda
                else:
                    total_brl = custo_brl

                valor_unit_brl = total_brl / qtd if qtd else 0.0

        else:
            if ativo_exterior == "S" and custo_usd > 0:
                cotacao_moeda = obter_cotacao_moeda("USD")
                total_brl = custo_usd * cotacao_moeda
            else:
                total_brl = custo_brl

            valor_unit_brl = total_brl / qtd if qtd else 0.0

        ativo = {
            "CodigoAtivo": r["CodigoAtivo"],
            "DescricaoAtivo": r.get("DescricaoAtivo", r["CodigoAtivo"]),
            "DescricaoSegmento": r.get("DescricaoSegmento", ""),
            "CodigoSegmento": r.get("CodigoSegmento"),
            "CodigoTipo": r.get("CodigoTipo"),
            "DescricaoTipo": r.get("DescricaoTipo", ""),   
            
            "PercentualLimiteAtivo": float(r.get("PercentualLimiteAtivo") or 0.0),
            "PercentualLimiteSegmento": float(r.get("PercentualLimiteSegmento") or 0.0),
            "PercentualLimiteTipo": float(r.get("PercentualLimiteTipo") or 0.0),

            "Moeda": moeda,
            "Cotacao": cotacao_moeda,
            "Quantidade": qtd,
            "ValorOriginal": preco_original,
            "ValorUnitario": valor_unit_brl,
            "TotalLocalizado": total_brl,
            "AtivoExterior": ativo_exterior,
        }
        ativos.append(ativo)

    total_geral = sum(a["TotalLocalizado"] for a in ativos)
    if total_geral == 0:
        return [], [], []

    for a in ativos:
        a["PercentualCalculado"] = (a["TotalLocalizado"] / total_geral) * 100
        limite = a.get("PercentualLimiteAtivo", 0) or 0
        a["PercentualLimite"] = limite
        a["Status"] = calcular_status(a["PercentualCalculado"], limite)

    segmentos = {}
    for a in ativos:
        cod_seg = a.get("CodigoSegmento")
        if not cod_seg:
            continue
        if cod_seg not in segmentos:
            segmentos[cod_seg] = {
                "Codigo": cod_seg,
                "Descricao": a.get("DescricaoSegmento", cod_seg),
                "Total": 0.0,
                "PercentualLimite": a.get("PercentualLimiteSegmento", 0.0),
            }
        segmentos[cod_seg]["Total"] += a["TotalLocalizado"]

    for seg in segmentos.values():
        seg["PercentualCalculado"] = (seg["Total"] / total_geral) * 100
        seg["Status"] = calcular_status(seg["PercentualCalculado"], seg["PercentualLimite"])

    tipos = {}
    for a in ativos:
        cod_tipo = a.get("CodigoTipo")
        if not cod_tipo:
            continue
        if cod_tipo not in tipos:
            tipos[cod_tipo] = {
                "Codigo": cod_tipo,
                "Descricao": a.get("DescricaoTipo", cod_tipo),
                "Total": 0.0,
                "PercentualLimite": a.get("PercentualLimiteTipo", 0.0),
            }
        tipos[cod_tipo]["Total"] += a["TotalLocalizado"]

    for t in tipos.values():
        t["PercentualCalculado"] = (t["Total"] / total_geral) * 100
        t["Status"] = calcular_status(t["PercentualCalculado"], t["PercentualLimite"])

    return list(tipos.values()), list(segmentos.values()), ativos
'''