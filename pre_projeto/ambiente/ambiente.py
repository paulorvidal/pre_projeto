from maspy import *

from dados.chamados import (
    TAMANHO_GRID,
    POSICOES_INICIAIS
)


class AmbienteViolenciaDomestica(
    Environment
):

    def __init__(
        self,
        chamados,
        paredes
    ):

        super().__init__(
            "MapaVD"
        )

        self.chamados = {}

        self.paredes = set(
            paredes
        )

        self.posicoes_agentes = {}

        self.posicoes_iniciais = list(
            POSICOES_INICIAIS
        )

        # -----------------------------
        # TARGETS
        # -----------------------------

        for chamado in chamados:

            id_chamado = (
                chamado["id"]
            )

            x = (
                chamado["x"]
            )

            y = (
                chamado["y"]
            )

            valor = (
                chamado["valor"]
            )

            self.chamados[
                id_chamado
            ] = {
                "x": x,
                "y": y,
                "valor": valor,
                "status": "disponivel"
            }

            self.create(
                Percept(
                    "target",
                    (
                        id_chamado,
                        x,
                        y,
                        valor,
                        "disponivel"
                    ),
                    adds_event=False
                )
            )

    # =================================
    # CONEXÃO DOS AGENTES
    # =================================

    def on_connect(
        self,
        nome_agente
    ):

        indice = len(
            self.posicoes_agentes
        )

        posicao = (
            self.posicoes_iniciais[
                indice
            ]
        )

        self.posicoes_agentes[
            nome_agente
        ] = posicao

        self.create(
            Percept(
                "agt_position",
                (
                    nome_agente,
                    posicao[0],
                    posicao[1]
                ),
                adds_event=False
            )
        )

        self.print(
            f"{nome_agente} iniciou "
            f"em {posicao}"
        )

    # =================================
    # MOVIMENTO
    # =================================

    def mover(
        self,
        nome_agente,
        id_chamado,
        direcao
    ):

        chamado = (
            self.chamados[
                id_chamado
            ]
        )

        # Outro agente pode ter
        # atendido enquanto este
        # estava se deslocando.
        if (
            chamado["status"]
            != "disponivel"
        ):

            return (
                "indisponivel",
                self.posicoes_agentes[
                    nome_agente
                ],
                None
            )

        x, y = (
            self.posicoes_agentes[
                nome_agente
            ]
        )

        posicao_antiga = (
            x,
            y
        )

        novo_x = x
        novo_y = y

        if direcao == "direita":
            novo_x += 1

        elif direcao == "esquerda":
            novo_x -= 1

        elif direcao == "baixo":
            novo_y += 1

        elif direcao == "cima":
            novo_y -= 1

        # Segurança para não sair
        # dos limites do grid.
        if not (
            0 <= novo_x
            < TAMANHO_GRID
            and
            0 <= novo_y
            < TAMANHO_GRID
        ):

            return (
                "bloqueado",
                posicao_antiga,
                None
            )

        nova_posicao = (
            novo_x,
            novo_y
        )

        # =================================
        # PAREDE
        # =================================

        if (
            nova_posicao
            in self.paredes
        ):

            self.print(
                f"{nome_agente} encontrou "
                f"parede em "
                f"{nova_posicao}"
            )

            return (
                "bloqueado",
                posicao_antiga,
                nova_posicao
            )

        # =================================
        # MOVIMENTO VÁLIDO
        # =================================

        self.posicoes_agentes[
            nome_agente
        ] = nova_posicao

        percepto_antigo = self.get(
            Percept(
                "agt_position",
                (
                    nome_agente,
                    posicao_antiga[0],
                    posicao_antiga[1]
                )
            )
        )

        if percepto_antigo:

            self.delete(
                percepto_antigo
            )

        self.create(
            Percept(
                "agt_position",
                (
                    nome_agente,
                    novo_x,
                    novo_y
                ),
                adds_event=False
            )
        )

        self.print(
            f"{nome_agente} moveu "
            f"para {nova_posicao}"
        )

        destino = (
            chamado["x"],
            chamado["y"]
        )

        # =================================
        # TARGET ALCANÇADO
        # =================================

        if (
            nova_posicao
            == destino
        ):

            if (
                chamado["status"]
                != "disponivel"
            ):

                return (
                    "indisponivel",
                    nova_posicao,
                    None
                )

            chamado["status"] = (
                "atendido"
            )

            percepto_target = self.get(
                Percept(
                    "target",
                    (
                        id_chamado,
                        chamado["x"],
                        chamado["y"],
                        chamado["valor"],
                        "disponivel"
                    )
                )
            )

            if percepto_target:

                self.delete(
                    percepto_target
                )

            self.create(
                Percept(
                    "target",
                    (
                        id_chamado,
                        chamado["x"],
                        chamado["y"],
                        chamado["valor"],
                        "atendido"
                    ),
                    adds_event=False
                )
            )

            self.print(
                f"{nome_agente} chegou "
                f"ao chamado "
                f"{id_chamado}"
            )

            return (
                "atendido",
                nova_posicao,
                None
            )

        return (
            "movendo",
            nova_posicao,
            None
        )