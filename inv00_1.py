'''
Rotinas Diversas
JC 01/2026
Ver 1

'''
import yfinance as yf
import tkinter as tk
from tkinter import ttk


def validar_campos(cod, desc, seg, perc):

    # Campos obrigatórios
    if not cod:
        return False, "Código não pode estar vazio.", "cod"

    if not desc:
        return False, "Descrição não pode estar vazia.", "desc"

    if not perc:
        return False, "Percentual não pode estar vazio.", "perc"

    # Validação do percentual
    try:
        perc_val = float(perc.replace(",", "."))
    except ValueError:
        return False, "Percentual deve ser um número.", "perc"

    if perc_val < 0 or perc_val > 100:
        return False, "Percentual deve estar entre 0 e 100.", "perc"

    # Validação do campo segmento
    if seg not in ("S", "N"):
        return False, "Requer Segmento deve ser S ou N.", "seg"

    # Tudo OK
    return True, "", ""

def validar_campos_inv01(cod, desc, atv, per):

    # Campos obrigatórios
    if not cod:
        return False, "Código não pode estar vazio.", "cod"

    if not desc:
        return False, "Descrição não pode estar vazia.", "desc"

    if not atv:
        return False, "Tipo de Ativo não pode estar vazio.", "atv"

    if not per:
        return False, "Percentual não pode estar vazio.", "per"

     # Tudo OK
    return True, "", ""

def validar_campos_inv02(cod, desc, tipo, segm, atv, data, peri):

    # Campos obrigatórios
    if not cod:
        return False, "Código não pode estar vazio.", "cod"

    if not desc:
        return False, "Descrição não pode estar vazia.", "desc"

    if not tipo:
        return False, "Tipo Ativo não pode estar vazio.", "tipo"

    if not segm:
        return False, "Segmento do Ativo não pode estar vazia.", "segm"

    if not atv:
        return False, "Ativo no Exterior não pode estar vazio.", "atv"

    if not data:
        return False, "Data não pode estar vazia.", "data"

    if not peri:
        return False, "Percentual a Investir não pode estar vazio.", "peri"

    # Tudo OK
    return True, "", ""


def validar_campos_inv03(reg):
  
    # Código
    if not reg["INV03_06"]:
        return "Código não pode ser vazio."

    # Descrição
    if not reg["INV03_02"]:
        return "Descrição não pode ser vazia."

    # Tipo de movimento
    if reg["INV03_12"] not in ("C", "D", "V"):
        return "Tp Mov. deve ser C, D ou V."

    # Quantidade
    try:
        if float(reg["INV03_07"]) <= 0:
            return "Quantidade deve ser maior que zero."
    except:
        return "Quantidade inválida."
    
    #Data
    if not reg["INV03_18"]:
        return "Data não pode ser vazia."

    # Se chegou até aqui, está tudo ok
    return None

# ============================================================
#   FUNÇÕES DE CONVERSÃO DE DATAS
# ============================================================
def br_para_iso_compacto(data_br):
    """
    Converte DD/MM/AAAA → AAAAMMDD
    """
    if not data_br:
        return None
    d, m, a = data_br.split("/")
    return f"{a}{m}{d}"

def iso_compacto_para_br(data_iso):
    """
    Converte AAAAMMDD → DD/MM/AAAA
    """
    if not data_iso:
        return ""
    return f"{data_iso[6:8]}/{data_iso[4:6]}/{data_iso[0:4]}"

# ============================================================
#   FUNÇÕES DE CONVERSÃO PONTOS E VIRGULAS
# ============================================================
def brstilo(num):
    return f"{num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

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
# BUSCA DE COTAÇÕES
# ============================================================
def obter_valor_atual(codigo, exterior="N"):
    """
    Retorna o valor atual do ativo usando yfinance.
    Usa ajustar_ticker para garantir o formato correto.
    """

    # Ajusta o ticker conforme nacional/exterior
    ticker = ajustar_ticker(codigo, exterior)

    if not ticker:
        return None

    try:
        yf_ticker = yf.Ticker(ticker)

        # Fast info é mais rápido e leve
        info = yf_ticker.fast_info
        preco = info.get("last_price")

        # Se não tiver last_price, tenta pegar o fechamento do último dia
        if preco is None:
            hist = yf_ticker.history(period="1d")
            if not hist.empty:
                preco = hist["Close"].iloc[-1]

        return float(preco) if preco is not None else None

    except Exception as e:
        print(f"Erro ao obter cotação de {ticker}: {e}")
        return None
    
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
# MENSAGENS
# ============================================================
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
