import random
from collections import deque


TAMANHO_GRID = 20

LIMIAR_URGENCIA = 10

PERCENTUAL_PAREDES = 0.10

# Velocidade da simulação para auditoria visual.
ATRASO_MOVIMENTO = 0.60
ATRASO_EVENTO = 1.00


CHAMADOS = [
    {
        "id": 1,
        "x": 1,
        "y": 5,
        "valor": 5
    },
    {
        "id": 2,
        "x": 18,
        "y": 18,
        "valor": 10
    }
]


def distancia_manhattan(
    origem,
    destino
):
    return (
        abs(
            origem[0]
            - destino[0]
        )
        +
        abs(
            origem[1]
            - destino[1]
        )
    )


def obter_vizinhos(
    posicao
):
    x, y = posicao

    candidatos = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]

    return [
        (nx, ny)
        for nx, ny
        in candidatos

        if (
            0 <= nx
            < TAMANHO_GRID
            and
            0 <= ny
            < TAMANHO_GRID
        )
    ]


def gerar_posicoes_iniciais():
    """
    Sorteia as duas equipes.

    A regra importante é:
    ambas precisam começar com
    distância semelhante do C2.

    Assim realmente existe uma
    disputa pelo target de valor 10.
    """

    target_prioritario = (
        CHAMADOS[1]["x"],
        CHAMADOS[1]["y"]
    )

    targets = {
        (
            chamado["x"],
            chamado["y"]
        )
        for chamado in CHAMADOS
    }

    celulas = [
        (x, y)

        for x
        in range(TAMANHO_GRID)

        for y
        in range(TAMANHO_GRID)

        if (
            (x, y)
            not in targets
        )
    ]

    while True:

        equipe_1 = random.choice(
            celulas
        )

        equipe_2 = random.choice(
            celulas
        )

        if (
            equipe_1
            == equipe_2
        ):
            continue

        distancia_1 = (
            distancia_manhattan(
                equipe_1,
                target_prioritario
            )
        )

        distancia_2 = (
            distancia_manhattan(
                equipe_2,
                target_prioritario
            )
        )

        # Nenhuma equipe começa
        # praticamente em cima do C2.
        if (
            distancia_1 < 8
            or
            distancia_2 < 8
        ):
            continue

        # A diferença de distância
        # entre as equipes deve ser
        # pequena.
        if (
            abs(
                distancia_1
                - distancia_2
            )
            <= 3
        ):

            return [
                equipe_1,
                equipe_2
            ]


POSICOES_INICIAIS = (
    gerar_posicoes_iniciais()
)


def obter_pontos_obrigatorios():

    pontos = list(
        POSICOES_INICIAIS
    )

    for chamado in CHAMADOS:

        pontos.append(
            (
                chamado["x"],
                chamado["y"]
            )
        )

    return pontos


def obter_celulas_protegidas():

    protegidas = set()

    for ponto in (
        obter_pontos_obrigatorios()
    ):

        protegidas.add(
            ponto
        )

        protegidas.update(
            obter_vizinhos(
                ponto
            )
        )

    return protegidas


def mapa_possui_conectividade(
    paredes
):

    pontos = (
        obter_pontos_obrigatorios()
    )

    origem = (
        pontos[0]
    )

    fila = deque(
        [origem]
    )

    visitados = {
        origem
    }

    while fila:

        atual = (
            fila.popleft()
        )

        for vizinho in (
            obter_vizinhos(
                atual
            )
        ):

            if (
                vizinho
                in paredes
            ):
                continue

            if (
                vizinho
                in visitados
            ):
                continue

            visitados.add(
                vizinho
            )

            fila.append(
                vizinho
            )

    return all(
        ponto
        in visitados

        for ponto
        in pontos
    )


def gerar_paredes():

    protegidas = (
        obter_celulas_protegidas()
    )

    candidatas = [
        (x, y)

        for x
        in range(TAMANHO_GRID)

        for y
        in range(TAMANHO_GRID)

        if (
            (x, y)
            not in protegidas
        )
    ]

    quantidade = int(
        TAMANHO_GRID
        * TAMANHO_GRID
        * PERCENTUAL_PAREDES
    )

    for _ in range(500):

        paredes = set(
            random.sample(
                candidatas,
                quantidade
            )
        )

        if (
            mapa_possui_conectividade(
                paredes
            )
        ):

            return paredes

    raise RuntimeError(
        "Não foi possível gerar "
        "um mapa válido."
    )


PAREDES = gerar_paredes()