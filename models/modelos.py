from dataclasses import dataclass, field
from typing import List, Optional


# ── Ranges fixos do sistema (% da kcal da refeição) ──────────────────────────
RANGES = {
    "carboidratos": (0.45, 0.60),
    "proteinas":    (0.10, 0.20),
    "lipideos":     (0.20, 0.30),
}

# Calorias por grama de cada macro
KCAL_POR_GRAMA = {
    "carboidratos": 4,
    "proteinas":    4,
    "lipideos":     9,
}


@dataclass
class Alimento:
    id: Optional[int]
    grupo: str
    descricao: str
    calorias: float      # por 100g
    proteinas: float     # por 100g
    lipideos: float      # por 100g
    carboidratos: float  # por 100g
    fonte: str = "taco"

    def calcular_para(self, quantidade_g: float) -> dict:
        """Retorna os macros para uma dada quantidade em gramas."""
        fator = quantidade_g / 100
        return {
            "calorias":     round(self.calorias     * fator, 2),
            "proteinas":    round(self.proteinas    * fator, 2),
            "lipideos":     round(self.lipideos     * fator, 2),
            "carboidratos": round(self.carboidratos * fator, 2),
        }


@dataclass
class ItemRefeicao:
    alimento: Alimento
    quantidade_g: float
    id: Optional[int] = None  # id na tabela refeicao_alimentos (None se ainda não salvo)

    @property
    def macros(self) -> dict:
        return self.alimento.calcular_para(self.quantidade_g)


@dataclass
class Refeicao:
    nome: str
    percentual: float          # % das kcal diárias (0–100)
    kcal_diaria: float         # kcal total do cardápio (passada pelo cardápio pai)
    itens: List[ItemRefeicao] = field(default_factory=list)
    id: Optional[int] = None
    ordem: int = 0

    @property
    def kcal_refeicao(self) -> float:
        """Kcal teóricas desta refeição."""
        return round(self.kcal_diaria * self.percentual / 100, 2)

    @property
    def ranges_gramas(self) -> dict:
        """Calcula os ranges mínimo/máximo em gramas para cada macro."""
        kcal = self.kcal_refeicao
        result = {}
        for macro, (pct_min, pct_max) in RANGES.items():
            kcal_por_g = KCAL_POR_GRAMA[macro]
            result[macro] = {
                "min": round(kcal * pct_min / kcal_por_g, 2),
                "max": round(kcal * pct_max / kcal_por_g, 2),
            }
        return result

    @property
    def totais(self) -> dict:
        """Soma os macros de todos os itens da refeição."""
        totais = {"calorias": 0.0, "proteinas": 0.0, "lipideos": 0.0, "carboidratos": 0.0}
        for item in self.itens:
            for k, v in item.macros.items():
                totais[k] += v
        return {k: round(v, 2) for k, v in totais.items()}

    @property
    def validacao(self) -> dict:
        """Retorna True/False para cada macro e se a refeição está completamente válida."""
        ranges = self.ranges_gramas
        totais = self.totais
        result = {}
        for macro in ("carboidratos", "proteinas", "lipideos"):
            val = totais[macro]
            r = ranges[macro]
            result[macro] = r["min"] <= val <= r["max"]
        result["valida"] = all(result[m] for m in ("carboidratos", "proteinas", "lipideos"))
        return result


@dataclass
class Cardapio:
    nome: str
    kcal_total: float
    refeicoes: List[Refeicao] = field(default_factory=list)
    id: Optional[int] = None
    data_criacao: Optional[str] = None

    @property
    def soma_percentuais(self) -> float:
        return round(sum(r.percentual for r in self.refeicoes), 2)

    @property
    def todas_validas(self) -> bool:
        return (
            len(self.refeicoes) > 0
            and self.soma_percentuais == 100
            and all(r.validacao["valida"] for r in self.refeicoes)
        )
