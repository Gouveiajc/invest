"""Dividendos
Tabela INV04
Módulo: inv24_01.py
Mar/2026
"""
import tkinter as tk
from tkinter import messagebox
import calendar
from datetime import datetime
import yfinance as yf
import inv00_0

import inv23_01
from inv23_01 import ajustar_ticker, obter_cotacao_moeda


# ------------------------------------------------------------
# Centralizar janela
# ------------------------------------------------------------
def centralizar_janela(janela, largura, altura):
    janela.update_idletasks()
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()
    x = (largura_tela // 2) - (largura // 2)
    y = (altura_tela // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")


# ------------------------------------------------------------
# Abrir tela para digitar mês/ano
# ------------------------------------------------------------
def abrir_tela_dividendos(root):
    janela = tk.Toplevel(root)
    janela.title("Buscar Dividendos")
    janela.resizable(False, False)

    centralizar_janela(janela, 300, 180)

    tk.Label(janela, text="Mês (1-12):").pack(pady=5)
    entry_mes = tk.Entry(janela)
    entry_mes.pack()

    tk.Label(janela, text="Ano (YYYY):").pack(pady=5)
    entry_ano = tk.Entry(janela)
    entry_ano.pack()

    tk.Button(
        janela,
        text="Processar",
        command=lambda: executar_dividendos(janela, entry_mes.get(), entry_ano.get())
    ).pack(pady=15)


# ------------------------------------------------------------
# Calcular intervalo do mês
# ------------------------------------------------------------
def calcular_intervalo(mes, ano):
    mes = int(mes)
    ano = int(ano)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    data_inicial = datetime(ano, mes, 1)
    data_final = datetime(ano, mes, ultimo_dia)
    return data_inicial, data_final


# ------------------------------------------------------------
# Função principal
# ------------------------------------------------------------
def executar_dividendos(janela, mes, ano):
    try:
        mes = int(mes)
        ano = int(ano)
    except:
        messagebox.showerror("Erro", "Mês e ano inválidos.")
        return

    data_inicial, data_final = calcular_intervalo(mes, ano)

    # Buscar ativos pagadores (Inv02_22 = 'S')
    ativos = inv00_0.buscar_ativos_pagadores()

    total_registros = 0

    for ativo in ativos:
        codigo_segmento = ativo["CodigoSegmento"]
        codigo_ativo = ativo["CodigoAtivo"]
        quantidade = ativo["Quantidade"]
        ativo_exterior = ativo["AtivoExterior"]

        # Ajustar ticker
        ticker = ajustar_ticker(codigo_ativo, ativo_exterior)

        try:
            yf_t = yf.Ticker(ticker)
            dividendos = yf_t.dividends.loc[data_inicial:data_final]
        except:
            continue

        for data_pagamento, valor in dividendos.items():

            # ------------------------------------------------------------
            # Ativo exterior
            # ------------------------------------------------------------
            if ativo_exterior == "S":
                cotacao_usd = obter_cotacao_moeda("USD")
                valor_usd = float(valor)
                total_usd = valor_usd * quantidade

                valor_rs = valor_usd * cotacao_usd
                total_rs = total_usd * cotacao_usd

            # ------------------------------------------------------------
            # Ativo nacional
            # ------------------------------------------------------------
            else:
                cotacao_usd = 0
                valor_usd = 0
                total_usd = 0

                valor_rs = float(valor)
                total_rs = valor_rs * quantidade

            # ------------------------------------------------------------
            # Montar registro
            # ------------------------------------------------------------
            registro = {
                "CodigoSegmento": codigo_segmento,
                "CodigoAtivo": codigo_ativo,
                "ValorRS": valor_rs,
                "Quantidade": quantidade,
                "TotalRS": total_rs,
                "CotacaoUS": cotacao_usd,
                "ValorUS": valor_usd,
                "TotalUS": total_usd,
                "DataPagamento": data_pagamento.strftime("%Y-%m-%d")
            }

            # ------------------------------------------------------------
            # Verificar existência (ticker + data pagamento)
            # ------------------------------------------------------------
            existe = inv00_0.buscar_dividendo_existente(codigo_ativo, registro["DataPagamento"])

            if existe:
                inv00_0.atualizar_dividendo(registro, existe["Inv04_00"])
            else:
                inv00_0.inserir_dividendo(registro)

            total_registros += 1

    janela.destroy()
    messagebox.showinfo("Concluído", f"Processo finalizado.\nRegistros processados: {total_registros}")
