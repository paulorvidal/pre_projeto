class Terminal:
    def __init__(self, equipes):
        self.equipes = sorted(equipes)
        self.rodada_exibida = None
        self.fila_exibida = None

    def registrar(self, rodada, evento, mensagem):
        if evento == "FILA":
            if mensagem == self.fila_exibida:
                return
            self.fila_exibida = mensagem

        if rodada != self.rodada_exibida:
            print(f"\nRodada {rodada:02d}", flush=True)
            self.rodada_exibida = rodada

        for nome in self.equipes:
            mensagem = mensagem.replace(nome, nome.rsplit("_", 1)[0])

        print(f"  {evento:<10} {mensagem}", flush=True)

    def exibir_resumo(self, chamados):
        print("\nResultado final (tempos em rodadas)")
        print(f"{'Chamado':<8} {'Prioridade':<17} {'Equipe':<7} "
              f"{'Entrada':>7} {'Despacho':>8} {'Chegada':>7} "
              f"{'Espera':>7} {'Resposta':>8}")

        for c in chamados:
            prioridade = f"{c.prioridade}/10 {c.nivel}"
            equipe = c.equipe.rsplit("_", 1)[0]
            espera = c.despacho - c.entrada
            resposta = c.chegada - c.entrada
            print(f"{c.id:<8} {prioridade:<17} {equipe:<7} "
                  f"{c.entrada:>7} {c.despacho:>8} {c.chegada:>7} "
                  f"{espera:>7} {resposta:>8}", flush=True)
