import json
from dataclasses import dataclass
from pathlib import Path


MAPA = "Mapa"
CANAL = "Despacho"
LARGURA, ALTURA = 16, 10
# A divisória central tem passagens nas linhas 2 e 8.
PAREDES = (
    {(7, y) for y in range(ALTURA) if y not in (2, 8)}
    | {(x, 4) for x in range(1, 6) if x != 3}
    | {(x, 6) for x in range(9, 15) if x != 12}
    | {(11, y) for y in range(2, 5)}
)


@dataclass(frozen=True)
class DadosEquipe:
    id: str
    nome: str
    especialidade: str
    integrantes: int
    base: tuple[int, int]


@dataclass
class Chamado:
    id: str
    crime: str
    violencia_domestica: bool
    local: str
    destino: tuple[int, int]
    prioridade: int
    entrada: int
    equipe: str | None = None
    despacho: int | None = None
    chegada: int | None = None

    @property
    def urgente(self):
        return self.prioridade >= 7

    @property
    def nivel(self):
        if self.prioridade == 10:
            return "Crítica"
        if self.urgente:
            return "Alta"
        if self.prioridade >= 4:
            return "Moderada"
        return "Baixa"

    @property
    def status(self):
        if self.chegada is not None:
            return "atendido"
        if self.equipe is not None:
            return "em_deslocamento"
        return "pendente"


def posicao_livre(valores, identificador):
    if len(valores) == 2 and all(type(valor) is int for valor in valores):
        x, y = valores
        if 0 <= x < LARGURA and 0 <= y < ALTURA and (x, y) not in PAREDES:
            return x, y
    raise ValueError(f"{identificador}: posição fora da grade ou em uma parede.")


def carregar_cenario():
    arquivo = Path(__file__).with_name("dados_simulados.json")
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    equipes = [
        DadosEquipe(
            item["id_equipe"], item["nome"], item["especialidade"],
            item["integrantes"], posicao_livre(item["posicao_base"], item["id_equipe"]),
        )
        for item in dados["equipes"]
    ]
    if not equipes or len({equipe.id for equipe in equipes}) != len(equipes):
        raise ValueError("Cadastre equipes com identificadores únicos.")

    chamados = []
    for item in dados["ocorrencias"]:
        id_chamado = item["id_ocorrencia"]
        prioridade, entrada = item["prioridade"], item["instante_chamado"]
        if type(prioridade) is not int or not 1 <= prioridade <= 10:
            raise ValueError(f"{id_chamado}: prioridade deve ser um inteiro de 1 a 10.")
        if type(entrada) is not int or entrada < 0 or item["status"] != "pendente":
            raise ValueError(f"{id_chamado}: informe uma rodada inicial válida e status pendente.")
        chamados.append(Chamado(
            id_chamado, item["crime"], item["violencia_domestica"], item["local"],
            posicao_livre(item["posicao"], id_chamado), prioridade, entrada,
        ))

    if len({chamado.id for chamado in chamados}) != len(chamados):
        raise ValueError("Cada ocorrência precisa ter um identificador único.")
    return equipes, chamados
