from datetime import date, timedelta, datetime
import random
import tkinter as tk
from tkinter import *
import tkinter.messagebox as messagebox


"""
AD2 - 2025.1 - PROGRAMAÇÃO COM INTERFACES GRÁFICAS
ALUNA: Maria Carolina de Almeida Santos Rosa

OBSERVAÇÕES IMPORTANTES:

1. A credencial de acesso do Administrador é: 

# n° identificação: 000

2. Número da agência:  0219
"""

class Administrador:
    
    __usuario = "Admin"
    __codigo = "000"
    __contasCorrenteCadastradas = []
    __contasPoupancaCadastradas = []
    __solicitacoes = []
    __contasParaExclusao = []
    __solicitacoesPendentes = []  # Lista de dicionários com todas as informações
    __contasParaExclusao = []    # Lista apenas com números de conta

    #Usado classe Interface para identificar o acesso do Administrador
    @classmethod
    def getUsuario(cls):
        return cls.__usuario

    #Utilizado na classe Interface para identificar o acesso do Administrador
    @classmethod
    def getCodigo(cls):
        return cls.__codigo

    #Realiza a exclusão das contas
    @classmethod
    def excluirContas(cls, numeroConta):
        # Verifica contas correntes
        for conta in cls.__contasCorrenteCadastradas:
            if numeroConta == conta.numeroConta:
                cls.__contasCorrenteCadastradas.remove(conta)
                return

        # Verifica contas poupança
        for conta in cls.__contasPoupancaCadastradas:
            if numeroConta == conta.numeroConta:
                cls.__contasPoupancaCadastradas.remove(conta)
                return

    #Recebe as solicitações enviadas pelo cliente e armazena no vetor solicitacoes/contasParaExclusao
    @classmethod
    def recebeSolicitacao(cls, solicitacao):
        if solicitacao['numero_conta'] in cls.__contasParaExclusao:
            raise Exception("Já existe solicitação pendente para esta conta")
        
        cls.__solicitacoes.append(solicitacao)
        cls.__contasParaExclusao.append(solicitacao['numero_conta'])
            
    @classmethod
    def adicionarContaCorrente(cls, conta):
        cls.__contasCorrenteCadastradas.append(conta)

    #Adiciona as contas correntes criadas a um vetor, para controle do Administrador
    @classmethod
    def adicionarContaPoupanca(cls, conta):
        cls.__contasPoupancaCadastradas.append(conta)

    #Retornará uma cópia da lista contendo as contas corrente. Utilizada para validar a existência da conta, durante as transações. 
    @classmethod
    def get__contasCorrenteCadastradas(cls):
        return cls.__contasCorrenteCadastradas.copy() #retornará uma cópia da lista

    #Retornará uma cópia da lista contendo as contas poupança. Utilizada para validar a existência da conta, durante as transações. 
    @classmethod
    def get__contasPoupancaCadastradas(cls):
        return cls.__contasPoupancaCadastradas.copy() #retornará uma cópia da lista
    
    #Utiliza o número da conta e a agência para verificar se o cliente possui cadastro
    @classmethod
    def verificaSeExisteCadastro(cls, numeroConta, agencia): 

        if len(cls.__contasCorrenteCadastradas) > 0:
            for i in range(len(cls.__contasCorrenteCadastradas)):
                if numeroConta == cls.__contasCorrenteCadastradas[i].numeroConta and agencia == cls.__contasCorrenteCadastradas[i].numeroAgencia:
                    conta = cls.__contasCorrenteCadastradas[i]
                    return conta

        if len(cls.__contasPoupancaCadastradas) > 0:
            for i in range(len(cls.__contasPoupancaCadastradas)):
                if numeroConta == cls.__contasPoupancaCadastradas[i].numeroConta and agencia == cls.__contasPoupancaCadastradas[i].numeroAgencia:
                    conta = cls.__contasPoupancaCadastradas[i]
                    return conta

        messagebox.showerror("Erro!","Usuário não cadastrado.")
        return None

    #Atualiza o endereço das contas dos clientes que possuem mesmo nome e CPF
    @classmethod
    def alterarEnderecoPorNome(cls, titularConta, novoEndereco, cpf):
        contasAlteradas = 0
        
        for conta in cls.__contasCorrenteCadastradas:
            if conta.titularConta == titularConta and conta.cpf == cpf:
                conta.enderecoTitular = novoEndereco  # Atualiza diretamente
                contasAlteradas += 1
                
        for conta in cls.__contasPoupancaCadastradas:
            if conta.titularConta == titularConta and conta.cpf == cpf:
                conta.enderecoTitular = novoEndereco  # Atualiza diretamente
                contasAlteradas += 1
                
        return contasAlteradas 


#------------------------------FUNÇÕES CRIADAS NA CLASSE ADMINISTRADDOR PARA AUXILIAR NA IMPLEMENTAÇÃO DA INTERFACE -----------------------------------------

    #Adiciona solitação de exclusão às respectivas listas
    @classmethod
    def adicionarSolicitacao(cls, solicitacao):
        if solicitacao['numero_conta'] in cls.__contasParaExclusao:
            raise ValueError("Já existe solicitação pendente para esta conta")
        
        cls.__solicitacoesPendentes.append(solicitacao)
        cls.__contasParaExclusao.append(solicitacao['numero_conta'])
        # print(f"Solicitação registrada: {solicitacao}")

    #Exibe as solicitações enviadas na interface
    @classmethod
    def listarSolicitacoes(cls):
        return [
            f"ID: {idx} | Conta: {s['numero_conta']} | Titular: {s['titular']} | "
            f"Tipo: {s['tipo_conta']} | Data: {s['data']}"
            for idx, s in enumerate(cls.__solicitacoesPendentes, 1)
        ]

    #Aprova o pedido de exclusão de conta
    @classmethod
    def aprovarExclusao(cls, id_solicitacao):
        try:
            solicitacao = cls.__solicitacoesPendentes.pop(id_solicitacao - 1)
            cls.excluirContas(solicitacao['numero_conta'])
            return f"Conta {solicitacao['numero_conta']} excluída com sucesso"
        except IndexError:
            raise ValueError("ID de solicitação inválido")
   
    #Rejeita o pedido de exclusão de conta
    @classmethod
    def rejeitarExclusao(cls, id_solicitacao):
        try:
            solicitacao = cls.__solicitacoesPendentes.pop(id_solicitacao - 1)
            cls.__contasParaExclusao.remove(solicitacao['numero_conta'])
            return f"Solicitação da conta {solicitacao['numero_conta']} rejeitada"
        except IndexError:
            raise ValueError("ID de solicitação inválido")
        
    #Lista solicitações pendentes
    @classmethod
    def listarSolicitacoesPendentes(cls, tipo_conta=None):
        solicitacoes = cls.__solicitacoesPendentes.copy()
        
        if tipo_conta:  # 'ContaCorrente' ou 'ContaPoupanca'
            solicitacoes = [s for s in solicitacoes if s['tipo_conta'] == tipo_conta]
        
        return solicitacoes or "Nenhuma solicitação encontrada."

    #Cancela o pedido de exclusão de conta
    @classmethod
    def cancelarSolicitacao(cls, numero_conta):
        cls.__solicitacoesPendentes = [s for s in cls.__solicitacoesPendentes
                                    if s['numero_conta'] != numero_conta]
        if numero_conta in cls.__contasParaExclusao:
            cls.__contasParaExclusao.remove(numero_conta)

    # Retorna o status formatado para exibição
    @classmethod
    def verificarStatusExclusao(cls, numero_conta):
        if numero_conta in cls.__contasParaExclusao:
            return "Solicitação em análise (pendente)"
        return "Conta ativa (sem solicitação)"
#--------------------------------------------------------------------------------------------

class Conta:
    numeroAgencia = "0219" #Supondo que o Banco dos Universitários possui apenas 1 agência, todas as contas do exemplo receberam o mesmo número.
    numeroConta = 0

    #Construtor
    def __init__(self, titularConta, enderecoTitular, cpf, senha):
        # Geração do número da conta (mantido igual)
        Conta.numeroConta += 1
        self.numeroConta = f"C: {Conta.numeroConta}"
        self.login = self.numeroConta
        self.saldoAtual = 0.0
        self.historico = []
        
        # Validação e atribuição do nome
        nome = str(titularConta).strip()
        if not self.validarNome(nome):    
            raise ValueError("Nome inválido. Deve conter nome e sobrenome, não possuir números ou caracteres especiais, exceto: - . '.")
        self.titularConta = nome.title()  

         # Validação do CPF
        self.cpf = self.validarFormatarCPF(cpf)

        # Validação do endereço
        self.enderecoTitular = str(enderecoTitular).strip()
        if not self.validarEndereco(self.enderecoTitular):
            raise ValueError("Endereço deve conter letras e não pode ter apenas números")

        # Validação da senha
        self.senha = self.validarSenha(senha)

    #Utilizado para adicionar transações ao histórico da conta
    def adicionaTransacaoHistorico(self,transacao):
        self.historico.append(transacao)


    #Depósito sem login ou para clientes não cadastrados
    @classmethod
    def depositarSemlogar(cls, contaBeneficiada, cpf, valor):
        # Validação básica
        if not all([contaBeneficiada, cpf, valor]):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return False

        try:
            valor = float(valor)
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser positivo.")
                return False
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido para depósito.")
            return False

        # Busca a conta
        conta = None
        for cc in Administrador.get__contasCorrenteCadastradas():
            if contaBeneficiada == cc.numeroConta:
                conta = cc
                break
        
        if not conta:
            for cp in Administrador.get__contasPoupancaCadastradas():
                if contaBeneficiada == cp.numeroConta:
                    conta = cp
                    break

        if not conta:
            messagebox.showerror("Erro", f"Conta {contaBeneficiada} não encontrada!")
            return False

        # Valida CPF
        if not cls.validarCpfDepositante(cpf):
            return False

        # Processa o depósito
        data = date.today().strftime("%d/%m/%Y")
        conta.saldoAtual += valor
        transacao = f"Depósito externo - R$ {valor:.2f} - {data} - CPF depositante: {cpf}"
        conta.adicionaTransacaoHistorico(transacao)
        
        messagebox.showinfo("Sucesso", 
            f"Depósito de R$ {valor:.2f} realizado na conta {conta.numeroConta}!")
        return True

    #Envia a solicitação de exclusão para o administardor do sistema
    def solicitarExclusaoConta(self):
        if hasattr(self, 'solicitacaoExclusao'):
            raise ValueError("Já existe uma solicitação ativa para esta conta")
        
        solicitacao = {
            'numero_conta': self.numeroConta,
            'titular': self.titularConta,
            'tipo_conta': self.__class__.__name__,
            'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
            'status': 'pendente'
        }
        
        Administrador.adicionarSolicitacao(solicitacao)
        self.solicitacaoExclusao = solicitacao  # Armazena localmente

    #Método que efetivamente executa a alteração do endereço
    def alterarEndereco(self, novoEndereco):
        self.enderecoTitular = novoEndereco
    
    #Método de validação e formatação do CPF, limita a quantidade de digitos e formata para o padrão conhecido xxx.xxx.xxx-xx
    def validarFormatarCPF(self, cpf):
        cpf = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    #Método estático para validar o CPF em depósito de visitante.
    @staticmethod
    def validarCpfDepositante(cpfPassadoComoParametro):
        while True:
            cpf = cpfPassadoComoParametro
            cpfLimpo = ''.join(filter(str.isdigit, cpf))  # Remove caracteres não numéricos
            
            if len(cpfLimpo) == 11 and cpfLimpo.isdigit():
                return cpfLimpo  # Retorna o CPF válido (apenas números)
            else:
                messagebox.showerror("Erro.",
                                     "CPF deve conter 11 digitos numéricos.")
            return None

    #Valida a senha, limitando a 6 digitos numéricos
    @staticmethod
    def validarSenha(senha):
        senha = ''.join(filter(str.isdigit, str(senha)))
        if len(senha) != 6:
            raise ValueError("Senha deve conter 6 dígitos númericos")
        return senha

    #Garante que o nome não será vazio, ou contenha digitos numéricos. Alguns caracteres especiais como ' e . são permitidos (pois alguns nomes/sobrenomes os utilizam).
    @staticmethod
    def validarNome(titularConta):
        # Verifica se é string e remove espaços extras
        if not isinstance(titularConta, str):
            return False
        nome = titularConta.strip()
        
        # Validações básicas
        if not nome or len(nome) < 3:  # Nome muito curto
            return False
        
        if len(nome) > 100:  # Nome muito longo
            return False
        
        if "  " in nome:  # Múltiplos espaços
            return False
        
        # Verifica cada caractere individualmente
        caracteresPermitidos = (" ", "'", ".")  # Caracteres especiais permitidos
        for char in nome:
            if not (char.isalpha() or char in caracteresPermitidos):
                # Permite letras acentuadas (considerando Unicode)
                if char.lower() not in 'áéíóúâêîôûãõàèìòùäëïöüç':
                    return False
        
        # Verifica se tem pelo menos nome e sobrenome
        if len(nome.split()) < 2:
            return False
        
        return True
    
    #Garante que o endereço não estará vazio, e que não possua caracteres especiais inadequados.
    @staticmethod
    def validarEndereco(endereco):
        endereco = str(endereco).strip()
        
        # Verifica se está vazio ou contém apenas espaços
        if not endereco:
            return False
        
        # Verifica se contém APENAS números (não permitido)
        if endereco.replace(" ", "").isdigit():
            return False
        
        # Verifica caracteres permitidos (letras, números e alguns símbolos)
        caracteresPermitidos = {',', '.', '-', ' '}
        for char in endereco:
            if not (char.isalpha() or char.isdigit() or char in caracteresPermitidos):
                return False
        
        return True
    
