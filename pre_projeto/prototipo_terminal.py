import argparse

from maspy import Admin, Channel

from despacho.agentes.despachante import Despachante
from despacho.agentes.equipe import Equipe
from despacho.ambiente import Grade
from despacho.cenario import ALTURA, CANAL, LARGURA, MAPA, PAREDES, carregar_cenario
from despacho.terminal import Terminal


def main():
    parser = argparse.ArgumentParser(description="Simulação de despacho em uma grade")
    parser.add_argument("--fifo", action="store_true", help="Atende por ordem de entrada")
    parser.add_argument("--visual", action="store_true", help="Abre a reprodução no Pygame")
    args = parser.parse_args()

    try:
        cadastro, chamados = carregar_cenario()
    except (OSError, ValueError, KeyError, TypeError) as erro:
        parser.error(f"Dados simulados inválidos: {erro}")

    admin = Admin()
    grade = Grade(MAPA, {equipe.id: equipe.base for equipe in cadastro})
    canal = Channel(CANAL)
    equipes = [Equipe(dados) for dados in cadastro]
    nomes = [e.my_name for e in equipes]
    terminal = Terminal(nomes)

    historico = None
    if args.visual:
        from despacho.visualizacao import Historico, exibir

        historico = Historico(grade)

    despachante = Despachante(chamados, nomes, args.fifo, terminal, historico)

    admin.connect_to(equipes, [grade, canal])
    admin.connect_to(despachante, canal)
    admin.block_prints()

    politica = "Ordem de chegada (FIFO)" if args.fifo else "Prioridade da ocorrência"
    print(f"Simulação de despacho | {politica} | Registros fictícios")
    for equipe in equipes:
        dados = equipe.dados
        print(f"{dados.id} · {dados.nome} | {dados.especialidade} | {dados.integrantes} integrantes | Base {dados.base}")
    print(f"Mapa conhecido pelas equipes: {LARGURA} x {ALTURA}, {len(PAREDES)} paredes")

    admin.start_system()
    if despachante.erro:
        raise SystemExit(1)
    if historico is not None and historico.quadros:
        exibir(historico.quadros, fifo=args.fifo, equipes=cadastro)


if __name__ == "__main__":
    main()