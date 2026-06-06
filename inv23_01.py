"""
Programa de Analise de Ativos
Tela Inicial 
JC Mar/2026
Ver 1
Banco de Dados inv.db
Tabela inv04
Módulo: inv23_01.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import yfinance as yf  # mantido se usado em outros módulos
import inv00_0
import inv00_1

COR_VERDE = "VERDE"      # abaixo do limite → COMPRA
COR_AMARELO = "AMARELO"  # próximo do limite → NEUTRO
COR_VERMELHO = "VERMELHO"  # acima do limite → MANTER

# ============================================================
# JANELA DE AGUARDE
# ============================================================
def executar_analise(root):
    aguarde = mostrar_aguarde(root)

    # Executa a análise em thread separado
    threading.Thread(
        target=lambda: processar_analise(root, aguarde),
        daemon=True
    ).start()

def processar_analise(root, aguarde):
    # Tarefa pesada (roda fora do Tkinter)
    tipos, segmentos, ativos = obter_dados()

    # Volta para o Tkinter (thread principal)
    root.after(0, lambda: finalizar_analise(aguarde, tipos, segmentos, ativos))

def finalizar_analise(aguarde, tipos, segmentos, ativos):
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
# PROCESSAMENTO PRINCIPAL
# ============================================================
def obter_dados():
    linhas = inv00_0.buscar_ativos()
    if not linhas:
        return [], [], []

    ativos = []
    tickers = []

    # --------------------------------------------------------
    # COLETA DE TICKERS QUE USAM COTAÇÃO
    # --------------------------------------------------------
    for r in linhas:
        if r["Inv02_22"] == "S":
            tickers.append(inv00_1.ajustar_ticker(r["Inv02_06"], r["Inv02_17"]))

    cotacoes = inv00_1.obter_cotacoes_em_lote(tickers)

    # --------------------------------------------------------
    # PROCESSA CADA ATIVO
    # --------------------------------------------------------
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

        # --------------------------------------------------------
        # LÓGICA DE FALLBACK (cotação inválida → custo investido)
        # --------------------------------------------------------
        cotacao_valida = preco_original is not None and preco_original > 0

        if usa_cotacao and cotacao_valida:
            valor_unit_brl = preco_original * cotacao_moeda
            total_brl = valor_unit_brl * qtd
            valor_fallback = False
            total_aquis = custo_brl
            valoriza = ((total_brl/custo_brl) - 1) * 100 
        else:
            if exterior == "S":
                total_brl = custo_usd * cotacao_moeda
                total_aquis = custo_usd
                valoriza = ((total_aquis/custo_usd) - 1) * 100
            else:
                total_brl = custo_brl
                total_aquis = custo_brl
                valoriza = ((total_brl/custo_brl) - 1) * 100 

            valor_unit_brl = total_brl / qtd if qtd > 0.0 else 0.0
            valor_fallback = True  # valor baseado em custo, não em cotação

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
            "ValorAquis": total_aquis,
            "TotalLocalizado": total_brl,
            "TotalLimite": 0.00,
            "Valorizacao": valoriza,

            "AtivoExterior": exterior,
            "ValorFallback": valor_fallback,
        }

        ativos.append(ativo)

    # --------------------------------------------------------
    # CÁLCULO DE TOTAIS GERAIS
    # --------------------------------------------------------
    total_geral = sum(a["TotalLocalizado"] for a in ativos)

    # --------------------------------------------------------
    # AGREGAÇÃO POR TIPO
    # --------------------------------------------------------
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
        t["PercentualCalculado"] = (t["Total"] / total_geral) * 100 if total_geral > 0 else 0
        t["StatusTipo"] = inv00_1.calcular_status(t["PercentualCalculado"], t["PercentualLimite"])
        t["TotalLimTipo"] = total_geral * t["PercentualLimite"] / 100

    # --------------------------------------------------------
    # AGREGAÇÃO POR SEGMENTO
    # --------------------------------------------------------
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
                "TotalLim": 0.0,
            }
        segmentos[seg]["Total"] += a["TotalLocalizado"]

    for s in segmentos.values():
        total_tipo = tipos[s["CodigoTipo"]]["Total"]
        s["PercentualCalculado"] = (s["Total"] / total_tipo) * 100 if total_tipo > 0 else 0
        s["StatusSeg"] = inv00_1.calcular_status(s["PercentualCalculado"], s["PercentualLimite"])
        s["TotalLim"] += total_tipo * s["PercentualLimite"] / 100

    # --------------------------------------------------------
    # CÁLCULO DOS PERCENTUAIS E STATUS DOS ATIVOS
    # COM LÓGICA HIERÁRQUICA (TIPO → SEGMENTO → ATIVO)
    # --------------------------------------------------------
    for a in ativos:
        total_segmento = segmentos[a["CodigoSegmento"]]["Total"]
        a["PercentualCalculado"] = (a["TotalLocalizado"] / total_segmento) * 100 if total_segmento > 0 else 0
        a["TotalLimite"] = total_segmento * a["PercentualLimiteAtivo"] / 100

        # Status calculado originalmente do ativo 
        a["StatusAtivo"] = inv00_1.calcular_status(a["PercentualCalculado"], a["PercentualLimiteAtivo"])
        # Carrega Status do Tipo e Segmento
        a["StatusTipo"] = tipos[a["CodigoTipo"]]["StatusTipo"]
        a["StatusSeg"]  = segmentos[a["CodigoSegmento"]]["StatusSeg"]
        # --------------------------------------------------------
        # REGRA ESPECIAL: ativo = 100% do segmento → herda o status do segmento
        # --------------------------------------------------------
        if a["PercentualCalculado"] >= 99.999:  # tolerância para floats
            a["Status"] = a["StatusSeg"]

        # --------------------------------------------------------
        # REGRA 1: Tipo = Manter → tudo abaixo Manter
        # --------------------------------------------------------
        elif inv00_1.eh_manter(a["StatusTipo"]):
            a["Status"] = COR_VERMELHO

        # --------------------------------------------------------
        # REGRA 2: Tipo = Compra e Segmento = Manter → ativo Manter
        # --------------------------------------------------------
        elif inv00_1.eh_compra(a["StatusTipo"]) and inv00_1.eh_manter(a["StatusSeg"]):
            a["Status"] = COR_VERMELHO

        # --------------------------------------------------------
        # REGRA 3: Tipo = Compra e Segmento = Compra → ativo segue seu cálculo
        # --------------------------------------------------------
        else:
            a["Status"] = a["StatusAtivo"]

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
    janela.geometry("1600x750")

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

    cols_tipos = ("Codigo", "Descricao", "Total", "%Calc", "TotalLim", "%Limite", "Status")
    tree_tipos = ttk.Treeview(frame_tipos, columns=cols_tipos, show="headings")

    tree_tipos.heading("Codigo", text="Codigo")
    tree_tipos.column("Codigo", width=80, anchor="center")

    tree_tipos.heading("Descricao", text="Descricao")
    tree_tipos.column("Descricao", width=250, anchor="w")

    tree_tipos.heading("Total", text="Total")
    tree_tipos.column("Total", width=120, anchor="e")

    tree_tipos.heading("%Calc", text="%Calc")
    tree_tipos.column("%Calc", width=80, anchor="center")

    tree_tipos.heading("TotalLim", text="Total Limite")
    tree_tipos.column("TotalLim", width=120, anchor="e")

    tree_tipos.heading("%Limite", text="%Limite")
    tree_tipos.column("%Limite", width=80, anchor="center")

    tree_tipos.heading("Status", text="Status")
    tree_tipos.column("Status", width=90, anchor="center")

    tree_tipos.tag_configure("PRETO", foreground="black")
    tree_tipos.tag_configure("VERDE", foreground="green")
    tree_tipos.tag_configure("AMARELO", foreground="orange")
    tree_tipos.tag_configure("VERMELHO", foreground="red")

    for t in tipos:
        status = t["StatusTipo"]
        tree_tipos.insert(
            "",
            tk.END,
            values=(
                t["Codigo"],
                t["Descricao"],
                inv00_1.brstilo(t['Total']),
                inv00_1.brstilo(t['PercentualCalculado']),                
                inv00_1.brstilo(t['TotalLimTipo']),
                inv00_1.brstilo(t['PercentualLimite']),
                inv00_1.traduzir_status(status),
            ),
            tags=(status,)
        )

    tree_tipos.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # GRID SEGMENTOS
    # --------------------------------------------------------
    frame_seg = ttk.Frame(notebook)
    notebook.add(frame_seg, text="Segmentos")

    cols_seg = ("Codigo", "Descricao", "Total", "%Calc", "Valor Limite", "%Limite", "Status")
    tree_seg = ttk.Treeview(frame_seg, columns=cols_seg, show="headings")

    tree_seg.heading("Codigo", text="Codigo")
    tree_seg.column("Codigo", width=80, anchor="center")

    tree_seg.heading("Descricao", text="Descricao")
    tree_seg.column("Descricao", width=250, anchor="w")

    tree_seg.heading("Total", text="Valor Total")
    tree_seg.column("Total", width=120, anchor="e")

    tree_seg.heading("%Limite", text="%Limite")
    tree_seg.column("%Limite", width=80, anchor="center")

    tree_seg.heading("Valor Limite", text="Valor Limite")
    tree_seg.column("Valor Limite", width=100, anchor="e")

    tree_seg.heading("%Calc", text="%Calc")
    tree_seg.column("%Calc", width=80, anchor="center")

    tree_seg.heading("Status", text="Status")
    tree_seg.column("Status", width=90, anchor="center")

    tree_seg.tag_configure("PRETO", foreground="black")
    tree_seg.tag_configure("VERDE", foreground="green")
    tree_seg.tag_configure("AMARELO", foreground="orange")
    tree_seg.tag_configure("VERMELHO", foreground="red")

    for s in segmentos:
        status = s["StatusSeg"]
        tree_seg.insert(
            "",
            tk.END,
            values=(
                s["Codigo"],
                s["Descricao"],
                inv00_1.brstilo(s['Total']),
                inv00_1.brstilo(s['PercentualCalculado']),
                inv00_1.brstilo(s['TotalLim']),          
                inv00_1.brstilo(s['PercentualLimite']),
                inv00_1.traduzir_status(status),
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
        "Codigo", "Descricao", "Segmento", "Quantidade", "ValorTotal", "%Calc", 
        "TotalLimite", "%Limite", "Moeda", "Cotacao", "VlrBRL", "TotalBRL", "Aquisicao",
        "Valorizacao","Status"
    )

    tree = ttk.Treeview(frame_ativos, columns=colunas, show="headings")

    tree.heading("Codigo", text="Codigo")
    tree.column("Codigo", width=90, anchor="center")

    tree.heading("Descricao", text="Descricao")
    tree.column("Descricao", width=250, anchor="w")

    tree.heading("Segmento", text="Segmento")
    tree.column("Segmento", width=180, anchor="w")

    tree.heading("Quantidade", text="Quantidade")
    tree.column("Quantidade", width=80, anchor="e")

    tree.heading("ValorTotal", text="ValorTotal")
    tree.column("ValorTotal", width=120, anchor="e")

    tree.heading("%Calc", text="%Calc")
    tree.column("%Calc", width=80, anchor="center")

    tree.heading("TotalLimite", text="Valor Limite")
    tree.column("TotalLimite", width=100, anchor="e")

    tree.heading("%Limite", text="%Limite")
    tree.column("%Limite", width=80, anchor="center")

    tree.heading("Moeda", text="Moeda")
    tree.column("Moeda", width=60, anchor="center")

    tree.heading("Cotacao", text="Cotacao")
    tree.column("Cotacao", width=80, anchor="e")

    tree.heading("VlrBRL", text="Cotação BRL")
    tree.column("VlrBRL", width=80, anchor="e")

    tree.heading("TotalBRL", text="TotalBRL")
    tree.column("TotalBRL", width=100, anchor="e")

    tree.heading("Aquisicao", text="VlrAquis.")
    tree.column("Aquisicao", width=100, anchor="e")

    tree.heading("Valorizacao", text="% Valoriza.")
    tree.column("Valorizacao", width=90, anchor="e")

    tree.heading("Status", text="Status")
    tree.column("Status", width=80, anchor="center")

    # cores da linha (status do ativo final)
    tree.tag_configure("PRETO", foreground="black")
    tree.tag_configure("VERDE", foreground="green")
    tree.tag_configure("AMARELO", foreground="orange")
    tree.tag_configure("VERMELHO", foreground="red")

    tree.tag_configure("STATUS_VERDE", foreground="green")
    tree.tag_configure("STATUS_AMARELO", foreground="orange")
    tree.tag_configure("STATUS_VERMELHO", foreground="red")

    for a in ativos:
        status_final = a["Status"]
        status_original = a["StatusAtivo"]

        valor_unit = inv00_1.brstilo(a['ValorUnitario'])
        total_brl = inv00_1.brstilo(a['TotalLocalizado'])

        # Apenas adiciona o * — NÃO envolve o insert
        if a["ValorFallback"]:
            valor_unit = f"{valor_unit} *"
            total_brl = f"{total_brl} *"

        # Tag da linha (cor do ativo real)
        tag_linha = status_original

        # Tag da coluna STATUS (cor do status final)
        if status_final == COR_VERDE:
            tag_status = "STATUS_VERDE"
        elif status_final == COR_AMARELO:
            tag_status = "STATUS_AMARELO"
        else:
            tag_status = "STATUS_VERMELHO"

        tree.insert(
            "",
            tk.END,
            values=(
                a["CodigoAtivo"],
                a["DescricaoAtivo"],
                a["DescricaoSegmento"],
                a["Quantidade"],
                inv00_1.brstilo(a['ValorTotalCotacao']),
                inv00_1.brstilo(a['PercentualCalculado']),
                inv00_1.brstilo(a["TotalLimite"]),
                inv00_1.brstilo(a["PercentualLimiteAtivo"]),
                a["Moeda"],
                inv00_1.brstilo(a['Cotacao']),
                valor_unit,
                total_brl,
                inv00_1.brstilo(a['ValorAquis']),
                inv00_1.brstilo(a['Valorizacao']),
                inv00_1.traduzir_status(status_final)
            ),
            tags=(tag_linha, tag_status)
        )

    tree.pack(fill="both", expand=True)

    # --------------------------------------------------------
    # LEGENDA DO RODAPÉ
    # --------------------------------------------------------
    legenda = tk.Label(
        janela,
        text="* Valor baseado no custo investido (cotação indisponível)",
        font=("Arial", 10),
        fg="gray"
    )
    legenda.pack(anchor="w", padx=10, pady=5)