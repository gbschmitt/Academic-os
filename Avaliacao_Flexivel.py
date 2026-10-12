import flet as ft
import json
import os
import asyncio 
from datetime import datetime 
import webbrowser
import urllib.parse

# 1. VARIÁVEIS GLOBAIS DE ESTADO E CORES

AZUL_UERJ = "#0055A4"
VERMELHO_UERJ = "#E52321"
DOURADO_UERJ = "#C19A3F"

ARQUIVO_PADRAO = "dados_academicos.json"
ESTADO_GLOBAL = {"arquivo": ARQUIVO_PADRAO}

# 2. GESTOR DE DADOS (ARQUIVOS JSON)

def get_arquivo_ativo():
    return ESTADO_GLOBAL["arquivo"]

def set_arquivo_ativo(nome_arquivo):
    ESTADO_GLOBAL["arquivo"] = nome_arquivo

def garantir_arquivo_existe(nome_arquivo=ARQUIVO_PADRAO):
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump({}, f)

def ler_dados(nome_arquivo=None):
    if not nome_arquivo:
        nome_arquivo = get_arquivo_ativo()
    garantir_arquivo_existe(nome_arquivo)
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados, nome_arquivo=None):
    if not nome_arquivo:
        nome_arquivo = get_arquivo_ativo()
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def listar_arquivos_historico():
    garantir_arquivo_existe(ARQUIVO_PADRAO)
    return [f for f in os.listdir() if f.startswith("dados_academicos_arquivado_") and f.endswith(".json")]

def arquivar_semestre_atual(nome_personalizado):
    nome_seguro = "".join([c for c in nome_personalizado if c.isalnum() or c in " .-_"])
    if not nome_seguro:
        nome_seguro = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    novo_nome = f"dados_academicos_arquivado_{nome_seguro}.json"
    
    if os.path.exists(novo_nome):
        return False, "Já existe um histórico com este nome!"
        
    if os.path.exists(ARQUIVO_PADRAO):
        os.rename(ARQUIVO_PADRAO, novo_nome)
    
    garantir_arquivo_existe(ARQUIVO_PADRAO)
    return True, nome_seguro

# 3. MOTOR MATEMÁTICO E REGRAS DE NEGÓCIO

