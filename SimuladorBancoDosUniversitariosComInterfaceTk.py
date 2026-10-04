from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
import re
import tkinter as tk
from tkinter import messagebox
from typing import Any, Optional


"""
AD2 - 2025.1 - PROGRAMAÇÃO COM INTERFACES GRÁFICAS
Versão revisada e refatorada.

Principais correções:
- remove estados duplicados/inconsistentes do Administrador;
- garante número de conta único durante a execução;
- corrige aprovação/rejeição/cancelamento de exclusão;
- corrige saque com cheque especial e o bug de btnSacarHoje inexistente;
- programação de operações agora realmente agenda a operação;
- histórico usa estrutura de dados, evitando parsing frágil de strings;
- extrato filtra datas de forma consistente;
- evita exibir senha em texto aberto;
- reduz criação acumulada de Frames e centraliza a troca de telas;
- trata ausência da imagem da interface sem encerrar o programa.
"""


AGENCIA = "0219"


@dataclass
class Agendamento:
    tipo: str
    data: date
    valor: float
    conta_destino: Optional[str] = None


class Conta:
    numeroAgencia = AGENCIA
    _ultimo_sequencial = 10000

    def __init__(self, titularConta: str, enderecoTitular: str, cpf: str, senha: str, prefixo: str = "XX"):
        self.numeroConta = Conta._gerar_numero(prefixo)
        self.login = self.numeroConta
        self.saldoAtual = 0.0
        self.historico: list[dict[str, Any]] = []
        self.agendamentos: list[Agendamento] = []
        self.solicitacaoExclusao: Optional[dict[str, Any]] = None

        self.titularConta = self._validar_nome(titularConta)
        self.cpf = self.validarFormatarCPF(cpf)
        self.enderecoTitular = self._validar_endereco(enderecoTitular)
        self.senha = self.validarSenha(senha)

    @classmethod
    def _gerar_numero(cls, prefixo: str) -> str:
        # Usa explicitamente o contador da classe-base para que CC e CP compartilhem
        # a mesma sequência e nunca gerem o mesmo número.
        numero = Conta._ultimo_sequencial
        Conta._ultimo_sequencial += 1
        digito = numero % 10
        return f"{prefixo}{numero:05d}-{digito}"

    @staticmethod
    def _normalizar_data(valor: date | datetime | str) -> date:
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        return datetime.strptime(str(valor), "%d/%m/%Y").date()

    @staticmethod
    def _validar_nome(nome: str) -> str:
        nome = str(nome).strip()
        if not (3 <= len(nome) <= 100):
            raise ValueError("Nome inválido. Informe nome e sobrenome.")
        if "  " in nome:
            raise ValueError("Nome inválido. Não use espaços duplicados.")
        if len(nome.split()) < 2:
            raise ValueError("Informe pelo menos nome e sobrenome.")

        # Letras Unicode + espaço + apóstrofo + ponto + hífen.
        for char in nome:
            if not (char.isalpha() or char in " .'-"):
                raise ValueError(
                    "Nome inválido. Use apenas letras, espaços, hífen, apóstrofo ou ponto."
                )
        return nome.title()

    @staticmethod
    def _validar_endereco(endereco: str) -> str:
        endereco = str(endereco).strip()
        if not endereco:
            raise ValueError("O endereço não pode ficar vazio.")
        if endereco.replace(" ", "").isdigit():
            raise ValueError("O endereço não pode conter apenas números.")
        permitidos = {",", ".", "-", "/", " "}
        for char in endereco:
            if not (char.isalpha() or char.isdigit() or char in permitidos):
                raise ValueError("Endereço contém caracteres não permitidos.")
        return endereco

    @staticmethod
    def validarFormatarCPF(cpf: str) -> str:
        cpf_limpo = re.sub(r"\D", "", str(cpf))
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve conter 11 dígitos.")
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

    @staticmethod
    def validarCpfDepositante(cpf: str) -> Optional[str]:
        cpf_limpo = re.sub(r"\D", "", str(cpf))
        if len(cpf_limpo) != 11:
            return None
        return cpf_limpo

    @staticmethod
    def validarSenha(senha: str) -> str:
        senha = str(senha).strip()
        if len(senha) != 6 or not senha.isdigit():
            raise ValueError("Senha deve conter exatamente 6 dígitos numéricos.")
        return senha

    def adicionaTransacao(
        self,
        tipo: str,
        valor: float,
        data_transacao: date | datetime | str,
        descricao: str = "",
    ) -> None:
        data_obj = self._normalizar_data(data_transacao)
        self.historico.append(
            {
                "tipo": tipo,
                "valor": float(valor),
                "data": data_obj,
                "descricao": descricao,
            }
        )

    # Compatibilidade com chamadas antigas.
    def adicionaTransacaoHistorico(self, transacao: str) -> None:
        # Mantém uma única API interna estruturada. Este método existe para não quebrar
        # código externo que ainda envie uma string.
        self.historico.append(
            {
                "tipo": "Registro",
                "valor": 0.0,
                "data": date.today(),
                "descricao": str(transacao),
            }
        )

    def formatar_transacao(self, transacao: dict[str, Any]) -> str:
        valor = transacao["valor"]
        data_str = transacao["data"].strftime("%d/%m/%Y")
        tipo = transacao["tipo"]
        if tipo in {"Taxa de manutenção projetada", "Rendimento projetado", "Rendimento total projetado"}:
            return f"{tipo} - R$ {abs(valor):.2f} - {data_str}"
        if tipo == "Saldo projetado":
            return f"{tipo}: R$ {valor:.2f} - {data_str} - {transacao.get('descricao', '')}".rstrip(" -")
        texto = f"{tipo} - R$ {abs(valor):.2f} - {data_str}"
        if transacao.get("descricao"):
            texto += f" - {transacao['descricao']}"
        return texto

    def saldo_disponivel(self) -> float:
        if isinstance(self, ContaCorrente):
            return self.saldoAtual + self.limiteChequeEspecial
        return self.saldoAtual

    def solicitarExclusaoConta(self) -> None:
        if self.solicitacaoExclusao is not None:
            raise ValueError("Já existe uma solicitação ativa para esta conta.")
        solicitacao = {
            "numero_conta": self.numeroConta,
            "titular": self.titularConta,
            "tipo_conta": self.__class__.__name__,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "status": "pendente",
        }
        Administrador.adicionarSolicitacao(solicitacao)
        self.solicitacaoExclusao = solicitacao

    def agendar(self, tipo: str, valor: float, data_agendada: date, conta_destino: Optional[str] = None) -> None:
        if data_agendada <= date.today():
            raise ValueError("A data agendada deve ser futura.")
        if valor <= 0:
            raise ValueError("O valor deve ser positivo.")
        self.agendamentos.append(
            Agendamento(tipo=tipo, data=data_agendada, valor=float(valor), conta_destino=conta_destino)
        )

    def cancelar_agendamento(self, indice: int) -> None:
        try:
            self.agendamentos.pop(indice)
        except IndexError as exc:
            raise ValueError("Agendamento inválido.") from exc

    @staticmethod
    def depositar(conta: "Conta", valor: float, data_transacao: date, descricao: str = "") -> None:
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser positivo.")

        valor_original = valor
        if isinstance(conta, ContaCorrente):
            # Primeiro recompõe eventual cheque especial utilizado.
            deficit = conta.limiteChequeEspecialOriginal - conta.limiteChequeEspecial
            if deficit > 0:
                recomposicao = min(valor, deficit)
                conta.limiteChequeEspecial += recomposicao
                valor -= recomposicao

        conta.saldoAtual += valor
        conta.adicionaTransacao("Depósito", valor_original, data_transacao, descricao)

    @staticmethod
    def sacar(conta: "Conta", valor: float, data_transacao: date, permitir_cheque: bool = True) -> tuple[bool, float]:
        if valor <= 0:
            return False, 0.0

        if isinstance(conta, ContaPoupanca):
            if valor > conta.saldoAtual:
                return False, 0.0
            conta.saldoAtual -= valor
            conta.adicionaTransacao("Saque", valor, data_transacao)
            return True, 0.0

        # Conta corrente.
        if valor <= conta.saldoAtual:
            conta.saldoAtual -= valor
            conta.adicionaTransacao("Saque", valor, data_transacao)
            return True, 0.0

        valor_cheque = valor - conta.saldoAtual
        if not permitir_cheque or valor_cheque > conta.limiteChequeEspecial:
            return False, valor_cheque

        conta.saldoAtual -= valor
        conta.limiteChequeEspecial -= valor_cheque
        conta.adicionaTransacao(
            "Saque com cheque especial",
            valor,
            data_transacao,
            f"Cheque especial utilizado: R$ {valor_cheque:.2f}",
        )
        return True, valor_cheque


