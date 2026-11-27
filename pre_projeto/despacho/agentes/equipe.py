from collections import deque

from maspy import Agent, Any, Belief, Goal, gain, pl, tell

from ..ambiente import calcular_rota
from ..cenario import CANAL, MAPA


class Equipe(Agent):
    def __init__(self, dados):
        super().__init__(dados.id, max_intentions=1)
        self.dados = dados
        self.rota = deque()
        self.rota_proposta = None

    @pl(gain, Goal("calcular_rota", (Any, Any, Any)))
    def propor(self, origem_mensagem, pedido):
        id_chamado, destino, rodada = pedido
        self.perceive(MAPA)
        posicao = self.get(Belief("posicao", (self.my_name, Any, Any)), ck_src=False)
        mapa = self.get(Belief("mapa", (Any, Any, Any)), ck_src=False)
        largura, altura, paredes = mapa.values

        # A rota em curso continua intacta durante a consulta.
        espera = len(self.rota)
        origem = self.rota[-1] if espera else posicao.values[1:]
        rota = calcular_rota(origem, destino, largura, altura, paredes)
        self.rota_proposta = id_chamado, rodada, rota
        passos = -1 if rota is None else len(rota)

        proposta = Belief("proposta", (id_chamado, rodada, espera, passos))
        self.send(origem_mensagem, tell, proposta, CANAL)

    @pl(gain, Goal("assumir", (Any, Any)))
    def assumir(self, origem_mensagem, pedido):
        id_chamado, rodada = pedido
        passos = -1
        if not self.rota and self.rota_proposta is not None:
            id_proposto, rodada_proposta, rota = self.rota_proposta
            if (id_proposto, rodada_proposta) == (id_chamado, rodada) and rota is not None:
                self.rota = deque(rota)
                self.rota_proposta = None
                passos = len(rota)

        confirmacao = Belief("confirmacao_despacho", (id_chamado, rodada, passos))
        self.send(origem_mensagem, tell, confirmacao, CANAL)

    @pl(gain, Goal("avancar", (Any, Any)))
    def avancar(self, origem_mensagem, pedido):
        id_chamado, rodada = pedido
        destino = self.rota.popleft()
        origem = self.mover(destino)

        dados = id_chamado, rodada, origem, destino, len(self.rota)
        self.send(origem_mensagem, tell, Belief("passo_concluido", dados), CANAL)