def analisar_desempenho(dados_materia):
    carga_horaria = dados_materia.get("carga_horaria", 60)
    faltas = dados_materia.get("faltas", 0)
    limite_faltas = carga_horaria * 0.25
    
    regra_prof = dados_materia.get("regra_prof", "Padrão UERJ (Apenas P1 e P2)")
    
    percentual_falta = faltas / limite_faltas if limite_faltas > 0 else 0
    
    if faltas > limite_faltas: alerta, cor_barra = "Limite Excedido!", "#8B0000"
    elif percentual_falta >= 0.75: alerta, cor_barra = "Alerta Crítico: Risco de Reprovação", DOURADO_UERJ
    elif percentual_falta >= 0.50: alerta, cor_barra = "Atenção: Frequência Caindo", ft.Colors.ORANGE_400
    else: alerta, cor_barra = "Frequência Segura", ft.Colors.GREEN_400
        
    info_faltas = {"percentual": percentual_falta if percentual_falta <= 1 else 1.0, "texto_alerta": alerta, "texto_contagem": f"{faltas}/{int(limite_faltas)} faltas", "cor_barra": cor_barra}
    
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
                pesos_dit[chave.strip().upper()] = float(valor.strip())
        except ValueError: pass 

    notas_validas = {k.strip().upper(): v for k, v in notas.items()}

    if regra_prof == "Avaliação Flexível (Trabalhos e Testes)":
        if not pesos_dit:
            soma_pesos = len(notas_validas) if notas_validas else 1
            soma_notas = sum(notas_validas.values())
        else:
            soma_pesos = sum(pesos_dit.values())
            soma_notas = sum(notas_validas.get(av, 0.0) * peso for av, peso in pesos_dit.items())
        
        media_semestral = (soma_notas / soma_pesos) if soma_pesos > 0 else 0.0

    else:
        peso_p1 = pesos_dit.get("P1", 1.0)
        peso_p2 = pesos_dit.get("P2", 1.0)
        
        n1 = notas_validas.get("P1", 0.0)
        n2 = notas_validas.get("P2", 0.0)
        
        if regra_prof == "P1, P2 e P3 (Substitui a Menor Nota)" and "P3" in notas_validas:
            n3 = notas_validas["P3"]
            if n1 <= n2 and n3 > n1:
                n1 = n3
            elif n2 < n1 and n3 > n2:
                n2 = n3

        soma_pesos = peso_p1 + peso_p2
        soma_notas = (n1 * peso_p1) + (n2 * peso_p2)
        media_semestral = (soma_notas / soma_pesos) if soma_pesos > 0 else 0.0

    media_semestral = round(media_semestral, 2)

    if media_semestral >= 7.0: return {"status": "Aprovado Direto!", "cor": "#2E7D32", "texto_apoio": "Parabéns, não precisa de prova final.", "media_atual": media_semestral, "faltas": info_faltas}
    elif media_semestral < 4.0: return {"status": "Reprovado por Nota", "cor": "#D32F2F", "texto_apoio": "Média insuficiente para a Prova Final.", "media_atual": media_semestral, "faltas": info_faltas}
    else:
        nota_pf = round(10.0 - media_semestral, 2)
        return {"status": "Prova Final", "cor": DOURADO_UERJ, "texto_apoio": f"Você precisa tirar {nota_pf} na PF para passar.", "media_atual": media_semestral, "faltas": info_faltas}

# 4. EXPORTAÇÃO E UTILITÁRIOS DE E-MAIL

def preparar_conteudo_backup():
    arquivo_ativo = get_arquivo_ativo()
    dados = ler_dados(arquivo_ativo)
    
    nome_ciclo = "Semestre Atual" if arquivo_ativo == ARQUIVO_PADRAO else arquivo_ativo.replace("dados_academicos_arquivado_", "").replace(".json", "")
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    linhas_resumo = []
    for nome_mat, info in dados.items():
        analise = analisar_desempenho(info)
        notas_dict = info.get("notas", {})
        notas_str = " | ".join([f"{av.upper()}: { valor }" for av, valor in notas_dict.items()]) if notas_dict else "Nenhuma avaliação lançada"
            
        pesos_exib = info.get("pesos", "") if info.get("pesos", "") else "Padrão (Pesos Iguais)"
        regra_exib = info.get("regra_prof", "Padrão UERJ")

        status_txt = analise["status"]
        if "Aprovado" in status_txt: icone_status = "🟢"
        elif "Prova Final" in status_txt: icone_status = "🟡"
        elif "Reprovado" in status_txt: icone_status = "🔴"
        else: icone_status = "⚪"

        bloco_materia = (
            f"📘 {nome_mat.upper()}\n"
            f"   • Situação: {icone_status} {status_txt} ({analise['texto_apoio']})\n"
            f"   • Média Acumulada: {analise['media_atual']}  |  Notas: {notas_str}\n"
            f"   • Frequência: {analise['faltas']['texto_contagem']} ({analise['faltas']['texto_alerta']})  |  Carga Horária: {info.get('carga_horaria', 60)}h\n"
            f"   • Critério: {regra_exib}  |  Pesos: {pesos_exib}\n"
            f"--------------------------------------------------"
        )
        linhas_resumo.append(bloco_materia)

    resumo_visual = "\n".join(linhas_resumo)
    json_formatado = json.dumps(dados, indent=4, ensure_ascii=False)
    
    assunto = f"🎓 Boletim e Backup AcademicOS - {nome_ciclo}"
    corpo = (
        f"🎓 ACADEMICOS - BOLETIM E BACKUP ACADÊMICO\n"
        f"==================================================\n"
        f"📅 Ciclo / Semestre: {nome_ciclo}\n"
        f"🕒 Gerado em: {data_geracao}\n"
        f"📚 Total de Disciplinas: {len(dados)}\n"
        f"==================================================\n\n"
        f"📊 RESUMO EXECUTIVO DO SEU DESEMPENHO:\n\n"
        f"{resumo_visual}\n\n"
        f"💾 DADOS TÉCNICOS PARA RESTAURAÇÃO (ARQUIVO .JSON)\n"
        f"Caso precise restaurar seus dados no aplicativo futuramente, copie o código abaixo e salve em um arquivo chamado '{arquivo_ativo}':\n\n"
        f"{json_formatado}\n"
        f"==================================================\n"
        f"Gerado automaticamente por AcademicOS • UERJ"
    )
    return dados, assunto, corpo, nome_ciclo

