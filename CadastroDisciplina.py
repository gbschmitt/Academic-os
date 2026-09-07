import flet as ft
import json
import os

def main(page: ft.Page):

    page.title = "AcademicOS"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 0 
    

    azul_uerj = "#0055A4"
    vermelho_uerj = "#E52321"
    dourado_uerj = "#C19A3F"

    page.theme_mode = "light" 
    page.bgcolor = "#E3F2FD" 


    # FUNÇÕES DE NAVEGAÇÃO (TROCA DE VISIBILIDADE)

    def ir_para_cadastro(e):
        tela_intro.visible = False
        tela_cadastro.visible = True
        page.update()

    def ir_para_inicio(e):
        tela_cadastro.visible = False
        tela_intro.visible = True
        page.update()

    # 1. TELA INICIAL (INTRODUÇÃO)

    titulo_intro = ft.Text("AcademicOS", size=36, weight="bold", color=azul_uerj)
    logo_intro = ft.Image(src="image_ef4634.png", width=140, height=140, fit="contain")
    
    descricao = ft.Text(
        "Seu sistema inteligente para gestão de desempenho acadêmico.\n"
        "Acompanhe suas notas, calcule médias e controle suas faltas de forma simples e eficiente.",
        text_align="center",
        size=16,
        color="#333333",
        width=700
    )

    botao_iniciar = ft.ElevatedButton(
        "Acessar", 
        on_click=ir_para_cadastro, 
        width=400,
        color=ft.Colors.WHITE,
        bgcolor=azul_uerj,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    tela_intro = ft.Container(
        content=ft.Column(
            controls=[titulo_intro, logo_intro, descricao, ft.Container(height=10), botao_iniciar],
            horizontal_alignment="center",
            alignment="center",
            spacing=15
        ),
        bgcolor=ft.Colors.WHITE,
        padding=50,
        border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLUE_GREY_100),
        visible=True # Esta tela começa visível
    )


    # 2. TELA DE CADASTRO (CÓDIGO ESTÁVEL)

    botao_voltar = ft.TextButton("< Voltar para o Início", on_click=ir_para_inicio, icon_color=azul_uerj)
    logo_cadastro = ft.Image(src="image_ef4634.png", width=110, height=110, fit="contain")
    titulo_cadastro = ft.Text("Cadastrar Nova Disciplina", size=24, weight="bold", color=azul_uerj)
    subtitulo_cadastro = ft.Text("Faculdade de Engenharia - UERJ", size=16, italic=True, color=dourado_uerj)
    
    nome_input = ft.TextField(label="Nome da Disciplina", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)
    carga_horaria_input = ft.TextField(label="Carga Horária (ex: 60)", keyboard_type="number", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)
    pesos_input = ft.TextField(label="Pesos (ex: P1=1, P2=2)", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)

    def salvar_disciplina(e):
        if not nome_input.value or not carga_horaria_input.value:
            snack = ft.SnackBar(content=ft.Text("Preencha o nome e a carga horária!"), bgcolor=vermelho_uerj)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return

        arquivo_json = "dados_academicos.json"
        dados = {}

        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)

        dados[nome_input.value] = {
            "carga_horaria": int(carga_horaria_input.value),
            "pesos": pesos_input.value,
            "notas": {},
            "faltas": 0
        }

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        nome_input.value = ""
        carga_horaria_input.value = ""
        pesos_input.value = ""
        
        snack = ft.SnackBar(content=ft.Text("Disciplina salva com sucesso!"), bgcolor=ft.Colors.GREEN_700)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    botao_salvar = ft.ElevatedButton(
        "Salvar Disciplina", 
        on_click=salvar_disciplina, 
        width=350,
        color=ft.Colors.WHITE,
        bgcolor=azul_uerj,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    tela_cadastro = ft.Container(
        content=ft.Column(
            controls=[botao_voltar, logo_cadastro, titulo_cadastro, subtitulo_cadastro, nome_input, carga_horaria_input, pesos_input, botao_salvar],
            horizontal_alignment="center",
            spacing=10
        ),
        bgcolor=ft.Colors.WHITE,
        padding=40,
        border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLUE_GREY_100),
        visible=False # Esta tela começa invisível
    )

    # Adiciona as duas telas na página. Apenas a tela_intro aparecerá.
    page.add(tela_intro, tela_cadastro)

# Autorizando a pasta "assets"
ft.app(target=main, assets_dir="assets")