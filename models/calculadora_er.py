"""
Calculadora de Estimativa de Requerimento Energético (ER)
Implementação de todas as fórmulas da apostila de Planejamento Alimentar
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class ResultadoER:
    """Resultado do cálculo de ER"""
    categoria: str
    metodo: str
    tmb: float = None
    fator_atividade: float = None
    eer_total: float = None
    detalhes: Dict = None
    
    def __post_init__(self):
        if self.detalhes is None:
            self.detalhes = {}


# ── ADULTOS (19+ ANOS) ──────────────────────────────────────────────────────

def calcular_tmb_harris_benedict(sexo: str, peso: float, altura: float, idade: int) -> float:
    """
    Calcula TMB usando fórmula de Harris & Benedict (1919)
    Válida para IMC < 40 kg/m²
    
    sexo: 'homem' ou 'mulher'
    peso: em kg
    altura: em cm
    idade: em anos
    """
    if sexo.lower() == 'homem':
        tmb = 66 + (13.7 * peso) + (5 * altura) - (6.8 * idade)
    else:  # mulher
        tmb = 655 + (9.6 * peso) + (1.7 * altura) - (4.7 * idade)
    
    return round(tmb, 2)


def calcular_tmb_dri(sexo: str, peso: float, altura: float, idade: int) -> float:
    """
    Calcula TMB usando fórmula DRI (2002)
    Válida para IMC < 40 kg/m²
    Mais precisa que Harris & Benedict
    
    sexo: 'homem' ou 'mulher'
    peso: em kg
    altura: em metros
    idade: em anos
    """
    if sexo.lower() == 'homem':
        tmb = 293 - (3.8 * idade) + (456.4 * altura) + (10.12 * peso)
    else:  # mulher
        tmb = 247 - (2.67 * idade) + (401.5 * altura) + (8.6 * peso)
    
    return round(tmb, 2)


def calcular_eer_adulto_dri(sexo: str, peso: float, altura: float, idade: int, 
                             atividade: str) -> Tuple[float, float, float]:
    """
    Calcula EER para adultos usando DRI (2002)
    Retorna: (TMB, fator_atividade, EER)
    
    sexo: 'homem' ou 'mulher'
    peso: em kg
    altura: em metros
    idade: em anos
    atividade: 'sedentario', 'leve', 'moderado', 'intenso'
    """
    
    # Coeficientes de Atividade Física
    caf_tabela = {
        'sedentario': {'homem': 1.00, 'mulher': 1.00},
        'leve': {'homem': 1.11, 'mulher': 1.12},
        'moderado': {'homem': 1.25, 'mulher': 1.27},
        'intenso': {'homem': 1.45, 'mulher': 1.45},
    }
    
    caf = caf_tabela[atividade.lower()][sexo.lower()]
    
    # Calcula TMB primeiro
    tmb = calcular_tmb_dri(sexo, peso, altura, idade)
    
    # Fórmula EER
    if sexo.lower() == 'homem':
        eer = 662 - (9.53 * idade) + caf * (15.91 * peso + 539.6 * altura)
    else:  # mulher
        eer = 354 - (6.91 * idade) + caf * (9.36 * peso + 726 * altura)
    
    return round(tmb, 2), round(caf, 2), round(eer, 2)


def calcular_eer_adulto_harris_benedict(sexo: str, peso: float, altura: float, 
                                        idade: int, atividade: str) -> Tuple[float, float, float]:
    """
    Calcula EER para adultos usando Harris & Benedict (1919)
    Retorna: (TMB, fator_atividade, EER)
    """
    
    # Fatores de Atividade (FA)
    fa_tabela = {
        'sedentario': 1.2,
        'leve': 1.375,
        'moderado': 1.55,
        'intenso': 1.725,
    }
    
    fa = fa_tabela[atividade.lower()]
    
    # Calcula TMB
    altura_cm = altura * 100  # converte para cm
    tmb = calcular_tmb_harris_benedict(sexo, peso, altura_cm, idade)
    
    # EER = TMB × FA
    eer = tmb * fa
    
    return round(tmb, 2), round(fa, 2), round(eer, 2)


# ── GESTANTES ───────────────────────────────────────────────────────────────

def calcular_eer_gestante(peso: float, altura: float, idade: int, 
                          atividade: str, trimestre: int) -> Dict:
    """
    Calcula EER para gestantes usando DRI (2002)
    
    trimestre: 1, 2 ou 3
    Retorna dicionário com detalhes do cálculo
    """
    
    # Calcula EER base para mulher
    tmb, caf, eer_base = calcular_eer_adulto_dri('mulher', peso, altura, idade, atividade)
    
    # Adiciona incrementos por trimestre
    incrementos = {
        1: {'gasto': 0, 'armazenamento': 0},
        2: {'gasto': 160, 'armazenamento': 180},  # 8 kcal/semana × 20 semanas
        3: {'gasto': 272, 'armazenamento': 180},  # 8 kcal/semana × 34 semanas
    }
    
    inc = incrementos[trimestre]
    incremento_total = inc['gasto'] + inc['armazenamento']
    eer_final = eer_base + incremento_total
    
    return {
        'tmb': tmb,
        'eer_base': eer_base,
        'trimestre': trimestre,
        'incremento_gasto': inc['gasto'],
        'incremento_armazenamento': inc['armazenamento'],
        'incremento_total': incremento_total,
        'eer_final': round(eer_final, 2),
        'detalhes': f"EER base: {eer_base:.0f} + {incremento_total:.0f} kcal (trimestre {trimestre}) = {eer_final:.0f} kcal"
    }


# ── LACTANTES ───────────────────────────────────────────────────────────────

def calcular_eer_lactante(peso: float, altura: float, idade: int, 
                          atividade: str, mes_lactacao: int) -> Dict:
    """
    Calcula EER para lactantes usando DRI (2002)
    
    mes_lactacao: 1, 2, 3, ...
    Retorna dicionário com detalhes do cálculo
    """
    
    # Calcula EER base para mulher
    tmb, caf, eer_base = calcular_eer_adulto_dri('mulher', peso, altura, idade, atividade)
    
    # Adiciona incrementos por mês
    if mes_lactacao == 1:
        consumo_energia = 500  # kcal produção de leite
        mobilizacao = 170      # kcal mobilizadas do corpo
    else:  # 2º mês em diante
        consumo_energia = 400
        mobilizacao = 0
    
    incremento_liquido = consumo_energia - mobilizacao
    eer_final = eer_base + incremento_liquido
    
    return {
        'tmb': tmb,
        'eer_base': eer_base,
        'mes_lactacao': mes_lactacao,
        'consumo_energia': consumo_energia,
        'mobilizacao': mobilizacao,
        'incremento_liquido': incremento_liquido,
        'eer_final': round(eer_final, 2),
        'detalhes': f"EER base: {eer_base:.0f} + {consumo_energia:.0f} - {mobilizacao:.0f} = {eer_final:.0f} kcal"
    }


# ── CRIANÇAS 0-35 MESES ─────────────────────────────────────────────────────

def calcular_eer_bebe(peso: float, idade_meses: int) -> float:
    """
    Calcula EER para bebês 0-35 meses usando DRI (2002)
    
    peso: em kg
    idade_meses: idade em meses
    """
    
    if idade_meses <= 3:
        eer = (89 * peso - 100) + 175
    elif idade_meses <= 6:
        eer = (89 * peso - 100) + 56
    elif idade_meses <= 12:
        eer = (89 * peso - 100) + 22
    else:  # 13-35 meses
        eer = (89 * peso - 100) + 20
    
    return round(max(eer, 0), 2)  # garante que não seja negativo


# ── PRÉ-ESCOLARES E ESCOLARES (3-8 ANOS) ───────────────────────────────────

def calcular_eer_pre_escolar(sexo: str, idade: int, peso: float, 
                             altura: float, atividade: str) -> Tuple[float, float]:
    """
    Calcula EER para pré-escolares/escolares (3-8 anos) usando DRI (2002)
    
    Retorna: (EER, CAF)
    """
    
    caf_tabela = {
        'sedentario': {'menino': 1.00, 'menina': 1.00},
        'leve': {'menino': 1.13, 'menina': 1.16},
        'moderado': {'menino': 1.26, 'menina': 1.31},
        'intenso': {'menino': 1.42, 'menina': 1.56},
    }
    
    caf = caf_tabela[atividade.lower()][sexo.lower()]
    
    if sexo.lower() in ['menino', 'homem']:
        eer = 88.5 - (61.9 * idade) + caf * (26.7 * peso + 903 * altura) + 20
    else:  # menina
        eer = 135.3 - (30.8 * idade) + caf * (10 * peso + 934 * altura) + 20
    
    return round(eer, 2), round(caf, 2)


# ── CRIANÇAS E ADOLESCENTES (9-18 ANOS) ─────────────────────────────────────

def calcular_eer_adolescente(sexo: str, idade: int, peso: float, 
                            altura: float, atividade: str) -> Tuple[float, float]:
    """
    Calcula EER para crianças/adolescentes (9-18 anos) usando DRI (2002)
    
    Retorna: (EER, NAF)
    """
    
    naf_tabela = {
        'sedentario': {'masculino': 1.00, 'feminino': 1.00},
        'leve': {'masculino': 1.13, 'feminino': 1.16},
        'moderado': {'masculino': 1.26, 'feminino': 1.31},
        'intenso': {'masculino': 1.42, 'feminino': 1.56},
    }
    
    naf = naf_tabela[atividade.lower()][sexo.lower()]
    
    if sexo.lower() in ['masculino', 'homem']:
        eer = 88.5 - (61.9 * idade) + naf * (26.7 * peso + 903 * altura) + 25
    else:  # feminino
        eer = 135.3 - (30.8 * idade) + naf * (10 * peso + 934 * altura) + 25
    
    return round(eer, 2), round(naf, 2)


# ── IDOSOS (60+ ANOS) ───────────────────────────────────────────────────────

def calcular_eer_idoso_oms(sexo: str, idade: int, peso: float, 
                           atividade: str) -> Tuple[float, float]:
    """
    Calcula EER para idosos usando fórmulas OMS (1985)
    
    Retorna: (TMB, GET)
    """
    
    fator_atividade = {
        'leve': {'homem': 1.4, 'mulher': 1.4},
        'moderada': {'homem': 1.6, 'mulher': 1.6},
        'intensa': {'homem': 1.9, 'mulher': 1.8},
    }
    
    fa = fator_atividade[atividade.lower()][sexo.lower()]
    
    # Seleciona fórmula baseada na faixa etária
    if sexo.lower() == 'homem':
        if idade < 3:
            tmb = (60.9 * peso) - 54
        elif idade < 10:
            tmb = (22.7 * peso) + 495
        elif idade < 18:
            tmb = (17.5 * peso) + 651
        elif idade < 30:
            tmb = (15.3 * peso) + 679
        elif idade < 60:
            tmb = (11.6 * peso) + 879
        else:  # > 60
            tmb = (13.5 * peso) + 487
    else:  # mulher
        if idade < 3:
            tmb = (61 * peso) - 51
        elif idade < 10:
            tmb = (22.5 * peso) + 499
        elif idade < 18:
            tmb = (12.2 * peso) + 746
        elif idade < 30:
            tmb = (14.7 * peso) + 496
        elif idade < 60:
            tmb = (8.7 * peso) + 829
        else:  # > 60
            tmb = (10.5 * peso) + 596
    
    get = tmb * fa
    
    return round(tmb, 2), round(get, 2)


def calcular_eer_idoso_harris_benedict(sexo: str, peso: float, 
                                       altura: float, idade: int, 
                                       atividade: str) -> Tuple[float, float]:
    """
    Calcula EER para idosos usando Harris & Benedict (1919)
    Alternativa mais simples à fórmula OMS
    
    Retorna: (TMB, EER)
    """
    altura_cm = altura * 100
    tmb = calcular_tmb_harris_benedict(sexo, peso, altura_cm, idade)
    
    fa_tabela = {
        'leve': 1.2,
        'moderada': 1.375,
        'intensa': 1.55,
    }
    
    fa = fa_tabela[atividade.lower()]
    eer = tmb * fa
    
    return round(tmb, 2), round(eer, 2)


# ── FUNÇÃO PRINCIPAL ────────────────────────────────────────────────────────

def calcular_er(categoria: str, **dados) -> ResultadoER:
    """
    Função principal para calcular ER baseado na categoria
    
    Categorias: 'adulto', 'gestante', 'lactante', 'bebe', 
                'pre_escolar', 'adolescente', 'idoso'
    """
    
    resultado = ResultadoER(categoria=categoria, metodo='')
    
    try:
        if categoria == 'adulto':
            metodo = dados.get('metodo', 'dri')  # 'dri' ou 'harris_benedict'
            sexo = dados['sexo']
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            idade = int(dados['idade'])
            atividade = dados['atividade']
            
            if metodo == 'dri':
                resultado.metodo = 'DRI-EER (2002)'
                resultado.tmb, resultado.fator_atividade, resultado.eer_total = \
                    calcular_eer_adulto_dri(sexo, peso, altura, idade, atividade)
                resultado.detalhes = {
                    'formula': 'DRI-EER',
                    'tmb': resultado.tmb,
                    'caf': resultado.fator_atividade,
                    'eer': resultado.eer_total
                }
            else:  # harris_benedict
                resultado.metodo = 'Harris & Benedict (1919)'
                resultado.tmb, resultado.fator_atividade, resultado.eer_total = \
                    calcular_eer_adulto_harris_benedict(sexo, peso, altura, idade, atividade)
                resultado.detalhes = {
                    'formula': 'Harris & Benedict',
                    'tmb': resultado.tmb,
                    'fa': resultado.fator_atividade,
                    'eer': resultado.eer_total
                }
        
        elif categoria == 'gestante':
            resultado.metodo = 'DRI-EER Gestação (2002)'
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            idade = int(dados['idade'])
            atividade = dados['atividade']
            trimestre = int(dados['trimestre'])
            
            result_dict = calcular_eer_gestante(peso, altura, idade, atividade, trimestre)
            resultado.eer_total = result_dict['eer_final']
            resultado.detalhes = result_dict
        
        elif categoria == 'lactante':
            resultado.metodo = 'DRI-EER Lactação (2002)'
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            idade = int(dados['idade'])
            atividade = dados['atividade']
            mes = int(dados['mes_lactacao'])
            
            result_dict = calcular_eer_lactante(peso, altura, idade, atividade, mes)
            resultado.eer_total = result_dict['eer_final']
            resultado.detalhes = result_dict
        
        elif categoria == 'bebe':
            resultado.metodo = 'DRI (2002) - Lactentes'
            peso = float(dados['peso'])
            idade_meses = int(dados['idade_meses'])
            
            resultado.eer_total = calcular_eer_bebe(peso, idade_meses)
            resultado.detalhes = {
                'idade_meses': idade_meses,
                'peso': peso,
                'eer': resultado.eer_total
            }
        
        elif categoria == 'pre_escolar':
            resultado.metodo = 'DRI-EER (2002) - Pré-escolar/Escolar'
            sexo = dados['sexo']
            idade = int(dados['idade'])
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            atividade = dados['atividade']
            
            resultado.eer_total, resultado.fator_atividade = \
                calcular_eer_pre_escolar(sexo, idade, peso, altura, atividade)
            resultado.detalhes = {
                'idade': idade,
                'caf': resultado.fator_atividade,
                'eer': resultado.eer_total
            }
        
        elif categoria == 'adolescente':
            resultado.metodo = 'DRI-EER (2002) - Adolescente'
            sexo = dados['sexo']
            idade = int(dados['idade'])
            peso = float(dados['peso'])
            altura = float(dados['altura'])
            atividade = dados['atividade']
            
            resultado.eer_total, resultado.fator_atividade = \
                calcular_eer_adolescente(sexo, idade, peso, altura, atividade)
            resultado.detalhes = {
                'idade': idade,
                'naf': resultado.fator_atividade,
                'eer': resultado.eer_total
            }
        
        elif categoria == 'idoso':
            resultado.metodo = 'OMS (1985) ou Harris & Benedict (1919)'
            metodo = dados.get('metodo', 'oms')
            sexo = dados['sexo']
            idade = int(dados['idade'])
            peso = float(dados['peso'])
            altura = float(dados.get('altura', 1.70))  # altura é opcional
            atividade = dados['atividade']
            
            if metodo == 'oms':
                resultado.metodo = 'OMS (1985)'
                resultado.tmb, resultado.eer_total = \
                    calcular_eer_idoso_oms(sexo, idade, peso, atividade)
            else:  # harris_benedict
                resultado.metodo = 'Harris & Benedict (1919)'
                resultado.tmb, resultado.eer_total = \
                    calcular_eer_idoso_harris_benedict(sexo, peso, altura, idade, atividade)
            
            resultado.detalhes = {
                'tmb': resultado.tmb,
                'eer': resultado.eer_total
            }
    
    except Exception as e:
        resultado.eer_total = None
        resultado.detalhes = {'erro': str(e)}
    
    return resultado
