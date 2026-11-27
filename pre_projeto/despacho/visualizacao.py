from dataclasses import dataclass, replace

import pygame

from .cenario import ALTURA, LARGURA, PAREDES, Chamado


@dataclass
class Quadro:
    rodada: int
    equipes: dict[str, tuple[int, int]]
    fila: tuple[str, ...]
    chamados: list[Chamado]
    decisoes: tuple[str, ...]


class Historico:
    """Registra o estado que o MASPY produziu ao fim de cada rodada."""

    def __init__(self, grade):
        self.grade = grade
        self.quadros = []
        self.decisoes = []

    def registrar_decisao(self, texto):
        for nome in self.grade.posicoes:
            texto = texto.replace(nome, nome_curto(nome))
        self.decisoes.append(texto)

    def capturar(self, rodada, fila, chamados):
        equipes = {
            nome_curto(nome): percepto.values[1:]
            for nome, percepto in self.grade.posicoes.items()
        }
        self.quadros.append(Quadro(
            rodada,
            equipes,
            tuple(chamado.id for chamado in fila),
            [replace(chamado) for chamado in chamados if chamado.entrada <= rodada],
            tuple(self.decisoes),
        ))
        self.decisoes.clear()


CELULA = 40
MARGEM = 30
TOPO = 118
FIM_MAPA = TOPO + ALTURA * CELULA
PAINEL = MARGEM + LARGURA * CELULA + 24
LARGURA_JANELA = PAINEL + 390
ALTURA_JANELA = max(670, FIM_MAPA + 147)
INTERVALO_MS = 560
CORES_EQUIPES = ("#1754c5", "#7328bf")
TEXTO = "#f1f5ff"
SECUNDARIO = "#b8c7dc"
PAREDE = "#42536e"
CORES_PRIORIDADE = {
    "Baixa": "#bbcdf6",
    "Moderada": "#f9db91",
    "Alta": "#fcb876",
    "Crítica": "#ffadb7",
}
CHEGADA = "#83e5b0"


def nome_curto(nome):
    return nome.rsplit("_", 1)[0]


def centro(posicao):
    x, y = posicao
    return MARGEM + x * CELULA + CELULA // 2, TOPO + y * CELULA + CELULA // 2


def estado_chamado(chamado, rodada):
    if chamado.chegada is not None:
        espera = chamado.despacho - chamado.entrada
        resposta = chamado.chegada - chamado.entrada
        return CHEGADA, f"{nome_curto(chamado.equipe)} chegou  |  Espera {espera} · Resposta {resposta}"
    cor = CORES_PRIORIDADE[chamado.nivel]
    if chamado.equipe is not None:
        return cor, f"{nome_curto(chamado.equipe)} a caminho desde a rodada {chamado.despacho}"
    return cor, f"Na fila desde a rodada {chamado.entrada}  |  Espera {rodada - chamado.entrada}"


