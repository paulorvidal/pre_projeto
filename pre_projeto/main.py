import threading

from maspy import *

from agentes.agente_hibrido import (
    AgenteHibrido
)

from ambiente.ambiente import (
    AmbienteViolenciaDomestica
)

from dados.chamados import (
    CHAMADOS,
    LIMIAR_URGENCIA,
    PAREDES
)

from visualizacao.gui import (
    Visualizacao
)


if __name__ == "__main__":

    # -----------------------------
    # AMBIENTE
    # -----------------------------

    ambiente = (
        AmbienteViolenciaDomestica(
            CHAMADOS,
            PAREDES
        )
    )

    # -----------------------------
    # COMUNICAÇÃO
    # -----------------------------

    canal = Channel(
        "Cooperacao"
    )

    # -----------------------------
    # AGENTES
    # -----------------------------

    equipe_1 = AgenteHibrido(
        "Equipe1",
        LIMIAR_URGENCIA
    )

    equipe_2 = AgenteHibrido(
        "Equipe2",
        LIMIAR_URGENCIA
    )

    agentes = [
        equipe_1,
        equipe_2
    ]

    # -----------------------------
    # CONEXÕES
    # -----------------------------

    admin = Admin()

    admin.connect_to(
        agentes,
        [
            ambiente,
            canal
        ]
    )

    # -----------------------------
    # MASPY
    # -----------------------------

    thread_maspy = (
        threading.Thread(
            target=admin.start_system,
            daemon=True
        )
    )

    thread_maspy.start()

    # -----------------------------
    # GUI
    # -----------------------------

    interface = Visualizacao(
        ambiente,
        agentes
    )

    interface.executar()