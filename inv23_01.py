'''
Programa de Analise de Ativos
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv04
Módulo: inv23_01.py
'''

# ============================================================
# PROGRAMA DE ANÁLISE DE ATIVOS
# ============================================================
import tkinter as tk
from tkinter import ttk, messagebox
import inv00_0
import inv00_1

COR_VERDE = "VERDE"
COR_AMARELO = "AMARELO"
COR_VERMELHO = "VERMELHO"

# ============================================================
# JANELA DE AGUARDE
# ============================================================
def executar_analise(root):
    janela = mostrar_aguarde(root)
    root.after(100, lambda: processar_analise(root, janela))

def mostrar_aguarde(root):
    win = tk.Toplevel(root)
    win.title("Aguarde")
    win.resizable(False, False)
    centralizar(win, 300, 150)

    tk.Label(win, text="Pesquisando dados...\nPor favor, aguarde.",
             font=("Arial", 12)).pack(pady=10)

    barra = ttk.Progressbar(win, mode="indeterminate", length=250)
    barra.pack(pady=10)
    barra.start(10)

    win.update()
    return win

def centralizar(janela, w, h):
    janela.update_idletasks()
    sw = janela.winfo_screenwidth()
    sh = janela.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    janela.geometry(f"{w}x{h}+{x}+{y}")

def processar_analise(root, aguarde):
    tipos, segmentos, ativos = obter_dados()
    aguarde.destroy()
    abrir_grids(tipos, segmentos, ativos)

# ============================================================
# PROCESSAMENTO PRINCIPAL
# ============================================================
def obter_dados():
    linhas = inv00_0.buscar_ativos_pagadores()
    if not linhas:
        return [], [], []

    ativos = []
    tickers = [inv00_1.ajustar_ticker(r["Inv02_06"], r["Inv02_17"])
               for r in linhas if r["Inv02_22"] == "S"]

    cotacoes = inv00_1.obter_cotacoes_em_lote(tickers)

    for r in linhas:
        qtd = r["Inv02_07"]
        if qtd <= 0:
            continue

        exterior = r["Inv02_17"]
        usa_cotacao = r["Inv02_22"] == "S"
        ticker = inv00_1.ajustar_ticker(r["Inv02_06"], exterior)
        preco = cotacoes.get(ticker, 0.0)

        moeda = "USD" if exterior == "S" else "BRL"
        fx = inv00_1.obter_cotacao_moeda(moeda)

        if usa_cotacao and preco and preco > 0:
            valor_unit = preco * fx
            total = valor_unit * qtd
            fallback = False
        else:
            custo = float(r["Inv02_10"]) * fx if exterior == "S" else float(r["Inv02_09"])
            total = custo
            valor_unit = custo / qtd
            fallback = True

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
            "Cotacao": preco,
            "Quantidade": qtd,
            "ValorUnitario": valor_unit,
            "TotalLocalizado": total,
            "ValorFallback": fallback
        }
        ativos.append(ativo)

    total_geral = sum(a["TotalLocalizado"] for a in ativos)

    # ---------------- TIPO ----------------
    tipos = {}
    for a in ativos:
        t = a["CodigoTipo"]
        tipos.setdefault(t, {
            "Codigo": t,
            "Descricao": a["DescricaoTipo"],
            "Total": 0,
            "PercentualLimite": a["PercentualLimiteTipo"]
        })
        tipos[t]["Total"] += a["TotalLocalizado"]

    for t in tipos.values():
        t["PercentualCalculado"] = (t["Total"] / total_geral) * 100
        t["Status"] = inv00_1.calcular_status(t["PercentualCalculado"], t["PercentualLimite"])

    # ---------------- SEGMENTO ----------------
    segmentos = {}
    for a in ativos:
        s = a["CodigoSegmento"]
        segmentos.setdefault(s, {
            "Codigo": s,
            "Descricao": a["DescricaoSegmento"],
            "CodigoTipo": a["CodigoTipo"],
            "Total": 0,
            "PercentualLimite": a["PercentualLimiteSegmento"]
        })
        segmentos[s]["Total"] += a["TotalLocalizado"]

    for s in segmentos.values():
        total_tipo = tipos[s["CodigoTipo"]]["Total"]
        s["PercentualCalculado"] = (s["Total"] / total_tipo) * 100
        s["Status"] = inv00_1.calcular_status(s["PercentualCalculado"], s["PercentualLimite"])

        st_tipo = tipos[s["CodigoTipo"]]["Status"]
        if st_tipo == COR_VERMELHO:
            s["Status"] = COR_VERMELHO
        elif st_tipo == COR_AMARELO and s["Status"] == COR_VERDE:
            s["Status"] = COR_AMARELO

    # ---------------- ATIVOS ----------------
    for a in ativos:
        total_seg = segmentos[a["CodigoSegmento"]]["Total"]
        a["PercentualCalculado"] = (a["TotalLocalizado"] / total_seg) * 100

        st_calc = inv00_1.calcular_status(a["PercentualCalculado"], a["PercentualLimiteAtivo"])
        st_tipo = tipos[a["CodigoTipo"]]["Status"]
        st_seg = segmentos[a["CodigoSegmento"]]["Status"]

        if a["PercentualCalculado"] >= 99.999:
            a["Status"] = st_seg
        elif inv00_1.eh_manter(st_tipo):
            a["Status"] = COR_VERMELHO
        elif inv00_1.eh_compra(st_tipo) and inv00_1.eh_manter(st_seg):
            a["Status"] = COR_VERMELHO
        else:
            a["Status"] = st_calc

        a["StatusAtivoOriginal"] = st_calc

    return list(tipos.values()), list(segmentos.values()), ativos

# ============================================================
# GRIDS
# ============================================================

