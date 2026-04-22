'''
Rotinas Diversas
JC 01/2026
Ver 1

'''
import yfinance as yf

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