class ContaCorrente(Conta):
    numeroContaCorrente = 0
    TAXA_MANUTENCAO = 15.00

    #Construtor
    def __init__(self, titularConta, enderecoTitular, cpf, senha):
        # Simplesmente repassa todos os parâmetros para o construtor da superclasse
        super().__init__(titularConta, enderecoTitular, cpf, senha)
        ContaCorrente.numeroContaCorrente += 1
        self.numeroConta = f"CC{random.randint(10000, 99999)}-{random.randint(0,9)}" 
        self.limiteChequeEspecial = 100.00
        self.tipoContaCriada = "CORRENTE"
        self.login = self.numeroConta #Login definido como o numero da conta
        print(f"{titularConta.upper()}, seu login: {self.numeroConta} + agência: {Conta.numeroAgencia}")

        Administrador.adicionarContaCorrente(self)

    #Simula a aplicação da taxa de manutenção para a projeção do histórico e ordena as transações em ordem crecente
    def aplicarTaxaManutencaoPeriodo(self, meses, dataFinal, transacoesFiltradas):
        # Cria uma lista combinada de transações reais + taxas projetadas
        historico_completo = transacoesFiltradas.copy()
        saldoTemp = self.saldoAtual  # Cópia temporária do saldo (apenas para cálculo)
        
        for i in range(meses):
            # Calcula a data correta para cada taxa (dia 5 de cada mês, por exemplo)
            data_taxa = dataFinal.replace(day=5) - timedelta(days=(meses - i - 1) * 30)
            
            # Adiciona a taxa ao histórico combinado
            historico_completo.append(
                f"Taxa de Manutenção Projetada - R$ {self.TAXA_MANUTENCAO:.2f} - {data_taxa.strftime('%d/%m/%Y')}")
            saldoTemp -= self.TAXA_MANUTENCAO  # Atualiza saldo temporário
        
        # Ordena todas as transações por data
        historico_ordenado = sorted(historico_completo, key=lambda x: datetime.strptime(x.split(" - ")[2], "%d/%m/%Y"))

class ContaPoupanca(Conta):        

    #Construtor
    def __init__(self, titularConta, enderecoTitular, cpf, senha):
        super().__init__(titularConta, enderecoTitular, cpf, senha)
        self.numeroConta = f"CP{random.randint(10000, 99999)}-{random.randint(0,9)}"
        Administrador.adicionarContaPoupanca(self)
        print(f"{titularConta.upper()}, seu login: {self.numeroConta} + agência: {Conta.numeroAgencia}")
        self.TAXA_RENDIMENTO = 0.005 
        self.tipoContaCriada = "POUPANÇA"
        self.DIAS_ANIVERSARIO = 30 

    #Implementa o cálculo dos rendimentos
    def calcularRendimentoAniversario(self, dataInicial, dataFinal, transacoesFiltradas):
        historico_temp = transacoesFiltradas.copy()
        saldoTemp = self.saldoAtual
        rendimentoTotal = 0

        # 1. Filtrar apenas depósitos/transferências recebidas
        transacoes_entrada = []
        for transacao in transacoesFiltradas:
            if any(t in transacao for t in ["Depósito", "Transferência recebida"]):
                try:
                    partes = transacao.split(" - ")
                    # Corrige a extração do valor (remove R$ e espaços, trata vírgulas)
                    valor_str = partes[1].replace("R$", "").replace(" ", "").replace(",", ".")
                    valor = float(valor_str)
                    data_transacao = datetime.strptime(partes[2].strip(), "%d/%m/%Y").date()
                    transacoes_entrada.append((valor, data_transacao, transacao))
                except (IndexError, ValueError, AttributeError) as e:
                    print(f"Erro ao processar transação: {transacao} | Erro: {str(e)}")
                    continue

        # 2. Para cada transação válida, calcular os rendimentos
        for valor, data_transacao, transacao_original in transacoes_entrada:
            print(f"\nCalculando rendimentos para: {transacao_original}")
            
            dias_corridos = (dataFinal - data_transacao).days
            ciclos = dias_corridos // 30

            if ciclos > 0:
                for ciclo in range(1, ciclos + 1):
                    data_aniversario = data_transacao + timedelta(days=30 * ciclo)
                    
                    if data_aniversario <= dataFinal:
                        rendimento = valor * self.TAXA_RENDIMENTO
                        rendimentoTotal += rendimento
                        
                        descricao = (f"Rendimento (aniv. {ciclo}°) - R$ {rendimento:.2f} - "
                                    f"{data_aniversario.strftime('%d/%m/%Y')} "
                                    f"(origem: {data_transacao.strftime('%d/%m/%Y')})")
                        historico_temp.append(descricao)
                        print(f"- {descricao}")

        # 3. Ordena e exibe
        historico_ordenado = sorted(historico_temp, key=lambda x: datetime.strptime(x.split(" - ")[2].split()[0], "%d/%m/%Y"))

class Janela:
    def __init__(self): #Construtor
        self.janelaPrincipal = Tk()
        self.janelaPrincipal.configure(bg='#E3F2F9')
        self.janelaPrincipal.geometry("420x600")
        self.janelaPrincipal.title("Banco dos Universitários")
        self.nomeMenu = None
        self.contaLogin = None #Será que dá ruim?

        #Váriaveis responsáveis por armazenar os Frames
        self.menuLogin = None
        self.menuPrincipal = None
        self.menuAberturaDeConta = None
        self.menuAberturaDeContaCorrentePoupanca = None
        self.informacoesContaCliente = None
        self.informacoesContaAdministrador = None
        self.menuDepositoExpress = None
        self.telaPosCadastro = None
        self.menuLoginAdministrador = None
        self.menuLoginCliente = None
        self.menuAdministrador = None
        self.menuCliente = None
        self.trasacoesBancarias = None
        self.gerenciamentoDeContasAdministrador = None
        self.menuDepositoLogado = None
        self.menuSaque = None
        self.menuTransferir = None
        self.menuAlteracaoEndereco = None
        self.telaExclusaoConta = None
        self.telaAcompanhamentoExclusaoConta = None
        self.menuExtrato = None
        
        #Cria o menu principal
        self.criarMenuPrincipal()

        #Chama função que evita interrupção
        self.configurarProtecaoTeclado()

    #Exibe a janela principal
    def exibirJanela(self):
        self.janelaPrincipal.mainloop()

    #Responsável por ocultar frames, recebe como parâmetro o seu nome
    def ocultarFrame(self, nomeFrame):
        frame = getattr(self, nomeFrame,None)
        if frame:
            frame.pack_forget()
    
    #Evita interupções (teclado)
    def configurarProtecaoTeclado(self):
        # Bloqueia Ctrl+C (KeyInterrupt)
        self.janelaPrincipal.bind('<Control-c>', lambda e: None)
        
        # Bloqueia outros atalhos comuns que podem fechar a janela
        self.janelaPrincipal.bind('<Control-q>', lambda e: None)  # Ctrl+Q
        self.janelaPrincipal.bind('<Escape>', lambda e: None)     # Tecla Esc
        
