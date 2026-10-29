import threading


class Auditoria:

    _lock = threading.Lock()

    _contador = 0

    _atendimentos = {}

    _finalizada = False

    @classmethod
    def _nome(cls, nome):
        """
        Converte Equipe1_1 para Equipe1.
        """

        if nome is None:
            return "-"

        return str(nome).split("_")[0]

    @classmethod
    def iniciar(
        cls,
        ambiente,
        agentes
    ):

        with cls._lock:

            cls._contador = 0

            cls._atendimentos = {}

            cls._finalizada = False

            print()
            print(
                "=" * 72
            )

            print(
                " SIMULACAO MULTIAGENTE "
                "- VIOLENCIA DOMESTICA"
            )

            print(
                "=" * 72
            )

            print()
            print(
                "AGENTES"
            )

            for agente in agentes:

                posicao = (
                    ambiente
                    .posicoes_agentes
                    .get(
                        agente.my_name
                    )
                )

                print(
                    f"  "
                    f"{cls._nome(agente.my_name):<10}"
                    f" inicio={posicao}"
                )

            print()
            print(
                "CHAMADOS"
            )

            for (
                id_chamado,
                chamado
            ) in ambiente.chamados.items():

                print(
                    f"  C{id_chamado}"
                    f"  posicao="
                    f"({chamado['x']}, "
                    f"{chamado['y']})"
                    f"  valor="
                    f"{chamado['valor']}"
                )

            print()
            print(
                "-" * 72
            )

            print(
                "EVENTOS DA SIMULACAO"
            )

            print(
                "-" * 72
            )

    @classmethod
    def evento(
        cls,
        tipo,
        agente,
        mensagem
    ):

        with cls._lock:

            cls._contador += 1

            nome = (
                cls._nome(
                    agente
                )
            )

            print(
                f"{cls._contador:03d}"
                f" | "
                f"{tipo:<13}"
                f" | "
                f"{nome:<8}"
                f" | "
                f"{mensagem}",
                flush=True
            )

    @classmethod
    def movimento(
        cls,
        agente,
        origem,
        destino,
        chamado
    ):

        cls.evento(
            "MOVIMENTO",
            agente,
            (
                f"{origem} -> "
                f"{destino} "
                f"| destino C{chamado}"
            )
        )

    @classmethod
    def parede(
        cls,
        agente,
        posicao
    ):

        cls.evento(
            "PAREDE",
            agente,
            (
                f"descobriu obstaculo "
                f"em {posicao} "
                f"| recalculando rota"
            )
        )

    @classmethod
    def decisao_reativa(
        cls,
        agente,
        id_chamado,
        valor
    ):

        cls.evento(
            "REATIVO",
            agente,
            (
                f"priorizou C{id_chamado} "
                f"| valor={valor}"
            )
        )

    @classmethod
    def decisao_deliberativa(
        cls,
        agente,
        id_chamado,
        valor,
        utilidade
    ):

        cls.evento(
            "DELIBERATIVO",
            agente,
            (
                f"escolheu C{id_chamado} "
                f"| valor={valor} "
                f"| utilidade={utilidade}"
            )
        )

    @classmethod
    def mapa_enviado(
        cls,
        agente,
        qtd_celulas,
        qtd_paredes
    ):

        cls.evento(
            "COMUNICACAO",
            agente,
            (
                "compartilhou mapa "
                f"| celulas={qtd_celulas} "
                f"| paredes={qtd_paredes}"
            )
        )

    @classmethod
    def mapa_recebido(
        cls,
        agente,
        origem,
        novas_paredes
    ):

        cls.evento(
            "COMUNICACAO",
            agente,
            (
                "recebeu mapa de "
                f"{cls._nome(origem)} "
                f"| novas paredes="
                f"{novas_paredes}"
            )
        )

    @classmethod
    def target_enviado(
        cls,
        agente,
        id_chamado
    ):

        cls.evento(
            "MENSAGEM",
            agente,
            (
                f"avisou que "
                f"C{id_chamado} "
                "foi atendido"
            )
        )

    @classmethod
    def target_recebido(
        cls,
        agente,
        origem,
        id_chamado
    ):

        cls.evento(
            "MENSAGEM",
            agente,
            (
                f"recebeu de "
                f"{cls._nome(origem)}: "
                f"C{id_chamado} "
                "ja foi atendido"
            )
        )

    @classmethod
    def reavaliacao(
        cls,
        agente
    ):

        cls.evento(
            "REAVALIACAO",
            agente,
            (
                "alvo perdido "
                "| analisando "
                "ocorrencias restantes"
            )
        )

    @classmethod
    def atendimento(
        cls,
        agente,
        id_chamado,
        posicao,
        total_chamados
    ):

        nome = (
            cls._nome(
                agente
            )
        )

        cls._atendimentos[
            id_chamado
        ] = nome

        cls.evento(
            "ATENDIMENTO",
            agente,
            (
                f"CHEGOU AO C{id_chamado} "
                f"em {posicao}"
            )
        )

        cls.finalizar_se_necessario(
            total_chamados
        )

    @classmethod
    def finalizar_se_necessario(
        cls,
        total_chamados
    ):

        with cls._lock:

            if cls._finalizada:
                return

            if (
                len(cls._atendimentos)
                < total_chamados
            ):
                return

            cls._finalizada = True

            print()
            print(
                "-" * 72
            )

            print(
                "SIMULACAO FINALIZADA"
            )

            print(
                "-" * 72
            )

            for id_chamado in sorted(
                cls._atendimentos
            ):

                equipe = (
                    cls._atendimentos[
                        id_chamado
                    ]
                )

                print(
                    f"  C{id_chamado}"
                    f" atendido por "
                    f"{equipe}"
                )

            print(
                "=" * 72
            )
            print()