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
        tela_desempenho.visible = False
        tela_cadastro.visible = True
        page.update()

    def ir_para_lancamento(e):
        atualizar_dropdown_disciplinas()
        tela_intro.visible = False
        tela_cadastro.visible = False
        tela_desempenho.visible = False
        tela_lancamento.visible = True
        page.update()

    def ir_para_desempenho(e):
        atualizar_dropdown_desempenho()
        dropdown_desemp.value = None
        texto_media.value = "--"
        texto_status.value = "Selecione uma disciplina"
        texto_apoio.value = "Aguardando seleção..."
        card_resultado.bgcolor = "#424242"
        
        texto_alerta_falta.value = "Status da Frequência"
        texto_alerta_falta.color = ft.Colors.WHITE70
        barra_falta.value = 0.0
        barra_falta.color = ft.Colors.GREEN_400
        texto_contagem_falta.value = "--/-- faltas"
        
        tela_intro.visible = False
        tela_cadastro.visible = False
        tela_lancamento.visible = False
        tela_desempenho.visible = True
        page.update()

    def ir_para_inicio(e):
        tela_cadastro.visible = False
        tela_lancamento.visible = False
        tela_desempenho.visible = False
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

    botao_desempenho = ft.ElevatedButton(
        "Ver Painel de Desempenho", on_click=ir_para_desempenho, width=300,
        color=ft.Colors.WHITE, bgcolor=dourado_uerj, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
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
            controls=[
                titulo_intro, 
                logo_intro, 
                ft.Container(height=10), 
                botao_iniciar, 
                botao_lancar, 
                botao_desempenho, 
                ft.Container(height=10), 
                rodape_descricao
            ],
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
    
    regra_prof_dropdown = ft.Dropdown(
        label="Regra do Professor (Avaliações)",
        width=350,
        border_color=azul_uerj,
        focused_border_color=dourado_uerj,
        options=[
            ft.dropdown.Option("Padrão UERJ (Apenas P1 e P2)"),
            ft.dropdown.Option("Com P3 (Substitui Menor Nota)")
        ],
        value="Com P3 (Substitui Menor Nota da P1 ou P2)" 
    )
    
    def salvar_disciplina(e):
        if not nome_input.value or not carga_horaria_input.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Preencha o nome e a carga horária!"), bgcolor=vermelho_uerj, open=True))
            page.update()
            return

        dados = {}
        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)

        dados[nome_input.value] = {
            "carga_horaria": int(carga_horaria_input.value), 
            "pesos": pesos_input.value, 
            "regra_prof": regra_prof_dropdown.value, 
            "notas": {}, 
            "faltas": 0
        }

        with open(arquivo_json, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        nome_input.value = ""
        carga_horaria_input.value = ""
        pesos_input.value = ""
        regra_prof_dropdown.value = "Com P3 (Substitui Menor Nota)"
        
        page.overlay.append(ft.SnackBar(content=ft.Text("Disciplina salva!"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    tela_cadastro = ft.Container(
        content=ft.Column(
            controls=[
                botao_voltar_cad, 
                ft.Text("Cadastrar Disciplina", size=24, weight="bold", color=azul_uerj), 
                nome_input, 
                carga_horaria_input, 
                regra_prof_dropdown,
                pesos_input,
                ft.ElevatedButton("Salvar", on_click=salvar_disciplina, width=350, bgcolor=azul_uerj, color=ft.Colors.WHITE)
            ],
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

    # 4. TELA DE DESEMPENHO (DASHBOARD)

    botao_voltar_desemp = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=azul_uerj)

    dropdown_desemp = ft.Dropdown(
        label="Selecione a Disciplina", 
        width=350, 
        border_color=azul_uerj, 
        focused_border_color=dourado_uerj
    )

    texto_status = ft.Text("Selecione uma disciplina", size=22, weight="bold", color=ft.Colors.WHITE)
    texto_media = ft.Text("--", size=45, weight="bold", color=ft.Colors.WHITE)
    texto_apoio = ft.Text("Aguardando seleção...", size=14, color=ft.Colors.WHITE70, text_align="center")

    texto_alerta_falta = ft.Text("Status da Frequência", size=14, weight="bold", color=ft.Colors.WHITE70)
    barra_falta = ft.ProgressBar(width=250, value=0.0, color=ft.Colors.GREEN_400, bgcolor=ft.Colors.WHITE24)
    texto_contagem_falta = ft.Text("--/-- faltas", size=12, color=ft.Colors.WHITE54)

    card_resultado = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("MÉDIA ATUAL", size=12, weight="bold", color=ft.Colors.WHITE70),
                texto_media,
                ft.Divider(color=ft.Colors.WHITE24),
                texto_status,
                texto_apoio,
                ft.Container(height=10),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            texto_alerta_falta,
                            barra_falta,
                            texto_contagem_falta
                        ],
                        horizontal_alignment="center", spacing=3
                    ),
                    bgcolor=ft.Colors.BLACK12,
                    padding=10,
                    border_radius=8
                )
            ],
            horizontal_alignment="center",
            alignment="center",
            spacing=5
        ),
        width=350,
        padding=30,
        border_radius=15,
        bgcolor="#424242", 
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLUE_GREY_100),
    )

    def analisar_desempenho(dados_materia):
        carga_horaria = dados_materia.get("carga_horaria", 60)
        faltas = dados_materia.get("faltas", 0)
        limite_faltas = carga_horaria * 0.25
        
        regra_prof = dados_materia.get("regra_prof", "Com P3 (Substitui Menor Nota da P1 ou P2)")
        
        # Lógica da Barra de Faltas
        percentual_falta = faltas / limite_faltas if limite_faltas > 0 else 0
        
        if faltas > limite_faltas:
            alerta, cor_barra = "Limite Excedido!", "#8B0000"
        elif percentual_falta >= 0.75:
            alerta, cor_barra = "Alerta Crítico: Risco de Reprovação", dourado_uerj
        elif percentual_falta >= 0.50:
            alerta, cor_barra = "Atenção: Frequência Caindo", ft.Colors.ORANGE_400
        else:
            alerta, cor_barra = "Frequência Segura", ft.Colors.GREEN_400
            
        info_faltas = {
            "percentual": percentual_falta if percentual_falta <= 1 else 1.0,
            "texto_alerta": alerta,
            "texto_contagem": f"{faltas}/{int(limite_faltas)} faltas",
            "cor_barra": cor_barra
        }
        
        if faltas > limite_faltas:
            return {"status": "Reprovado por Falta", "cor": "#8B0000", "texto_apoio": f"Você estourou o limite de {int(limite_faltas)} faltas.", "media_atual": 0.0, "faltas": info_faltas}

        notas = dados_materia.get("notas", {})
        pesos_str = dados_materia.get("pesos", "")
        
        if not notas:
            return {"status": "Sem avaliações", "cor": "#757575", "texto_apoio": "Nenhuma nota lançada ainda.", "media_atual": 0.0, "faltas": info_faltas}

        pesos_dit = {}
        if pesos_str:
            try:
                for p in pesos_str.split(","):
                    chave, valor = p.split("=")
                    pesos_dit[chave.strip()] = float(valor.strip())
            except ValueError:
                pass 

        # REGRA MATEMÁTICA EXATA DO CÓDIGO ANTERIOR
    
        notas_validas = dict(notas)
        
        if regra_prof == "Com P3 (Substitui Menor Nota da P1 ou P2)" or len(notas_validas) > 2:
            while len(notas_validas) > 2:
                menor_chave = min(notas_validas, key=notas_validas.get)
                notas_validas.pop(menor_chave)

        # Cálculo da Média
        soma_notas = sum(nota * pesos_dit.get(av, 1.0) for av, nota in notas_validas.items())
        soma_pesos = sum(pesos_dit.get(av, 1.0) for av in notas_validas.keys())
        
        media_semestral = (soma_notas / soma_pesos) if soma_pesos > 0 else 0.0
        media_semestral = round(media_semestral, 2)

        if media_semestral >= 7.0:
            return {"status": "Aprovado Direto!", "cor": "#2E7D32", "texto_apoio": "Parabéns, não precisa de prova final.", "media_atual": media_semestral, "faltas": info_faltas}
        elif media_semestral < 4.0:
             return {"status": "Reprovado por Nota", "cor": "#D32F2F", "texto_apoio": "Média insuficiente para a Prova Final.", "media_atual": media_semestral, "faltas": info_faltas}
        else:
            nota_pf = round(10.0 - media_semestral, 2)
            return {"status": "Prova Final", "cor": dourado_uerj, "texto_apoio": f"Você precisa tirar {nota_pf} na PF para passar.", "media_atual": media_semestral, "faltas": info_faltas}

    def atualizar_painel(e):
        materia_selecionada = dropdown_desemp.value
        
        if not materia_selecionada:
            page.overlay.append(ft.SnackBar(content=ft.Text("Por favor, selecione uma disciplina na lista acima."), bgcolor=vermelho_uerj, open=True))
            page.update()
            return
            
        if not os.path.exists(arquivo_json):
            return
            
        try:
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
                
            materia_dados = dados.get(materia_selecionada, {})
            resultado = analisar_desempenho(materia_dados)
            
            # Atualiza Card de Notas
            texto_media.value = str(resultado["media_atual"])
            texto_status.value = resultado["status"]
            texto_apoio.value = resultado["texto_apoio"]
            card_resultado.bgcolor = resultado["cor"]
            
            # Atualiza Card de Faltas
            texto_alerta_falta.value = resultado["faltas"]["texto_alerta"]
            texto_alerta_falta.color = resultado["faltas"]["cor_barra"]
            barra_falta.value = resultado["faltas"]["percentual"]
            barra_falta.color = resultado["faltas"]["cor_barra"]
            texto_contagem_falta.value = resultado["faltas"]["texto_contagem"]
            
            texto_media.update()
            texto_status.update()
            texto_apoio.update()
            texto_alerta_falta.update()
            barra_falta.update()
            texto_contagem_falta.update()
            card_resultado.update()
            page.update()
            
        except Exception as erro:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Erro interno: {erro}"), bgcolor=vermelho_uerj, open=True))
            page.update()

    botao_analisar = ft.ElevatedButton(
        "Gerar Análise", 
        on_click=atualizar_painel, 
        width=350,
        bgcolor=azul_uerj, 
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
    )

    def atualizar_dropdown_desempenho():
        dropdown_desemp.options.clear()
        if os.path.exists(arquivo_json):
            with open(arquivo_json, "r", encoding="utf-8") as f:
                dados = json.load(f)
                for materia in dados.keys():
                    dropdown_desemp.options.append(ft.dropdown.Option(materia))

    tela_desempenho = ft.Container(
        content=ft.Column(
            controls=[
                botao_voltar_desemp, 
                ft.Text("Painel Analítico", size=24, weight="bold", color=azul_uerj), 
                dropdown_desemp, 
                botao_analisar, 
                card_resultado
            ],
            horizontal_alignment="center", spacing=20
        ),
        bgcolor=ft.Colors.WHITE, padding=40, border_radius=20, visible=False
    )

    # MONTAGEM FINAL DA PÁGINA

    page.add(tela_splash, tela_intro, tela_cadastro, tela_lancamento, tela_desempenho)
    
    await asyncio.sleep(2.5) 
    
    tela_splash.visible = False
    tela_intro.visible = True
    page.update()

ft.app(target=main, assets_dir="assets")