def abrir_grids(tipos, segmentos, ativos):
    if not ativos:
        messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
        return

    win = tk.Toplevel()
    win.title("Análise de Ativos")
    win.geometry("1500x750")

    top = tk.Frame(win)
    top.pack(fill="x")

    tk.Button(top, text="Retornar", font=("Arial", 12),
              command=win.destroy).pack(side="right", padx=10, pady=10)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True)

    # Criar Grids
    criar_grid_tipos(notebook, tipos)
    criar_grid_segmentos(notebook, segmentos)
    criar_grid_ativos(notebook, ativos)

    tk.Label(win, text="* Valor baseado no custo investido (cotação indisponível)",
             fg="gray", font=("Arial", 10)).pack(anchor="w", padx=10, pady=5)

# ============================================================
# GRID TIPO
# ============================================================
def criar_grid_tipos(notebook, tipos):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Tipos")

    cols = ("Codigo", "Descricao", "Total", "%Limite", "%Calc", "Status")
    tree = ttk.Treeview(frame, columns=cols, show="headings")

    inv00_1.configurar_colunas(tree, {
        "Codigo": (80, "center"),
        "Descricao": (250, "w"),
        "Total": (120, "e"),
        "%Limite": (80, "center"),
        "%Calc": (80, "center"),
        "Status": (90, "center")
    })

    inv00_1.configurar_tags(tree)

    for t in tipos:
        st = t["Status"]
        tree.insert("", tk.END, values=(
            t["Codigo"],
            t["Descricao"],
            inv00_1.brstilo(t["Total"]),
            inv00_1.brstilo(t["PercentualLimite"]),
            inv00_1.brstilo(t["PercentualCalculado"]),
            inv00_1.traduzir_status(st)
        ), tags=(st,))

    tree.pack(fill="both", expand=True)

# ============================================================
# GRID SEGMENTO
# ============================================================
def criar_grid_segmentos(notebook, segmentos):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Segmentos")

    cols = ("Codigo", "Descricao", "Total", "%Limite", "%Calc", "Status")
    tree = ttk.Treeview(frame, columns=cols, show="headings")

    inv00_1.configurar_colunas(tree, {
        "Codigo": (80, "center"),
        "Descricao": (250, "w"),
        "Total": (120, "e"),
        "%Limite": (80, "center"),
        "%Calc": (80, "center"),
        "Status": (90, "center")
    })

    inv00_1.configurar_tags(tree)

    for s in segmentos:
        st = s["Status"]
        tree.insert("", tk.END, values=(
            s["Codigo"],
            s["Descricao"],
            inv00_1.brstilo(s["Total"]),
            inv00_1.brstilo(s["PercentualLimite"]),
            inv00_1.brstilo(s["PercentualCalculado"]),
            inv00_1.traduzir_status(st)
        ), tags=(st,))

    tree.pack(fill="both", expand=True)

# ============================================================
# GRID ATIVO
# ============================================================
def criar_grid_ativos(notebook, ativos):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="Ativos")

    cols = (
        "Codigo", "Descricao", "Segmento", "%Limite", "%Calc",
        "Moeda", "Cotacao", "Quantidade", "ValorTotal",
        "VlrBRL", "TotalBRL", "Status"
    )

    tree = ttk.Treeview(frame, columns=cols, show="headings")

    config = {
        "Codigo": (90, "center"),
        "Descricao": (250, "w"),
        "Segmento": (180, "w"),
        "%Limite": (80, "center"),
        "%Calc": (80, "center"),
        "Moeda": (70, "center"),
        "Cotacao": (100, "e"),
        "Quantidade": (100, "e"),
        "ValorTotal": (120, "e"),
        "VlrBRL": (120, "e"),
        "TotalBRL": (140, "e"),
        "Status": (90, "center")
    }

    for col, (w, anchor) in config.items():
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor=anchor)

    # TAGS GLOBAIS PARA STATUS
    tree.tag_configure("status_verde", foreground="green")
    tree.tag_configure("status_amarelo", foreground="orange")
    tree.tag_configure("status_vermelho", foreground="red")

    # TAGS GLOBAIS PARA LINHA
    tree.tag_configure(COR_VERDE, foreground="green")
    tree.tag_configure(COR_AMARELO, foreground="orange")
    tree.tag_configure(COR_VERMELHO, foreground="red")

    for a in ativos:
        st_final = a["Status"]
        st_original = a["StatusAtivoOriginal"]

        valor_unit = inv00_1.brstilo(a["ValorUnitario"])
        total_brl = inv00_1.brstilo(a["TotalLocalizado"])

        if a["ValorFallback"]:
            valor_unit += " *"
            total_brl += " *"

        valor_total_cotacao = a["Cotacao"] * a["Quantidade"]

        # 1) Insere a linha com a cor da linha original
        item = tree.insert(
            "",
            tk.END,
            values=(
                a["CodigoAtivo"],
                a["DescricaoAtivo"],
                a["DescricaoSegmento"],
                inv00_1.brstilo(a["PercentualLimiteAtivo"]),
                inv00_1.brstilo(a["PercentualCalculado"]),
                a["Moeda"],
                inv00_1.brstilo(a["Cotacao"]),
                a["Quantidade"],
                inv00_1.brstilo(valor_total_cotacao),
                valor_unit,
                total_brl,
                inv00_1.traduzir_status(st_final)
            ),
            tags=(st_original,)  # mantém cor da linha
        )

        # 2) Aplica cor da coluna Status usando tags globais
        if st_final == COR_VERDE:
            tree.item(item, tags=(st_original, "status_verde"))
        elif st_final == COR_AMARELO:
            tree.item(item, tags=(st_original, "status_amarelo"))
        else:
            tree.item(item, tags=(st_original, "status_vermelho"))

    tree.pack(fill="both", expand=True)