def desenhar(tela, fontes, quadros, indice, politica, reproduzindo, botoes, equipes):
    quadro = quadros[indice]
    grande, titulo, normal, pequena = fontes

    def texto(conteudo, x, y, fonte=normal, cor=TEXTO):
        tela.blit(fonte.render(conteudo, True, cor), (x, y))

    tela.fill("#111b2d")
    texto("Despacho de equipes", MARGEM, 20, grande)
    texto(politica, MARGEM, 57, normal, SECUNDARIO)
    texto(f"Mapa {LARGURA} × {ALTURA}  |  {len(PAREDES)} paredes conhecidas antes do despacho",
          MARGEM, 82, pequena, SECUNDARIO)

    for x in range(LARGURA):
        texto(str(x), centro((x, 0))[0] - 6, TOPO - 18, pequena, SECUNDARIO)
    for y in range(ALTURA):
        texto(str(y), 10, centro((0, y))[1] - 7, pequena, SECUNDARIO)
        for x in range(LARGURA):
            caixa = pygame.Rect(
                MARGEM + x * CELULA, TOPO + y * CELULA, CELULA - 1, CELULA - 1
            )
            pygame.draw.rect(tela, PAREDE if (x, y) in PAREDES else "#dce6f3", caixa)

    for i, nome in enumerate(quadro.equipes):
        cor = CORES_EQUIPES[i % len(CORES_EQUIPES)]
        trilha = [centro(passo.equipes[nome]) for passo in quadros[:indice + 1]]
        if len(trilha) > 1:
            pygame.draw.lines(tela, cor, False, trilha, 3)

    for chamado in quadro.chamados:
        cor, _ = estado_chamado(chamado, quadro.rodada)
        x, y = centro(chamado.destino)
        pygame.draw.rect(tela, cor, (x - 18, y - 18, 36, 18), border_radius=5)
        largura_id = pequena.size(chamado.id)[0]
        texto(chamado.id, x - largura_id // 2, y - 17, pequena, "#111b2d")

    for i, (nome, posicao) in enumerate(quadro.equipes.items()):
        cor = CORES_EQUIPES[i % len(CORES_EQUIPES)]
        x, y = centro(posicao)
        x += -7 if i == 0 else 7
        pygame.draw.circle(tela, cor, (x, y + 8), 11)
        texto(nome, x - 7, y + 1, pequena)

    texto(f"Rodada {quadro.rodada:02d} de {quadros[-1].rodada:02d}", PAINEL, 24, grande)
    concluidos = sum(chamado.chegada is not None for chamado in quadro.chamados)
    texto(f"Equipes chegaram a {concluidos} de {len(quadro.chamados)} chamados",
          PAINEL, 62, pequena, SECUNDARIO)

    texto("Fila de espera · em ordem de despacho", PAINEL, TOPO, titulo)
    ordem = [
        f"{c.id} [{c.prioridade}/10]" for id_chamado in quadro.fila
        for c in quadro.chamados if c.id == id_chamado
    ]
    texto("  >  ".join(ordem) or "Vazia", PAINEL, TOPO + 30, normal, SECUNDARIO)
    texto("Chamados · tempos em rodadas", PAINEL, TOPO + 61, titulo)

    for i, chamado in enumerate(quadro.chamados):
        cor, estado = estado_chamado(chamado, quadro.rodada)
        linha = TOPO + 93 + i * 67
        pygame.draw.rect(tela, "#1c2a40", (PAINEL, linha, 361, 61), border_radius=6)
        prioridade = f"{chamado.prioridade}/10 {chamado.nivel}"
        texto(f"{chamado.id}  ·  {prioridade}  ·  {chamado.destino}", PAINEL + 10, linha + 5, normal,
              CORES_PRIORIDADE[chamado.nivel])
        texto(f"{chamado.crime} · {chamado.local}", PAINEL + 10, linha + 26, pequena, SECUNDARIO)
        texto(estado, PAINEL + 10, linha + 43, pequena, cor)

    texto("Decisões · previsão em rodadas", PAINEL, 486, titulo)
    for i, linha in enumerate(quadro.decisoes or ("Sem nova decisão de despacho nesta rodada.",)):
        texto(linha, PAINEL, 514 + 20 * i, pequena, SECUNDARIO)

    pygame.draw.rect(tela, PAREDE, (MARGEM, FIM_MAPA + 13, 16, 16), border_radius=3)
    texto("Parede", MARGEM + 22, FIM_MAPA + 13, pequena, SECUNDARIO)
    texto("E1 · percurso azul", MARGEM + 102, FIM_MAPA + 13, pequena, "#8db6ff")
    texto("E2 · percurso roxo", MARGEM + 243, FIM_MAPA + 13, pequena, "#d5a6ff")
    perfis = "   |   ".join(
        f"{equipe.id} · {equipe.nome} · {equipe.integrantes} integrantes" for equipe in equipes
    )
    texto(perfis, MARGEM, FIM_MAPA + 40, pequena, SECUNDARIO)

    for rect, tecla, rotulo in botoes:
        if tecla == pygame.K_SPACE and reproduzindo:
            rotulo = "Pausar"
        pygame.draw.rect(tela, "#253954", rect, border_radius=6)
        texto(rotulo, rect.x + 12, rect.y + 9)
    texto("Setas para navegar  ·  Espaço para reproduzir ou pausar  ·  Esc para sair",
          MARGEM, ALTURA_JANELA - 30, pequena, SECUNDARIO)


def exibir(quadros, fifo=False, equipes=()):
    pygame.display.init()
    pygame.font.init()
    try:
        tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
        pygame.display.set_caption("Simulação de despacho")
        fontes = tuple(pygame.font.Font(None, tamanho) for tamanho in (37, 24, 22, 18))
        relogio = pygame.time.Clock()
        politica = "Ordem de chegada (FIFO)" if fifo else "Prioridade da ocorrência"
        botoes = [
            (pygame.Rect(MARGEM + deslocamento, ALTURA_JANELA - 78, largura, 36), tecla, rotulo)
            for deslocamento, largura, tecla, rotulo in (
                (0, 82, pygame.K_HOME, "Início"),
                (92, 92, pygame.K_LEFT, "Voltar"),
                (194, 120, pygame.K_SPACE, "Reproduzir"),
                (324, 101, pygame.K_RIGHT, "Avançar"),
                (435, 72, pygame.K_END, "Fim"),
            )
        ]
        indice = 0
        decorrido = 0
        reproduzindo = False
        ultimo = len(quadros) - 1

        while True:
            intervalo = relogio.tick(30)
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    return
                tecla = None
                if evento.type == pygame.KEYDOWN:
                    tecla = evento.key
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    tecla = next((atalho for rect, atalho, _ in botoes if rect.collidepoint(evento.pos)), None)

                if tecla == pygame.K_ESCAPE:
                    return
                if tecla in (pygame.K_LEFT, pygame.K_RIGHT):
                    passo = 1 if tecla == pygame.K_RIGHT else -1
                    indice = max(0, min(ultimo, indice + passo))
                    reproduzindo = False
                elif tecla in (pygame.K_HOME, pygame.K_END):
                    indice = 0 if tecla == pygame.K_HOME else ultimo
                    reproduzindo = False
                elif tecla == pygame.K_SPACE:
                    if indice == ultimo and not reproduzindo:
                        indice = 0
                    reproduzindo = not reproduzindo
                    decorrido = 0

            if reproduzindo:
                decorrido += intervalo
                if decorrido >= INTERVALO_MS:
                    indice = min(ultimo, indice + 1)
                    decorrido = 0
                    reproduzindo = indice < ultimo

            desenhar(tela, fontes, quadros, indice, politica, reproduzindo, botoes, equipes)
            pygame.display.flip()
    finally:
        pygame.quit()