class ContaCorrente(Conta):
    TAXA_MANUTENCAO = 15.00

    def __init__(self, titularConta: str, enderecoTitular: str, cpf: str, senha: str):
        super().__init__(titularConta, enderecoTitular, cpf, senha, prefixo="CC")
        self.login = self.numeroConta
        self.limiteChequeEspecialOriginal = 100.00
        self.limiteChequeEspecial = self.limiteChequeEspecialOriginal
        self.tipoContaCriada = "CORRENTE"
        Administrador.adicionarContaCorrente(self)


class ContaPoupanca(Conta):
    TAXA_RENDIMENTO = 0.005
    DIAS_ANIVERSARIO = 30

    def __init__(self, titularConta: str, enderecoTitular: str, cpf: str, senha: str):
        super().__init__(titularConta, enderecoTitular, cpf, senha, prefixo="CP")
        self.login = self.numeroConta
        self.tipoContaCriada = "POUPANÇA"
        Administrador.adicionarContaPoupanca(self)


class Administrador:
    __usuario = "Admin"
    __codigo = "000"
    __contasCorrenteCadastradas: list[ContaCorrente] = []
    __contasPoupancaCadastradas: list[ContaPoupanca] = []
    __solicitacoesPendentes: list[dict[str, Any]] = []

    @classmethod
    def getUsuario(cls) -> str:
        return cls.__usuario

    @classmethod
    def getCodigo(cls) -> str:
        return cls.__codigo

    @classmethod
    def adicionarContaCorrente(cls, conta: ContaCorrente) -> None:
        cls.__contasCorrenteCadastradas.append(conta)

    @classmethod
    def adicionarContaPoupanca(cls, conta: ContaPoupanca) -> None:
        cls.__contasPoupancaCadastradas.append(conta)

    @classmethod
    def get__contasCorrenteCadastradas(cls) -> list[ContaCorrente]:
        return cls.__contasCorrenteCadastradas.copy()

    @classmethod
    def get__contasPoupancaCadastradas(cls) -> list[ContaPoupanca]:
        return cls.__contasPoupancaCadastradas.copy()

    @classmethod
    def todasContas(cls) -> list[Conta]:
        return cls.__contasCorrenteCadastradas.copy() + cls.__contasPoupancaCadastradas.copy()

    @classmethod
    def buscarConta(cls, numeroConta: str) -> Optional[Conta]:
        numeroConta = str(numeroConta).strip().upper()
        for conta in cls.todasContas():
            if conta.numeroConta.upper() == numeroConta:
                return conta
        return None

    @classmethod
    def verificaSeExisteCadastro(cls, numeroConta: str, agencia: str) -> Optional[Conta]:
        agencia = str(agencia).strip()
        numeroConta = str(numeroConta).strip().upper()
        conta = cls.buscarConta(numeroConta)
        if conta and conta.numeroAgencia == agencia:
            return conta
        return None

    @classmethod
    def excluirContas(cls, numeroConta: str) -> None:
        conta = cls.buscarConta(numeroConta)
        if conta is None:
            raise ValueError("Conta não encontrada.")
        if isinstance(conta, ContaCorrente):
            cls.__contasCorrenteCadastradas.remove(conta)
        else:
            cls.__contasPoupancaCadastradas.remove(conta)

    @classmethod
    def adicionarSolicitacao(cls, solicitacao: dict[str, Any]) -> None:
        numero = solicitacao["numero_conta"]
        if any(s["numero_conta"] == numero for s in cls.__solicitacoesPendentes):
            raise ValueError("Já existe solicitação pendente para esta conta.")
        cls.__solicitacoesPendentes.append(solicitacao)

    @classmethod
    def listarSolicitacoes(cls) -> list[str]:
        return [
            f"ID: {idx} | Conta: {s['numero_conta']} | Titular: {s['titular']} | "
            f"Tipo: {s['tipo_conta']} | Data: {s['data']}"
            for idx, s in enumerate(cls.__solicitacoesPendentes, 1)
        ]

    @classmethod
    def aprovarExclusao(cls, id_solicitacao: int) -> str:
        if id_solicitacao < 1 or id_solicitacao > len(cls.__solicitacoesPendentes):
            raise ValueError("ID de solicitação inválido.")
        solicitacao = cls.__solicitacoesPendentes.pop(id_solicitacao - 1)
        numero = solicitacao["numero_conta"]
        conta = cls.buscarConta(numero)
        if conta is None:
            raise ValueError("A conta associada à solicitação não existe mais.")
        cls.excluirContas(numero)
        conta.solicitacaoExclusao = None
        return f"Conta {numero} excluída com sucesso."

    @classmethod
    def rejeitarExclusao(cls, id_solicitacao: int) -> str:
        if id_solicitacao < 1 or id_solicitacao > len(cls.__solicitacoesPendentes):
            raise ValueError("ID de solicitação inválido.")
        solicitacao = cls.__solicitacoesPendentes.pop(id_solicitacao - 1)
        conta = cls.buscarConta(solicitacao["numero_conta"])
        if conta:
            conta.solicitacaoExclusao = None
        return f"Solicitação da conta {solicitacao['numero_conta']} rejeitada."

    @classmethod
    def cancelarSolicitacao(cls, numero_conta: str) -> None:
        encontrou = False
        restante = []
        for solicitacao in cls.__solicitacoesPendentes:
            if solicitacao["numero_conta"] == numero_conta:
                encontrou = True
            else:
                restante.append(solicitacao)
        cls.__solicitacoesPendentes = restante
        if not encontrou:
            raise ValueError("Não existe solicitação pendente para esta conta.")

    @classmethod
    def verificarStatusExclusao(cls, numero_conta: str) -> str:
        pendente = any(s["numero_conta"] == numero_conta for s in cls.__solicitacoesPendentes)
        return "Solicitação em análise (pendente)" if pendente else "Conta ativa (sem solicitação)"

    @classmethod
    def alterarEnderecoPorNome(cls, titularConta: str, novoEndereco: str, cpf: str) -> int:
        novoEndereco = Conta._validar_endereco(novoEndereco)
        cpf_normalizado = Conta.validarFormatarCPF(cpf)
        alteradas = 0
        for conta in cls.todasContas():
            if conta.titularConta == titularConta and conta.cpf == cpf_normalizado:
                conta.enderecoTitular = novoEndereco
                alteradas += 1
        return alteradas

    @classmethod
    def processarAgendamentos(cls, data_referencia: Optional[date] = None) -> list[str]:
        data_ref = data_referencia or date.today()
        mensagens: list[str] = []

        # Cópia evita alteração da lista durante iteração.
        for conta in cls.todasContas():
            vencidos = [a for a in conta.agendamentos if a.data <= data_ref]
            conta.agendamentos = [a for a in conta.agendamentos if a.data > data_ref]

            for ag in sorted(vencidos, key=lambda x: x.data):
                if ag.tipo == "Depósito":
                    Conta.depositar(conta, ag.valor, ag.data, "Operação agendada")
                    mensagens.append(f"Depósito agendado executado na conta {conta.numeroConta}.")
                    continue

                if ag.tipo == "Saque":
                    ok, usado = Conta.sacar(conta, ag.valor, ag.data, permitir_cheque=True)
                    if ok:
                        mensagens.append(f"Saque agendado executado na conta {conta.numeroConta}.")
                    else:
                        conta.adicionaTransacao(
                            "Agendamento não executado",
                            0.0,
                            ag.data,
                            f"Saque de R$ {ag.valor:.2f} sem saldo disponível",
                        )
                        mensagens.append(f"Saque agendado não executado na conta {conta.numeroConta}.")
                    continue

                if ag.tipo == "Transferência":
                    destino = cls.buscarConta(ag.conta_destino or "")
                    if destino is None or destino is conta:
                        conta.adicionaTransacao(
                            "Agendamento não executado",
                            0.0,
                            ag.data,
                            "Conta destino inválida",
                        )
                        mensagens.append(f"Transferência agendada não executada: destino inválido ({conta.numeroConta}).")
                        continue

                    ok, usado = Conta.sacar(conta, ag.valor, ag.data, permitir_cheque=True)
                    if not ok:
                        conta.adicionaTransacao(
                            "Agendamento não executado",
                            0.0,
                            ag.data,
                            f"Transferência de R$ {ag.valor:.2f} sem saldo disponível",
                        )
                        mensagens.append(f"Transferência agendada não executada na conta {conta.numeroConta}.")
                        continue

                    destino.saldoAtual += ag.valor
                    destino.adicionaTransacao(
                        "Transferência recebida",
                        ag.valor,
                        ag.data,
                        f"De: {conta.numeroConta}",
                    )
                    # Acrescenta o detalhe à última transação da origem.
                    conta.historico[-1]["descricao"] += f" | Para: {destino.numeroConta}"
                    mensagens.append(f"Transferência agendada executada: {conta.numeroConta} → {destino.numeroConta}.")

        return mensagens

    @classmethod
    def resetarDados(cls) -> None:
        # Útil para testes automatizados.
        cls.__contasCorrenteCadastradas.clear()
        cls.__contasPoupancaCadastradas.clear()
        cls.__solicitacoesPendentes.clear()
        Conta._ultimo_sequencial = 10000


