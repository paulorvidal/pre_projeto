from maspy import *


class AmbienteViolenciaDomestica(Environment):

    def __init__(self, regioes):
        super().__init__("AmbienteVD")

        self.regioes = {}
        self.posicoes_agentes = {}

        self.posicoes_iniciais = [
            (0, 0),
            (0, 4)
        ]

        for regiao in regioes:

            nome = regiao["nome"]
            x, y = regiao["posicao"]
            prioridade = regiao["prioridade"]

            self.regioes[nome] = {
                "nome": nome,
                "posicao": (x, y),
                "prioridade": prioridade,
                "status": "disponivel"
            }

            self.create(
                Percept(
                    "regiao",
                    (
                        nome,
                        x,
                        y,
                        prioridade,
                        "disponivel"
                    ),
                    adds_event=False
                )
            )

    def on_connect(self, nome_agente):

        indice = len(self.posicoes_agentes)

        posicao = self.posicoes_iniciais[indice]

        self.posicoes_agentes[nome_agente] = posicao

        self.create(
            Percept(
                "posicao",
                (
                    nome_agente,
                    posicao[0],
                    posicao[1]
                ),
                adds_event=False
            )
        )

        self.print(
            f"{nome_agente} iniciou em {posicao}"
        )

    def mover_para(self, nome_agente, nome_regiao):

        regiao = self.regioes[nome_regiao]

        if regiao["status"] != "disponivel":
            return "indisponivel"

        x, y = self.posicoes_agentes[nome_agente]

        destino_x, destino_y = regiao["posicao"]

        if x < destino_x:
            x += 1

        elif x > destino_x:
            x -= 1

        elif y < destino_y:
            y += 1

        elif y > destino_y:
            y -= 1

        self.posicoes_agentes[nome_agente] = (x, y)

        self.print(
            f"{nome_agente} moveu para {(x, y)}"
        )

        if (x, y) == regiao["posicao"]:

            if regiao["status"] != "disponivel":
                return "indisponivel"

            regiao["status"] = "atendida"

            percepto_antigo = self.get(
                Percept(
                    "regiao",
                    (
                        regiao["nome"],
                        destino_x,
                        destino_y,
                        regiao["prioridade"],
                        "disponivel"
                    )
                )
            )

            if percepto_antigo:
                self.delete(percepto_antigo)

            self.create(
                Percept(
                    "regiao",
                    (
                        regiao["nome"],
                        destino_x,
                        destino_y,
                        regiao["prioridade"],
                        "atendida"
                    ),
                    adds_event=False
                )
            )

            self.print(
                f"{nome_agente} chegou em {regiao['nome']}"
            )

            return "atendida"

        return "movendo"