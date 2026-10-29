import pygame

from dados.chamados import TAMANHO_GRID


class Visualizacao:

    # ---------------------------------
    # CONFIGURAÇÃO DA JANELA
    # ---------------------------------

    TAMANHO_MAPA_PIXELS = 700

    LARGURA_PAINEL = 420

    TAMANHO_CELULA = (
        TAMANHO_MAPA_PIXELS
        // TAMANHO_GRID
    )

    LARGURA_GRID = (
        TAMANHO_GRID
        * TAMANHO_CELULA
    )

    ALTURA_GRID = (
        TAMANHO_GRID
        * TAMANHO_CELULA
    )

    LARGURA_JANELA = (
        LARGURA_GRID
        + LARGURA_PAINEL
    )

    ALTURA_JANELA = (
        ALTURA_GRID
    )

    # ---------------------------------
    # CORES
    # ---------------------------------

    BRANCO = (
        245,
        245,
        245
    )

    PRETO = (
        30,
        30,
        30
    )

    CINZA = (
        180,
        180,
        180
    )

    CINZA_ESCURO = (
        70,
        70,
        70
    )

    AZUL = (
        50,
        110,
        220
    )

    VERMELHO = (
        220,
        70,
        70
    )

    AMARELO = (
        240,
        190,
        60
    )

    VERDE = (
        70,
        180,
        100
    )

    FUNDO_PAINEL = (
        35,
        38,
        45
    )

    # ---------------------------------
    # INICIALIZAÇÃO
    # ---------------------------------

    def __init__(
        self,
        ambiente,
        agentes
    ):

        self.ambiente = (
            ambiente
        )

        self.agentes = (
            agentes
        )

        pygame.init()

        self.tela = (
            pygame.display.set_mode(
                (
                    self.LARGURA_JANELA,
                    self.ALTURA_JANELA
                )
            )
        )

        pygame.display.set_caption(
            "Sistema Multiagente - "
            "Violencia Domestica"
        )

        self.relogio = (
            pygame.time.Clock()
        )

        self.fonte_grande = (
            pygame.font.Font(
                None,
                30
            )
        )

        self.fonte_media = (
            pygame.font.Font(
                None,
                23
            )
        )

        self.fonte_pequena = (
            pygame.font.Font(
                None,
                18
            )
        )

        self.executando = True

    # =================================
    # AUXILIARES
    # =================================

    def centro_celula(
        self,
        x,
        y
    ):

        centro_x = (
            x
            * self.TAMANHO_CELULA
            + self.TAMANHO_CELULA // 2
        )

        centro_y = (
            y
            * self.TAMANHO_CELULA
            + self.TAMANHO_CELULA // 2
        )

        return (
            centro_x,
            centro_y
        )

    def escrever(
        self,
        texto,
        x,
        y,
        fonte,
        cor
    ):

        superficie = (
            fonte.render(
                texto,
                True,
                cor
            )
        )

        self.tela.blit(
            superficie,
            (
                x,
                y
            )
        )

    # =================================
    # GRID
    # =================================

    def desenhar_grid(self):

        pygame.draw.rect(
            self.tela,
            self.BRANCO,
            (
                0,
                0,
                self.LARGURA_GRID,
                self.ALTURA_GRID
            )
        )

        for linha in range(
            TAMANHO_GRID + 1
        ):

            pos = (
                linha
                * self.TAMANHO_CELULA
            )

            # Linha horizontal
            pygame.draw.line(
                self.tela,
                self.CINZA,
                (
                    0,
                    pos
                ),
                (
                    self.LARGURA_GRID,
                    pos
                ),
                1
            )

            # Linha vertical
            pygame.draw.line(
                self.tela,
                self.CINZA,
                (
                    pos,
                    0
                ),
                (
                    pos,
                    self.ALTURA_GRID
                ),
                1
            )

    # =================================
    # PAREDES
    # =================================

    def desenhar_paredes(self):

        for x, y in (
            self.ambiente.paredes
        ):

            esquerda = (
                x
                * self.TAMANHO_CELULA
            )

            topo = (
                y
                * self.TAMANHO_CELULA
            )

            retangulo = (
                pygame.Rect(
                    esquerda + 2,
                    topo + 2,
                    self.TAMANHO_CELULA - 4,
                    self.TAMANHO_CELULA - 4
                )
            )

            pygame.draw.rect(
                self.tela,
                self.CINZA_ESCURO,
                retangulo
            )

    # =================================
    # CAMINHO PERCORRIDO
    # =================================

    def desenhar_caminhos(self):

        cores = [
            self.AZUL,
            self.VERMELHO
        ]

        for (
            indice,
            agente
        ) in enumerate(
            self.agentes
        ):

            cor = (
                cores[
                    indice
                    % len(cores)
                ]
            )

            for x, y in (
                agente.caminho_percorrido
            ):

                centro = (
                    self.centro_celula(
                        x,
                        y
                    )
                )

                pygame.draw.circle(
                    self.tela,
                    cor,
                    centro,
                    max(
                        2,
                        self.TAMANHO_CELULA
                        // 10
                    )
                )

    # =================================
    # CHAMADOS
    # =================================

    def desenhar_chamados(self):

        for (
            id_chamado,
            chamado
        ) in (
            self.ambiente
            .chamados
            .items()
        ):

            x = (
                chamado["x"]
            )

            y = (
                chamado["y"]
            )

            (
                centro_x,
                centro_y
            ) = (
                self.centro_celula(
                    x,
                    y
                )
            )

            if (
                chamado["status"]
                == "disponivel"
            ):

                cor = (
                    self.AMARELO
                )

            else:

                cor = (
                    self.VERDE
                )

            tamanho = int(
                self.TAMANHO_CELULA
                * 0.75
            )

            retangulo = (
                pygame.Rect(
                    centro_x
                    - tamanho // 2,

                    centro_y
                    - tamanho // 2,

                    tamanho,
                    tamanho
                )
            )

            pygame.draw.rect(
                self.tela,
                cor,
                retangulo,
                border_radius=5
            )

            texto = (
                self.fonte_pequena.render(
                    f"C{id_chamado}",
                    True,
                    self.PRETO
                )
            )

            texto_rect = (
                texto.get_rect(
                    center=(
                        centro_x,
                        centro_y
                    )
                )
            )

            self.tela.blit(
                texto,
                texto_rect
            )

    # =================================
    # AGENTES
    # =================================

    def desenhar_agentes(self):

        cores = [
            self.AZUL,
            self.VERMELHO
        ]

        for (
            indice,
            agente
        ) in enumerate(
            self.agentes
        ):

            posicao = (
                self.ambiente
                .posicoes_agentes
                .get(
                    agente.my_name
                )
            )

            if (
                posicao is None
            ):
                continue

            x, y = (
                posicao
            )

            (
                centro_x,
                centro_y
            ) = (
                self.centro_celula(
                    x,
                    y
                )
            )

            # Impede sobreposição total
            # quando dois agentes estão
            # na mesma célula.
            if indice == 0:

                deslocamento = (
                    -self.TAMANHO_CELULA
                    // 6
                )

            else:

                deslocamento = (
                    self.TAMANHO_CELULA
                    // 6
                )

            centro_x += (
                deslocamento
            )

            raio = max(
                6,
                self.TAMANHO_CELULA
                // 3
            )

            cor = (
                cores[
                    indice
                    % len(cores)
                ]
            )

            pygame.draw.circle(
                self.tela,
                cor,
                (
                    centro_x,
                    centro_y
                ),
                raio
            )

            nome = (
                self.fonte_pequena.render(
                    f"E{indice + 1}",
                    True,
                    self.BRANCO
                )
            )

            retangulo_nome = (
                nome.get_rect(
                    center=(
                        centro_x,
                        centro_y
                    )
                )
            )

            self.tela.blit(
                nome,
                retangulo_nome
            )

    # =================================
    # PAINEL LATERAL
    # =================================

    def desenhar_painel(self):

        pygame.draw.rect(
            self.tela,
            self.FUNDO_PAINEL,
            (
                self.LARGURA_GRID,
                0,
                self.LARGURA_PAINEL,
                self.ALTURA_JANELA
            )
        )

        x = (
            self.LARGURA_GRID
            + 20
        )

        y = 20

        self.escrever(
            "SIMULACAO MULTIAGENTE",
            x,
            y,
            self.fonte_grande,
            self.BRANCO
        )

        y += 45

        cores = [
            self.AZUL,
            self.VERMELHO
        ]

        # ---------------------------------
        # INFORMAÇÕES DOS AGENTES
        # ---------------------------------

        for (
            indice,
            agente
        ) in enumerate(
            self.agentes
        ):

            cor = (
                cores[
                    indice
                    % len(cores)
                ]
            )

            # IMPORTANTE:
            # posição precisa ser obtida
            # aqui dentro do for.
            posicao = (
                self.ambiente
                .posicoes_agentes
                .get(
                    agente.my_name
                )
            )

            self.escrever(
                agente.nome_exibicao,
                x,
                y,
                self.fonte_media,
                cor
            )

            y += 25

            self.escrever(
                f"Camada: "
                f"{agente.modo_atual}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            if (
                agente.alvo_atual
                is None
            ):

                alvo = "-"

            else:

                alvo = (
                    f"Chamado "
                    f"{agente.alvo_atual}"
                )

            self.escrever(
                f"Alvo: {alvo}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            self.escrever(
                f"Estado: "
                f"{agente.estado_atual}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            self.escrever(
                f"Posicao: "
                f"{posicao}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            self.escrever(
                "Mapa conhecido: "
                f"{len(agente.path_graph)} "
                "celulas",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            self.escrever(
                "Paredes conhecidas: "
                f"{len(agente.wall_set)}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            mensagem = (
                agente.ultima_mensagem
            )

            # Evita textos muito grandes
            # extrapolando o painel.
            if len(mensagem) > 34:

                mensagem = (
                    mensagem[:31]
                    + "..."
                )

            self.escrever(
                f"Mensagem: "
                f"{mensagem}",
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 20

            if (
                agente.ultima_utilidade
                is not None
            ):

                self.escrever(
                    "Utilidade: "
                    f"{agente.ultima_utilidade}",
                    x + 10,
                    y,
                    self.fonte_pequena,
                    self.BRANCO
                )

                y += 20

            y += 15

        # ---------------------------------
        # CHAMADOS
        # ---------------------------------

        self.escrever(
            "CHAMADOS",
            x,
            y,
            self.fonte_media,
            self.BRANCO
        )

        y += 28

        for (
            id_chamado,
            chamado
        ) in (
            self.ambiente
            .chamados
            .items()
        ):

            texto = (
                f"C{id_chamado}  "
                f"valor={chamado['valor']}  "
                f"{chamado['status']}"
            )

            self.escrever(
                texto,
                x + 10,
                y,
                self.fonte_pequena,
                self.BRANCO
            )

            y += 22

        # ---------------------------------
        # STATUS FINAL
        # ---------------------------------

        finalizado = all(
            chamado["status"]
            == "atendido"

            for chamado
            in (
                self.ambiente
                .chamados
                .values()
            )
        )

        if finalizado:

            y += 20

            self.escrever(
                "SIMULACAO FINALIZADA",
                x,
                y,
                self.fonte_media,
                self.VERDE
            )

    # =================================
    # LOOP PRINCIPAL
    # =================================

    def executar(self):

        while (
            self.executando
        ):

            for evento in (
                pygame.event.get()
            ):

                if (
                    evento.type
                    == pygame.QUIT
                ):

                    self.executando = (
                        False
                    )

                if (
                    evento.type
                    == pygame.KEYDOWN
                    and
                    evento.key
                    == pygame.K_ESCAPE
                ):

                    self.executando = (
                        False
                    )

            self.tela.fill(
                self.BRANCO
            )

            self.desenhar_grid()

            self.desenhar_paredes()

            self.desenhar_caminhos()

            self.desenhar_chamados()

            self.desenhar_agentes()

            self.desenhar_painel()

            pygame.display.flip()

            self.relogio.tick(
                30
            )

        pygame.quit()