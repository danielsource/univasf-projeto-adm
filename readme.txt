""ERP"" para um sistema PDV fictício, desenvolvido para a disciplina de
Administração do curso de Ciência da Computação na Univasf.

Usuários padrões de exemplo:
  Role: ADMIN
  Username: adm
  Password: 1234

  Role: MANAGER
  Username: man
  Password: 1234

  Role: OPERATOR
  Username: op
  Password: 1234

#
# Instruções básicas para execução
#

0. Requisitos: Python 3.11 e pip (vem normalmente instalado com o Python).

1. Criar ambiente "virtual" python
  % # Esse ambiente não tem a ver com máquinas virtuais, é só um
  % # contêiner lógico onde pacotes específicos de um projeto são
  % # armazenados. Entre na raiz do projeto em uma shell e execute os comandos:

  % # Crie o ambiente virtual (só é preciso fazer uma vez!)
  % python -m venv .venv

  $ # LINUX bash: ative o ambiente virtual (toda vez ao entrar no projeto)
  $ . .venv/bin/activate

  > # WINDOWS PowerShell.exe: ative o ambiente virtual (toda vez ao entrar no projeto)
  > .venv\Scripts\Activate.ps1

  > # WINDOWS cmd.exe: ative o ambiente virtual (toda vez ao entrar no projeto)
  > .venv\Scripts\Activate.bat

2. Instalar as dependências:
  $ pip install -r requirements.txt

3. Executar o servidor de desenvolvimento:
  % flask run --debug
  % # Note que toda vez que for necessário executar o servidor ou fazer
  % # qualquer coisa relacionada com o projeto é preciso ativar o ambiente
  % # virtual Python.

#
# Observações
#

  - O banco de dados utilizado é o SQLite 3 e fica situado em
    ./instance/store.sqlite. Quando alguma atualização no código quebra
    a compatibilidade com o banco de dados, remova o banco (hahaha).

  - Valores monetários são guardados como inteiros em centavos.
    Ex: R$ 12,50 --> 1250
