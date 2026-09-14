# AcademicOS: Gestor Inteligente de Desempenho

O **AcademicOS** é uma aplicação desktop desenvolvida para otimizar o acompanhamento do desempenho acadêmico de universitários. O objetivo do projeto é automatizar o registro de disciplinas, o controle de faltas e calcular automaticamente projeções de aprovação com base nas regras de avaliação da UERJ (cálculo de Média Semestral, nota necessária para Prova Final e teto de 25% de ausências).

## Tecnologias

As seguintes ferramentas, linguagens e frameworks foram utilizados na construção do projeto:

*   **Python:** Linguagem base do sistema e do motor matemático.
*   **Flet:** Framework utilizado para a construção da Interface Gráfica de Usuário (GUI).
*   **Asyncio:** Biblioteca padrão do Python para gerenciamento de processos assíncronos.
*   **JSON:** Estruturação e persistência local do banco de dados das disciplinas.
*   **Git / GitHub:** Controle de versionamento estruturado em *feature branches* e *issues*.

## Pré-requisitos e Instalação

Para rodar o código na sua máquina, você precisará ter o [Python 3.x](https://www.python.org/downloads/) instalado.

**Passo a passo da instalação:**

1. Clone este repositório para a sua máquina local:
```bash
git clone https://github.com/gbschmitt/Academic-os

```

2. Acesse a pasta do projeto pelo terminal:

```bash
cd Academic-os

```

3. Instale a biblioteca gráfica necessária:

```bash
pip install flet

```

## Como usar

Para iniciar o aplicativo, execute o seguinte comando no terminal, dentro da pasta do projeto:

```bash
python main.py

```

**Fluxo prático de uso:**

* Clique em **Cadastrar Nova Disciplina** para inserir o nome, carga horária e pesos das avaliações (ex: P1=1, P2=2).
* Acesse **Lançar Notas e Faltas** no dia a dia para atualizar seus registros logo após as aulas ou provas.
* Utilize o **Painel de Desempenho** para visualizar um *card* inteligente que calcula sua Média Semestral na hora e alerta visualmente (verde, amarelo ou vermelho) sobre a sua situação, inclusive projetando a nota exata que você precisa tirar caso vá para a Prova Final.

## Licença

Este projeto está sob a licença MIT - veja o arquivo LICENSE.md para detalhes.

---

**Autor:** Gabriel Schmitt

*Engenharia Elétrica (Sistemas e Computação) - UERJ*














