import time

from collections import deque

from maspy import *

from dados.chamados import (
    TAMANHO_GRID
)


class AgenteHibrido(Agent):

    def __init__(
        self,
        nome,
        limiar_urgencia
    ):

        super().__init__(
            nome,
            beliefs=Belief(
                "iniciar"
            ),
            max_intentions=1
        )

        self.nome_exibicao = nome

        self.limiar_urgencia = (
            limiar_urgencia
        )

        # =================================
        # MEMÓRIA / CRENÇAS DO AGENTE
        # =================================

        # Células livres que o agente
        # conhece.
        self.path_graph = set()

        # Paredes descobertas pelo próprio
        # agente ou informadas por outro.
        self.wall_set = set()

        # Targets conhecidos.
        self.targets_conhecidos = {}

        # Usado apenas para desenhar
        # a trilha individual na GUI.
        self.caminho_percorrido = set()

        # Targets que outro agente informou
        # que já foram atendidos.
        self.targets_atendidos_por_mensagem = (
            set()
        )

        # =================================
        # INFORMAÇÕES PARA GUI
        # =================================

        self.modo_atual = (
            "INICIANDO"
        )

        self.alvo_atual = None

        self.estado_atual = (
            "Aguardando"
        )

        self.ultima_utilidade = None

        self.ultima_mensagem = "-"

    # =================================
    # PERCEPÇÃO
    # =================================

    def perceber_ambiente(self):

        self.perceive(
            "MapaVD"
        )

        targets = self.get(
            Belief(
                "target",
                (
                    Any,
                    Any,
                    Any,
                    Any,
                    Any
                )
            ),
            all=True,
            ck_src=False
        )

        self.targets_conhecidos.clear()

        if not targets:
            return

        for target in targets:

            (
                id_chamado,
                x,
                y,
                valor,
                status
            ) = target.values

            self.targets_conhecidos[
                id_chamado
            ] = {
                "x": x,
                "y": y,
                "valor": valor,
                "status": status
            }

    def obter_posicao(self):

        self.perceive(
            "MapaVD"
        )

        posicoes = self.get(
            Belief(
                "agt_position",
                (
                    self.my_name,
                    Any,
                    Any
                )
            ),
            all=True,
            ck_src=False
        )

        if not posicoes:
            return None

        posicao = (
            posicoes[-1]
        )

        return (
            posicao.values[1],
            posicao.values[2]
        )

    # =================================
    # COMUNICAÇÃO
    # =================================

    def compartilhar_mapa(self):

        grafo = tuple(
            sorted(
                self.path_graph
            )
        )

        paredes = tuple(
            sorted(
                self.wall_set
            )
        )

        self.send(
            broadcast,
            tell,
            Belief(
                "info_mapa",
                (
                    grafo,
                    paredes
                ),
                adds_event=False
            ),
            "Cooperacao"
        )

        self.ultima_mensagem = (
            "Compartilhou mapa"
        )

    def avisar_target_atendido(
        self,
        x,
        y
    ):

        self.send(
            broadcast,
            tell,
            Belief(
                "target_atendido",
                (
                    x,
                    y
                ),
                adds_event=False
            ),
            "Cooperacao"
        )

        self.ultima_mensagem = (
            f"Avisou target "
            f"atendido em ({x}, {y})"
        )

        self.print(
            "Enviou mensagem "
            f"target_atendido"
            f"({x}, {y})"
        )

    def processar_mensagens(self):

        # =================================
        # INFO_MAPA
        # =================================

        mensagens_mapa = self.get(
            Belief(
                "info_mapa",
                (
                    Any,
                    Any
                )
            ),
            all=True,
            ck_src=False
        )

        if mensagens_mapa:

            for mensagem in (
                mensagens_mapa
            ):

                grafo_recebido = (
                    mensagem.values[0]
                )

                paredes_recebidas = (
                    mensagem.values[1]
                )

                qtd_paredes_antes = len(
                    self.wall_set
                )

                qtd_caminhos_antes = len(
                    self.path_graph
                )

                self.path_graph.update(
                    grafo_recebido
                )

                self.wall_set.update(
                    paredes_recebidas
                )

                recebeu_novidade = (
                    len(self.wall_set)
                    > qtd_paredes_antes
                    or
                    len(self.path_graph)
                    > qtd_caminhos_antes
                )

                if recebeu_novidade:

                    self.print(
                        "Recebeu novas "
                        "informações de mapa "
                        f"de {mensagem.source}"
                    )

                    self.ultima_mensagem = (
                        "Mapa recebido de "
                        f"{mensagem.source}"
                    )

                self.rm(
                    mensagem
                )

        # =================================
        # TARGET ATENDIDO
        # =================================

        mensagens_target = self.get(
            Belief(
                "target_atendido",
                (
                    Any,
                    Any
                )
            ),
            all=True,
            ck_src=False
        )

        if mensagens_target:

            for mensagem in (
                mensagens_target
            ):

                x = (
                    mensagem.values[0]
                )

                y = (
                    mensagem.values[1]
                )

                for (
                    id_chamado,
                    chamado
                ) in (
                    self.targets_conhecidos
                    .items()
                ):

                    if (
                        chamado["x"] == x
                        and
                        chamado["y"] == y
                    ):

                        chamado[
                            "status"
                        ] = "atendido"

                        self.targets_atendidos_por_mensagem.add(
                            id_chamado
                        )

                        self.print(
                            "Recebeu mensagem: "
                            f"chamado "
                            f"{id_chamado} "
                            "já foi atendido por "
                            f"{mensagem.source}"
                        )

                        self.ultima_mensagem = (
                            f"C{id_chamado} "
                            f"atendido por "
                            f"{mensagem.source}"
                        )

                self.rm(
                    mensagem
                )

    # =================================
    # CAMADA REATIVA
    # =================================

    def camada_reativa(self):

        candidatos = []

        for (
            id_chamado,
            chamado
        ) in (
            self.targets_conhecidos
            .items()
        ):

            if (
                chamado["status"]
                == "disponivel"
                and
                chamado["valor"]
                >= self.limiar_urgencia
            ):

                candidatos.append(
                    (
                        id_chamado,
                        chamado
                    )
                )

        if not candidatos:
            return None

        # Se existirem vários urgentes,
        # prioriza o maior valor.
        return max(
            candidatos,
            key=lambda item:
            item[1]["valor"]
        )

    # =================================
    # BFS
    # =================================

    def obter_vizinhos_livres(
        self,
        posicao
    ):

        x, y = posicao

        candidatos = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        livres = []

        for candidato in candidatos:

            cx, cy = candidato

            if not (
                0 <= cx
                < TAMANHO_GRID
                and
                0 <= cy
                < TAMANHO_GRID
            ):
                continue

            # O agente só evita as
            # paredes que conhece.
            if (
                candidato
                in self.wall_set
            ):
                continue

            livres.append(
                candidato
            )

        return livres

    def planejar_rota(
        self,
        origem,
        destino
    ):
        """
        BFS:
        procura o menor caminho conhecido
        da posição atual até o target.

        Paredes ainda desconhecidas são
        tratadas como possíveis caminhos.

        Quando uma parede é descoberta,
        o BFS será executado novamente.
        """

        if (
            origem == destino
        ):
            return [
                origem
            ]

        fila = deque(
            [origem]
        )

        anterior = {
            origem: None
        }

        encontrou = False

        while fila:

            atual = (
                fila.popleft()
            )

            for vizinho in (
                self.obter_vizinhos_livres(
                    atual
                )
            ):

                if (
                    vizinho
                    in anterior
                ):
                    continue

                anterior[
                    vizinho
                ] = atual

                if (
                    vizinho
                    == destino
                ):

                    encontrou = True
                    fila.clear()
                    break

                fila.append(
                    vizinho
                )

        if not encontrou:

            return None

        # Reconstrói o caminho:
        #
        # origem -> ... -> destino

        rota = [
            destino
        ]

        atual = destino

        while (
            anterior[atual]
            is not None
        ):

            atual = (
                anterior[atual]
            )

            rota.append(
                atual
            )

        rota.reverse()

        return rota

    def obter_direcao(
        self,
        atual,
        proxima
    ):

        atual_x, atual_y = (
            atual
        )

        prox_x, prox_y = (
            proxima
        )

        if (
            prox_x
            > atual_x
        ):
            return "direita"

        if (
            prox_x
            < atual_x
        ):
            return "esquerda"

        if (
            prox_y
            > atual_y
        ):
            return "baixo"

        if (
            prox_y
            < atual_y
        ):
            return "cima"

        return None

    # =================================
    # CAMADA DELIBERATIVA
    # =================================

    def camada_deliberativa(self):

        posicao = (
            self.obter_posicao()
        )

        if (
            posicao is None
        ):
            return None

        melhor_target = None
        melhor_utilidade = None

        for (
            id_chamado,
            chamado
        ) in (
            self.targets_conhecidos
            .items()
        ):

            if (
                chamado["status"]
                != "disponivel"
            ):
                continue

            destino = (
                chamado["x"],
                chamado["y"]
            )

            rota = (
                self.planejar_rota(
                    posicao,
                    destino
                )
            )

            if (
                rota is None
            ):
                continue

            distancia = (
                len(rota) - 1
            )

            utilidade = (
                chamado["valor"]
                - distancia
            )

            if (
                melhor_utilidade is None
                or
                utilidade
                > melhor_utilidade
            ):

                melhor_utilidade = (
                    utilidade
                )

                melhor_target = (
                    id_chamado,
                    chamado
                )

        self.ultima_utilidade = (
            melhor_utilidade
        )

        return melhor_target

    # =================================
    # EXECUÇÃO DA NAVEGAÇÃO
    # =================================

    def executar_atendimento(
        self,
        id_chamado,
        chamado
    ):

        destino = (
            chamado["x"],
            chamado["y"]
        )

        self.estado_atual = (
            "Planejando rota"
        )

        while True:

            # -----------------------------
            # COMUNICAÇÃO
            # -----------------------------

            self.processar_mensagens()

            if (
                id_chamado
                in
                self.targets_atendidos_por_mensagem
            ):

                self.estado_atual = (
                    "Alvo atendido "
                    "por outra equipe"
                )

                return (
                    "indisponivel"
                )

            # -----------------------------
            # POSIÇÃO
            # -----------------------------

            posicao = (
                self.obter_posicao()
            )

            if (
                posicao is None
            ):

                time.sleep(
                    0.05
                )

                continue

            self.path_graph.add(
                posicao
            )

            self.caminho_percorrido.add(
                posicao
            )

            # -----------------------------
            # PLANEJAMENTO BFS
            # -----------------------------

            self.estado_atual = (
                "Planejando rota"
            )

            rota = (
                self.planejar_rota(
                    posicao,
                    destino
                )
            )

            if (
                rota is None
            ):

                self.estado_atual = (
                    "Sem caminho conhecido"
                )

                self.print(
                    "Não encontrou rota "
                    f"para o chamado "
                    f"{id_chamado}"
                )

                return (
                    "sem_caminho"
                )

            # Se já estiver no destino.
            if (
                len(rota) < 2
            ):

                return (
                    "atendido"
                )

            proxima_posicao = (
                rota[1]
            )

            direcao = (
                self.obter_direcao(
                    posicao,
                    proxima_posicao
                )
            )

            if (
                direcao is None
            ):

                return (
                    "sem_caminho"
                )

            self.estado_atual = (
                "Deslocando"
            )

            (
                resultado,
                nova_posicao,
                parede
            ) = self.mover(
                id_chamado,
                direcao
            )

            # =================================
            # PAREDE NOVA
            # =================================

            if (
                resultado
                == "bloqueado"
            ):

                # É parede real.
                if (
                    parede is not None
                    and
                    parede
                    not in self.wall_set
                ):

                    self.wall_set.add(
                        parede
                    )

                    self.estado_atual = (
                        "Parede descoberta"
                    )

                    self.print(
                        "Descobriu parede "
                        f"em {parede}"
                    )

                    # Compartilha imediatamente.
                    self.compartilhar_mapa()

                # Aqui está a correção:
                #
                # NÃO tenta andar para trás
                # e depois voltar.
                #
                # Volta ao começo do while,
                # executa BFS novamente usando
                # o Wall_Set atualizado.

                time.sleep(
                    0.15
                )

                continue

            # =================================
            # MOVIMENTO
            # =================================

            if (
                resultado
                == "movendo"
            ):

                self.path_graph.add(
                    nova_posicao
                )

                self.caminho_percorrido.add(
                    nova_posicao
                )

                time.sleep(
                    0.15
                )

                continue

            # =================================
            # TARGET ATENDIDO
            # =================================

            if (
                resultado
                == "atendido"
            ):

                self.path_graph.add(
                    nova_posicao
                )

                self.caminho_percorrido.add(
                    nova_posicao
                )

                self.estado_atual = (
                    f"Atendeu chamado "
                    f"{id_chamado}"
                )

                self.print(
                    f"Atendeu o chamado "
                    f"{id_chamado}"
                )

                # Informa a outra equipe.
                self.avisar_target_atendido(
                    destino[0],
                    destino[1]
                )

                # Compartilha também seu
                # conhecimento do mapa.
                self.compartilhar_mapa()

                return (
                    "atendido"
                )

            # =================================
            # OUTRA EQUIPE CHEGOU PRIMEIRO
            # =================================

            if (
                resultado
                == "indisponivel"
            ):

                self.estado_atual = (
                    "Chamado perdido"
                )

                self.print(
                    f"Chamado "
                    f"{id_chamado} "
                    "já foi atendido por "
                    "outra equipe."
                )

                return (
                    "indisponivel"
                )

    # =================================
    # CICLO DO AGENTE HÍBRIDO
    # =================================

    @pl(
        gain,
        Belief(
            "iniciar"
        )
    )
    def iniciar(
        self,
        src
    ):

        while True:

            self.estado_atual = (
                "Percebendo ambiente"
            )

            # Incorpora informação
            # dos outros agentes.
            self.processar_mensagens()

            # Atualiza os perceptos
            # vindos do mapa.
            self.perceber_ambiente()

            # =================================
            # 1. CAMADA REATIVA
            # =================================

            escolha = (
                self.camada_reativa()
            )

            if (
                escolha
                is not None
            ):

                (
                    id_chamado,
                    chamado
                ) = escolha

                self.modo_atual = (
                    "REATIVO"
                )

                self.alvo_atual = (
                    id_chamado
                )

                self.ultima_utilidade = (
                    None
                )

                self.estado_atual = (
                    "Resposta imediata"
                )

                self.print(
                    "CAMADA REATIVA: "
                    f"chamado "
                    f"{id_chamado} "
                    f"com valor "
                    f"{chamado['valor']}"
                )

            # =================================
            # 2. CAMADA DELIBERATIVA
            # =================================

            else:

                escolha = (
                    self.camada_deliberativa()
                )

                if (
                    escolha is None
                ):

                    self.modo_atual = (
                        "FINALIZADO"
                    )

                    self.alvo_atual = None

                    self.estado_atual = (
                        "Sem chamados"
                    )

                    self.stop_cycle()

                    return

                (
                    id_chamado,
                    chamado
                ) = escolha

                self.modo_atual = (
                    "DELIBERATIVO"
                )

                self.alvo_atual = (
                    id_chamado
                )

                self.estado_atual = (
                    "Escolha por utilidade"
                )

                self.print(
                    "CAMADA DELIBERATIVA: "
                    f"escolheu chamado "
                    f"{id_chamado} "
                    f"com valor "
                    f"{chamado['valor']} "
                    f"(utilidade "
                    f"{self.ultima_utilidade})"
                )

            # =================================
            # NAVEGA
            # =================================

            resultado = (
                self.executar_atendimento(
                    id_chamado,
                    chamado
                )
            )

            # Esta equipe passou a ficar
            # ocupada com o chamado atendido.
            if (
                resultado
                == "atendido"
            ):

                self.modo_atual = (
                    "FINALIZADO"
                )

                self.alvo_atual = None

                self.stop_cycle()

                return

            # Perdeu o target para outra
            # equipe: volta ao começo para
            # reconsiderar os targets.
            if (
                resultado
                == "indisponivel"
            ):

                self.alvo_atual = None

                self.estado_atual = (
                    "Reavaliando"
                )

                self.print(
                    "Reavaliando os "
                    "chamados..."
                )

                continue

            if (
                resultado
                == "sem_caminho"
            ):

                self.alvo_atual = None

                self.estado_atual = (
                    "Reavaliando"
                )

                self.print(
                    "Rota indisponível. "
                    "Reavaliando..."
                )

                time.sleep(
                    0.1
                )