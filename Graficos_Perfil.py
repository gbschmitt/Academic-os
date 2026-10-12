import asyncio
import json
import os
import urllib.parse
import webbrowser
from datetime import datetime
import flet as ft

# 1. CONFIGURAÇÕES, CONSTANTES E ESTADO GLOBAL

AZUL_UERJ = "#0055A4"
VERMELHO_UERJ = "#E52321"
DOURADO_UERJ = "#C19A3F"

ARQUIVO_PADRAO = "dados_academicos.json"
ARQUIVO_PERFIL = "perfil_aluno.json"
ESTADO_GLOBAL = {"arquivo": ARQUIVO_PADRAO}

# 2. PERSISTÊNCIA: ARQUIVOS, PERFIL E HISTÓRICO

def get_arquivo_ativo(): 
    return ESTADO_GLOBAL["arquivo"]

def set_arquivo_ativo(nome_arquivo): 
    ESTADO_GLOBAL["arquivo"] = nome_arquivo

def garantir_arquivo_existe(nome_arquivo=ARQUIVO_PADRAO):
    if not os.path.exists(nome_arquivo):
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            json.dump({}, f)

def ler_dados(nome_arquivo=None):
    garantir_arquivo_existe(nome_arquivo or get_arquivo_ativo())
    with open(nome_arquivo or get_arquivo_ativo(), "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados, nome_arquivo=None):
    with open(nome_arquivo or get_arquivo_ativo(), "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def ler_perfil():
    if not os.path.exists(ARQUIVO_PERFIL):
        return {"nome": "", "curso": ""}
    with open(ARQUIVO_PERFIL, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_perfil(nome, curso):
    with open(ARQUIVO_PERFIL, "w", encoding="utf-8") as f:
        json.dump({"nome": nome, "curso": curso}, f, ensure_ascii=False)

def listar_arquivos_historico():
    garantir_arquivo_existe(ARQUIVO_PADRAO)
    return [f for f in os.listdir() if f.startswith("dados_academicos_arquivado_") and f.endswith(".json")]

def arquivar_semestre_atual(nome_personalizado):
    nome_seguro = "".join([c for c in nome_personalizado if c.isalnum() or c in " .-_"]) or datetime.now().strftime("%Y%m%d_%H%M%S")
    novo_nome = f"dados_academicos_arquivado_{nome_seguro}.json"
    if os.path.exists(novo_nome): 
        return False, "Já existe um histórico com este nome!"
    if os.path.exists(ARQUIVO_PADRAO): 
        os.rename(ARQUIVO_PADRAO, novo_nome)
    
    garantir_arquivo_existe(ARQUIVO_PADRAO)
    return True, nome_seguro

# 3. REGRAS DE NEGÓCIO: CÁLCULOS DE DESEMPENHO

def analisar_desempenho(dados_materia):
    carga_horaria = dados_materia.get("carga_horaria", 60)
    faltas = dados_materia.get("faltas", 0)
    limite_faltas = carga_horaria * 0.25
    regra_prof = dados_materia.get("regra_prof", "Padrão UERJ (Apenas P1 e P2)")
    percentual_falta = faltas / limite_faltas if limite_faltas > 0 else 0
    
    if faltas > limite_faltas: 
        alerta, cor_barra = "Limite Excedido!", "#8B0000"
    elif percentual_falta >= 0.75: 
        alerta, cor_barra = "Alerta Crítico: Risco de Reprovação", DOURADO_UERJ
    elif percentual_falta >= 0.50: 
        alerta, cor_barra = "Atenção: Frequência Caindo", "orange"
    else: 
        alerta, cor_barra = "Frequência Segura", "green"
        
    info_faltas = {
        "percentual": min(percentual_falta, 1.0), 
        "texto_alerta": alerta, 
        "texto_contagem": f"{faltas}/{int(limite_faltas)} faltas", 
        "cor_barra": cor_barra
    }
    
    if faltas > limite_faltas:
        return {
            "status": "Reprovado por Falta", 
            "cor": "#8B0000", 
            "texto_apoio": f"Você estourou o limite de {int(limite_faltas)} faltas.", 
            "media_atual": 0.0, 
            "faltas": info_faltas
        }

    notas = dados_materia.get("notas", {})
    if not notas: 
        return {
            "status": "Sem avaliações", 
            "cor": "#757575", 
            "texto_apoio": "Nenhuma nota lançada ainda.", 
            "media_atual": 0.0, 
            "faltas": info_faltas
        }

    pesos_dit = {}
    if pesos_str := dados_materia.get("pesos", ""):
        try:
            for p in pesos_str.split(","):
                chave, valor = p.split("=")
                pesos_dit[chave.strip().upper()] = float(valor.strip())
        except ValueError: 
            pass

    notas_validas = {k.strip().upper(): v for k, v in notas.items()}
    if regra_prof == "Avaliação Flexível (Trabalhos e Testes)":
        soma_pesos = sum(pesos_dit.values()) if pesos_dit else (len(notas_validas) or 1)
        soma_notas = sum(notas_validas.get(av, 0.0) * p for av, p in pesos_dit.items()) if pesos_dit else sum(notas_validas.values())
        media_semestral = (soma_notas / soma_pesos) if soma_pesos > 0 else 0.0
    else:
        peso_p1, peso_p2 = pesos_dit.get("P1", 1.0), pesos_dit.get("P2", 1.0)
        n1, n2 = notas_validas.get("P1", 0.0), notas_validas.get("P2", 0.0)
        if regra_prof == "P1, P2 e P3 (Substitui a Menor Nota)" and "P3" in notas_validas:
            n3 = notas_validas["P3"]
            if n1 <= n2 and n3 > n1: n1 = n3
            elif n2 < n1 and n3 > n2: n2 = n3
        soma_pesos = peso_p1 + peso_p2
        media_semestral = ((n1 * peso_p1) + (n2 * peso_p2)) / soma_pesos if soma_pesos > 0 else 0.0
        
    media_semestral = round(media_semestral, 2)
    
    if media_semestral >= 7.0: 
        return {"status": "Aprovado Direto!", "cor": "#2E7D32", "texto_apoio": "Parabéns, não precisa de prova final.", "media_atual": media_semestral, "faltas": info_faltas}
    elif media_semestral < 4.0: 
        return {"status": "Reprovado por Nota", "cor": "#D32F2F", "texto_apoio": "Média insuficiente para a Prova Final.", "media_atual": media_semestral, "faltas": info_faltas}
        
    return {"status": "Prova Final", "cor": DOURADO_UERJ, "texto_apoio": f"Você precisa tirar {round(10.0 - media_semestral, 2)} na PF para passar.", "media_atual": media_semestral, "faltas": info_faltas}

# 4. EXPORTAÇÃO, BACKUP E E-MAIL

def preparar_conteudo_backup():
    arquivo_ativo = get_arquivo_ativo()
    dados = ler_dados(arquivo_ativo)
    perfil = ler_perfil()
    nome_aluno = perfil.get("nome", "Estudante")
    nome_ciclo = "Semestre Atual" if arquivo_ativo == ARQUIVO_PADRAO else arquivo_ativo.replace("dados_academicos_arquivado_", "").replace(".json", "")
    linhas_resumo = []
    
    for nome_mat, info in dados.items():
        analise = analisar_desempenho(info)
        notas_str = " | ".join([f"{av.upper()}: { valor }" for av, valor in info.get("notas", {}).items()]) or "Nenhuma avaliação lançada"
        status_txt = analise["status"]
        icone_status = "🟢" if "Aprovado" in status_txt else "🟡" if "Prova Final" in status_txt else "🔴" if "Reprovado" in status_txt else "⚪"
        linhas_resumo.append(
            f"📘 {nome_mat.upper()}\n   • Situação: {icone_status} {status_txt} ({analise['texto_apoio']})\n"
            f"   • Média Acumulada: {analise['media_atual']}  |  Notas: {notas_str}\n"
            f"   • Frequência: {analise['faltas']['texto_contagem']} ({analise['faltas']['texto_alerta']})  |  Carga Horária: {info.get('carga_horaria', 60)}h\n"
            f"   • Critério: {info.get('regra_prof', 'Padrão UERJ')}  |  Pesos: {info.get('pesos', '') or 'Padrão (Pesos Iguais)'}\n"
            f"--------------------------------------------------"
        )
        
    corpo = (
        f"🎓 ACADEMICOS - BOLETIM E BACKUP ACADÊMICO\n{'='*50}\n👤 Aluno: {nome_aluno}\n📅 Ciclo: {nome_ciclo}\n🕒 Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}\n📚 Disciplinas: {len(dados)}\n{'='*50}\n\n"
        f"📊 RESUMO EXECUTIVO DO SEU DESEMPENHO:\n\n{chr(10).join(linhas_resumo)}\n\n"
        f"💾 DADOS TÉCNICOS PARA RESTAURAÇÃO (ARQUIVO .JSON)\n{json.dumps(dados, indent=4, ensure_ascii=False)}\n{'='*50}\nGerado automaticamente por AcademicOS • UERJ"
    )
    return dados, f"🎓 Boletim AcademicOS - {nome_aluno}", corpo, nome_ciclo

def abrir_cliente_email(email_dest, assunto, corpo, modo_webmail):
    if modo_webmail:
        url = f"https://outlook.live.com/owa/?path=/mail/action/compose&to={email_dest}&subject={urllib.parse.quote(assunto)}&body={urllib.parse.quote(corpo)}" if any(p in email_dest.split("@")[-1].lower() for p in ["outlook", "hotmail", "live", "msn"]) else f"https://mail.google.com/mail/?view=cm&fs=1&to={email_dest}&su={urllib.parse.quote(assunto)}&body={urllib.parse.quote(corpo)}"
    else:
        url = f"mailto:{email_dest}?subject={urllib.parse.quote(assunto)}&body={urllib.parse.quote(corpo)}"
    webbrowser.open(url)

# 5. COMPONENTES VISUAIS REUTILIZÁVEIS: GRÁFICOS

def criar_grafico_faltas(faltas_atuais, limite_faltas):
    percentual = (faltas_atuais / limite_faltas) if limite_faltas > 0 else 0
    cor_falta = "red" if percentual >= 0.75 else ("orange" if percentual >= 0.50 else "blue")
    return ft.Container(
        content=ft.Column([
            ft.Text("Consumo de Faltas", weight="bold", size=12, color="#424242"),
            ft.Stack([
                ft.ProgressRing(value=1.0, color="#EEEEEE", stroke_width=8, width=70, height=70),
                ft.ProgressRing(value=min(percentual, 1.0), color=cor_falta, stroke_width=8, width=70, height=70),
                ft.Container(
                    content=ft.Row([ft.Text(f"{int(percentual * 100)}%", weight="bold", size=14, color=cor_falta)], alignment="center"), 
                    width=70, height=70
                )
            ], width=70, height=70)
        ], horizontal_alignment="center"),
        padding=5
    )

def criar_grafico_notas(media_atual):
    meta_uerj = 7.0 
    cor_nota = "green" if media_atual >= meta_uerj else ("orange" if media_atual >= 4.0 else "red")
    percentual = media_atual / 10.0
    return ft.Container(
        content=ft.Column([
            ft.Text("Desempenho vs Meta", weight="bold", size=12, color="#424242"),
            ft.Text(f"Nota Atual: {media_atual}", size=14, weight="bold", color=cor_nota),
            ft.ProgressBar(value=percentual, color=cor_nota, bgcolor="#EEEEEE", width=120)
        ], horizontal_alignment="center"),
        padding=5
    )

# 6. INICIALIZAÇÃO E INTERFACE GRÁFICA PRINCIPAL (MAIN)

async def main(page: ft.Page): 
    page.title, page.vertical_alignment, page.horizontal_alignment, page.padding, page.theme_mode, page.bgcolor = "AcademicOS", "center", "center", 0, "light", "#E3F2FD"
    
    disciplina_dropdown = ft.Dropdown(label="Selecione a Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    dropdown_desemp = ft.Dropdown(label="Selecione a Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    
    def atualizar_dropdown_disciplinas():
        disciplina_dropdown.options = [ft.dropdown.Option(m) for m in ler_dados().keys()]
        
    def atualizar_dropdown_desempenho():
        dropdown_desemp.options = [ft.dropdown.Option(m) for m in ler_dados().keys()]
        
    # --- PERFIL DO ALUNO (ONBOARDING E DADOS) 
    perfil_salvo = ler_perfil()
    texto_boas_vindas = ft.Text(f"👤 Olá, {perfil_salvo.get('nome', '')}" if perfil_salvo.get('nome') else "", size=14, weight="bold", color="#424242")
    texto_curso_header = ft.Text(perfil_salvo.get('curso', '') if perfil_salvo.get('curso') else "", size=12, color="#757575", italic=True)
    
    cabecalho_perfil_discreto = ft.Column(
        controls=[texto_boas_vindas, texto_curso_header],
        horizontal_alignment="center", spacing=2
    )
    
    input_nome_perfil = ft.TextField(label="Nome do usuário", value=perfil_salvo.get("nome", ""), width=320, border_color=AZUL_UERJ)
    input_curso_perfil = ft.TextField(label="Curso do usuário", value=perfil_salvo.get("curso", ""), width=320, border_color=AZUL_UERJ)
    
    def avancar_para_intro(e):
        nome_val = input_nome_perfil.value.strip()
        curso_val = input_curso_perfil.value.strip()
        salvar_perfil(nome_val, curso_val)
        texto_boas_vindas.value = f"👤 Olá, {nome_val}" if nome_val else ""
        texto_curso_header.value = curso_val if curso_val else ""
        tela_perfil.visible = False
        tela_intro.visible = True
        verificar_alertas_iniciais()
        page.update()
        
    tela_perfil = ft.Container(
        content=ft.Column(
            controls=[
                ft.Image(src="image_ef4634.png", width=110, height=110, fit="contain"),
                ft.Text("Identidade do Aluno", size=26, weight="bold", color=AZUL_UERJ),
                ft.Text("Configure os seus dados académicos.", size=14, color="#757575", text_align="center"),
                ft.Container(height=15),
                input_nome_perfil,
                input_curso_perfil,
                ft.Container(height=15),
                ft.ElevatedButton("Salvar e Voltar", on_click=avancar_para_intro, width=320, bgcolor=AZUL_UERJ, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
            ], horizontal_alignment="center", alignment="center", spacing=10
        ),
        bgcolor="white", padding=40, border_radius=20, visible=False
    )
    
    # --- LÓGICA DE NAVEGAÇÃO E NOTIFICAÇÕES 
    texto_notificacao = ft.Text("", color="white", weight="bold", size=11)
    btn_ver_status = ft.TextButton("Ver Status", style=ft.ButtonStyle(color="white"))
    
    container_notificacao = ft.Container(
        content=ft.Row([
            ft.Container(content=texto_notificacao, width=220), 
            ft.Row([btn_ver_status, ft.TextButton("X", style=ft.ButtonStyle(color="white"), on_click=lambda e: setattr(container_notificacao, 'visible', False) or page.update())], spacing=0)
        ], alignment="spaceBetween"),
        bgcolor=VERMELHO_UERJ, padding=10, border_radius=10, width=380, visible=False
    )
    
    def verificar_alertas_iniciais():
        alertas = []
        for m, d in ler_dados().items():
            limite = d.get("carga_horaria", 60) * 0.25
            if limite > 0 and (d.get("faltas", 0) / limite) >= 0.5:
                alertas.append((m, d.get("faltas", 0) / limite))
        if alertas:
            pior_mat, pior_perc = max(alertas, key=lambda x: x[1])
            critico = pior_perc >= 0.75
            container_notificacao.bgcolor = VERMELHO_UERJ if critico else DOURADO_UERJ
            texto_notificacao.value = f"{'🚨' if critico else '⚠️'} {len(alertas)} disciplina(s) em {'risco CRÍTICO!' if critico else 'alerta (Faltas).'}"
            btn_ver_status.on_click = lambda e: ir_para_desempenho(materia_alvo=pior_mat)
        container_notificacao.visible = bool(alertas)
        try: page.update()
        except: pass

    def ir_para_cadastro(e):
        tela_intro.visible = tela_lancamento.visible = tela_desempenho.visible = tela_perfil.visible = False
        tela_cadastro.visible = True
        page.update()

    def ir_para_lancamento(e):
        atualizar_dropdown_disciplinas()
        disciplina_dropdown.value, pesos_input.value = None, ""
        painel_historico.controls.clear()
        tela_intro.visible = tela_cadastro.visible = tela_desempenho.visible = tela_perfil.visible = False
        tela_lancamento.visible = True
        page.update()

    def ir_para_desempenho(e=None, materia_alvo=None):
        container_notificacao.visible = False 
        atualizar_dropdown_desempenho()
        if materia_alvo and materia_alvo in [opt.key for opt in dropdown_desemp.options]:
            dropdown_desemp.value = materia_alvo
            atualizar_painel_callback(None) 
        else:
            dropdown_desemp.value = None
            texto_media.value, texto_status.value, texto_apoio.value = "--", "Selecione uma disciplina", "Aguardando seleção..."
            card_resultado.bgcolor = "#424242"
            texto_alerta_falta.value, texto_alerta_falta.color = "Status da Frequência", "white70"
            barra_falta.value, barra_falta.color = 0.0, "green"
            texto_contagem_falta.value = "--/-- faltas"
            container_graficos.visible = False 
        tela_intro.visible = tela_cadastro.visible = tela_lancamento.visible = tela_perfil.visible = False
        tela_desempenho.visible = True
        page.update()

    def ir_para_inicio(e=None):
        atualizar_dropdown_semestres()
        verificar_alertas_iniciais()
        tela_cadastro.visible = tela_lancamento.visible = tela_desempenho.visible = tela_perfil.visible = False
        tela_intro.visible = True
        page.update()

    # --- TELA SPLASH 
    tela_splash = ft.Stack(
        controls=[
            ft.Image(src="image_f56f29.jpg", fit="cover", width=4000, height=4000),
            ft.Container(content=ft.Column(controls=[ft.Image(src="image_ef4636.png", width=180, height=180, fit="contain"), ft.Container(height=10), ft.Text("AcademicOS", size=42, weight="bold", color="white"), ft.Text("Seu sistema inteligente para gestão\nde desempenho acadêmico.", text_align="center", color="#F2D794", size=15, italic=True), ft.Container(height=60), ft.ProgressRing(color="#F2D794", stroke_width=2, width=30, height=30)], horizontal_alignment="center", alignment="center", spacing=0), expand=True)
        ], expand=True, visible=True 
    )

    # --- MENU DE OPÇÕES, SELETORES E MODAIS 
    seletor_semestre = ft.Dropdown(label="Histórico de Semestres (Base de Dados)", width=300, border_color=DOURADO_UERJ, focused_border_color=AZUL_UERJ)
    
    def notificar_mudanca_semestre(e):
        set_arquivo_ativo(seletor_semestre.value or ARQUIVO_PADRAO)
        nome_exibir = get_arquivo_ativo().replace("dados_academicos_arquivado_", "").replace(".json", "") if get_arquivo_ativo() != ARQUIVO_PADRAO else "Semestre Atual"
        page.overlay.append(ft.SnackBar(content=ft.Text(f"A ler a base de dados: {nome_exibir}"), bgcolor=DOURADO_UERJ, open=True))
        verificar_alertas_iniciais() 
        
    seletor_semestre.on_change = notificar_mudanca_semestre
    
    def atualizar_dropdown_semestres(forcar_atual=False):
        val_ant = get_arquivo_ativo()
        seletor_semestre.options = [ft.dropdown.Option(key=ARQUIVO_PADRAO, text="Semestre Atual (Ativo)")] + [ft.dropdown.Option(key=a, text=f"Histórico: {a.replace('dados_academicos_arquivado_', '').replace('.json', '')}") for a in sorted(listar_arquivos_historico(), reverse=True)]
        if forcar_atual or not val_ant:
            seletor_semestre.value = ARQUIVO_PADRAO
            set_arquivo_ativo(ARQUIVO_PADRAO)
        else:
            seletor_semestre.value = val_ant if val_ant in [opt.key for opt in seletor_semestre.options] else ARQUIVO_PADRAO
            set_arquivo_ativo(seletor_semestre.value)
        try: seletor_semestre.update()
        except: pass

    input_nome_semestre = ft.TextField(label="Nome do Semestre", hint_text="Como quer chamar este histórico?", width=300, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    
    def arquivar_semestre_callback(e):
        sucesso, msg = arquivar_semestre_atual(input_nome_semestre.value.strip())
        if sucesso:
            input_nome_semestre.value = "" 
            atualizar_dropdown_semestres(True)
            verificar_alertas_iniciais()
            dlg_modal.open = False 
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Semestre '{msg}' arquivado!"), bgcolor="green", open=True))
        else:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Erro: {msg}"), bgcolor=VERMELHO_UERJ, open=True))
        page.update()

    dlg_modal = ft.AlertDialog(modal=True, title=ft.Text("Encerrar Semestre Atual", weight="bold", color=AZUL_UERJ), content=ft.Column(controls=[ft.Text("As disciplinas atuais ficarão guardadas no histórico.", size=14), ft.Container(height=10), input_nome_semestre], tight=True), actions=[ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg_modal, 'open', False) or page.update()), ft.ElevatedButton("Salvar e Arquivar", on_click=arquivar_semestre_callback, bgcolor=VERMELHO_UERJ, color="white")], actions_alignment="end")
    page.overlay.append(dlg_modal)
    
    def abrir_modal_novo_semestre(e):
        if get_arquivo_ativo() != ARQUIVO_PADRAO: page.overlay.append(ft.SnackBar(content=ft.Text("Erro: Volte para o 'Semestre Atual' no menu acima para arquivar."), bgcolor=VERMELHO_UERJ, open=True))
        else: dlg_modal.open = True
        page.update()

    input_email_destino = ft.TextField(label="Seu E-mail", hint_text="E-mail de sua escolha.", width=320, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    
    def disparar_email_callback(modo_webmail=False):
        if not input_email_destino.value.strip() or "@" not in input_email_destino.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Digite um e-mail válido!"), bgcolor=VERMELHO_UERJ, open=True))
            return page.update()
        dados, assunto, corpo, nome_ciclo = preparar_conteudo_backup()
        if not dados:
            page.overlay.append(ft.SnackBar(content=ft.Text("Atenção: Semestre vazio."), bgcolor=VERMELHO_UERJ, open=True))
            return page.update()
        try: page.set_clipboard(corpo)
        except: pass
        abrir_cliente_email(input_email_destino.value.strip(), assunto, corpo, modo_webmail)
        dlg_modal_email.open = False
        page.overlay.append(ft.SnackBar(content=ft.Text(f"Boletim preparado para {input_email_destino.value.strip()}!"), bgcolor="green", open=True))
        page.update()

    dlg_modal_email = ft.AlertDialog(modal=True, title=ft.Text("Exportar Histórico por E-mail", weight="bold", color=AZUL_UERJ), content=ft.Column(controls=[ft.Text("Envie um Boletim Executivo + Backup (.json) para o seu e-mail:", size=13), ft.Container(height=8), input_email_destino], tight=True), actions=[ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg_modal_email, 'open', False) or page.update()), ft.OutlinedButton("Abrir no App de E-mail", on_click=lambda e: disparar_email_callback(False)), ft.ElevatedButton("Abrir no Webmail", on_click=lambda e: disparar_email_callback(True), bgcolor=AZUL_UERJ, color="white")], actions_alignment="end")
    page.overlay.append(dlg_modal_email)

    # --- TELA INICIAL (INTRO) 
    titulo_intro = ft.Text("AcademicOS", size=36, weight="bold", color=AZUL_UERJ)
    logo_intro = ft.Image(src="image_ef4634.png", width=140, height=140, fit="contain")
    botao_iniciar = ft.ElevatedButton("Cadastrar Nova Disciplina", on_click=ir_para_cadastro, width=300, color="white", bgcolor=AZUL_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    botao_lancar = ft.ElevatedButton("Lançar Notas e Faltas", on_click=ir_para_lancamento, width=300, color=AZUL_UERJ, bgcolor="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    botao_desempenho = ft.ElevatedButton("Ver Painel de Desempenho", on_click=ir_para_desempenho, width=300, color="white", bgcolor=DOURADO_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    
    linha_acoes_dados = ft.Row(
        controls=[
            ft.TextButton("Perfil", style=ft.ButtonStyle(color=AZUL_UERJ), on_click=lambda e: (setattr(tela_intro, 'visible', False), setattr(tela_perfil, 'visible', True), page.update())),
            ft.Text("|", color="#BDBDBD"),
            ft.TextButton("Encerrar Semestre", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=abrir_modal_novo_semestre), 
            ft.Text("|", color="#BDBDBD"), 
            ft.TextButton("Exportar", style=ft.ButtonStyle(color=AZUL_UERJ), on_click=lambda e: setattr(dlg_modal_email, 'open', True) or page.update())
        ], alignment="center", spacing=5
    )
    
    rodape_descricao = ft.Container(content=ft.Row(controls=[ft.Text("💡", size=28), ft.Container(content=ft.Text("Acompanhe as suas notas, calcule médias e controle as suas faltas de forma inteligente.", size=13, color="#424242", text_align="left"), width=230)], alignment="center", spacing=10), bgcolor="#F4F8FC", padding=15, border_radius=12, width=320)
    
    tela_intro = ft.Container(
        content=ft.Stack([
            ft.Column(controls=[
                ft.Container(height=10), 
                titulo_intro, 
                logo_intro, 
                cabecalho_perfil_discreto,
                seletor_semestre, 
                ft.Container(height=5), 
                botao_iniciar, 
                botao_lancar, 
                botao_desempenho, 
                linha_acoes_dados, 
                ft.Container(height=5), 
                rodape_descricao
            ], horizontal_alignment="center", alignment="center", spacing=10),
            ft.Container(content=ft.Row([container_notificacao], alignment="center"), top=0, left=0, right=0)
        ]), bgcolor="white", padding=30, border_radius=20, visible=False 
    )

    # --- TELA DE CADASTRO DE MATÉRIAS 
    botao_voltar_cad = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    nome_input = ft.TextField(label="Nome da Disciplina", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    carga_horaria_input = ft.TextField(label="Carga Horária (ex: 60)", keyboard_type="number", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    regra_prof_dropdown = ft.Dropdown(label="Regra do Professor (Avaliações)", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ, options=[ft.dropdown.Option("Padrão UERJ (Apenas P1 e P2)"), ft.dropdown.Option("P1, P2 e P3 (Substitui a Menor Nota)"), ft.dropdown.Option("Avaliação Flexível (Trabalhos e Testes)")], value="Padrão UERJ (Apenas P1 e P2)")
    
    def salvar_disciplina_callback(e):
        if not nome_input.value or not carga_horaria_input.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Preencha o nome e a carga horária!"), bgcolor=VERMELHO_UERJ, open=True))
            return page.update()
        dados = ler_dados()
        dados[nome_input.value] = {"carga_horaria": int(carga_horaria_input.value), "pesos": "", "regra_prof": regra_prof_dropdown.value, "notas": {}, "faltas": 0}
        salvar_dados(dados)
        nome_input.value, carga_horaria_input.value, regra_prof_dropdown.value = "", "", "Padrão UERJ (Apenas P1 e P2)"
        page.overlay.append(ft.SnackBar(content=ft.Text("Disciplina salva! Vá em Lançamentos para definir os pesos."), bgcolor="green", open=True))
        page.update()

    tela_cadastro = ft.Container(content=ft.Column(controls=[botao_voltar_cad, ft.Text("Cadastrar Disciplina", size=24, weight="bold", color=AZUL_UERJ), nome_input, carga_horaria_input, regra_prof_dropdown, ft.ElevatedButton("Salvar", on_click=salvar_disciplina_callback, width=350, bgcolor=AZUL_UERJ, color="white")], horizontal_alignment="center", spacing=10), bgcolor="white", padding=40, border_radius=20, visible=False)

    # --- TELA DE LANÇAMENTOS 
    botao_voltar_lanc = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    pesos_input = ft.TextField(label="Pesos (ex: P1=2, P2=2, T1=1)", width=350, border_color=AZUL_UERJ, focused_border_color=DOURADO_UERJ)
    painel_historico = ft.Column(spacing=8, scroll="auto")
    container_historico = ft.Container(content=painel_historico, width=350, height=140, border_radius=8, padding=10, bgcolor="#FAFAFA")
    
    def acao_historico_callback(materia, avaliacao=None, excluir=False):
        dados = ler_dados()
        if excluir and avaliacao in dados.get(materia, {}).get("notas", {}): del dados[materia]["notas"][avaliacao]
        else: dados.setdefault(materia, {})["faltas"] = 0
        salvar_dados(dados)
        page.overlay.append(ft.SnackBar(content=ft.Text(f"{avaliacao if excluir else 'Faltas'} removida(s) com sucesso!"), bgcolor="green", open=True))
        reconstruir_historico(materia, dados[materia])
        page.update()

    def reconstruir_historico(materia, materia_dados):
        painel_historico.controls.clear()
        notas, faltas = materia_dados.get("notas", {}), materia_dados.get("faltas", 0)
        painel_historico.controls.append(ft.Text("Registros Salvos", weight="bold", color=AZUL_UERJ))
        painel_historico.controls.append(ft.Container(content=ft.Row([ft.Text(f"Faltas Totais: {faltas}", weight="bold", color=VERMELHO_UERJ), ft.TextButton("Zerar", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=lambda e: acao_historico_callback(materia))], alignment="spaceBetween"), bgcolor="#ffebee", padding=10, border_radius=8))
        if notas:
            for av, nt in notas.items():
                painel_historico.controls.append(ft.Container(content=ft.Row([ft.Text(f"Avaliação: {av}", weight="bold", color=AZUL_UERJ), ft.Text(f"Nota: {nt}", weight="bold", color="#424242"), ft.TextButton("Excluir", style=ft.ButtonStyle(color=VERMELHO_UERJ), on_click=lambda e, a=av: acao_historico_callback(materia, a, True))], alignment="spaceBetween"), bgcolor="#F4F8FC", padding=10, border_radius=8))
        else: painel_historico.controls.append(ft.Text("Nenhuma nota lançada no sistema.", italic=True, color="grey", text_align="center"))
    
    def carregar_dados_materia(e=None):
        if disciplina_dropdown.value:
            dados = ler_dados()
            pesos_input.value = dados.get(disciplina_dropdown.value, {}).get("pesos", "")
            reconstruir_historico(disciplina_dropdown.value, dados.get(disciplina_dropdown.value, {}))
        else: pesos_input.value = ""; painel_historico.controls.clear()
        page.update()

    disciplina_dropdown.on_change = carregar_dados_materia
    linha_notas = ft.Row(controls=[ft.TextField(label="Avaliação (ex: P1)", width=170, border_color=AZUL_UERJ), ft.TextField(label="Nota (ex: 8.5)", width=170, keyboard_type="number", border_color=AZUL_UERJ)], alignment="center", spacing=10)
    faltas_input = ft.TextField(value="0", text_align="center", width=80, keyboard_type="number", border_color=AZUL_UERJ)
    
    def ajustar_falta(valor):
        try: faltas_input.value = str(max(0, int(faltas_input.value or 0) + valor))
        except ValueError: faltas_input.value = "1" if valor > 0 else "0"
        page.update()

    linha_faltas = ft.Row(controls=[ft.Text("Adicionar Faltas:", size=16, color=AZUL_UERJ), ft.ElevatedButton("-", on_click=lambda e: ajustar_falta(-1), bgcolor=VERMELHO_UERJ, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10)), faltas_input, ft.ElevatedButton("+", on_click=lambda e: ajustar_falta(1), bgcolor=AZUL_UERJ, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), padding=10))], alignment="center")
    
    def salvar_lancamentos_callback(e):
        if not disciplina_dropdown.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Selecione uma disciplina primeiro!"), bgcolor=VERMELHO_UERJ, open=True))
            return page.update()
        dados, materia, avaliacao, nota = ler_dados(), disciplina_dropdown.value, linha_notas.controls[0].value, linha_notas.controls[1].value
        dados[materia]["pesos"] = pesos_input.value
        if avaliacao and nota:
            try: dados[materia]["notas"][avaliacao.strip().upper()] = float(nota.replace(",", "."))
            except ValueError:
                page.overlay.append(ft.SnackBar(content=ft.Text("Formato de nota inválido!"), bgcolor=VERMELHO_UERJ, open=True))
                return page.update()
        if faltas_input.value and faltas_input.value != "0":
            try: dados[materia]["faltas"] = max(0, dados[materia]["faltas"] + int(faltas_input.value))
            except ValueError: pass 
        salvar_dados(dados)
        linha_notas.controls[0].value = linha_notas.controls[1].value = ""
        faltas_input.value = "0"
        reconstruir_historico(materia, dados[materia])
        page.overlay.append(ft.SnackBar(content=ft.Text(f"Dados salvos em {materia}!"), bgcolor="green", open=True))
        page.update()

    botao_salvar_lancamentos = ft.ElevatedButton("Registrar no Sistema", on_click=salvar_lancamentos_callback, width=350, color="white", bgcolor=AZUL_UERJ, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    tela_lancamento = ft.Container(content=ft.Column(controls=[botao_voltar_lanc, ft.Text("Lançar Desempenho", size=24, weight="bold", color=AZUL_UERJ), disciplina_dropdown, pesos_input, linha_notas, linha_faltas, botao_salvar_lancamentos, container_historico], horizontal_alignment="center", spacing=10), bgcolor="white", padding=30, border_radius=20, visible=False)
    
    # --- TELA DE DESEMPENHO (DASHBOARD) ---
    botao_voltar_desemp = ft.TextButton("< Voltar", on_click=ir_para_inicio, icon_color=AZUL_UERJ)
    texto_status = ft.Text("Selecione uma disciplina", size=22, weight="bold", color="white")
    texto_media = ft.Text("--", size=45, weight="bold", color="white")
    texto_apoio = ft.Text("Aguardando seleção...", size=14, color="white70", text_align="center")
    texto_alerta_falta = ft.Text("Status da Frequência", size=14, weight="bold", color="white70")
    barra_falta = ft.ProgressBar(width=250, value=0.0, color="green", bgcolor="white24")
    texto_contagem_falta = ft.Text("--/-- faltas", size=12, color="white54")
    
    card_resultado = ft.Container(
        content=ft.Column([ft.Text("MÉDIA ATUAL", size=12, weight="bold", color="white70"), texto_media, ft.Divider(color="white24"), texto_status, texto_apoio, ft.Container(height=10), ft.Container(content=ft.Column(controls=[texto_alerta_falta, barra_falta, texto_contagem_falta], horizontal_alignment="center", spacing=3), bgcolor="black12", padding=10, border_radius=8)], horizontal_alignment="center", alignment="center", spacing=5),
        width=350, padding=30, border_radius=15, bgcolor="#424242", shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color="#CFD8DC"),
    )
    
    container_graficos = ft.Container(
        width=350,
        padding=20,
        border_radius=15,
        bgcolor="#FAFAFA",
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color="#CFD8DC"),
        visible=False
    )
    
    def atualizar_painel_callback(e):
        if not dropdown_desemp.value:
            page.overlay.append(ft.SnackBar(content=ft.Text("Por favor, selecione uma disciplina na lista acima."), bgcolor=VERMELHO_UERJ, open=True))
            return page.update()
        try:
            dados_materia = ler_dados().get(dropdown_desemp.value, {})
            resultado = analisar_desempenho(dados_materia)
            texto_media.value, texto_status.value, texto_apoio.value, card_resultado.bgcolor = str(resultado["media_atual"]), resultado["status"], resultado["texto_apoio"], resultado["cor"]
            texto_alerta_falta.value, texto_alerta_falta.color, barra_falta.value, barra_falta.color, texto_contagem_falta.value = resultado["faltas"]["texto_alerta"], resultado["faltas"]["cor_barra"], resultado["faltas"]["percentual"], resultado["faltas"]["cor_barra"], resultado["faltas"]["texto_contagem"]
            card_resultado.update()
            faltas_atuais = dados_materia.get("faltas", 0)
            limite_faltas = dados_materia.get("carga_horaria", 60) * 0.25
            conteudo_graficos = ft.Column([
                ft.Text("VISÃO DETALHADA", size=12, weight="bold", color=AZUL_UERJ),
                ft.Divider(color="#E0E0E0", height=15),
                ft.ResponsiveRow([
                    ft.Column(col={"xs": 12, "sm": 6}, controls=[criar_grafico_notas(media_atual=resultado["media_atual"])]),
                    ft.Column(col={"xs": 12, "sm": 6}, controls=[criar_grafico_faltas(faltas_atuais=faltas_atuais, limite_faltas=limite_faltas)])
                ], alignment="center")
            ], horizontal_alignment="center", spacing=5)
            container_graficos.content = conteudo_graficos
            container_graficos.visible = True
            container_graficos.update()
        except Exception as erro:
            page.overlay.append(ft.SnackBar(content=ft.Text(f"Erro interno: {erro}"), bgcolor=VERMELHO_UERJ, open=True))
            page.update()
            
    botao_analisar = ft.ElevatedButton("Gerar Análise", on_click=atualizar_painel_callback, width=350, bgcolor=AZUL_UERJ, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
    
    tela_desempenho = ft.Container(
        content=ft.Column(
            controls=[botao_voltar_desemp, ft.Text("Painel Analítico", size=24, weight="bold", color=AZUL_UERJ), dropdown_desemp, botao_analisar, card_resultado, container_graficos], 
            horizontal_alignment="center", 
            spacing=20, 
            scroll="auto"
        ), 
        bgcolor="white", padding=40, border_radius=20, visible=False, expand=True
    )
    
    page.add(tela_splash, tela_perfil, tela_intro, tela_cadastro, tela_lancamento, tela_desempenho)
    atualizar_dropdown_semestres()
    
    await asyncio.sleep(2.5) 
    tela_splash.visible = False
    
    if not ler_perfil().get("nome"):
        tela_perfil.visible = True
    else:
        tela_intro.visible = True
        verificar_alertas_iniciais()
        
    page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")