def abrir_cliente_email(email_dest, assunto, corpo, modo_webmail):
    assunto_url = urllib.parse.quote(assunto)
    corpo_url = urllib.parse.quote(corpo)

    if modo_webmail:
        dominio = email_dest.split("@")[-1].lower()
        if any(provedor in dominio for provedor in ["outlook", "hotmail", "live", "msn"]):
            url = f"https://outlook.live.com/owa/?path=/mail/action/compose&to={email_dest}&subject={assunto_url}&body={corpo_url}"
        else:
            url = f"https://mail.google.com/mail/?view=cm&fs=1&to={email_dest}&su={assunto_url}&body={corpo_url}"
        webbrowser.open(url)
    else:
        mailto_link = f"mailto:{email_dest}?subject={assunto_url}&body={corpo_url}"
        webbrowser.open(mailto_link)

# 5. INTERFACE GRÁFICA (FUNÇÃO MAIN)

async def main(page: ft.Page): 
    
    page.title = "AcademicOS"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.padding = 0 
    page.theme_mode = "light" 
    page.bgcolor = "#E3F2FD" 

    # NAVEGAÇÃO SPA
    def ir_para_cadastro(e):
        tela_intro.visible = False
        tela_lancamento.visible = False
        tela_desempenho.visible = False
        tela_cadastro.visible = True
        page.update()

    def ir_para_lancamento(e):
        atualizar_dropdown_disciplinas()
        disciplina_dropdown.value = None
        pesos_input.value = ""
        painel_historico.controls.clear()
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

    def ir_para_inicio(e=None):
        atualizar_dropdown_semestres()
        tela_cadastro.visible = False
        tela_lancamento.visible = False
        tela_desempenho.visible = False
        tela_intro.visible = True
        page.update()

    # TELA 0: SPLASH
    tela_splash = ft.Stack(
        controls=[
            ft.Image(src="image_f56f29.jpg", fit="cover", width=4000, height=4000),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Image(src="image_ef4636.png", width=180, height=180, fit="contain"),
                        ft.Container(height=10),
                        ft.Text("AcademicOS", size=42, weight="bold", color=ft.Colors.WHITE),
                        ft.Text("Seu sistema inteligente para gestão\nde desempenho acadêmico.", text_align="center", color="#F2D794", size=15, italic=True),
                        ft.Container(height=60),
                        ft.ProgressRing(color="#F2D794", stroke_width=2, width=30, height=30)
                    ],
                    horizontal_alignment="center", alignment="center", spacing=0 
                ),
                expand=True 
            )
        ],
        expand=True, visible=True 
    )

    # TELA 1: INÍCIO E SELETOR DE SEMESTRE
    seletor_semestre = ft.Dropdown(
        label="Histórico de Semestres (Base de Dados)", width=300, border_color=DOURADO_UERJ, focused_border_color=AZUL_UERJ
    )

    def notificar_mudanca_semestre(e):
        set_arquivo_ativo(seletor_semestre.value if seletor_semestre.value else ARQUIVO_PADRAO)
        nome_exibicao = get_arquivo_ativo().replace("dados_academicos_arquivado_", "").replace(".json", "")
        if get_arquivo_ativo() == ARQUIVO_PADRAO: nome_exibicao = "Semestre Atual"
        page.overlay.append(ft.SnackBar(content=ft.Text(f"A ler a base de dados: {nome_exibicao}"), bgcolor=DOURADO_UERJ, open=True))
        page.update()
        
    seletor_semestre.on_change = notificar_mudanca_semestre

    def atualizar_dropdown_semestres(forcar_atual=False):
        valor_anterior = get_arquivo_ativo()
        seletor_semestre.options.clear()
        
        arquivos = listar_arquivos_historico()
        seletor_semestre.options.append(ft.dropdown.Option(key=ARQUIVO_PADRAO, text="Semestre Atual (Ativo)"))
        
        for arq in sorted(arquivos, reverse=True):
            nome_exibicao = arq.replace("dados_academicos_arquivado_", "").replace(".json", "")
            seletor_semestre.options.append(ft.dropdown.Option(key=arq, text=f"Histórico: {nome_exibicao}"))
            
        if forcar_atual or not valor_anterior:
            seletor_semestre.value = ARQUIVO_PADRAO
            set_arquivo_ativo(ARQUIVO_PADRAO)
        else:
            chaves = [opt.key for opt in seletor_semestre.options]
            if valor_anterior in chaves:
                seletor_semestre.value = valor_anterior
            else:
                seletor_semestre.value = ARQUIVO_PADRAO
                set_arquivo_ativo(ARQUIVO_PADRAO)
        try:
            seletor_semestre.update()
        except Exception:
            pass

    # COMPONENTES MODAL DE ARQUIVAMENTO
    input_nome_semestre = ft.TextField(label="Nome do Semestre", hint_text="Como quer chamar este histórico?", width=300, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)

    def arquivar_semestre_callback(e):
        sucesso, mensagem = arquivar_semestre_atual(input_nome_semestre.value.strip())
        if sucesso:
            input_nome_semestre.value = "" 
            atualizar_dropdown_semestres(forcar_atual=True)
            dlg_modal.open = False 
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Semestre '{mensagem}' arquivado com sucesso!"), bgcolor=ft.Colors.GREEN_700, open=True))
        else:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Erro: {mensagem}"), bgcolor=VERMELHO_UERJ, open=True))
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Encerrar Semestre Atual", weight="bold", color=AZUL_UERJ),
        content=ft.Column(controls=[ft.Text("Tem a certeza? As disciplinas atuais ficarão guardadas no histórico.", size=14), ft.Container(height=10), input_nome_semestre], tight=True),
        actions=[ft.TextButton("Cancelar", on_click=lambda e: fechar_modal(dlg_modal)), ft.ElevatedButton("Salvar e Arquivar", on_click=arquivar_semestre_callback, bgcolor=VERMELHO_UERJ, color=ft.Colors.WHITE)],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg_modal)

    def abrir_modal_novo_semestre(e):
        if get_arquivo_ativo() != ARQUIVO_PADRAO:
            page.overlay.append(ft.SnackBar(content=ft.Text("Erro: Volte para o 'Semestre Atual' no menu acima para arquivar."), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return
        dlg_modal.open = True
        page.update()

    # COMPONENTES MODAL DE E-MAIL
    input_email_destino = ft.TextField(label="Seu E-mail", hint_text="E-mail de sua escolha.", width=320, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)

    def disparar_email_callback(modo_webmail=False):
        email_dest = input_email_destino.value.strip()
        if not email_dest or "@" not in email_dest:
            page.overlay.append(ft.SnackBar(content=ft.Text("Por favor, digite um endereço de e-mail válido!"), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return

        dados, assunto, corpo, nome_ciclo = preparar_conteudo_backup()
        
        if not dados:
            page.overlay.append(ft.SnackBar(content=ft.Text("Atenção: Este semestre não possui disciplinas para exportar."), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return

        try:
            page.set_clipboard(corpo)
        except Exception:
            pass

        abrir_cliente_email(email_dest, assunto, corpo, modo_webmail)

        dlg_modal_email.open = False
        page.overlay.append(ft.SnackBar(content=ft.Text(f"Boletim de '{nome_ciclo}' preparado para {email_dest}!"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    def fechar_modal(dialogo):
        dialogo.open = False
        page.update()

    dlg_modal_email = ft.AlertDialog(
        modal=True,
        title=ft.Text("Exportar Histórico por E-mail", weight="bold", color=AZUL_UERJ),
        content=ft.Column(controls=[ft.Text("Envie um Boletim Executivo + Backup (.json) para o seu e-mail:", size=13), ft.Container(height=8), input_email_destino], tight=True),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: fechar_modal(dlg_modal_email)),
            ft.OutlinedButton("Abrir no App de E-mail", on_click=lambda e: disparar_email_callback(modo_webmail=False)),
            ft.ElevatedButton("Abrir no Webmail", on_click=lambda e: disparar_email_callback(modo_webmail=True), bgcolor=AZUL_UERJ, color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg_modal_email)

    # ELEMENTOS DA TELA INICIAL
    titulo_intro = ft.Text("AcademicOS", size=36, weight="bold", color=AZUL_UERJ)
    logo_intro = ft.Image(src="image_ef4634.png", width=140, height=140, fit="contain")
    botao_iniciar = ft.ElevatedButton("Cadastrar Nova Disciplina", on_click=ir_para_cadastro, width=300, color=ft.Colors.WHITE, bgcolor=AZUL_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    botao_lancar = ft.ElevatedButton("Lançar Notas e Faltas", on_click=ir_para_lancamento, width=300, color=AZUL_UERJ, bgcolor=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    botao_desempenho = ft.ElevatedButton("Ver Painel de Desempenho", on_click=ir_para_desempenho, width=300, color=ft.Colors.WHITE, bgcolor=DOURADO_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    
    linha_acoes_dados = ft.Row(
        controls=[
            ft.TextButton("Encerrar Semestre", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=abrir_modal_novo_semestre), 
            ft.Text("|", color="#BDBDBD"), 
            ft.TextButton("Exportar Backup", style=ft.ButtonStyle(color=AZUL_UERJ), on_click=lambda e: setattr(dlg_modal_email, 'open', True) or page.update())
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=5
    )

    descricao_texto = ft.Text("Acompanhe as suas notas, calcule médias e controle as suas faltas de forma inteligente.", size=13, color="#424242", text_align="left")
    rodape_descricao = ft.Container(content=ft.Row(controls=[ft.Text("💡", size=28), ft.Container(content=descricao_texto, width=230)], alignment="center", spacing=10), bgcolor="#F4F8FC", padding=15, border_radius=12, width=320)

    tela_intro = ft.Container(
        content=ft.Column(controls=[titulo_intro, logo_intro, seletor_semestre, ft.Container(height=5), botao_iniciar, botao_lancar, botao_desempenho, linha_acoes_dados, ft.Container(height=5), rodape_descricao], horizontal_alignment="center", alignment="center", spacing=10),
        bgcolor=ft.Colors.WHITE, padding=50, border_radius=20, shadow=ft.BoxShadow(spread_radius=1, blur_radius=20, color=ft.Colors.BLUE_GREY_100), visible=False 
    )

    # TELA 2: CADASTRO
    botao_voltar_cad = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    nome_input = ft.TextField(label="Nome da Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    carga_horaria_input = ft.TextField(label="Carga Horária (ex: 60)", keyboard_type="number", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    
    regra_prof_dropdown = ft.Dropdown(
        label="Regra do Professor (Avaliações)", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ, 
        options=[
            ft.dropdown.Option("Padrão UERJ (Apenas P1 e P2)"), 
            ft.dropdown.Option("P1, P2 e P3 (Substitui a Menor Nota)"),
            ft.dropdown.Option("Avaliação Flexível (Trabalhos e Testes)")
        ], 
        value="Padrão UERJ (Apenas P1 e P2)"
    )
    
    def salvar_disciplina_callback(e):
        if not nome_input.value or not carga_horaria_input.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Preencha o nome e a carga horária!"), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return

        dados = ler_dados()
        dados[nome_input.value] = {"carga_horaria": int(carga_horaria_input.value), "pesos": "", "regra_prof": regra_prof_dropdown.value, "notas": {}, "faltas": 0}
        salvar_dados(dados)

        nome_input.value = ""
        carga_horaria_input.value = ""
        regra_prof_dropdown.value = "Padrão UERJ (Apenas P1 e P2)"
        
        page.overlay.append(ft.SnackBar(content=ft.Text("Disciplina salva! Vá em Lançamentos para definir os pesos."), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    tela_cadastro = ft.Container(
        content=ft.Column(controls=[botao_voltar_cad, ft.Text("Cadastrar Disciplina", size=24, weight="bold", color=AZUL_UERJ), nome_input, carga_horaria_input, regra_prof_dropdown, ft.ElevatedButton("Salvar", on_click=salvar_disciplina_callback, width=350, bgcolor=AZUL_UERJ, color=ft.Colors.WHITE)], horizontal_alignment="center", spacing=10),
        bgcolor=ft.Colors.WHITE, padding=40, border_radius=20, visible=False
    )

    # TELA 3: LANÇAMENTOS COM PAINEL VISUAL DE HISTÓRICO
    botao_voltar_lanc = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    
    pesos_input = ft.TextField(label="Pesos (ex: P1=2, P2=2, T1=1)", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    
    painel_historico = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    
    container_historico = ft.Container(
        content=painel_historico,
        width=350,
        height=140, 
        border_radius=8,
        padding=10,
        bgcolor="#FAFAFA"
    )

    def apagar_nota_callback(materia, avaliacao):
        dados = ler_dados()
        if avaliacao in dados.get(materia, {}).get("notas", {}):
            del dados[materia]["notas"][avaliacao]
            salvar_dados(dados)
            page.overlay.append(ft.SnackBar(content=ft.Text(f"{avaliacao} removida com sucesso!"), bgcolor=ft.Colors.GREEN_700, open=True))
            reconstruir_historico(materia, dados[materia])
            page.update()
            
    def zerar_faltas_callback(materia):
        dados = ler_dados()
        if materia in dados:
            dados[materia]["faltas"] = 0
            salvar_dados(dados)
            page.overlay.append(ft.SnackBar(content=ft.Text("Faltas zeradas com sucesso!"), bgcolor=ft.Colors.GREEN_700, open=True))
            reconstruir_historico(materia, dados[materia])
            page.update()

    def reconstruir_historico(materia, materia_dados):
        painel_historico.controls.clear()
        notas = materia_dados.get("notas", {})
        faltas = materia_dados.get("faltas", 0)
        
        painel_historico.controls.append(ft.Text("Registros Salvos", weight="bold", color=AZUL_UERJ))
        
        painel_historico.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"Faltas Totais: {faltas}", weight="bold", color=VERMELHO_UERJ),
                    ft.TextButton("Zerar", tooltip="Zerar Faltas", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=lambda e: zerar_faltas_callback(materia))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#ffebee", padding=10, border_radius=8
            )
        )
        
        if notas:
            for av, nt in notas.items():
                painel_historico.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(f"Avaliação: {av}", weight="bold", color=AZUL_UERJ),
                            ft.Text(f"Nota: {nt}", weight="bold", color="#424242"),
                            ft.TextButton("Excluir", tooltip="Excluir Nota", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=lambda e, a=av: apagar_nota_callback(materia, a))
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor="#F4F8FC", padding=10, border_radius=8
                    )
                )
        else:
            painel_historico.controls.append(ft.Text("Nenhuma nota lançada no sistema.", italic=True, color=ft.Colors.GREY, text_align="center"))

    def carregar_dados_materia(e=None):
        if disciplina_dropdown.value:
            dados = ler_dados()
            materia_dados = dados.get(disciplina_dropdown.value, {})
            pesos_input.value = materia_dados.get("pesos", "")
            reconstruir_historico(disciplina_dropdown.value, materia_dados)
        else:
            pesos_input.value = ""
            painel_historico.controls.clear()
        page.update()

    disciplina_dropdown = ft.Dropdown(label="Selecione a Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    disciplina_dropdown.on_change = carregar_dados_materia
    
    linha_notas = ft.Row(controls=[ft.TextField(label="Avaliação (ex: P1)", width=170, border_color=AZUL_UERJ), ft.TextField(label="Nota (ex: 8.5)", width=170, keyboard_type="number", border_color=AZUL_UERJ)], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
    faltas_input = ft.TextField(value="0", text_align="center", width=80, keyboard_type="number", border_color=AZUL_UERJ)

    def ajustar_falta(valor):
        try:
            atual = int(faltas_input.value) if faltas_input.value else 0
            faltas_input.value = str(max(0, atual + valor))
        except ValueError:
            faltas_input.value = "1" if valor > 0 else "0"
        page.update()

    linha_faltas = ft.Row(controls=[ft.Text("Adicionar Faltas:", size=16, color=AZUL_UERJ), ft.ElevatedButton("-", on_click=lambda e: ajustar_falta(-1), bgcolor=VERMELHO_UERJ, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10)), faltas_input, ft.ElevatedButton("+", on_click=lambda e: ajustar_falta(1), bgcolor=AZUL_UERJ, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10))], alignment=ft.MainAxisAlignment.CENTER)

    def atualizar_dropdown_disciplinas():
        disciplina_dropdown.options.clear()
        dados = ler_dados()
        for materia in dados.keys():
            disciplina_dropdown.options.append(ft.dropdown.Option(materia))

    def salvar_lancamentos_callback(e):
        if not disciplina_dropdown.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Selecione uma disciplina primeiro!"), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return

        dados = ler_dados()
        materia = disciplina_dropdown.value
        
        dados[materia]["pesos"] = pesos_input.value

        avaliacao = linha_notas.controls[0].value
        nota = linha_notas.controls[1].value

        if avaliacao and nota:
            try:
                dados[materia]["notas"][avaliacao.strip().upper()] = float(nota.replace(",", "."))
            except ValueError:
                page.overlay.append(ft.SnackBar(content=ft.Text("Formato de nota inválido!"), bgcolor=VERMELHO_UERJ, open=True))
                page.update()
                return

        if faltas_input.value and faltas_input.value != "0":
            try:
                dados[materia]["faltas"] += int(faltas_input.value)
                if dados[materia]["faltas"] < 0: dados[materia]["faltas"] = 0 
            except ValueError: pass 

        salvar_dados(dados)

        linha_notas.controls[0].value = ""
        linha_notas.controls[1].value = ""
        faltas_input.value = "0"
        
        reconstruir_historico(materia, dados[materia])
        
        page.overlay.append(ft.SnackBar(content=ft.Text(f"Dados salvos em {materia}!"), bgcolor=ft.Colors.GREEN_700, open=True))
        page.update()

    botao_salvar_lancamentos = ft.ElevatedButton("Registrar no Sistema", on_click=salvar_lancamentos_callback, width=350, color=ft.Colors.WHITE, bgcolor=AZUL_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    tela_lancamento = ft.Container(
        content=ft.Column(controls=[botao_voltar_lanc, ft.Text("Lançar Desempenho", size=24, weight="bold", color=AZUL_UERJ), disciplina_dropdown, pesos_input, linha_notas, linha_faltas, botao_salvar_lancamentos, container_historico], horizontal_alignment="center", spacing=10),
        bgcolor=ft.Colors.WHITE, padding=30, border_radius=20, visible=False
    )

    # TELA 4: DESEMPENHO (DASHBOARD)
    botao_voltar_desemp = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    dropdown_desemp = ft.Dropdown(label="Selecione a Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    texto_status = ft.Text("Selecione uma disciplina", size=22, weight="bold", color=ft.Colors.WHITE)
    texto_media = ft.Text("--", size=45, weight="bold", color=ft.Colors.WHITE)
    texto_apoio = ft.Text("Aguardando seleção...", size=14, color=ft.Colors.WHITE70, text_align="center")
    texto_alerta_falta = ft.Text("Status da Frequência", size=14, weight="bold", color=ft.Colors.WHITE70)
    barra_falta = ft.ProgressBar(width=250, value=0.0, color=ft.Colors.GREEN_400, bgcolor=ft.Colors.WHITE24)
    texto_contagem_falta = ft.Text("--/-- faltas", size=12, color=ft.Colors.WHITE54)

    card_resultado = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("MÉDIA ATUAL", size=12, weight="bold", color=ft.Colors.WHITE70), texto_media, ft.Divider(color=ft.Colors.WHITE24), texto_status, texto_apoio, ft.Container(height=10),
                ft.Container(content=ft.Column(controls=[texto_alerta_falta, barra_falta, texto_contagem_falta], horizontal_alignment="center", spacing=3), bgcolor=ft.Colors.BLACK12, padding=10, border_radius=8)
            ], horizontal_alignment="center", alignment="center", spacing=5
        ), width=350, padding=30, border_radius=15, bgcolor="#424242", shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLUE_GREY_100),
    )

    def atualizar_painel_callback(e):
        materia_selecionada = dropdown_desemp.value
        if not materia_selecionada:
            page.overlay.append(ft.SnackBar(content=ft.Text("Por favor, selecione uma disciplina na lista acima."), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            return
            
        try:
            dados = ler_dados()
            materia_dados = dados.get(materia_selecionada, {})
            resultado = analisar_desempenho(materia_dados)
            
            texto_media.value = str(resultado["media_atual"])
            texto_status.value = resultado["status"]
            texto_apoio.value = resultado["texto_apoio"]
            card_resultado.bgcolor = resultado["cor"]
            
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
        except Exception as erro:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Erro interno: {erro}"), bgcolor=VERMELHO_UERJ, open=True))
            page.update()

    botao_analisar = ft.ElevatedButton("Gerar Análise", on_click=atualizar_painel_callback, width=350, bgcolor=AZUL_UERJ, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

    def atualizar_dropdown_desempenho():
        dropdown_desemp.options.clear()
        dados = ler_dados()
        for materia in dados.keys():
            dropdown_desemp.options.append(ft.dropdown.Option(materia))

    tela_desempenho = ft.Container(
        content=ft.Column(controls=[botao_voltar_desemp, ft.Text("Painel Analítico", size=24, weight="bold", color=AZUL_UERJ), dropdown_desemp, botao_analisar, card_resultado], horizontal_alignment="center", spacing=20),
        bgcolor=ft.Colors.WHITE, padding=40, border_radius=20, visible=False
    )

    # MONTAGEM FINAL DA PÁGINA
    page.add(tela_splash, tela_intro, tela_cadastro, tela_lancamento, tela_desempenho)
    
    atualizar_dropdown_semestres()
    
    await asyncio.sleep(2.5) 
    tela_splash.visible = False
    tela_intro.visible = True
    page.update()

ft.app(target=main, assets_dir="assets")