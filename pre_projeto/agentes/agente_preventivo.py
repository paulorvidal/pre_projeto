from maspy import *


class AgentePreventivo(Agent):

    def __init__(self, nome):

        super().__init__(
            nome,
            max_intentions=1
        )

    def buscar_regioes_disponiveis(self):

        self.perceive("AmbienteVD")

        regioes = self.get(
            Belief(
                "regiao",
                (Any, Any, Any, Any, Any)
            ),
            all=True,
            ck_src=False
        )

        if not regioes:
            return []

        return [
            regiao.values
            for regiao in regioes
            if regiao.values[4] == "disponivel"
        ]

    @pl(gain, Goal("atender_regiao"))
    def atender_regiao(self, src):

        while True:

            regioes = self.buscar_regioes_disponiveis()

            if not regioes:

                self.print(
                    "Não existem mais regiões disponíveis."
                )

                self.stop_cycle()
                return

            melhor_regiao = max(
                regioes,
                key=lambda regiao: regiao[3]
            )

            nome = melhor_regiao[0]
            prioridade = melhor_regiao[3]

            self.print(
                f"Escolheu {nome} "
                f"com prioridade {prioridade}"
            )

            while True:

                resultado = self.mover_para(nome)

                if resultado == "movendo":
                    continue

                if resultado == "atendida":

                    self.print(
                        f"Atendimento realizado em {nome}"
                    )

                    self.stop_cycle()
                    return

                if resultado == "indisponivel":

                    self.print(
                        f"{nome} já foi atendida "
                        f"por outro agente."
                    )

                    break