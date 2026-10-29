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

from auditoria import (
    Auditoria
)


if __name__ == "__main__":

    # =================================
    # ADMIN
    # =================================

    admin = Admin()

    admin.permit_print = False

    # False:
    # mostra somente nossa auditoria.
    #
    # True:
    # mostra também os logs internos
    # do MASPY para depuração.
    MOSTRAR_LOG_MASPY = False

    admin.permit_print = (
        MOSTRAR_LOG_MASPY
    )

    admin.show_exec = False

    admin.agt_sh_exec = False
    admin.agt_sh_cycle = False
    admin.agt_sh_prct = False
    admin.agt_sh_slct = False

    admin.env_sh_exec = False
    admin.ch_sh_exec = False

    # =================================
    # AMBIENTE
    # =================================

    ambiente = (
        AmbienteViolenciaDomestica(
            CHAMADOS,
            PAREDES
        )
    )

    # =================================
    # CANAL
    # =================================

    canal = Channel(
        "Cooperacao"
    )

    # =================================
    # AGENTES
    # =================================

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

    # =================================
    # CONEXÕES
    # =================================

    admin.connect_to(
        agentes,
        [
            ambiente,
            canal
        ]
    )

    # =================================
    # AUDITORIA
    # =================================

    Auditoria.iniciar(
        ambiente,
        agentes
    )

    # =================================
    # MASPY
    # =================================

    thread_maspy = (
        threading.Thread(
            target=admin.start_system,
            daemon=True
        )
    )

    thread_maspy.start()

    # =================================
    # GUI
    # =================================

    interface = Visualizacao(
        ambiente,
        agentes
    )

    interface.executar()