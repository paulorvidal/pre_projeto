from collections import deque
from dataclasses import dataclass

from maspy import Admin, Agent, Any, Belief, Goal, achieve, gain, pl

from ..cenario import CANAL


@dataclass(frozen=True)
class Proposta:
    equipe: str
    espera: int
    passos: int

    @property
    def previsao(self):
        return self.espera + self.passos


class Despachante(Agent):
    def __init__(self, chamados, equipes, fifo, terminal, historico=None):
        super().__init__("Despachante", goals=Goal("rodada", 0), max_intentions=1)
        self.chamados = {chamado.id: chamado for chamado in chamados}
        self.equipes = sorted(equipes)
        self.fifo = fifo
        self.rodada = 0
        self.consulta = None
        self.propostas = {}
        self.passos_pendentes = deque()
        self.erro = None
        self.terminal = terminal
        self.historico = historico

    def registrar(self, evento, texto):
        self.terminal.registrar(self.rodada, evento, texto)

    def registrar_decisao(self, texto):
        if self.historico is not None:
            self.historico.registrar_decisao(texto)

    @pl(gain, Goal("rodada", Any))
    def abrir_rodada(self, _origem, rodada):
        self.rodada = rodada

        for chamado in self.chamados.values():
            if chamado.entrada == rodada:
                contexto = "violência doméstica" if chamado.violencia_domestica else "outro contexto"
                self.registrar(
                    "ENTRADA",
                    f"Recepção registrou {chamado.id} em {chamado.destino}: "
                    f"{chamado.crime} em {chamado.local} ({contexto}). "
                    f"Prioridade {chamado.prioridade}/10 ({chamado.nivel}).",
                )

        self.despachar()

    def em_deslocamento(self):
        return [c for c in self.chamados.values() if c.status == "em_deslocamento"]

    def fila_pendente(self):
        fila = [
            c for c in self.chamados.values()
            if c.entrada <= self.rodada and c.status == "pendente"
        ]
        if self.fifo:
            return sorted(fila, key=lambda c: (c.entrada, c.id))
        return sorted(fila, key=lambda c: (-c.prioridade, c.entrada, c.id))

    def despachar(self):
        fila = self.fila_pendente()
        ordem = " -> ".join(f"{c.id} [{c.prioridade}/10]" for c in fila)
        self.registrar("FILA", ordem or "vazia")
        ocupadas = {c.equipe for c in self.em_deslocamento()}

        if fila and len(ocupadas) < len(self.equipes):
            chamado = fila[0]
            self.consulta = chamado
            self.propostas.clear()

            self.registrar(
                "CONSULTA",
                f"Despachante pediu propostas para {chamado.id} a {', '.join(self.equipes)}. "
                "Cada equipe informa quanto falta para liberar e chegar.",
            )
            pedido = Goal("calcular_rota", (chamado.id, chamado.destino, self.rodada))
            self.send(self.equipes, achieve, pedido, CANAL)
            return

        if fila:
            self.registrar(
                "ESPERA",
                f"{fila[0].id} está à frente da fila. Todas as equipes seguem em atendimento.",
            )
        self.encerrar_rodada(fila)

    @pl(gain, Belief("proposta", (Any, Any, Any, Any)))
    def receber_proposta(self, equipe, dados):
        id_chamado, rodada, espera, passos = dados
        chamado = self.consulta
        if chamado is None or (id_chamado, rodada) != (chamado.id, self.rodada):
            return

        self.propostas[equipe] = Proposta(equipe, espera, passos)
        if len(self.propostas) != len(self.equipes):
            return

        validas = []
        for proposta in sorted(self.propostas.values(), key=lambda p: p.equipe):
            if proposta.passos < 0:
                self.registrar("PROPOSTA", f"{proposta.equipe} informa que não encontrou rota para {chamado.id}.")
                continue
            self.registrar(
                "PROPOSTA",
                f"{proposta.equipe} para {chamado.id}: {proposta.espera} para liberar "
                f"+ {proposta.passos} de trajeto = {proposta.previsao} rodadas até chegar.",
            )
            validas.append(proposta)

        if not validas:
            self.encerrar_com_erro(f"Nenhuma equipe tem rota para {chamado.id}.")
            return

        validas.sort(key=lambda p: (p.previsao, p.espera, p.equipe))
        mais_rapida = validas[0]
        livre = next((p for p in validas if p.espera == 0), None)
        if livre is None:
            self.aguardar_liberacao(chamado, mais_rapida)
            return
        if mais_rapida.espera and not chamado.urgente:
            self.aguardar_liberacao(chamado, mais_rapida, livre)
            return

        if chamado.urgente:
            motivo = "prioridade alta ou crítica. Sai a equipe livre com menor rota."
        else:
            motivo = "menor tempo previsto até a chegada entre as propostas."
        self.registrar(
            "DISPUTA",
            f"{livre.equipe} venceu a disputa por {chamado.id} com {livre.previsao} rodadas. Motivo: {motivo}",
        )
        chamado.equipe, chamado.despacho = livre.equipe, self.rodada
        estimativas = " · ".join(f"{p.equipe} {p.previsao}" for p in validas)
        self.registrar_decisao(f"{chamado.id} para {livre.equipe} · {estimativas}")
        self.registrar("DESPACHO", f"Despachante atribuiu {chamado.id} a {livre.equipe} e aguarda confirmação.")
        self.send(livre.equipe, achieve, Goal("assumir", (chamado.id, self.rodada)), CANAL)

    def aguardar_liberacao(self, chamado, melhor, alternativa=None):
        motivo = f"{melhor.equipe} libera em {melhor.espera} e estima chegada em {melhor.previsao} rodadas"
        resumo = f"{chamado.id} aguarda {melhor.equipe} · previsão {melhor.previsao}"
        if alternativa is not None:
            motivo += f", contra {alternativa.previsao} com {alternativa.equipe} livre"
            resumo += f" contra {alternativa.previsao}"
        self.registrar("DECISÃO", f"{chamado.id} segue na fila: {motivo}. Nova consulta na próxima rodada.")
        self.registrar_decisao(resumo)
        self.consulta = None
        self.encerrar_rodada(self.fila_pendente())

    @pl(gain, Belief("confirmacao_despacho", (Any, Any, Any)))
    def receber_confirmacao(self, equipe, dados):
        id_chamado, rodada, passos = dados
        chamado = self.consulta
        if chamado is None or (id_chamado, rodada, equipe) != (chamado.id, self.rodada, chamado.equipe):
            return

        if passos < 0:
            chamado.equipe = chamado.despacho = None
            self.encerrar_com_erro(f"{equipe} recusou o despacho de {id_chamado}.")
            return

        self.registrar("CONFIRMA", f"{equipe} confirmou {id_chamado} com uma rota de {passos} passos.")
        self.consulta = None
        if passos == 0:
            self.confirmar_chegada(chamado)
        self.despachar()

    def encerrar_rodada(self, fila):
        if self.historico is not None:
            self.historico.capturar(self.rodada, fila, self.chamados.values())

        if all(c.status == "atendido" for c in self.chamados.values()):
            self.terminal.exibir_resumo(self.chamados.values())
            Admin().stop_system()
            return

        self.rodada += 1
        self.passos_pendentes = deque(sorted(self.em_deslocamento(), key=lambda c: c.equipe))
        self.enviar_passo()

    def enviar_passo(self):
        if not self.passos_pendentes:
            self.add(Goal("rodada", self.rodada))
            return

        chamado = self.passos_pendentes.popleft()
        pedido = Goal("avancar", (chamado.id, self.rodada))
        self.send(chamado.equipe, achieve, pedido, CANAL)

    @pl(gain, Belief("passo_concluido", (Any, Any, Any, Any, Any)))
    def receber_passo(self, equipe, dados):
        id_chamado, _rodada, origem, destino, restantes = dados
        self.registrar(
            "MOVIMENTO",
            f"{equipe} informou avanço para {id_chamado}: {origem} -> {destino}. Passos restantes: {restantes}.",
        )

        for outro in self.chamados.values():
            if outro.destino == destino and outro.id != id_chamado and outro.status == "atendido":
                self.registrar("PASSAGEM", f"{equipe} passou por {outro.id}, já atendido, e segue para {id_chamado}.")

        if restantes == 0:
            self.confirmar_chegada(self.chamados[id_chamado])
        self.enviar_passo()

    def confirmar_chegada(self, chamado):
        chamado.chegada = self.rodada
        resposta = chamado.chegada - chamado.entrada
        self.registrar(
            "CHEGADA",
            f"{chamado.equipe} comunicou chegada a {chamado.id} após {resposta} rodadas desde o registro. Equipe livre.",
        )

    def encerrar_com_erro(self, texto):
        self.erro = texto
        self.registrar("ERRO", texto)
        Admin().stop_system()
