from collections import deque

from maspy import Environment, Percept

from .cenario import ALTURA, LARGURA, PAREDES


def vizinhos(posicao, largura, altura, paredes):
    x, y = posicao
    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nx < largura and 0 <= ny < altura and (nx, ny) not in paredes:
            yield nx, ny


def calcular_rota(origem, destino, largura, altura, paredes):
    """Busca em largura pela menor rota válida no mapa percebido."""
    paredes = set(paredes)
    fila = deque([origem])
    anterior = {origem: None}

    while fila:
        atual = fila.popleft()
        if atual == destino:
            caminho = []
            while atual != origem:
                caminho.append(atual)
                atual = anterior[atual]
            return caminho[::-1]

        for vizinho in vizinhos(atual, largura, altura, paredes):
            if vizinho not in anterior:
                anterior[vizinho] = atual
                fila.append(vizinho)

    return None


class Grade(Environment):
    def __init__(self, nome, bases):
        super().__init__(nome)
        self.bases = bases
        self.posicoes = {}
        mapa = LARGURA, ALTURA, tuple(sorted(PAREDES))
        self.create(Percept("mapa", mapa, adds_event=False))

    def on_connect(self, agente):
        base = self.bases[agente.rsplit("_", 1)[0]]
        self.atualizar_posicao(agente, base)

    def atualizar_posicao(self, agente, posicao):
        anterior = self.posicoes.get(agente)
        if anterior is not None:
            self.delete(anterior)

        percepto = Percept("posicao", (agente, *posicao), adds_event=False)
        self.create(percepto)
        self.posicoes[agente] = percepto

    def mover(self, agente, destino):
        origem = self.posicoes[agente].values[1:]
        if destino not in vizinhos(origem, LARGURA, ALTURA, PAREDES):
            raise ValueError(f"Movimento inválido: {origem} -> {destino}")

        self.atualizar_posicao(agente, destino)
        return origem