#---------------------------------MENU PRINCIPAL---------------------------------  
    #Frame responsável por exibir o menu principal
    def criarMenuPrincipal(self):
        #Alguns frames são ocultados durante a exibição do menu principal
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")
        self.ocultarFrame("menuDepositoExpress")
        self.ocultarFrame("telaPosCadastro")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("menuLoginCliente")
        self.ocultarFrame("menuAdministrador")
        self.ocultarFrame("menuCliente")
        self.ocultarFrame("menuAprovacao")

        #Define o frame do menu principal
        self.menuPrincipal = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)

        #Título da página + logo
        self.logo = tk.PhotoImage(file="ImagemTelaPrincipal.png")
        self.labelImagem = tk.Label(self.menuPrincipal, image=self.logo,bd=0, highlightthickness=0, pady=5).pack()
        tk.Label(self.menuPrincipal, text="BANCO DOS UNIVERSITÁRIOS",font=('Arial',12, 'bold'),fg='#223C5E',bg='#E3F2F9').pack(pady=15)
                
        #Botões do menu principal
        Button(self.menuPrincipal, text="ABERTURA DE CONTA", height=3, width=300, command=self.criarMenuAberturaDeConta, bg="#78D1DE").pack(padx=15, pady=10)
        Button(self.menuPrincipal, text="ACESSAR CONTA",bg='#E3F2F9', height=3, width=300, command= self.criarMenuLogin).pack(padx=15, pady=10)
        Button(self.menuPrincipal, text="DEPÓSITO EXPRESS", bg='#E3F2F9',height=3, width=300, command=self.criarMenuDepositoExpress).pack(padx=15, pady=10)
        Button(self.menuPrincipal, text="SAIR",bg='#D26060', height=3, width=300, command=self.janelaPrincipal.destroy).pack(padx=15, pady=10)

        self.menuPrincipal.pack(padx=20, pady=20)
        
#---------------------------------TIPO DE LOGIN(ADMIN OU CLIENTE)---------------------------------  
    def criarMenuLogin(self):
        #Alguns frames são ocultados durante a exibição do menu de login
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("menuLoginCliente")

        #Define o frame do menu de login
        self.menuLogin = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)

        #Imagem/Logo da empresa + Título do Frame
        self.labelImagem = tk.Label(self.menuLogin, image=self.logo,bd=0, highlightthickness=0).pack()
        tk.Label(self.menuLogin, text="ESCOLHA O TIPO DE ACESSO",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack()

        #Botões do menu de Login
        Button(self.menuLogin, text="CLIENTE",bg="#78D1DE", height=3, width=300, command=self.exibirMenuLoginCliente).pack(padx=15, pady=15)
        Button(self.menuLogin, text="ADMINISTRADOR", height=3, width=300, command=self.exibirMenuLoginAdministrador, bg="#78D1DE").pack(padx=15, pady=15)
        Button(self.menuLogin, text="VOLTAR AO MENU ANTERIOR", bg='#E3F2F9', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)

        self.menuLogin.pack(padx=20, pady=20) 

#---------------------------------MENU ABERTURA DE CONTA---------------------------------   
    def criarMenuAberturaDeConta(self):
        #Alguns frames são ocultados durante a exibição do menu de abertura de conta
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")

        #Define o frame do menu de abertura de conta
        self.menuAberturaDeConta = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)

        #Logo + Título do Frame
        self.labelImagem = tk.Label(self.menuAberturaDeConta, image=self.logo,bd=0, highlightthickness=0).pack()
        tk.Label(self.menuAberturaDeConta, text="SELECIONE O TIPO DE CONTA",font=('Arial',12, 'bold'),fg='#223C5E', bg='#E3F2F9').pack(pady=10)

        #Botões do menu de abertura de conta
        Button(self.menuAberturaDeConta, text="CONTA CORRENTE", height=3, width=300, bg="#78D1DE", command= lambda: self.criarMenuAberturaDeContaCorrentePoupanca("corrente")).pack(padx=15, pady=15)
        Button(self.menuAberturaDeConta, text="CONTA POUPANÇA", bg="#78D1DE", height=3, width=300, command=lambda: self.criarMenuAberturaDeContaCorrentePoupanca("poupanca")).pack(padx=15, pady=15)
        Button(self.menuAberturaDeConta, text="VOLTAR AO MENU ANTERIOR", bg='#E3F2F9', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)
    
        self.menuAberturaDeConta.pack(padx=20, pady=20)

