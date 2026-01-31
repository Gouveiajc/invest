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
