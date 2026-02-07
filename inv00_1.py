'''
Programa de Validar Dados
JC 01/2026
Ver 1

'''
def validar_campos(cod, desc, perc, seg):

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
