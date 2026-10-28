from maspy import *

from agentes.agente_preventivo import AgentePreventivo
from ambiente.ambiente import AmbienteViolenciaDomestica
from dados.regioes import REGIOES


if __name__ == "__main__":

    ambiente = AmbienteViolenciaDomestica(REGIOES)

    agente_1 = AgentePreventivo("Equipe1")
    agente_2 = AgentePreventivo("Equipe2")

    Admin().connect_to(
        [agente_1, agente_2],
        ambiente
    )

    agente_1.add(
        Goal("atender_regiao")
    )

    agente_2.add(
        Goal("atender_regiao")
    )

    Admin().start_system()