#---------------------------------ABERTURA DE CONTA CORRENTE / POUPANÇA ---------------------------------   
    def criarMenuAberturaDeContaCorrentePoupanca(self, tipoConta):

        #Alguns frames são ocultados durante a exibição do menu de abertura de conta corrente ou poupança
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("informacoesConta")

        self.tipoConta = tipoConta

        #Criação do frame
        self.menuAberturaDeContaCorrentePoupanca = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)
        self.menuAberturaDeContaCorrentePoupanca.pack(padx=20, pady=20)

        tk.Label(self.menuAberturaDeContaCorrentePoupanca, text="ABERTURA DE CONTA",font=('Arial',12, 'bold'),fg='#223C5E', bg='#E3F2F9').pack()

        #Nome
        tk.Label(self.menuAberturaDeContaCorrentePoupanca,text="Nome completo:",bg="#E3F2F9", justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeNomeCompleto = tk.Entry(self.menuAberturaDeContaCorrentePoupanca, width=300)
        self.recebeNomeCompleto.pack(ipady=10, padx=15)

        #Endereço
        tk.Label(self.menuAberturaDeContaCorrentePoupanca,text="Endereço:",bg="#E3F2F9", justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeEndereco = tk.Entry(self.menuAberturaDeContaCorrentePoupanca, width=300)
        self.recebeEndereco.pack(ipady=10, padx=15)

        #CPF:
        tk.Label(self.menuAberturaDeContaCorrentePoupanca,text="CPF:",bg="#E3F2F9", justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeCPF = tk.Entry(self.menuAberturaDeContaCorrentePoupanca, width=300)
        self.recebeCPF.pack(ipady=10, padx=15)

        #Senha
        tk.Label(self.menuAberturaDeContaCorrentePoupanca,text="Senha numérica (6 dígitos):",bg="#E3F2F9", justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeSenha = tk.Entry(self.menuAberturaDeContaCorrentePoupanca, width=300)
        self.recebeSenha.pack(ipady=10, padx=15)

        #Botões do menu de criação de contas
        Button(self.menuAberturaDeContaCorrentePoupanca, text="CRIAR CONTA", height=3, width=300, bg="#78D1DE", command= self.funcaoCriarContaCorrentePoupanca).pack(padx=15, pady=15)
        Button(self.menuAberturaDeContaCorrentePoupanca, text="VOLTAR AO MENU ANTERIOR", bg='#E3F2F9', height=3, width=300, command=self.criarMenuAberturaDeConta).pack(padx=15, pady=15)
    
    def funcaoCriarContaCorrentePoupanca(self):
        # Pega valores dos campos de entrada
        nome = self.recebeNomeCompleto.get().strip()
        endereco = self.recebeEndereco.get().strip()
        cpf = self.recebeCPF.get().strip()
        senha = self.recebeSenha.get().strip()
        
        # Verifica se todos os campos foram preenchidos
        if not all([nome, endereco, cpf, senha]):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        try:

            if hasattr(self, 'tipoConta') and self.tipoConta == "corrente":
                self.contaLogin = ContaCorrente(nome, endereco, cpf, senha)
            else:
                self.contaLogin = ContaPoupanca(nome, endereco, cpf, senha)
            self.exibirTelaPosCadastro()
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

#------------------------------TELA PÓS CADASTRO---------------------------------------------
    def exibirTelaPosCadastro(self):
            self.ocultarFrame("menuPrincipal")
            self.ocultarFrame("menuAberturaDeConta")
            self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")

            self.telaPosCadastro = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)

            tk.Label(self.telaPosCadastro, text="CONTA CADASTRADA COM SUCESSO!",font=('Arial',12, 'bold'), bg='#E3F2F9',width=380).pack(pady=(30,10))
            self.labelImagem = tk.Label(self.telaPosCadastro, image=self.logo,bd=0, highlightthickness=0, pady=5).pack()
            tk.Label(self.telaPosCadastro, text=f"{self.contaLogin.titularConta.upper()}, é um prazer ter você com a gente.\nEstamos aqui para apoiar sua jornada com soluções pensadas\nespecialmente para estudantes como você.", bg='#E3F2F9').pack(padx=30, pady=15)
           
            # AGÊNCIA (selecionável)
            tk.Label(self.telaPosCadastro, text="AGÊNCIA:", bg='#E3F2F9', font=('Arial',10, 'bold')).pack(padx=15, pady=(15, 0), anchor='w')

            agencia = tk.Text(self.telaPosCadastro, height=1, font=('Arial',10), bg='white', bd=1, padx=5, pady=3)
            agencia.insert(tk.END, self.contaLogin.numeroAgencia)
            agencia.config(state='disabled')
            agencia.pack(padx=15, fill='x')

            # NÚMERO DA CONTA (selecionável)
            tk.Label(self.telaPosCadastro, text="NÚMERO DA CONTA:", bg='#E3F2F9', font=('Arial',10, 'bold')).pack(padx=15, pady=(15, 0), anchor='w')

            conta = tk.Text(self.telaPosCadastro, height=1, font=('Arial',10), bg='white', bd=1, padx=5, pady=3)
            conta.insert(tk.END, self.contaLogin.numeroConta)
            conta.config(state='disabled')
            conta.pack(padx=15, fill='x', pady=(0, 15))
            
            tk.Label(self.telaPosCadastro, text="Utilize as informações acima para realizar login.", bg='#E3F2F9',width=380).pack(pady=(15,20))
            tk.Button(self.telaPosCadastro, text="VOLTAR AO MENU PRINCIPAL",bg="#78D1DE", height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=(15,20))

            self.telaPosCadastro.pack()

#-------------------------------TELA LOGIN ADMINISTRADOR------------------------------------
    def exibirMenuLoginAdministrador(self):
        #Alguns frames são ocultados durante a exibição do menu de login
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuAprovacao")

        #Criação do Frame
        self.menuLoginAdministrador = tk.Frame(self.janelaPrincipal,bg='#E3F2F9', height=600, width=380)
        
        self.labelImagem = tk.Label(self.menuLoginAdministrador, image=self.logo,bd=0, highlightthickness=0).pack()
        tk.Label(self.menuLoginAdministrador,text="ÁREA DO ADMINISTRADOR",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(20,20))

        #Credencial para acesso do Administrador
        tk.Label(self.menuLoginAdministrador,text="N° de identificação (dica: 000): ",bg='#E3F2F9',justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeCodigoIdentificacaoAdm = tk.Entry(self.menuLoginAdministrador, width=300)
        self.recebeCodigoIdentificacaoAdm.pack(ipady=10, padx=15)

        #Botões do Frame
        tk.Button(self.menuLoginAdministrador, text="ACESSAR CONTA", height=3, width=300, bg="#78D1DE", command=self.validaLoginAdm).pack(padx=15, pady=15)
        tk.Button(self.menuLoginAdministrador, text="SAIR", bg='#D26060', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)

        self.menuLoginAdministrador.pack()

#-------------------------------TELA PRINCIPAL ADMINISTRADOR------------------------------------
    def exibirMenuAdministrador(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("gerenciamentoDeContasAdministrador")
        self.ocultarFrame("informacoesContaAdministrador")
        self.ocultarFrame("menuAprovacao")
        
        self.menuAdministrador = tk.Frame(self.janelaPrincipal,bg='#E3F2F9', height=600, width=380)

        tk.Label(self.menuAdministrador,text="Bem-vindo, ADMINISTRADOR",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(50,50))

        tk.Button(self.menuAdministrador, text="EXIBIR SOLICITAÇÕES", bg="#78D1DE", height=3, width=300, command=self.criarMenuAprovacaoExclusao).pack(padx=15, pady=15) #Gerencia solicitação de exclusão
        tk.Button(self.menuAdministrador, text="GERENCIAMENTO DE CONTAS", bg="#78D1DE", height=3, width=300, command=self.exibirGerenciamentoDeConntasAdministrador).pack(padx=15, pady=15) #Exibe informações sobre as contas selecionadas
        tk.Button(self.menuAdministrador, text="VOLTAR AO MENU PRINCIPAL", bg='#E3F2F9', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)

        self.menuAdministrador.pack()       


    def validaLoginAdm(self):
        if not self.recebeCodigoIdentificacaoAdm.get(): #Indiica que o campo é obrigatório
            messagebox.showerror("Erro","Digite número de identificação do Administrador.")
            return False
        if self.recebeCodigoIdentificacaoAdm.get() == Administrador.getCodigo():
            self.exibirMenuAdministrador()
        else:
            messagebox.showerror("Erro","Login inválido!")

#-------------------------------GERENCIA SOLICITAÇÕES DE EXCLUSÃO------------------------------------
    def criarMenuAprovacaoExclusao(self):
        if hasattr(self, 'menuAprovacao'):
            self.menuAprovacao.destroy()
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("menuAdministrador")
        self.ocultarFrame("informacoesContaAdministrador")
        self.ocultarFrame("menuExclusaoConta")
        self.ocultarFrame("menuAprovação")
        
        self.menuAprovacao = tk.Frame(self.janelaPrincipal, bg='#E3F2F9')
        self.menuAprovacao.pack(fill='both', expand=True)
        
        self.padronizarLabels(self.janelaPrincipal)

        # Título
        tk.Label(self.menuAprovacao, text="SOLICITAÇÕES DE EXCLUSÃO", font=('Arial',12, 'bold'), bg='#E3F2F9').pack(pady=20)
        
        # Lista de solicitações
        frameLista = tk.Frame(self.menuAprovacao, bg='#E3F2F9')
        frameLista.pack(fill='x', padx=20)
        
        solicitacoes = Administrador.listarSolicitacoes()
        if not solicitacoes:
            tk.Label(frameLista, text="Nenhuma solicitação pendente", bg='#E3F2F9').pack()
        else:
            for solic in solicitacoes:
                tk.Label(frameLista, text=solic, anchor='w', bg='#E3F2F9').pack(fill='x', pady=5)
        
        # Controles de aprovação
        frameControles = tk.Frame(self.menuAprovacao, bg='#E3F2F9')
        frameControles.pack(pady=20)

        # Frame para Label + Entry
        frameId = tk.Frame(frameControles, bg='#E3F2F9')
        frameId.pack()

        tk.Label(frameId, text="ID da solicitação:", bg='#E3F2F9').pack(side='left')
        self.entryIdSolicitacao = tk.Entry(frameId, width=10)
        self.entryIdSolicitacao.pack(side='left', padx=5, pady=10,ipady=6)

        # Frame para os botões Aprovar/Rejeitar
        frameBotoes = tk.Frame(frameControles, bg='#E3F2F9')
        frameBotoes.pack()

        tk.Button(frameBotoes, text="APROVAR", bg="#78D1DE", width=300, height=3, command=lambda: self.processarAprovacao(True)).pack(padx=15,pady=15)
        tk.Button(frameBotoes, text="REJEITAR",bg='#D26060', width=300, height=3, command=lambda: self.processarAprovacao(False)).pack(padx=15,pady=15)
        tk.Button(self.menuAprovacao, text="VOLTAR", bg='#E3F2F9', width=300,  height=3, command=self.exibirMenuAdministrador).pack(padx=15,pady=15)

    def processarAprovacao(self, aprovar):
        try:
            idSolicitacao = int(self.entryIdSolicitacao.get())
            if aprovar:
                resultado = Administrador.aprovarExclusao(idSolicitacao)
                messagebox.showinfo("Sucesso", resultado)
            else:
                resultado = Administrador.rejeitarExclusao(idSolicitacao)
                messagebox.showinfo("Sucesso", resultado)
            
            self.criarMenuAprovacaoExclusao()  # Atualiza a lista

        except ValueError:
            messagebox.showerror("Erro", "ID da solicitação inválido! Por favor, digite apenas números.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")

#-------------------------------TELA GERENCIAMENTO DE CONTAS - ADMINISTRADOR------------------------------------
    def exibirGerenciamentoDeConntasAdministrador(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("menuAdministrador")
        self.ocultarFrame("informacoesContaAdministrador")
        
        self.gerenciamentoDeContasAdministrador = tk.Frame(self.janelaPrincipal,bg='#E3F2F9', height=600, width=380)
        self.gerenciamentoDeContasAdministrador.pack()       
        tk.Label(self.gerenciamentoDeContasAdministrador,text="GERENCIAMENTO DE CONTAS",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(50,50))
        tk.Label(self.gerenciamentoDeContasAdministrador, text="Número da agência:", width=300, justify="left",anchor="w",bg='#E3F2F9').pack(anchor="w",padx=15, pady=15)
        self.agenciaPesquisaAdm = tk.Entry(self.gerenciamentoDeContasAdministrador,width=300)
        self.agenciaPesquisaAdm.pack(ipady=10, padx=15)
        tk.Label(self.gerenciamentoDeContasAdministrador, text="Número da conta:", width=300, justify="left",anchor="w",bg='#E3F2F9').pack(anchor="w",padx=15, pady=15)
        self.contaPesquisaAdm = tk.Entry(self.gerenciamentoDeContasAdministrador,width=300)
        self.contaPesquisaAdm.pack(ipady=10, padx=15)
        tk.Button(self.gerenciamentoDeContasAdministrador, text="EXIBIR DETALHES", bg="#78D1DE", height=3, width=300, command=self.recebeContaParaAnalise).pack(padx=15, pady=(50,15))
        tk.Button(self.gerenciamentoDeContasAdministrador, text="VOLTAR AO MENU ANTERIOR",bg='#E3F2F9', height=3, width=300, command=self.exibirMenuAdministrador).pack(padx=15, pady=(50,15))

    def recebeContaParaAnalise(self):
        agencia = self.agenciaPesquisaAdm.get().strip()
        numeroC = self.contaPesquisaAdm.get().strip()

        self.contaLogin = Administrador.verificaSeExisteCadastro(numeroC,agencia)
        if self.contaLogin is not None:
            self.exibirInformacoesContaAdministrador()
        else:
            messagebox.showerror("Erro","Conta não encontrada.")

#------------------------------INFORMAÇÕES DA CONTA -> Administrador----------------------------------------
    def exibirInformacoesContaAdministrador(self): 
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginAdministrador")
        self.ocultarFrame("menuAdministrador")
        self.ocultarFrame("gerenciamentoDeContasAdministrador")
        
        self.informacoesContaAdministrador = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)
        tk.Label(self.informacoesContaAdministrador, text="DADOS DO CLIENTE:", bg='#E3F2F9',width=380,font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(50,10))
        tk.Label(self.informacoesContaAdministrador, text = f"Tipo de conta: {self.contaLogin.tipoContaCriada}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaAdministrador, text=f"Agência: {self.contaLogin.numeroAgencia}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaAdministrador, text=f"Número da conta: {self.contaLogin.numeroConta}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaAdministrador, text=f"Titular: {self.contaLogin.titularConta}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaAdministrador, text=f"Endereço: {self.contaLogin.enderecoTitular}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaAdministrador, text=f"Senha: {self.contaLogin.senha}", bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Button(self.informacoesContaAdministrador, text="VOLTAR MENU ANTERIOR",bg='#D26060', height=3, width=300, command=self.exibirGerenciamentoDeConntasAdministrador).pack(padx=15, pady=(30,50))
        # self.atualizarLabelsEndereco()
        self.informacoesContaAdministrador.pack()

#-------------------------------TELA LOGIN CLIENTE------------------------------------
    def exibirMenuLoginCliente(self):
        #Alguns frames são ocultados durante a exibição do menu de login do cliente
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuExtrato")

        #Define o frame do menu de abertura de conta
        self.menuLoginCliente = tk.Frame(self.janelaPrincipal,bg='#E3F2F9', height=600, width=380)

        #Logo + título do frame
        self.labelImagem = tk.Label(self.menuLoginCliente, image=self.logo,bd=0, highlightthickness=0).pack()
        tk.Label(self.menuLoginCliente,text="ÁREA DO CLIENTE",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(20,20))
        
        #Recebe o número da agência digitada pelo usuário
        tk.Label(self.menuLoginCliente,text="Agência (dica -> ver CLI):",bg='#E3F2F9',justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeAgenciaCliente = tk.Entry(self.menuLoginCliente, width=300)
        self.recebeAgenciaCliente.pack(ipady=10, padx=15)
        
        #Recebe o número da conta digitado
        tk.Label(self.menuLoginCliente,text="N° da conta: (CPXXXXX-X ou CCXXXXX-X):" ,bg='#E3F2F9',justify="left").pack(padx=15, pady=10, anchor="w")
        self.recebeNumContaCliente = tk.Entry(self.menuLoginCliente, width=300)
        self.recebeNumContaCliente.pack(ipady=10, padx=15)

        #Botões de Login/Sair da página
        tk.Button(self.menuLoginCliente, text="ACESSAR CONTA", height=3, width=300, bg="#78D1DE", command=self.validaLoginCliente).pack(padx=15, pady=15)
        tk.Button(self.menuLoginCliente, text="SAIR", bg='#D26060', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)


        self.menuLoginCliente.pack()


#-------------------------------TELA MENU PRINCIPAL CLIENTE------------------------------------
    def exibirMenuCliente(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginCliente")
        self.ocultarFrame("informacoesConta")
        self.ocultarFrame("trasacoesBancarias")
        self.ocultarFrame("informacoesContaCliente")
        self.ocultarFrame("menuAlteracaoEndereco")
        self.ocultarFrame("telaExclusaoConta")       
        self.ocultarFrame("menuExtrato")
        self.ocultarFrame("menuCliente")
        self.ocultarFrame("menuSaque")
        self.ocultarFrame("menuTransferir")
        self.ocultarFrame("menuDepositoLogado")



        self.menuCliente = tk.Frame(self.janelaPrincipal,bg='#E3F2F9', height=600, width=380)
        self.menuCliente.pack()       
        tk.Label(self.menuCliente,text=f"Bem-vindo(a), {self.contaLogin.titularConta.upper()}",bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(30,20))
        saldoDisplay = tk.Frame(self.menuCliente, bg='white', padx=20, pady=10, highlightbackground="#DDD", highlightthickness=1)
        saldoDisplay.pack(padx=10)
        tk.Label(saldoDisplay, text=f"R$ {self.contaLogin.saldoAtual:.2f}", bg='white', font=('Arial', 12, 'bold'), fg='#223C5E').pack()
        tk.Button(self.menuCliente, text="REALIZAR TRANSAÇÃO", bg="#78D1DE", height=3, width=300, command=self.exibirTransacoesBancarias).pack(padx=15, pady=15)
        tk.Button(self.menuCliente, text="ALTERAR ENDEREÇO", bg="#78D1DE", height=3, width=300, command=self.criaMenuAlteracaoEndereco).pack(padx=15, pady=15)
        tk.Button(self.menuCliente, text="INFORMAÇÕES DA CONTA", bg="#78D1DE", height=3, width=300, command=self.exibirInformacoesContaCliente).pack(padx=15, pady=15)
        tk.Button(self.menuCliente, text="EXCLUSÃO DA CONTA",bg='#E3F2F9', height=3, width=300, command=self.criaMenuExclusaoConta).pack(padx=15, pady=15)
        tk.Button(self.menuCliente, text="VOLTAR AO MENU PRINCIPAL", bg='#E3F2F9', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)

    def validaLoginCliente(self):

        agenciaParametro = self.recebeAgenciaCliente.get().strip()
        contaParametro = self.recebeNumContaCliente.get().strip().upper()

        if not all([agenciaParametro, contaParametro]):
            messagebox.showerror("Erro","Todos os campos devem ser preenchidos.")
            return False
        
        self.contaLogin =  Administrador.verificaSeExisteCadastro(contaParametro,agenciaParametro)
        if self.contaLogin is not None:
            self.exibirMenuCliente()
        
#-------------------------------VER TRANSAÇÕES BANCÁRIAS------------------------------------
    def exibirTransacoesBancarias(self, refresh=False):
    # Oculta todos os frames relevantes
        frames_para_ocultar = [
            "menuPrincipal", "menuLogin", "menuLoginCliente",
            "informacoesConta", "menuCliente", "menuDepositoLogado",
            "menuSaque", "menuExtrato", "menuTransferir"
        ]
        
        for frame in frames_para_ocultar:
            self.ocultarFrame(frame)
        
        # Destrói o frame antigo se for um refresh
        if refresh and hasattr(self, 'trasacoesBancarias'):
            self.trasacoesBancarias.destroy()
        
        # Cria um NOVO frame
        self.trasacoesBancarias = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        self.trasacoesBancarias.pack()
        
        tk.Label(self.trasacoesBancarias, text="TRANSAÇÕES DISPONÍVEIS", 
                bg='#E3F2F9', font=('Arial',12, 'bold'), fg='#223C5E').pack(pady=(50,50))
        
        # Botões com verificação de estado
        botoes = [
            ("EXIBIR EXTRATO", self.criarMenuExtrato),
            ("TRANSFERIR", self.criarMenuTransferir),
            ("DEPOSITAR", self.criarMenuDepositoLogado),
            ("SACAR", self.criarMenuSaque),
            ("VOLTAR", self.exibirMenuCliente)
        ]
        
        for texto, comando in botoes:
            btn = tk.Button(self.trasacoesBancarias, text=texto, 
                        bg="#78D1DE" if texto != "VOLTAR" else '#E3F2F9',
                        height=3, width=300, command=comando)
            btn.pack(padx=15, pady=15)
            
            # Desativa botões se saldo for negativo (opcional)
            if texto in ["TRANSFERIR", "SACAR"] and self.contaLogin.saldoAtual < 0:
                btn.config(state='disabled', bg='#CCCCCC')

#------------------------------INFORMAÇÕES DA CONTA -> Cliente----------------------------------------
    def exibirInformacoesContaCliente(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")
        self.ocultarFrame("menuCliente")
        self.ocultarFrame("menuAlteracaoEndereco")

        self.informacoesContaCliente = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)
        self.informacoesContaCliente.pack()
        tk.Label(self.informacoesContaCliente, text="MEUS DADOS:", bg='#E3F2F9',width=380,font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(50,10))
        tk.Label(self.informacoesContaCliente, text = "Tipo de conta: "+self.contaLogin.tipoContaCriada, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaCliente, text="Agência: "+self.contaLogin.numeroAgencia, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaCliente, text="Número da conta: "+self.contaLogin.numeroConta, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaCliente, text="Titular: "+self.contaLogin.titularConta, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaCliente, text="Endereço: "+self.contaLogin.enderecoTitular, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Label(self.informacoesContaCliente, text="Senha: "+self.contaLogin.senha, bg='#E3F2F9').pack(anchor="w",padx=30, pady=5)
        tk.Button(self.informacoesContaCliente, text="VOLTAR AO MENU DA CONTA", bg="#78D1DE", height=3, width=300, command=self.exibirMenuCliente).pack(padx=15, pady=(30,50))
    
#-------------------------------TELA ALTERAÇÃO DE ENDEREÇO------------------------------------
    def criaMenuAlteracaoEndereco(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")
        self.ocultarFrame("menuCliente")
        
        self.menuAlteracaoEndereco = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        self.menuAlteracaoEndereco.pack()       
        
        # Componentes da interface
        tk.Label(self.menuAlteracaoEndereco, text="ALTERAR ENDEREÇO", bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(50,20))
        tk.Label(self.menuAlteracaoEndereco, text="A alteração será refletida em todas as suas contas.", width=300, bg='#E3F2F9', wraplength=350).pack(padx=15, pady=15)
        tk.Label(self.menuAlteracaoEndereco, text="Novo endereço completo:", width=300, justify="left", anchor="w", bg='#E3F2F9').pack(anchor="w", padx=15, pady=5)
        self.entryNovoEndereco = tk.Entry(self.menuAlteracaoEndereco, width=300)
        self.entryNovoEndereco.pack(ipady=10, padx=15, pady=(0,15))
        tk.Button(self.menuAlteracaoEndereco, text="CONFIRMAR ALTERAÇÃO", bg="#78D1DE", height=3, width=300, command=self.processarAlteracaoEndereco).pack(padx=15, pady=(30,15))
        tk.Button(self.menuAlteracaoEndereco, text="VOLTAR AO MENU", bg='#E3F2F9', height=3, width=300, command=self.exibirMenuCliente).pack(padx=15, pady=15)
    
    def processarAlteracaoEndereco(self):
        novoEndereco = self.entryNovoEndereco.get().strip()
        
        if not novoEndereco:
            messagebox.showerror("Erro", "Por favor, informe o novo endereço!")
            return
        
        try:
            contasAlteradas = Administrador.alterarEnderecoPorNome(
                self.contaLogin.titularConta,novoEndereco,self.contaLogin.cpf)
            
            if contasAlteradas > 0:
                # Atualiza o objeto local imediatamente
                self.contaLogin.enderecoTitular = novoEndereco
                
                # Força atualização da UI
                self.exibirInformacoesContaCliente()
                
                messagebox.showinfo("Sucesso", 
                                f"Endereço atualizado em {contasAlteradas} conta(s)!\n"
                                f"Novo endereço: {novoEndereco}")
            else:
                messagebox.showerror("Erro", "Nenhuma conta encontrada para alteração!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na alteração:\n{str(e)}")

#-------------------------------EXCLUSÃO DE CONTA------------------------------------
    def criaMenuExclusaoConta(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")
        self.ocultarFrame("menuCliente")

        self.telaExclusaoConta = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        self.telaExclusaoConta.pack()       
        
        # Componentes da interface
        tk.Label(self.telaExclusaoConta, text="EXCLUSÃO DA CONTA", bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(30,20))
        
        # Status da solicitação (agora com mais informações)
        self.labelStatus = tk.Label(self.telaExclusaoConta, text="", bg='#E3F2F9', fg='#333333', wraplength=350)
        self.labelStatus.pack(pady=10)
        
        tk.Label(self.telaExclusaoConta, text="Solicitações podem ser canceladas até a aprovação do administrador.", width=300, bg='#E3F2F9', wraplength=350).pack(padx=15, pady=15)
        
        # Frame para botões principais
        frameBotoes = tk.Frame(self.telaExclusaoConta, bg='#E3F2F9')
        frameBotoes.pack(pady=10)
        
        self.btnConfirmar = tk.Button(frameBotoes, text="SOLICITAR EXCLUSÃO", height=3, width=300,command=self.confirmarExclusaoConta, bg='#FF6B6B')
        self.btnConfirmar.pack(padx=15, pady=15)
        self.btnCancelar = tk.Button(frameBotoes, text="CANCELAR SOLICITAÇÃO", height=3, width=300,command=self.cancelarExclusaoConta, bg="#78D1DE", state='disabled')
        self.btnCancelar.pack(padx=15,pady=15)
        tk.Button(self.telaExclusaoConta, text="VOLTAR",bg='#E3F2F9', height=3, width=300,command=self.exibirMenuCliente).pack(pady=10)
        
        self.atualizarStatusExclusao()

    #Auxilia no processo de exclusão atualizando o status
    def atualizarStatusExclusao(self):
        if hasattr(self.contaLogin, 'solicitacaoExclusao'):
            status = Administrador.verificarStatusExclusao(self.contaLogin.numeroConta)
            self.labelStatus.config(text=f"Status: {status}\nEnviada em: {self.contaLogin.solicitacaoExclusao['data']}", fg='#006600')
            self.btnConfirmar.config(state='disabled')
            self.btnCancelar.config(state='normal')
        else:
            self.labelStatus.config(text="Nenhuma solicitação ativa", fg='#333333')
            self.btnConfirmar.config(state='normal')
            self.btnCancelar.config(state='disabled')

    def confirmarExclusaoConta(self):
        try:
            self.contaLogin.solicitarExclusaoConta()
            self.atualizarStatusExclusao()
        except ValueError as e:
            self.labelStatus.config(text=str(e), fg='#CC0000')
        except Exception as e:
            messagebox.showerror("Erro", f"Falha inesperada:\n{str(e)}")

    def cancelarExclusaoConta(self):
        try:
            if hasattr(self.contaLogin, 'solicitacaoExclusao'):
                Administrador.cancelarSolicitacao(self.contaLogin.numeroConta)
                del self.contaLogin.solicitacaoExclusao
                self.labelStatus.config(text="Solicitação cancelada com sucesso!", fg='#006600')
                self.janelaPrincipal.after(2000, self.atualizarStatusExclusao)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao cancelar:\n{str(e)}")
    
#---------------------------------DEPÓSITO LOGADO---------------------------------   

    def criarMenuDepositoLogado(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginCliente")
        self.ocultarFrame("trasacoesBancarias")
        self.ocultarFrame("informacoesContaCliente")  
        
        self.menuDepositoLogado = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        
        tk.Label(self.menuDepositoLogado, text="DEPÓSITO", bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(0,10))
        
        tk.Label(self.menuDepositoLogado, text="Valor do depósito:", bg='#E3F2F9').pack(anchor="w", padx=15)
        self.recebeValorDepositoLogado = tk.Entry(self.menuDepositoLogado, width=300)
        self.recebeValorDepositoLogado.pack(ipady=10, padx=15, pady=(0,15))
        
        tk.Button(self.menuDepositoLogado, text="DEPOSITAR HOJE", bg="#78D1DE", height=3, width=300, command=lambda: self.processarDeposito("hoje")).pack(padx=15, pady=(25,5))
        tk.Button(self.menuDepositoLogado, text="PROGRAMAR DEPÓSITO",bg='#E3F2F9', height=3, width=300, command=lambda: self.processarDeposito("programar")).pack(padx=15, pady=(25,5))
        tk.Button(self.menuDepositoLogado, text="CANCELAR", bg='#D26060', height=3, width=300, command=self.exibirTransacoesBancarias).pack(padx=15, pady=15)
        
        self.menuDepositoLogado.pack()

    def processarDeposito(self, tipoDeposito):
        valor = self.recebeValorDepositoLogado.get()
        
        if not self.validarValorDeposito(valor):
            return
        
        if tipoDeposito == "hoje":
            data = date.today().strftime("%d/%m/%Y")
            self.executarDeposito(float(valor), data)
        else:
            self.solicitarDataDeposito(float(valor))

    def validarValorDeposito(self, valor):
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                messagebox.showerror("Erro", "O valor deve ser positivo!")
                return False
            return True
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido! Digite um número.")
            return False

    def executarDeposito(self, valor, data):
        try:
            # Verifica se o valor é positivo
            if valor <= 0:
                messagebox.showerror("Erro", "O valor do depósito deve ser positivo.")
                return

            valor_depositado_total = valor  # Guarda o valor original para exibição
            
            # Para contas corrente: repõe cheque especial primeiro
            if hasattr(self.contaLogin, 'limiteChequeEspecial'):
                # Verifica se há limite original definido, senão usa o atual como referência
                limite_original = getattr(self.contaLogin, 'limiteChequeEspecialOriginal', 
                                    self.contaLogin.limiteChequeEspecial)
                
                # Calcula quanto falta para repor totalmente o cheque especial
                deficit_cheque_especial = limite_original - self.contaLogin.limiteChequeEspecial
                
                if deficit_cheque_especial > 0:
                    # Repõe o cheque especial com parte ou todo o valor depositado
                    valor_repor = min(valor, deficit_cheque_especial)
                    self.contaLogin.limiteChequeEspecial += valor_repor
                    valor -= valor_repor  # Subtrai do valor a ser depositado

            # Deposita o valor restante na conta
            self.contaLogin.saldoAtual += valor
            
            # Registra a transação no histórico
            transacao = f"Depósito - R$ {valor_depositado_total:.2f} - {data}"
            self.contaLogin.adicionaTransacaoHistorico(transacao)
            
            # Prepara mensagem de sucesso
            mensagem = f"Depósito de R${valor_depositado_total:.2f} realizado!\n"
            mensagem += f"Saldo atual: R${self.contaLogin.saldoAtual:.2f}"
            
            if hasattr(self.contaLogin, 'limiteChequeEspecial'):
                mensagem += f"\nCheque especial disponível: R${self.contaLogin.limiteChequeEspecial:.2f}"
            
            messagebox.showinfo("Sucesso", mensagem)
            
            # Atualiza a interface se necessário
            if hasattr(self, 'textoExtrato'):
                self.atualizarExibicaoExtrato()
                
            self.exibirTransacoesBancarias()  # Volta ao menu

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao realizar o depósito: {str(e)}")
    
    def solicitarDataDeposito(self, valor):
        top = tk.Toplevel()
        top.title("Programar Depósito")
        top.geometry("300x200")
        
        tk.Label(top, text="Data (DD/MM/AAAA):").pack(pady=10)
        entrada_data = tk.Entry(top)
        entrada_data.pack(pady=5)
        
        def confirmar():
            dataStr = entrada_data.get()
            try:
                data = datetime.strptime(dataStr, "%d/%m/%Y").date()
                if data < date.today():
                    messagebox.showerror("Erro", "Data deve ser futura!")
                else:
                    top.destroy()
                    self.executarDeposito(valor, data.strftime("%d/%m/%Y"))
            except ValueError:
                messagebox.showerror("Erro", "Formato inválido! Use DD/MM/AAAA")
        
        tk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)
        
#---------------------------------SAQUE---------------------------------   

    def criarMenuSaque(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginCliente")
        self.ocultarFrame("trasacoesBancarias")
        self.ocultarFrame("informacoesContaCliente")        

        self.menuSaque = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        
        # Componentes da interface
        tk.Label(self.menuSaque, text="SAQUE", bg='#E3F2F9',font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(0,10))
        
        tk.Label(self.menuSaque, text="Valor do saque:", bg='#E3F2F9').pack(anchor="w", padx=15)
        self.recebeValorSaque = tk.Entry(self.menuSaque, width=300)
        self.recebeValorSaque.pack(ipady=10, padx=15, pady=(0,15))
        
        tk.Button(self.menuSaque, text="SACAR HOJE", bg="#78D1DE", height=3, width=300, command=lambda: self.processarSaque("hoje")).pack(padx=15, pady=(25,5))
        
        tk.Button(self.menuSaque, text="PROGRAMAR SAQUE",bg='#E3F2F9', height=3, width=300, command=lambda: self.processarSaque("programar")).pack(padx=15, pady=(25,5))
        
        tk.Button(self.menuSaque, text="CANCELAR", bg='#D26060', height=3, width=300, command=self.exibirTransacoesBancarias).pack(padx=15, pady=15)
        
        self.menuSaque.pack()

        #Adicionado recentemente
        self.recebeValorSaque.focus_set()
        if self.contaLogin.saldoAtual < 0:
            messagebox.showwarning("Aviso", "Você está no cheque especial.\nNovos saques podem ser limitados.")
            self.btnSacarHoje.config(state='disabled', bg='#CCCCCC')
        
    def processarSaque(self, tipoSaque):
        try:
            valor = self.recebeValorSaque.get()
            
            if not self.validarValorSaque(valor):
                return
            
            if tipoSaque == "hoje":
                data = date.today().strftime("%d/%m/%Y")
                self.executarSaque(float(valor), data)
            else:
                self.solicitarDataSaque(float(valor))
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")
            print(f"Erro detalhado: {e}")

    def validarValorSaque(self, valor):
        try:
            valorFloat = float(valor)
            if valorFloat <= 0:
                self.recebeValorSaque.config(bg='#FFDDDD')  # Fundo vermelho claro
                messagebox.showerror("Erro", "Valor deve ser positivo!")
                return False
            self.recebeValorSaque.config(bg='white')  # Reset ao acertar
            return True
        except ValueError:
            self.recebeValorSaque.config(bg='#FFDDDD')
            messagebox.showerror("Erro", "Valor inválido! Digite um número.")
            return False

    def executarSaque(self, valor, data):
        if self.contaLogin.tipoContaCriada.upper() == "CORRENTE":
            self.processarSaqueContaCorrente(valor, data)
        else:
            self.processarSaquePoupanca(valor, data)

    def processarSaqueContaCorrente(self, valor, data):
        saldoTotal = self.contaLogin.saldoAtual + self.contaLogin.limiteChequeEspecial
        
        if valor > saldoTotal:
            messagebox.showerror("Erro", f"Saldo total insuficiente (R${saldoTotal:.2f})")
            self.recebeValorSaque.delete(0, tk.END)
            self.recebeValorSaque.focus_set()
            return
        
        try:
            if valor <= self.contaLogin.saldoAtual:
                # Saque normal
                self.contaLogin.saldoAtual -= valor
                self.contaLogin.adicionaTransacaoHistorico(f"Saque - R${valor:.2f} - {data}")
                mensagem = f"Saque de R${valor:.2f} realizado!\nNovo saldo: R${self.contaLogin.saldoAtual:.2f}"
            else:
                # Usar cheque especial
                self.utilizarChequeEspecial(valor, data)
                mensagem = f"Saque com cheque especial realizado!\nSaldo atual: R${self.contaLogin.saldoAtual:.2f}\nLimite restante: R${self.contaLogin.limiteChequeEspecial:.2f}"
            
            # Atualização completa da interface
            self.recebeValorSaque.delete(0, tk.END)
            messagebox.showinfo("Sucesso", mensagem)
            self.exibirTransacoesBancarias(refresh=True)  # Força atualização
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no saque: {str(e)}")
            self.recebeValorSaque.focus_set()


    def utilizarChequeEspecial(self, valor, data):
        resposta = messagebox.askyesno(
            "Cheque Especial", 
            f"Saldo insuficiente. Usar cheque especial?\n"
            f"Valor necessário: R$ {valor - self.contaLogin.saldoAtual:.2f}\n"
            f"Limite disponível: R$ {self.contaLogin.limiteChequeEspecial:.2f}")
        
        if not resposta:
            self.recebeValorSaque.delete(0, tk.END)
            self.recebeValorSaque.focus_set()
            return

        valorCheque = valor - self.contaLogin.saldoAtual
        self.contaLogin.saldoAtual -= valor  # Isso deixará o saldo negativo
        self.contaLogin.limiteChequeEspecial -= valorCheque
        
        self.contaLogin.adicionaTransacaoHistorico(
            f"Saque com Cheque Especial - R$ {valor:.2f} - {data}")
        
        messagebox.showinfo("Sucesso", 
            f"Saque realizado!\n"
            f"Saldo atual: -R$ {abs(self.contaLogin.saldoAtual):.2f}\n"
            f"Limite restante: R$ {self.contaLogin.limiteChequeEspecial:.2f}")
        
        self.exibirTransacoesBancarias()
        self.atualizarExibicaoExtrato()

    def processarSaquePoupanca(self, valor, data):
        if valor > self.contaLogin.saldoAtual:
            messagebox.showerror("Erro", f"Saldo insuficiente (R${self.contaLogin.saldoAtual:.2f})")
            self.recebeValorSaque.delete(0, tk.END)
            self.recebeValorSaque.focus_set()
            return
        
        self.contaLogin.saldoAtual -= valor
        # Adicione esta linha:
        self.contaLogin.adicionaTransacaoHistorico(f"Saque - R$ {valor:.2f} - {data}")
        messagebox.showinfo("Sucesso", f"Saque de R${valor:.2f} realizado!\nNovo saldo: R${self.contaLogin.saldoAtual:.2f}")
        self.exibirMenuCliente()
        self.atualizarExibicaoExtrato()

    def solicitarDataSaque(self, valor):
        top = tk.Toplevel()
        top.title("Programar Saque")
        top.geometry("300x200")
        
        tk.Label(top, text="Data (DD/MM/AAAA):").pack(pady=10)
        entradaData = tk.Entry(top)
        entradaData.pack(pady=5)
        
        def confirmar():
            dataStr = entradaData.get()
            try:
                data = datetime.strptime(dataStr, "%d/%m/%Y").date()
                if data < date.today():
                    messagebox.showerror("Erro", "Data deve ser futura!")
                else:
                    top.destroy()
                    self.executarSaque(valor, data.strftime("%d/%m/%Y"))
            except ValueError:
                messagebox.showerror("Erro", "Formato inválido! Use DD/MM/AAAA")
        
        tk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

#---------------------------------TRANSFERÊNCIA---------------------------------   
    def criarMenuTransferir(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuLogin")
        self.ocultarFrame("menuLoginCliente")
        self.ocultarFrame("trasacoesBancarias")
        self.ocultarFrame("informacoesContaCliente")      

        self.menuTransferir = tk.Frame(self.janelaPrincipal, bg='#E3F2F9', height=600, width=380)
        
        # Componentes da interface
        tk.Label(self.menuTransferir, text="TRANSFERÊNCIA", bg='#E3F2F9', font=('Arial', 12, 'bold')).pack(pady=(10,20))
        
        # Conta destino
        tk.Label(self.menuTransferir, text="Conta beneficiada:", bg='#E3F2F9').pack(anchor="w", padx=15)
        self.entryContaDestino = tk.Entry(self.menuTransferir, width=300)
        self.entryContaDestino.pack(ipady=10, padx=15, pady=(0,15))
        
        # Valor
        tk.Label(self.menuTransferir, text="Valor:", bg='#E3F2F9').pack(anchor="w", padx=15)
        self.entryValorTransferencia = tk.Entry(self.menuTransferir, width=300)
        self.entryValorTransferencia.pack(ipady=10, padx=15, pady=(0,15))
        
        # Botões
        tk.Button(self.menuTransferir, text="TRANSFERIR AGORA", bg="#78D1DE", height=3, width=300,command=lambda: self.processarTransferencia("hoje")).pack(padx=15, pady=(25,5))
        
        tk.Button(self.menuTransferir, text="PROGRAMAR TRANSFERÊNCIA",bg='#E3F2F9', height=3, width=300,command=lambda: self.processarTransferencia("programar")).pack(padx=15, pady=(25,5))
        
        tk.Button(self.menuTransferir, text="CANCELAR", bg='#D26060', height=3, width=300,command=self.exibirTransacoesBancarias).pack(padx=15, pady=15)
        
        self.menuTransferir.pack()

    def processarTransferencia(self, tipoTransferencia):
        contaDestino = self.entryContaDestino.get().strip().upper()
        valor_str = self.entryValorTransferencia.get().strip()
        
        if not self.validarDadosTransferencia(contaDestino, valor_str):
            return
        
        valor = float(valor_str)
        
        if tipoTransferencia == "hoje":
            data = date.today().strftime("%d/%m/%Y")
            self.executarTransferencia(contaDestino, valor, data)
        else:
            self.solicitarDataTransferencia(contaDestino, valor)

    def validarDadosTransferencia(self, contaDestino, valor_str):
        if not contaDestino:
            messagebox.showerror("Erro", "Informe a conta destino!")
            return False
        
        try:
            valor = float(valor_str)
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser positivo!")
                return False
            return True
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido! Digite um número.")
            return False

    def executarTransferencia(self, contaDestino, valor, data):
        # Verifica se não está transferindo para si mesmo
        if contaDestino == self.contaLogin.numeroConta:
            messagebox.showerror("Erro", "Não é possível transferir para a própria conta!")
            return
        
        # Encontra a conta destino
        contaDestino_obj = None
        for conta in Administrador.get__contasCorrenteCadastradas() + Administrador.get__contasPoupancaCadastradas():
            if conta.numeroConta == contaDestino:
                contaDestino_obj = conta
                break
        
        if not contaDestino_obj:
            messagebox.showerror("Erro", "Conta destino não encontrada!")
            return
        
        # Verifica saldo e cheque especial (se conta corrente)
        if isinstance(self.contaLogin, ContaCorrente):
            saldo_total = self.contaLogin.saldoAtual + self.contaLogin.limiteChequeEspecial
            
            if valor > saldo_total:
                messagebox.showerror("Erro", f"Saldo total insuficiente (R${saldo_total:.2f})")
                return
            
            if valor > self.contaLogin.saldoAtual:
                self.usarChequeEspecialTransferencia(contaDestino_obj, valor, data)
                return
        
        # Executa transferência normal
        self.contaLogin.saldoAtual -= valor
        contaDestino_obj.saldoAtual += valor
        
        # Registra transações
        operacao_origem = f"Transferência - R${valor:.2f} - {data} - Para: {contaDestino_obj.numeroConta}"
        operacao_destino = f"Transferência recebida - R${valor:.2f} - {data} - De: {self.contaLogin.numeroConta}"
        
        self.contaLogin.adicionaTransacaoHistorico(operacao_origem)
        contaDestino_obj.adicionaTransacaoHistorico(operacao_destino)
        
        messagebox.showinfo("Sucesso", f"Transferência de R${valor:.2f} realizada com sucesso!")
        self.exibirTransacoesBancarias()
        self.atualizarExibicaoExtrato()  # Atualiza o extrato

    def usarChequeEspecialTransferencia(self, contaDestino, valor, data):
        resposta = messagebox.askyesno(
            "Cheque Especial", 
            f"Saldo insuficiente. Usar cheque especial?\n\n"
            f"Valor necessário: R${valor:.2f}\n"
            f"Saldo disponível: R${self.contaLogin.saldoAtual:.2f}\n"
            f"Limite cheque especial: R${self.contaLogin.limiteChequeEspecial:.2f}"
        )
        
        if resposta:
            valor_cheque = valor - self.contaLogin.saldoAtual
            self.contaLogin.saldoAtual = 0
            self.contaLogin.limiteChequeEspecial -= valor_cheque
            
            contaDestino.saldoAtual += valor
            
            # Registra transações
            operacao_origem = f"Transferência (cheque especial) - R${valor:.2f} - {data} - Para: {contaDestino.numeroConta}"
            operacao_destino = f"Transferência recebida - R${valor:.2f} - {data} - De: {self.contaLogin.numeroConta}"
            
            self.contaLogin.adicionaTransacaoHistorico(operacao_origem)
            contaDestino.adicionaTransacaoHistorico(operacao_destino)
            
            messagebox.showinfo("Sucesso", 
                f"Transferência realizada com cheque especial!\n\n"
                f"Valor: R${valor:.2f}\n"
                f"Cheque especial utilizado: R${valor_cheque:.2f}\n"
                f"Limite restante: R${self.contaLogin.limiteChequeEspecial:.2f}")
            
            # Atualiza apenas a interface da conta ORIGEM (a logada)
            self.exibirTransacoesBancarias()

    def solicitarDataTransferencia(self, contaDestino, valor):
        top = tk.Toplevel(self.janelaPrincipal)
        top.title("Programar Transferência")
        top.geometry("300x200")
        
        tk.Label(top, text="Data (DD/MM/AAAA):").pack(pady=10)
        entry_data = tk.Entry(top)
        entry_data.pack(pady=5)
        
        def confirmar():
            dataStr = entry_data.get()
            try:
                data = datetime.strptime(dataStr, "%d/%m/%Y").date()
                if data < date.today():
                    messagebox.showerror("Erro", "Data deve ser futura!")
                else:
                    top.destroy()
                    self.executarTransferencia(contaDestino, valor, data.strftime("%d/%m/%Y"))
            except ValueError:
                messagebox.showerror("Erro", "Formato inválido! Use DD/MM/AAAA")
        
        tk.Button(top, text="Confirmar", command=confirmar).pack(pady=10)

#---------------------------------DEPÓSITO EXPRESS---------------------------------   
    def criarMenuDepositoExpress(self):
        self.ocultarFrame("menuPrincipal")

        self.menuDepositoExpress = tk.Frame(self.janelaPrincipal,bg='#E3F2F9',height=600, width=380)
        
        #Título da janela
        tk.Label(self.menuDepositoExpress, text="DEPÓSITO EXPRES", bg='#E3F2F9', pady=5,font=('Arial',12, 'bold'),fg='#223C5E').pack(pady=(0,10))
        tk.Label(self.menuDepositoExpress, text="Depósito rápido e sem burocracia", bg='#E3F2F9').pack()
        tk.Label(self.menuDepositoExpress, text="Faça sem login ou cadastro.", bg='#E3F2F9').pack(pady=(0,20))

        #---------------------------------ENTRADAS---------------------------------

        #Entrada para o número da conta
        tk.Label(self.menuDepositoExpress, text="Digite o número da conta: ", bg='#E3F2F9',pady=5, justify="left").pack(anchor="w",padx=15)
        self.recebeNumeroDaConta = tk.Entry(self.menuDepositoExpress, width=300)
        self.recebeNumeroDaConta.pack(ipady=10,padx=15,pady=(0,15))

        #Label deposito
        tk.Label(self.menuDepositoExpress, text="Valor do depósito: ", bg='#E3F2F9', pady=5, justify="left").pack(anchor="w",padx=15)
        
        #Entry depósito
        self.recebeValorDeposito = tk.Entry(self.menuDepositoExpress, width=300)
        self.recebeValorDeposito.pack(ipady=10, padx=15,pady=(0,15))

        #Label CPF
        tk.Label(self.menuDepositoExpress, text="Digite o seu CPF: ", bg='#E3F2F9',pady=5, justify="left").pack(anchor="w",padx=15)

        #Entry CPF
        self.recebeCPFDepositante = tk.Entry(self.menuDepositoExpress, width=300)
        self.recebeCPFDepositante.pack(ipady=10,padx=15)
        self.menuDepositoExpress.pack(padx=20, pady=20) #Se quiser oculta-lo, retiro essa linha
        tk.Button(self.menuDepositoExpress, text="EFETUAR DEPÓSITO", bg="#78D1DE", height=3, width=300, command=self.processarDepositoSemLogar).pack(padx=15, pady=(25,5))
        tk.Button(self.menuDepositoExpress, text="CANCELAR DEPÓSITO",bg='#D26060', height=3, width=300, command=self.criarMenuPrincipal).pack(padx=15, pady=15)
    
    def processarDepositoSemLogar(self):
        numero_conta = self.recebeNumeroDaConta.get().strip().upper()
        cpf = self.recebeCPFDepositante.get().strip()
        valor = self.recebeValorDeposito.get().strip().replace(",", ".")
        
        # Chama o método da classe Conta corretamente
        if Conta.depositarSemlogar(numero_conta, cpf, valor):
            self.criarMenuPrincipal()

#---------------------------------EXTRATO BANCÁRIO---------------------------------   
    def criarMenuExtrato(self):
        self.ocultarFrame("menuPrincipal")
        self.ocultarFrame("menuAberturaDeConta")
        self.ocultarFrame("menuAberturaDeContaCorrentePoupanca")
        self.ocultarFrame("menuCliente")
        self.ocultarFrame("trasacoesBancarias")
        self.ocultarFrame("menuSaque")
        self.ocultarFrame("menuTransferir")
        self.ocultarFrame("menuDepositoLogado")


        self.menuExtrato = tk.Frame(self.janelaPrincipal, bg='#E3F2F9')
        self.menuExtrato.pack(fill='both', expand=True)
        
        # Título
        tk.Label(self.menuExtrato, text="EXTRATO BANCÁRIO",font=('Arial',12, 'bold'),fg='#223C5E',bg='#E3F2F9').pack(pady=(10,5))
        
        # Frame principal do extrato (80% da altura)
        frameExtrato = tk.Frame(self.menuExtrato, bg='#E3F2F9')
        frameExtrato.pack(fill='both', expand=True, padx=20, pady=5)
        
        # Área de exibição com scrollbar
        scrollbar = tk.Scrollbar(frameExtrato)
        self.textoExtrato = tk.Text(frameExtrato, wrap=tk.WORD, yscrollcommand=scrollbar.set,bg='white', height=10, padx=10, pady=10)
        scrollbar.config(command=self.textoExtrato.yview)
        
        self.textoExtrato.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame inferior (20% da altura)
        frameInferior = tk.Frame(self.menuExtrato, bg='#E3F2F9')
        frameInferior.pack(fill='x', padx=20, pady=5)
        
        # Seção de filtro (organizada verticalmente)
        tk.Label(frameInferior, text="FILTRAR POR PERÍODO", bg='#E3F2F9',font=('Arial', 10, 'bold')).pack(anchor='w')
        
        frameDatas = tk.Frame(frameInferior, bg='#E3F2F9')
        frameDatas.pack(fill='x', pady=5)
        
        tk.Label(frameDatas, text="De:", bg='#E3F2F9').pack(side=tk.LEFT)
        self.entryDataInicial = tk.Entry(frameDatas, width=12)
        self.entryDataInicial.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frameDatas, text="Até:", bg='#E3F2F9').pack(side=tk.LEFT, padx=(10,0))
        self.entryDataFinal = tk.Entry(frameDatas, width=12)
        self.entryDataFinal.pack(side=tk.LEFT, padx=5)
        
        frameBotoes = tk.Frame(frameInferior, bg='#E3F2F9')
        frameBotoes.pack(pady=5)
        
        btnFiltrar = tk.Button(frameBotoes, text="APLICAR FILTRO",bg='#E3F2F9', command=self.aplicarFiltroExtrato, width=15)
        btnFiltrar.pack(side=tk.LEFT, padx=5)
        
        btnLimpar = tk.Button(frameBotoes, text="LIMPAR FILTRO",bg='#E3F2F9', command=self.limparFiltroExtrato, width=15)
        btnLimpar.pack(side=tk.LEFT, padx=5)
        
        # Botão Voltar (no rodapé)
        tk.Button(self.menuExtrato, text="VOLTAR",bg='#E3F2F9', command=self.exibirTransacoesBancarias, width=20).pack(pady=10)
        
        # Carrega extrato inicial
        self.atualizarExibicaoExtrato()

    def limparFiltroExtrato(self):
        self.entryDataInicial.delete(0, tk.END)
        self.entryDataFinal.delete(0, tk.END)
        self.atualizarExibicaoExtrato()

    def atualizarExibicaoExtrato(self, transacoes=None):
        if not hasattr(self, 'textoExtrato'):
            return
                
        try:
            self.textoExtrato.delete(1.0, tk.END)
            
            # Sempre pega o histórico atualizado da conta
            transacoes = self.contaLogin.historico if transacoes is None else transacoes
            
            if not transacoes:
                self.textoExtrato.insert(tk.END, "Nenhuma transação efetuada")
                return
            
            # Cabeçalho completo (mantido igual)
            cabecalho = f"{'BANCO DOS UNIVERSITÁRIOS':^50}\n\n"
            cabecalho += f"Agência: {self.contaLogin.numeroAgencia}\n"
            cabecalho += f"Conta: {self.contaLogin.numeroConta}\n"
            cabecalho += f"Titular: {self.contaLogin.titularConta}\n"
            cabecalho += f"Saldo Atual: R$ {self.contaLogin.saldoAtual:.2f}\n"
            
            if hasattr(self.contaLogin, 'limiteChequeEspecial'):
                cabecalho += f"Cheque Especial Disponível: R$ {self.contaLogin.limiteChequeEspecial:.2f}\n"
            
            cabecalho += "\nHistórico de Transações:\n"
            cabecalho += "="*50 + "\n"
            
            self.textoExtrato.insert(tk.END, cabecalho)
            
            # Função auxiliar para extração segura de datas
            def extrair_data(transacao):
                partes = transacao.split(" - ")
                # Verifica se é uma transação com CPF (formato diferente)
                if any("CPF" in parte for parte in partes):
                    # Padrão: "Tipo - Valor - Data - CPF: xxx"
                    data_str = partes[-2]  # Pega o penúltimo elemento (data)
                else:
                    # Padrão normal: "Tipo - Valor - Data"
                    data_str = partes[-1]  # Pega o último elemento
                
                try:
                    return datetime.strptime(data_str.strip(), "%d/%m/%Y")
                except ValueError:
                    # Se não encontrar data válida, retorna data mínima para aparecer primeiro
                    return datetime.min
            
            # Ordena as transações pela data extraída
            for transacao in sorted(transacoes, key=extrair_data, reverse=True):
                self.textoExtrato.insert(tk.END, f"• {transacao}\n")
                
            self.textoExtrato.see(tk.END)
            
        except Exception as e:
            print(f"Erro ao atualizar extrato: {str(e)}")
            # Mensagem amigável ao usuário
            self.textoExtrato.insert(tk.END, "\nErro ao carregar transações. Formato inválido detectado.")

    def aplicarFiltroExtrato(self):
        try:
            if not self.entryDataInicial.get() or not self.entryDataFinal.get():
                messagebox.showerror("Erro", "Preencha ambas as datas!")
                return

            # Converter para date (não datetime)
            dataInicial = datetime.strptime(self.entryDataInicial.get(), "%d/%m/%Y").date()
            dataFinal = datetime.strptime(self.entryDataFinal.get(), "%d/%m/%Y").date()

            def extrair_data(transacao):
                partes = transacao.split(" - ")
                if any("CPF" in parte for parte in partes):
                    data_str = partes[-2]  # penúltimo é a data
                else:
                    data_str = partes[-1]  # último é a data
                try:
                    # Retorna date em vez de datetime
                    return datetime.strptime(data_str.strip(), "%d/%m/%Y").date()
                except:
                    return None

            historicoFiltrado = []
            for t in self.contaLogin.historico:
                dataTransacao = extrair_data(t)
                if dataTransacao and dataInicial <= dataTransacao <= dataFinal:
                    historicoFiltrado.append(t)

            if isinstance(self.contaLogin, ContaCorrente):
                dataTaxa = date(dataInicial.year, dataInicial.month, 5)
                if dataInicial.day > 5:
                    dataTaxa = date(dataTaxa.year, dataTaxa.month + 1 if dataTaxa.month < 12 else 1, 5)

                while dataTaxa <= dataFinal:
                    historicoFiltrado.append(
                        f"Taxa de Manutenção Projetada - R$ {self.contaLogin.TAXA_MANUTENCAO:.2f} - {dataTaxa.strftime('%d/%m/%Y')}"
                    )
                    if dataTaxa.month == 12:
                        dataTaxa = date(dataTaxa.year + 1, 1, 5)
                    else:
                        dataTaxa = date(dataTaxa.year, dataTaxa.month + 1, 5)

                meses_projecao = (dataFinal.year - dataInicial.year) * 12 + (dataFinal.month - dataInicial.month)
                if dataFinal.day < dataInicial.day:
                    meses_projecao -= 1
                
                saldo_projetado = self.contaLogin.saldoAtual - (self.contaLogin.TAXA_MANUTENCAO * max(0, meses_projecao))
                historicoFiltrado.append(f"Saldo projetado após {meses_projecao} meses: R$ {saldo_projetado:.2f}")

            else:
                for t in historicoFiltrado[:]:
                    if "Depósito" in t or "Transferência recebida" in t:
                        partes = t.split(" - ")
                        try:
                            valor = float(partes[1].replace("R$", "").strip())
                            dataTrans = extrair_data(t)
                            if dataTrans:
                                meses = (dataFinal.year - dataTrans.year) * 12 + (dataFinal.month - dataTrans.month)
                                if dataFinal.day < dataTrans.day:
                                    meses -= 1
                                
                                for mes in range(1, max(1, meses) + 1):
                                    novo_mes = dataTrans.month + mes
                                    ano = dataTrans.year + (novo_mes - 1) // 12
                                    mes_final = (novo_mes - 1) % 12 + 1
                                    ultimo_dia = [31, 29 if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0) else 28, 
                                                31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes_final - 1]
                                    dia = min(dataTrans.day, ultimo_dia)
                                    dataRendimento = date(ano, mes_final, dia)
                                    
                                    rendimento = valor * self.contaLogin.TAXA_RENDIMENTO
                                    historicoFiltrado.append(
                                        f"Rendimento (origem: {dataTrans.strftime('%d/%m/%Y')}) - R$ {rendimento:.2f} - {dataRendimento.strftime('%d/%m/%Y')}"
                                    )
                        except:
                            continue

                total_rendimentos = sum(
                    float(t.split("R$")[1].split("-")[0].strip()) 
                    for t in historicoFiltrado 
                    if "Rendimento" in t
                )
                historicoFiltrado.append(f"Rendimento total no período: R$ {total_rendimentos:.2f}")

            historicoFiltrado.sort(key=lambda x: extrair_data(x) or date.min)
            self.atualizarExibicaoExtrato(historicoFiltrado)

        except ValueError as e:
            messagebox.showerror("Erro", f"Data inválida! Use DD/MM/AAAA\nErro: {str(e)}")


    #Padroniza todos os labels, exceto os que contêm imagens

    def padronizarLabels(self, container=None):
        container = container or self.janelaPrincipal  # Se não especificado, usa a janela principal
        
        for widget in container.winfo_children():
            if isinstance(widget, tk.Label):
                # Verifica se o label tem imagem antes de modificar
                if not widget.cget('image'):
                    widget.config(font=('Arial', 10),fg='#223C5E',bg='#E3F2F9')
            elif isinstance(widget, (tk.Frame, tk.Toplevel)):
                self.padronizarLabels(widget)  # Chama recursivamente para containers internos

    

janela = Janela()
janela.exibirJanela()