def gerar_rendimentos_poupanca(conta: ContaPoupanca, data_inicial: date, data_final: date) -> list[dict[str, Any]]:
    """Projeta rendimentos de 0,5% a cada 30 dias sobre depósitos/entradas."""
    projetados: list[dict[str, Any]] = []
    for transacao in conta.historico:
        if transacao["tipo"] not in {"Depósito", "Transferência recebida"}:
            continue
        origem = transacao["data"]
        valor = transacao["valor"]
        ciclo = 1
        while True:
            aniversario = origem + timedelta(days=30 * ciclo)
            if aniversario > data_final:
                break
            if aniversario >= data_inicial:
                rendimento = valor * conta.TAXA_RENDIMENTO
                projetados.append(
                    {
                        "tipo": "Rendimento projetado",
                        "valor": rendimento,
                        "data": aniversario,
                        "descricao": f"Origem: {origem.strftime('%d/%m/%Y')}",
                    }
                )
            ciclo += 1
    return projetados


def gerar_taxas_corrente(conta: ContaCorrente, data_inicial: date, data_final: date) -> list[dict[str, Any]]:
    taxas: list[dict[str, Any]] = []
    ano, mes = data_inicial.year, data_inicial.month
    data_taxa = date(ano, mes, 5)
    if data_taxa < data_inicial:
        if mes == 12:
            data_taxa = date(ano + 1, 1, 5)
        else:
            data_taxa = date(ano, mes + 1, 5)

    while data_taxa <= data_final:
        taxas.append(
            {
                "tipo": "Taxa de manutenção projetada",
                "valor": conta.TAXA_MANUTENCAO,
                "data": data_taxa,
                "descricao": "Projeção",
            }
        )
        if data_taxa.month == 12:
            data_taxa = date(data_taxa.year + 1, 1, 5)
        else:
            data_taxa = date(data_taxa.year, data_taxa.month + 1, 5)
    return taxas


def transferir(conta_origem: Conta, conta_destino: Conta, valor: float, data_transacao: date, permitir_cheque: bool = True) -> tuple[bool, float]:
    if valor <= 0:
        return False, 0.0
    if conta_origem is conta_destino:
        return False, 0.0

    ok, usado = Conta.sacar(conta_origem, valor, data_transacao, permitir_cheque=permitir_cheque)
    if not ok:
        return False, usado

    conta_destino.saldoAtual += valor
    conta_destino.adicionaTransacao(
        "Transferência recebida",
        valor,
        data_transacao,
        f"De: {conta_origem.numeroConta}",
    )
    conta_origem.historico[-1]["descricao"] += f" | Para: {conta_destino.numeroConta}"
    return True, usado


