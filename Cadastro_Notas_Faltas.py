import flet as ft
import json
import os
import asyncio 

async def main(page: ft.Page): 
    
    
    # CONFIGURAÇÕES GERAIS E CORES DA UERJ
    
    page.title = "AcademicOS"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 0 
    
    azul_uerj = "#0055A4"
    vermelho_uerj = "#E52321"
    dourado_uerj = "#C19A3F"

    page.theme_mode = "light" 
    page.bgcolor = "#E3F2FD" 
    arquivo_json = "dados_academicos.json"

    
    # FUNÇÕES DE NAVEGAÇÃO SPA
    
    def ir_para_cadastro(e):
        tela_intro.visible = False
        tela_lancamento.visible = False
        tela_cadastro.visible = True
        page.update()

    def ir_para_lancamento(e):
        atualizar_dropdown_disciplinas()
        tela_intro.visible = False
        tela_cadastro.visible = False
        tela_lancamento.visible = True
        page.update()

    def ir_para_inicio(e):
        tela_cadastro.visible = False
        tela_lancamento.visible = False
        tela_intro.visible = True
        page.update()

    
    # 0. TELA DE SPLASH (ABERTURA COM STACK)
    
    tela_splash = ft.Stack(
        controls=[
            
            ft.Image(
                src="image_f56f29.jpg",
                fit="cover",
                width=4000, 
                height=4000,
            ),
            
            
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Image(src="image_ef4636.png", width=180, height=180, fit="contain"),
                        ft.Container(height=10),
                        ft.Text("AcademicOS", size=42, weight="bold", color=ft.Colors.WHITE),
                        ft.Text(
                            "Seu sistema inteligente para gestão\nde desempenho acadêmico.", 
                            text_align="center", 
                            color="#F2D794", 
                            size=15, 
                            italic=True
                        ),
                        ft.Container(height=60),
                        ft.ProgressRing(color="#F2D794", stroke_width=2, width=30, height=30)
                    ],
                    horizontal_alignment="center",
                    alignment="center", 
                    spacing=0 
                ),
                expand=True 
            )
        ],
        expand=True,
        visible=True 
    )

    
    # 1. TELA INICIAL 
    
    titulo_intro = ft.Text("AcademicOS", size=36, weight="bold", color=azul_uerj)
    logo_intro = ft.Image(src="image_ef4634.png", width=140, height=140, fit="contain")
        
    botao_iniciar = ft.ElevatedButton(
        "Cadastrar Nova Disciplina", on_click=ir_para_cadastro, width=300,
        color=ft.Colors.WHITE, bgcolor=azul_uerj, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )
    
    botao_lancar = ft.ElevatedButton(
        "Lançar Notas e Faltas", on_click=ir_para_lancamento, width=300,
        color=azul_uerj, bgcolor=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    descricao_texto = ft.Text(
        "Acompanhe suas notas, calcule médias e controle as suas faltas de forma inteligente.",
        size=13,
        color="#424242",
        text_align="left",
    )

    rodape_descricao = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text("💡", size=28), 
                ft.Container(content=descricao_texto, width=230) 
            ],
            alignment="center",
            spacing=10
        ),
        bgcolor="#F4F8FC", 
        padding=15,
        border_radius=12,  
        width=320, 
    )

    tela_intro = ft.Container(
        content=ft.Column(
            controls=[titulo_intro, logo_intro, ft.Container(height=10), botao_iniciar, botao_lancar, ft.Container(height=10), rodape_descricao],
            horizontal_alignment="center", alignment="center", spacing=15
        ),
        bgcolor=ft.Colors.WHITE, padding=50, border_radius=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLUE_GREY_100),
        visible=False 
    )

    
    # 2. TELA DE CADASTRO 
    
    botao_voltar_cad = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=azul_uerj)
    nome_input = ft.TextField(label="Nome da Disciplina", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)
    carga_horaria_input = ft.TextField(label="Carga Horária (ex: 60)", keyboard_type="number", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)
    pesos_input = ft.TextField(label="Pesos (ex: P1=1, P2=2)", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)

    def salvar_disciplina(e):
        if not nome_input.value or not carga_horaria_input.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Preencha o nome e a carga horária!"), bgcolor=vermelho_uerj, open=True))
            page.update()
            return

        dados = {}
        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)

        dados[nome_input.value] = {"carga_horaria": int(carga_horaria_input.value), "pesos": pesos_input.value, "notas": {}, "faltas": 0}

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        nome_input.value = ""; carga_horaria_input.value = ""; pesos_input.value = ""
        page.overlay.append(ft.SnackBar(content=ft.Text("Disciplina salva!"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    tela_cadastro = ft.Container(
        content=ft.Column(
            controls=[botao_voltar_cad, ft.Text("Cadastrar Disciplina", size=24, weight="bold", color=azul_uerj), nome_input, carga_horaria_input, pesos_input, ft.ElevatedButton("Salvar", on_click=salvar_disciplina, width=350, bgcolor=azul_uerj, color=ft.Colors.WHITE)],
            horizontal_alignment="center", spacing=10
        ),
        bgcolor=ft.Colors.WHITE, padding=40, border_radius=20, visible=False
    )

    
    # 3. TELA DE LANÇAMENTOS 
    
    botao_voltar_lanc = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=azul_uerj)
    disciplina_dropdown = ft.Dropdown(label="Selecione a Disciplina", width=350, border_color=azul_uerj, focused_border_color=dourado_uerj)
    
    linha_notas = ft.Row(
        controls=[
            ft.TextField(label="Avaliação (ex: P1)", width=170, border_color=azul_uerj),
            ft.TextField(label="Nota (ex: 8.5)", width=170, keyboard_type="number", border_color=azul_uerj)
        ],
        alignment=ft.MainAxisAlignment.CENTER, spacing=10
    )
    
    faltas_input = ft.TextField(value="0", text_align="center", width=80, keyboard_type="number", border_color=azul_uerj)

    def somar_falta(e):
        try:
            atual = int(faltas_input.value) if faltas_input.value else 0
            faltas_input.value = str(atual + 1)
            page.update()
        except ValueError:
            faltas_input.value = "1"
            page.update()

    def subtrair_falta(e):
        try:
            atual = int(faltas_input.value) if faltas_input.value else 0
            faltas_input.value = str(atual - 1) 
            page.update()
        except ValueError:
            faltas_input.value = "0"
            page.update()

    linha_faltas = ft.Row(
        controls=[
            ft.Text("Faltas a lançar:", size=16, color=azul_uerj),
            ft.ElevatedButton(
                content=ft.Text("-", size=24, weight="bold"),
                on_click=subtrair_falta,
                bgcolor=vermelho_uerj,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10)
            ),
            faltas_input,
            ft.ElevatedButton(
                content=ft.Text("+", size=24, weight="bold"),
                on_click=somar_falta,
                bgcolor=azul_uerj,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10)
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    def atualizar_dropdown_disciplinas():
        disciplina_dropdown.options.clear()
        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for materia in dados.keys():
                    disciplina_dropdown.options.append(ft.dropdown.Option(materia))

    def salvar_lancamentos(e):
        if not disciplina_dropdown.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Selecione uma disciplina primeiro!"), bgcolor=vermelho_uerj, open=True))
            page.update()
            return

        with open(arquivo_json, "r", encoding="utf-8") as f:
            dados = json.load(f)

        materia = disciplina_dropdown.value
        avaliacao = linha_notas.controls[0].value
        nota = linha_notas.controls[1].value

        if avaliacao and nota:
            try:
                dados[materia]["notas"][avaliacao] = float(nota.replace(",", "."))
            except ValueError:
                page.overlay.append(ft.SnackBar(content=ft.Text("Formato de nota inválido!"), bgcolor=vermelho_uerj, open=True))
                page.update()
                return

        if faltas_input.value and faltas_input.value != "0":
            try:
                dados[materia]["faltas"] += int(faltas_input.value)
                if dados[materia]["faltas"] < 0:
                    dados[materia]["faltas"] = 0 
            except ValueError:
                pass 

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        linha_notas.controls[0].value = ""
        linha_notas.controls[1].value = ""
        faltas_input.value = "0"
        
        page.overlay.append(ft.SnackBar(content=ft.Text(f"Lançamentos salvos em {materia}!"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    botao_salvar_lancamentos = ft.ElevatedButton(
        "Registrar no Sistema", on_click=salvar_lancamentos, width=350,
        color=ft.Colors.WHITE, bgcolor=azul_uerj, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    tela_lancamento = ft.Container(
        content=ft.Column(
            controls=[botao_voltar_lanc, ft.Text("Lançar Desempenho", size=24, weight="bold", color=azul_uerj), disciplina_dropdown, linha_notas, linha_faltas, botao_salvar_lancamentos],
            horizontal_alignment="center", spacing=15
        ),
        bgcolor=ft.Colors.WHITE, padding=40, border_radius=20, visible=False
    )

    
    # MONTAGEM FINAL DA PÁGINA
    
    
    
    page.add(tela_splash, tela_intro, tela_cadastro, tela_lancamento)
    
    
    await asyncio.sleep(2.5) 
    
    
    tela_splash.visible = False
    tela_intro.visible = True
    page.update()

ft.app(target=main, assets_dir="assets")