class Janela:
    BG = "#E3F2F9"
    PRIMARY = "#78D1DE"
    DANGER = "#D26060"
    TEXT = "#223C5E"

    def __init__(self):
        self.janelaPrincipal = tk.Tk()
        self.janelaPrincipal.configure(bg=self.BG)
        self.janelaPrincipal.geometry("520x680")
        self.janelaPrincipal.minsize(520, 680)
        self.janelaPrincipal.title("Banco dos Universitários")
        self.contaLogin: Optional[Conta] = None
        self.tipoConta: Optional[str] = None
        self.telaAtual: Optional[tk.Frame] = None
        self.logo = self._carregar_logo()
        self.criarMenuPrincipal()
        self.configurarProtecaoTeclado()

    def _carregar_logo(self):
        try:
            return tk.PhotoImage(file="ImagemTelaPrincipal.png")
        except tk.TclError:
            return None

    def _nova_tela(self) -> tk.Frame:
        if self.telaAtual is not None and self.telaAtual.winfo_exists():
            self.telaAtual.destroy()
        self.telaAtual = tk.Frame(self.janelaPrincipal, bg=self.BG, padx=20, pady=20)
        self.telaAtual.pack(fill="both", expand=True)
        return self.telaAtual

    def _cabecalho(self, parent: tk.Frame, titulo: str) -> None:
        if self.logo is not None:
            tk.Label(parent, image=self.logo, bg=self.BG, bd=0).pack(pady=(0, 10))
        tk.Label(
            parent,
            text=titulo,
            bg=self.BG,
            font=("Arial", 13, "bold"),
            fg=self.TEXT,
        ).pack(pady=(0, 15))

    def _botao(self, parent, texto, comando, destaque=True, danger=False):
        bg = self.DANGER if danger else (self.PRIMARY if destaque else self.BG)
        return tk.Button(
            parent,
            text=texto,
            bg=bg,
            activebackground=bg,
            height=2,
            width=44,
            command=comando,
            relief="groove",
        )

    def _rotulo(self, parent, texto):
        tk.Label(parent, text=texto, bg=self.BG, fg=self.TEXT).pack(anchor="w", pady=(6, 3))

    def configurarProtecaoTeclado(self):
        # Não bloqueia o encerramento normal do programa; apenas atalhos usados na atividade.
        self.janelaPrincipal.bind("<Control-c>", lambda e: "break")
        self.janelaPrincipal.bind("<Control-q>", lambda e: "break")
        self.janelaPrincipal.bind("<Escape>", lambda e: "break")

    def exibirJanela(self):
        self.janelaPrincipal.mainloop()

    def criarMenuPrincipal(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "BANCO DOS UNIVERSITÁRIOS")
        tk.Label(
            tela,
            text="Soluções pensadas para estudantes",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 10),
        ).pack(pady=(0, 20))
        self._botao(tela, "ABERTURA DE CONTA", self.criarMenuAberturaDeConta).pack(pady=8)
        self._botao(tela, "ACESSAR CONTA", self.criarMenuLogin, destaque=False).pack(pady=8)
        self._botao(tela, "DEPÓSITO EXPRESS", self.criarMenuDepositoExpress, destaque=False).pack(pady=8)
        self._botao(tela, "SAIR", self.janelaPrincipal.destroy, danger=True).pack(pady=8)

    # ---------------- LOGIN ----------------
    def criarMenuLogin(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "ESCOLHA O TIPO DE ACESSO")
        self._botao(tela, "CLIENTE", self.exibirMenuLoginCliente).pack(pady=8)
        self._botao(tela, "ADMINISTRADOR", self.exibirMenuLoginAdministrador).pack(pady=8)
        self._botao(tela, "VOLTAR", self.criarMenuPrincipal, destaque=False).pack(pady=8)

    def exibirMenuLoginAdministrador(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "ÁREA DO ADMINISTRADOR")
        self._rotulo(tela, "Nº de identificação (dica: 000):")
        self.recebeCodigoIdentificacaoAdm = tk.Entry(tela, show="*")
        self.recebeCodigoIdentificacaoAdm.pack(fill="x", ipady=8)
        self._botao(tela, "ACESSAR CONTA", self.validaLoginAdm).pack(pady=18)
        self._botao(tela, "VOLTAR", self.criarMenuLogin, destaque=False).pack(pady=8)

    def validaLoginAdm(self):
        codigo = self.recebeCodigoIdentificacaoAdm.get().strip()
        if not codigo:
            messagebox.showerror("Erro", "Digite o número de identificação do administrador.")
            return
        if codigo == Administrador.getCodigo():
            self.exibirMenuAdministrador()
        else:
            messagebox.showerror("Erro", "Login inválido.")

    def exibirMenuLoginCliente(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "ÁREA DO CLIENTE")
        self._rotulo(tela, "Agência:")
        self.recebeAgenciaCliente = tk.Entry(tela)
        self.recebeAgenciaCliente.pack(fill="x", ipady=8)
        self._rotulo(tela, "Número da conta (CCXXXXX-X ou CPXXXXX-X):")
        self.recebeNumContaCliente = tk.Entry(tela)
        self.recebeNumContaCliente.pack(fill="x", ipady=8)
        self._botao(tela, "ACESSAR CONTA", self.validaLoginCliente).pack(pady=18)
        self._botao(tela, "VOLTAR", self.criarMenuLogin, destaque=False).pack(pady=8)

    def validaLoginCliente(self):
        agencia = self.recebeAgenciaCliente.get().strip()
        numero = self.recebeNumContaCliente.get().strip().upper()
        if not agencia or not numero:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        if agencia != AGENCIA:
            messagebox.showerror("Erro", "Agência inválida.")
            return

        self.contaLogin = Administrador.verificaSeExisteCadastro(numero, agencia)
        if self.contaLogin is None:
            messagebox.showerror("Erro", "Conta não encontrada.")
            return

        mensagens = Administrador.processarAgendamentos()
        self.exibirMenuCliente()
        if mensagens:
            messagebox.showinfo("Agendamentos", "\n".join(mensagens[:8]))

    # ---------------- ABERTURA DE CONTA ----------------
    def criarMenuAberturaDeConta(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "SELECIONE O TIPO DE CONTA")
        self._botao(tela, "CONTA CORRENTE", lambda: self.criarMenuAberturaDeContaCorrentePoupanca("corrente")).pack(pady=8)
        self._botao(tela, "CONTA POUPANÇA", lambda: self.criarMenuAberturaDeContaCorrentePoupanca("poupanca")).pack(pady=8)
        self._botao(tela, "VOLTAR", self.criarMenuPrincipal, destaque=False).pack(pady=8)

    def criarMenuAberturaDeContaCorrentePoupanca(self, tipoConta):
        self.tipoConta = tipoConta
        tela = self._nova_tela()
        self._cabecalho(tela, f"ABERTURA DE CONTA {'CORRENTE' if tipoConta == 'corrente' else 'POUPANÇA'}")

        self._rotulo(tela, "Nome completo:")
        self.recebeNomeCompleto = tk.Entry(tela)
        self.recebeNomeCompleto.pack(fill="x", ipady=8)
        self._rotulo(tela, "Endereço:")
        self.recebeEndereco = tk.Entry(tela)
        self.recebeEndereco.pack(fill="x", ipady=8)
        self._rotulo(tela, "CPF:")
        self.recebeCPF = tk.Entry(tela)
        self.recebeCPF.pack(fill="x", ipady=8)
        self._rotulo(tela, "Senha numérica (6 dígitos):")
        self.recebeSenha = tk.Entry(tela, show="*")
        self.recebeSenha.pack(fill="x", ipady=8)

        self._botao(tela, "CRIAR CONTA", self.funcaoCriarContaCorrentePoupanca).pack(pady=18)
        self._botao(tela, "VOLTAR", self.criarMenuAberturaDeConta, destaque=False).pack(pady=8)

    def funcaoCriarContaCorrentePoupanca(self):
        nome = self.recebeNomeCompleto.get().strip()
        endereco = self.recebeEndereco.get().strip()
        cpf = self.recebeCPF.get().strip()
        senha = self.recebeSenha.get().strip()
        if not all([nome, endereco, cpf, senha]):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        try:
            if self.tipoConta == "corrente":
                self.contaLogin = ContaCorrente(nome, endereco, cpf, senha)
            else:
                self.contaLogin = ContaPoupanca(nome, endereco, cpf, senha)
            self.exibirTelaPosCadastro()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    def exibirTelaPosCadastro(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "CONTA CADASTRADA COM SUCESSO!")
        tk.Label(
            tela,
            text=(
                f"{self.contaLogin.titularConta.upper()}, é um prazer ter você com a gente.\n"
                "Utilize os dados abaixo para acessar sua conta."
            ),
            bg=self.BG,
            fg=self.TEXT,
            justify="center",
            wraplength=450,
        ).pack(pady=10)
        for rotulo, valor in (("AGÊNCIA", self.contaLogin.numeroAgencia), ("NÚMERO DA CONTA", self.contaLogin.numeroConta)):
            self._rotulo(tela, rotulo)
            campo = tk.Entry(tela, state="normal")
            campo.insert(0, valor)
            campo.config(state="readonly")
            campo.pack(fill="x", ipady=7)
        self._botao(tela, "VOLTAR AO MENU PRINCIPAL", self.criarMenuPrincipal).pack(pady=25)

    # ---------------- ADMIN ----------------
    def exibirMenuAdministrador(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "BEM-VINDO, ADMINISTRADOR")
        self._botao(tela, "EXIBIR SOLICITAÇÕES", self.criarMenuAprovacaoExclusao).pack(pady=8)
        self._botao(tela, "GERENCIAMENTO DE CONTAS", self.exibirGerenciamentoDeConntasAdministrador).pack(pady=8)
        self._botao(tela, "VOLTAR AO MENU PRINCIPAL", self.criarMenuPrincipal, destaque=False).pack(pady=8)

    def criarMenuAprovacaoExclusao(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "SOLICITAÇÕES DE EXCLUSÃO")
        solicitacoes = Administrador.listarSolicitacoes()
        if solicitacoes:
            for item in solicitacoes:
                tk.Label(tela, text=item, bg=self.BG, fg=self.TEXT, justify="left", wraplength=470).pack(anchor="w", pady=4)
        else:
            tk.Label(tela, text="Nenhuma solicitação pendente.", bg=self.BG, fg=self.TEXT).pack(pady=20)

        self._rotulo(tela, "ID da solicitação:")
        self.entryIdSolicitacao = tk.Entry(tela)
        self.entryIdSolicitacao.pack(fill="x", ipady=8)
        frame = tk.Frame(tela, bg=self.BG)
        frame.pack(fill="x", pady=18)
        self._botao(frame, "APROVAR", lambda: self.processarAprovacao(True)).pack(side="left", expand=True, fill="x", padx=4)
        self._botao(frame, "REJEITAR", lambda: self.processarAprovacao(False), danger=True).pack(side="left", expand=True, fill="x", padx=4)
        self._botao(tela, "VOLTAR", self.exibirMenuAdministrador, destaque=False).pack(pady=8)

    def processarAprovacao(self, aprovar: bool):
        try:
            identificacao = int(self.entryIdSolicitacao.get().strip())
            resultado = Administrador.aprovarExclusao(identificacao) if aprovar else Administrador.rejeitarExclusao(identificacao)
            messagebox.showinfo("Sucesso", resultado)
            self.criarMenuAprovacaoExclusao()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    def exibirGerenciamentoDeConntasAdministrador(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "GERENCIAMENTO DE CONTAS")
        self._rotulo(tela, "Número da agência:")
        self.agenciaPesquisaAdm = tk.Entry(tela)
        self.agenciaPesquisaAdm.pack(fill="x", ipady=8)
        self._rotulo(tela, "Número da conta:")
        self.contaPesquisaAdm = tk.Entry(tela)
        self.contaPesquisaAdm.pack(fill="x", ipady=8)
        self._botao(tela, "EXIBIR DETALHES", self.recebeContaParaAnalise).pack(pady=20)
        self._botao(tela, "VOLTAR", self.exibirMenuAdministrador, destaque=False).pack(pady=8)

    def recebeContaParaAnalise(self):
        agencia = self.agenciaPesquisaAdm.get().strip()
        numero = self.contaPesquisaAdm.get().strip().upper()
        conta = Administrador.verificaSeExisteCadastro(numero, agencia)
        if conta is None:
            messagebox.showerror("Erro", "Conta não encontrada.")
            return
        self.contaLogin = conta
        self.exibirInformacoesContaAdministrador()

    def exibirInformacoesContaAdministrador(self):
        conta = self.contaLogin
        tela = self._nova_tela()
        self._cabecalho(tela, "DADOS DO CLIENTE")
        dados = [
            ("Tipo de conta", conta.tipoContaCriada),
            ("Agência", conta.numeroAgencia),
            ("Número da conta", conta.numeroConta),
            ("Titular", conta.titularConta),
            ("Endereço", conta.enderecoTitular),
            ("Saldo", f"R$ {conta.saldoAtual:.2f}"),
        ]
        if isinstance(conta, ContaCorrente):
            dados.append(("Cheque especial disponível", f"R$ {conta.limiteChequeEspecial:.2f}"))
        for chave, valor in dados:
            tk.Label(tela, text=f"{chave}: {valor}", bg=self.BG, fg=self.TEXT).pack(anchor="w", pady=5)
        self._botao(tela, "VOLTAR", self.exibirGerenciamentoDeConntasAdministrador, destaque=False).pack(pady=25)

    # ---------------- CLIENTE ----------------
    def exibirMenuCliente(self):
        Administrador.processarAgendamentos()
        tela = self._nova_tela()
        self._cabecalho(tela, f"BEM-VINDO(A), {self.contaLogin.titularConta.upper()}")
        saldo = tk.Frame(tela, bg="white", bd=1, relief="solid", padx=20, pady=12)
        saldo.pack(fill="x", pady=(0, 15))
        tk.Label(saldo, text=f"R$ {self.contaLogin.saldoAtual:.2f}", bg="white", fg=self.TEXT, font=("Arial", 13, "bold")).pack()
        if isinstance(self.contaLogin, ContaCorrente):
            tk.Label(saldo, text=f"Cheque especial disponível: R$ {self.contaLogin.limiteChequeEspecial:.2f}", bg="white", fg=self.TEXT).pack()

        self._botao(tela, "REALIZAR TRANSAÇÃO", self.exibirTransacoesBancarias).pack(pady=5)
        self._botao(tela, "ALTERAR ENDEREÇO", self.criaMenuAlteracaoEndereco).pack(pady=5)
        self._botao(tela, "INFORMAÇÕES DA CONTA", self.exibirInformacoesContaCliente).pack(pady=5)
        self._botao(tela, "EXCLUSÃO DA CONTA", self.criaMenuExclusaoConta, destaque=False).pack(pady=5)
        self._botao(tela, "VOLTAR AO MENU PRINCIPAL", self.criarMenuPrincipal, destaque=False).pack(pady=5)

    def exibirInformacoesContaCliente(self):
        conta = self.contaLogin
        tela = self._nova_tela()
        self._cabecalho(tela, "MEUS DADOS")
        dados = [
            ("Tipo de conta", conta.tipoContaCriada),
            ("Agência", conta.numeroAgencia),
            ("Número da conta", conta.numeroConta),
            ("Titular", conta.titularConta),
            ("Endereço", conta.enderecoTitular),
            ("Senha", "******"),
        ]
        for chave, valor in dados:
            tk.Label(tela, text=f"{chave}: {valor}", bg=self.BG, fg=self.TEXT).pack(anchor="w", pady=5)
        self._botao(tela, "VOLTAR", self.exibirMenuCliente).pack(pady=25)

    # ---------------- TRANSAÇÕES ----------------
    def exibirTransacoesBancarias(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "TRANSAÇÕES DISPONÍVEIS")
        self._botao(tela, "EXIBIR EXTRATO", self.criarMenuExtrato).pack(pady=6)
        self._botao(tela, "TRANSFERIR", self.criarMenuTransferir).pack(pady=6)
        self._botao(tela, "DEPOSITAR", self.criarMenuDepositoLogado).pack(pady=6)
        self._botao(tela, "SACAR", self.criarMenuSaque).pack(pady=6)
        self._botao(tela, "VOLTAR", self.exibirMenuCliente, destaque=False).pack(pady=6)

    def criarMenuDepositoLogado(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "DEPÓSITO")
        self._rotulo(tela, "Valor do depósito:")
        self.recebeValorDepositoLogado = tk.Entry(tela)
        self.recebeValorDepositoLogado.pack(fill="x", ipady=8)
        self._botao(tela, "DEPOSITAR HOJE", lambda: self.processarDeposito("hoje")).pack(pady=12)
        self._botao(tela, "PROGRAMAR DEPÓSITO", lambda: self.processarDeposito("programar"), destaque=False).pack(pady=8)
        self._botao(tela, "CANCELAR", self.exibirTransacoesBancarias, danger=True).pack(pady=8)

    def processarDeposito(self, tipoDeposito: str):
        valor_texto = self.recebeValorDepositoLogado.get().strip().replace(",", ".")
        try:
            valor = float(valor_texto)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico positivo.")
            return

        if tipoDeposito == "hoje":
            data = date.today()
            Conta.depositar(self.contaLogin, valor, data)
            messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:.2f} realizado com sucesso.")
            self.exibirTransacoesBancarias()
        else:
            self.solicitarDataAgendamento("Depósito", valor)

    def criarMenuSaque(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "SAQUE")
        self._rotulo(tela, "Valor do saque:")
        self.recebeValorSaque = tk.Entry(tela)
        self.recebeValorSaque.pack(fill="x", ipady=8)
        self._botao(tela, "SACAR HOJE", lambda: self.processarSaque("hoje")).pack(pady=12)
        self._botao(tela, "PROGRAMAR SAQUE", lambda: self.processarSaque("programar"), destaque=False).pack(pady=8)
        self._botao(tela, "CANCELAR", self.exibirTransacoesBancarias, danger=True).pack(pady=8)
        self.recebeValorSaque.focus_set()

    def processarSaque(self, tipoSaque: str):
        try:
            valor = float(self.recebeValorSaque.get().strip().replace(",", "."))
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico positivo.")
            return

        if tipoSaque == "programar":
            self.solicitarDataAgendamento("Saque", valor)
            return

        permitir_cheque = True
        if isinstance(self.contaLogin, ContaCorrente) and valor > self.contaLogin.saldoAtual:
            necessario = valor - self.contaLogin.saldoAtual
            if necessario > self.contaLogin.limiteChequeEspecial:
                messagebox.showerror("Erro", "Saldo + cheque especial insuficientes.")
                return
            permitir_cheque = messagebox.askyesno(
                "Cheque Especial",
                f"O saldo atual não cobre o saque.\n\n"
                f"Valor do saque: R$ {valor:.2f}\n"
                f"Uso do cheque especial: R$ {necessario:.2f}\n"
                f"Limite restante: R$ {self.contaLogin.limiteChequeEspecial:.2f}\n\n"
                "Deseja continuar?",
            )
            if not permitir_cheque:
                return

        ok, usado = Conta.sacar(self.contaLogin, valor, date.today(), permitir_cheque=permitir_cheque)
        if not ok:
            messagebox.showerror("Erro", "Saldo insuficiente.")
            return
        messagebox.showinfo("Sucesso", f"Saque de R$ {valor:.2f} realizado.\nCheque especial utilizado: R$ {usado:.2f}")
        self.exibirTransacoesBancarias()

    def criarMenuTransferir(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "TRANSFERÊNCIA")
        self._rotulo(tela, "Conta beneficiada:")
        self.entryContaDestino = tk.Entry(tela)
        self.entryContaDestino.pack(fill="x", ipady=8)
        self._rotulo(tela, "Valor:")
        self.entryValorTransferencia = tk.Entry(tela)
        self.entryValorTransferencia.pack(fill="x", ipady=8)
        self._botao(tela, "TRANSFERIR AGORA", lambda: self.processarTransferencia("hoje")).pack(pady=12)
        self._botao(tela, "PROGRAMAR TRANSFERÊNCIA", lambda: self.processarTransferencia("programar"), destaque=False).pack(pady=8)
        self._botao(tela, "CANCELAR", self.exibirTransacoesBancarias, danger=True).pack(pady=8)

    def processarTransferencia(self, tipoTransferencia: str):
        destino_numero = self.entryContaDestino.get().strip().upper()
        if not destino_numero:
            messagebox.showerror("Erro", "Informe a conta destino.")
            return
        destino = Administrador.buscarConta(destino_numero)
        if destino is None:
            messagebox.showerror("Erro", "Conta destino não encontrada.")
            return
        if destino is self.contaLogin:
            messagebox.showerror("Erro", "Não é possível transferir para a própria conta.")
            return

        try:
            valor = float(self.entryValorTransferencia.get().strip().replace(",", "."))
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico positivo.")
            return

        if tipoTransferencia == "programar":
            try:
                data = self._pedir_data()
                self.contaLogin.agendar("Transferência", valor, data, destino.numeroConta)
                messagebox.showinfo("Sucesso", f"Transferência agendada para {data.strftime('%d/%m/%Y')}.")
                self.exibirTransacoesBancarias()
            except ValueError as exc:
                messagebox.showerror("Erro", str(exc))
            return

        permitir_cheque = True
        if isinstance(self.contaLogin, ContaCorrente) and valor > self.contaLogin.saldoAtual:
            necessario = valor - self.contaLogin.saldoAtual
            if necessario > self.contaLogin.limiteChequeEspecial:
                messagebox.showerror("Erro", "Saldo + cheque especial insuficientes.")
                return
            permitir_cheque = messagebox.askyesno(
                "Cheque Especial",
                f"Será utilizado cheque especial no valor de R$ {necessario:.2f}.\nDeseja continuar?",
            )
            if not permitir_cheque:
                return

        ok, usado = transferir(self.contaLogin, destino, valor, date.today(), permitir_cheque=permitir_cheque)
        if not ok:
            messagebox.showerror("Erro", "Transferência não realizada por insuficiência de saldo.")
            return
        messagebox.showinfo("Sucesso", f"Transferência de R$ {valor:.2f} realizada.\nCheque especial utilizado: R$ {usado:.2f}")
        self.exibirTransacoesBancarias()

    def solicitarDataAgendamento(self, tipo: str, valor: float):
        top = tk.Toplevel(self.janelaPrincipal)
        top.title(f"Programar {tipo}")
        top.geometry("340x180")
        top.transient(self.janelaPrincipal)
        top.grab_set()
        tk.Label(top, text="Data (DD/MM/AAAA):").pack(pady=12)
        entrada = tk.Entry(top)
        entrada.pack(pady=5)

        def confirmar():
            try:
                data_agendada = datetime.strptime(entrada.get().strip(), "%d/%m/%Y").date()
                self.contaLogin.agendar(tipo, valor, data_agendada)
                top.destroy()
                messagebox.showinfo("Sucesso", f"{tipo} agendado para {data_agendada.strftime('%d/%m/%Y')}.")
                self.exibirTransacoesBancarias()
            except ValueError as exc:
                messagebox.showerror("Erro", str(exc))

        tk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)
        entrada.focus_set()

    def _pedir_data(self) -> date:
        # Janela modal simples e síncrona via wait_window.
        top = tk.Toplevel(self.janelaPrincipal)
        top.title("Data da transferência")
        top.geometry("340x180")
        top.transient(self.janelaPrincipal)
        top.grab_set()
        result: dict[str, Optional[date]] = {"data": None}
        tk.Label(top, text="Data (DD/MM/AAAA):").pack(pady=12)
        entrada = tk.Entry(top)
        entrada.pack(pady=5)

        def confirmar():
            try:
                data = datetime.strptime(entrada.get().strip(), "%d/%m/%Y").date()
                if data <= date.today():
                    raise ValueError("A data deve ser futura.")
                result["data"] = data
                top.destroy()
            except ValueError as exc:
                messagebox.showerror("Erro", str(exc), parent=top)

        tk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)
        entrada.focus_set()
        self.janelaPrincipal.wait_window(top)
        if result["data"] is None:
            raise ValueError("Operação cancelada.")
        return result["data"]

    # ---------------- DEPÓSITO EXPRESS ----------------
    def criarMenuDepositoExpress(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "DEPÓSITO EXPRESS")
        tk.Label(tela, text="Faça um depósito sem login.", bg=self.BG, fg=self.TEXT).pack(pady=(0, 12))
        self._rotulo(tela, "Número da conta:")
        self.recebeNumeroDaConta = tk.Entry(tela)
        self.recebeNumeroDaConta.pack(fill="x", ipady=8)
        self._rotulo(tela, "Valor do depósito:")
        self.recebeValorDeposito = tk.Entry(tela)
        self.recebeValorDeposito.pack(fill="x", ipady=8)
        self._rotulo(tela, "CPF do depositante:")
        self.recebeCPFDepositante = tk.Entry(tela)
        self.recebeCPFDepositante.pack(fill="x", ipady=8)
        self._botao(tela, "EFETUAR DEPÓSITO", self.processarDepositoSemLogar).pack(pady=18)
        self._botao(tela, "CANCELAR", self.criarMenuPrincipal, danger=True).pack(pady=8)

    def processarDepositoSemLogar(self):
        numero_conta = self.recebeNumeroDaConta.get().strip().upper()
        cpf = self.recebeCPFDepositante.get().strip()
        valor_texto = self.recebeValorDeposito.get().strip().replace(",", ".")
        if not numero_conta or not cpf or not valor_texto:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return
        if Conta.validarCpfDepositante(cpf) is None:
            messagebox.showerror("Erro", "CPF deve conter 11 dígitos numéricos.")
            return
        conta = Administrador.buscarConta(numero_conta)
        if conta is None:
            messagebox.showerror("Erro", "Conta não encontrada.")
            return
        try:
            valor = float(valor_texto)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido para depósito.")
            return

        Conta.depositar(conta, valor, date.today(), f"CPF depositante: {Conta.validarCpfDepositante(cpf)}")
        messagebox.showinfo("Sucesso", f"Depósito de R$ {valor:.2f} realizado na conta {conta.numeroConta}.")
        self.criarMenuPrincipal()

    # ---------------- ENDEREÇO ----------------
    def criaMenuAlteracaoEndereco(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "ALTERAR ENDEREÇO")
        tk.Label(
            tela,
            text="A alteração será refletida em todas as suas contas com o mesmo titular e CPF.",
            bg=self.BG,
            fg=self.TEXT,
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 15))
        self._rotulo(tela, "Novo endereço completo:")
        self.entryNovoEndereco = tk.Entry(tela)
        self.entryNovoEndereco.pack(fill="x", ipady=8)
        self._botao(tela, "CONFIRMAR ALTERAÇÃO", self.processarAlteracaoEndereco).pack(pady=18)
        self._botao(tela, "VOLTAR", self.exibirMenuCliente, destaque=False).pack(pady=8)

    def processarAlteracaoEndereco(self):
        novo = self.entryNovoEndereco.get().strip()
        try:
            contas_alteradas = Administrador.alterarEnderecoPorNome(self.contaLogin.titularConta, novo, self.contaLogin.cpf)
            if contas_alteradas == 0:
                raise ValueError("Nenhuma conta encontrada para alteração.")
            messagebox.showinfo("Sucesso", f"Endereço atualizado em {contas_alteradas} conta(s).")
            self.exibirInformacoesContaCliente()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    # ---------------- EXCLUSÃO ----------------
    def criaMenuExclusaoConta(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "EXCLUSÃO DA CONTA")
        status = Administrador.verificarStatusExclusao(self.contaLogin.numeroConta)
        texto = status
        if self.contaLogin.solicitacaoExclusao:
            texto += f"\nEnviada em: {self.contaLogin.solicitacaoExclusao['data']}"
        self.labelStatus = tk.Label(tela, text=texto, bg=self.BG, fg=self.TEXT, wraplength=460)
        self.labelStatus.pack(pady=15)

        pendente = self.contaLogin.solicitacaoExclusao is not None
        self._botao(tela, "SOLICITAR EXCLUSÃO", self.confirmarExclusaoConta, destaque=not pendente).pack(pady=8)
        self._botao(tela, "CANCELAR SOLICITAÇÃO", self.cancelarExclusaoConta, destaque=True).pack(pady=8)
        self._botao(tela, "VOLTAR", self.exibirMenuCliente, destaque=False).pack(pady=15)

    def confirmarExclusaoConta(self):
        try:
            self.contaLogin.solicitarExclusaoConta()
            messagebox.showinfo("Sucesso", "Solicitação enviada ao administrador.")
            self.criaMenuExclusaoConta()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    def cancelarExclusaoConta(self):
        try:
            Administrador.cancelarSolicitacao(self.contaLogin.numeroConta)
            self.contaLogin.solicitacaoExclusao = None
            messagebox.showinfo("Sucesso", "Solicitação cancelada.")
            self.criaMenuExclusaoConta()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))

    # ---------------- EXTRATO ----------------
    def criarMenuExtrato(self):
        tela = self._nova_tela()
        self._cabecalho(tela, "EXTRATO BANCÁRIO")

        frame_texto = tk.Frame(tela, bg=self.BG)
        frame_texto.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame_texto)
        scrollbar.pack(side="right", fill="y")
        self.textoExtrato = tk.Text(frame_texto, wrap=tk.WORD, yscrollcommand=scrollbar.set, bg="white")
        self.textoExtrato.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.textoExtrato.yview)

        filtros = tk.Frame(tela, bg=self.BG)
        filtros.pack(fill="x", pady=10)
        tk.Label(filtros, text="Período (DD/MM/AAAA):", bg=self.BG, fg=self.TEXT).pack(anchor="w")
        linha = tk.Frame(filtros, bg=self.BG)
        linha.pack(fill="x", pady=5)
        tk.Label(linha, text="De:", bg=self.BG, fg=self.TEXT).pack(side="left")
        self.entryDataInicial = tk.Entry(linha, width=12)
        self.entryDataInicial.pack(side="left", padx=5)
        tk.Label(linha, text="Até:", bg=self.BG, fg=self.TEXT).pack(side="left", padx=(10, 0))
        self.entryDataFinal = tk.Entry(linha, width=12)
        self.entryDataFinal.pack(side="left", padx=5)

        botoes = tk.Frame(tela, bg=self.BG)
        botoes.pack()
        tk.Button(botoes, text="APLICAR FILTRO", command=self.aplicarFiltroExtrato, width=15).pack(side="left", padx=4)
        tk.Button(botoes, text="LIMPAR FILTRO", command=self.limparFiltroExtrato, width=15).pack(side="left", padx=4)
        self._botao(tela, "VOLTAR", self.exibirTransacoesBancarias, destaque=False).pack(pady=10)
        self.atualizarExibicaoExtrato()

    def _cabecalho_extrato(self) -> str:
        conta = self.contaLogin
        texto = (
            "BANCO DOS UNIVERSITÁRIOS\n"
            f"Agência: {conta.numeroAgencia}\n"
            f"Conta: {conta.numeroConta}\n"
            f"Titular: {conta.titularConta}\n"
            f"Saldo Atual: R$ {conta.saldoAtual:.2f}\n"
        )
        if isinstance(conta, ContaCorrente):
            texto += f"Cheque Especial Disponível: R$ {conta.limiteChequeEspecial:.2f}\n"
        return texto + "\nHistórico de Transações:\n" + "=" * 70 + "\n"

    def atualizarExibicaoExtrato(self, transacoes: Optional[list[dict[str, Any]]] = None):
        if not hasattr(self, "textoExtrato"):
            return
        self.textoExtrato.delete("1.0", tk.END)
        self.textoExtrato.insert(tk.END, self._cabecalho_extrato())
        lista = self.contaLogin.historico if transacoes is None else transacoes
        if not lista:
            self.textoExtrato.insert(tk.END, "Nenhuma transação efetuada.\n")
            return
        for transacao in sorted(lista, key=lambda t: t["data"], reverse=True):
            self.textoExtrato.insert(tk.END, f"• {self.contaLogin.formatar_transacao(transacao)}\n")

    def _ler_periodo(self) -> tuple[date, date]:
        try:
            inicio = datetime.strptime(self.entryDataInicial.get().strip(), "%d/%m/%Y").date()
            fim = datetime.strptime(self.entryDataFinal.get().strip(), "%d/%m/%Y").date()
        except ValueError as exc:
            raise ValueError("Use o formato DD/MM/AAAA.") from exc
        if inicio > fim:
            raise ValueError("A data inicial não pode ser posterior à data final.")
        return inicio, fim

    def aplicarFiltroExtrato(self):
        try:
            inicio, fim = self._ler_periodo()
        except ValueError as exc:
            messagebox.showerror("Erro", str(exc))
            return

        transacoes = [t for t in self.contaLogin.historico if inicio <= t["data"] <= fim]
        saldo_projetado = self.contaLogin.saldoAtual

        if isinstance(self.contaLogin, ContaCorrente):
            taxas = gerar_taxas_corrente(self.contaLogin, inicio, fim)
            transacoes.extend(taxas)
            saldo_projetado -= sum(t["valor"] for t in taxas)
            transacoes.append(
                {
                    "tipo": "Saldo projetado",
                    "valor": saldo_projetado,
                    "data": fim,
                    "descricao": "Após taxas projetadas no período",
                }
            )
        else:
            rendimentos = gerar_rendimentos_poupanca(self.contaLogin, inicio, fim)
            transacoes.extend(rendimentos)
            total_rendimento = sum(t["valor"] for t in rendimentos)
            saldo_projetado += total_rendimento
            transacoes.append(
                {
                    "tipo": "Rendimento total projetado",
                    "valor": total_rendimento,
                    "data": fim,
                    "descricao": "No período filtrado",
                }
            )
            transacoes.append(
                {
                    "tipo": "Saldo projetado",
                    "valor": saldo_projetado,
                    "data": fim,
                    "descricao": "Incluindo rendimentos projetados",
                }
            )

        self.atualizarExibicaoExtrato(transacoes)

    def limparFiltroExtrato(self):
        self.entryDataInicial.delete(0, tk.END)
        self.entryDataFinal.delete(0, tk.END)
        self.atualizarExibicaoExtrato()


if __name__ == "__main__":
    janela = Janela()
    janela.exibirJanela()
