import streamlit as st
import pandas as pd
import time
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Royal", page_icon="👑", layout="wide")

# --- LISTA DE PRODUTOS ---
LISTA_ITENS = [
    "Internet 300 MEGA", "Internet 500 MEGA", "Internet 600 MEGA", "Internet 800 MEGA", "Internet 1 GIGA",
    "TV Basico", "TV Full",
    "Chip 20GB", "Chip 25GB", "Chip 30GB",
    "Camera de Seguranca (Avulsa)",
    "Ponto Extra", "Telefone Fixo VoIP", "Wi-Fi 6 (Roteador Extra)",
    "Combo 1 (300MB + TV Basico)",
    "Combo 2 (500MB + Chip 20GB + TV Basico)",
    "Combo 3 (600MB + Chip 25GB + TV Basico + Wi-Fi 6)",
    "Combo 4 (800MB + Chip 30GB + TV Full + Wi-Fi 6)",
    "Combo 5 (1GB + Chip 30GB + 2 Cameras + Wi-Fi 6)"
]

# --- FUNÇÃO: CONECTAR AO GOOGLE SHEETS ---
def get_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def carregar_dados(aba):
    conn = get_connection()
    # ttl=0 é essencial para não pegar cache velho
    df = conn.read(worksheet=aba, ttl=0)
    
    # 1. Limpa espaços nos nomes das colunas (cabeçalho)
    df.columns = df.columns.str.strip()
    
    # 2. Tratamento para USUARIOS
    if aba == "usuarios":
        if "Usuario" in df.columns:
            df = df.dropna(subset=["Usuario"])
            df = df[df["Usuario"].astype(str).str.strip() != ""]

    # 3. Tratamento para VENDAS (Evita erro de JSON/NaN)
    if aba == "vendas":
        # Se tiver coluna Cliente, remove as linhas onde Cliente está vazio
        if "Cliente" in df.columns:
            df = df.dropna(subset=["Cliente"])
            df = df[df["Cliente"].astype(str).str.strip() != ""]
        
        # O SEGREDO: Preenche buracos vazios (NaN) com texto vazio ("")
        df = df.fillna("")
        
        # SEGURANÇA EXTRA: Converte tudo para texto
        df = df.astype(str)
            
    return df

def salvar_no_google(df, aba):
    conn = get_connection()
    conn.update(worksheet=aba, data=df)

# --- FUNÇÕES DO SISTEMA ---
def cadastrar_novo_usuario(usuario, senha, nome):
    df = carregar_dados("usuarios")
    
    # Verifica se já existe
    if not df.empty and str(usuario) in df['Usuario'].astype(str).values:
        return False, "Usuario ja existe."
    
    novo_dado = {
        "Usuario": str(usuario), 
        "Senha": str(senha), 
        "Nome": str(nome), 
        # Envia como texto para o Google Sheets virar Checkbox desmarcado
        "Aprovado": "FALSE" 
    }
    
    novo_usuario = pd.DataFrame([novo_dado])
    df_final = pd.concat([df, novo_usuario], ignore_index=True)
    
    salvar_no_google(df_final, "usuarios")
    return True, "Cadastro realizado! Aguarde a aprovacao do Admin."

def salvar_indicacao(afiliado, cliente, endereco, telefone, plano_final, obs):
    df = carregar_dados("vendas")
    novo_dado = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Afiliado": afiliado,
        "Cliente": cliente,
        "Endereco": endereco,
        "Telefone": telefone,
        "Plano": plano_final,
        "Status": "Em Analise",
        "Obs": obs
    }])
    df = pd.concat([df, novo_dado], ignore_index=True)
    salvar_no_google(df, "vendas")
    return True

def calcular_nivel(qtd_vendas_validas):
    if qtd_vendas_validas >= 40: return "💎 Diamante", 400, 100
    elif qtd_vendas_validas >= 20: return "🥇 Ouro", 200, 40
    elif qtd_vendas_validas >= 10: return "🥈 Prata", 100, 20
    elif qtd_vendas_validas >= 5: return "🥉 Bronze", 50, 10
    else: return "👶 Iniciante", 0, 5

# --- ESTADO DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = ''

# ==========================================
# TELA DE LOGIN / CADASTRO
# ==========================================
if not st.session_state['logado']:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1E90FF;'>👑 Royal Acesso</h1>", unsafe_allow_html=True)
        tab_login, tab_cadastro = st.tabs(["🔑 Entrar", "📝 Solicitar Acesso"])
        
        with tab_login:
            login_user = st.text_input("Usuario", key="login_u")
            login_pass = st.text_input("Senha", type="password", key="login_p")
            
            if st.button("ENTRAR", use_container_width=True):
                df_users = carregar_dados("usuarios")
                
                if df_users.empty:
                    st.error("Nenhum usuario cadastrado. Crie o Admin na planilha primeiro ou cadastre-se.")
                else:
                    # Converte para string para evitar erros de comparação
                    df_users['Usuario'] = df_users['Usuario'].astype(str)
                    df_users['Senha'] = df_users['Senha'].astype(str)
                    
                    user_match = df_users[(df_users['Usuario'] == login_user) & (df_users['Senha'] == login_pass)]
                    
                    if not user_match.empty:
                        valor_aprovado = user_match.iloc[0]['Aprovado']
                        
                        # --- A CHAVE MESTRA ---
                        # Aceita TRUE, 1, VERDADEIRO, etc.
                        status_str = str(valor_aprovado).strip().upper()
                        
                        if status_str in ['TRUE', '1', '1.0', 'VERDADEIRO', 'SIM']:
                            st.session_state['logado'] = True
                            st.session_state['usuario'] = login_user
                            st.session_state['nome'] = user_match.iloc[0]['Nome']
                            st.rerun()
                        else:
                            st.warning(f"🔒 Seu cadastro ainda esta em analise. (Status: {valor_aprovado})")
                    else:
                        st.error("Usuario ou senha incorretos.")

        with tab_cadastro:
            st.info("Crie sua conta.")
            new_nome = st.text_input("Nome Completo")
            new_user = st.text_input("Usuario desejado")
            new_pass = st.text_input("Senha desejada", type="password")
            
            if st.button("SOLICITAR CADASTRO", use_container_width=True):
                if new_nome and new_user and new_pass:
                    sucesso, msg = cadastrar_novo_usuario(new_user, new_pass, new_nome)
                    if sucesso: 
                        st.success(msg)
                    else: 
                        st.error(msg)
                else: 
                    st.error("Preencha tudo!")

# ==========================================
# ÁREA LOGADA
# ==========================================
else:
    usuario_atual = st.session_state['usuario']
    nome_atual = st.session_state['nome']
    
    st.sidebar.title(f"Ola, {nome_atual}!")
    if st.sidebar.button("🔄 Atualizar Dados"):
        st.cache_data.clear()
        st.rerun()
        
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
    
    df_vendas = carregar_dados("vendas")

    # --- ADMIN ---
    if usuario_atual == 'admin':
        st.title("🛠️ Painel do Chefe (Google Sheets)")
        tab_vendas, tab_users = st.tabs(["💰 Aprovar Vendas", "👥 Aprovar Usuarios"])
        
        with tab_vendas:
            st.warning("Dados carregados da Planilha Google.")
            
            # Limpeza visual para o Editor não quebrar
            df_vendas = df_vendas.fillna("") 

            df_editado = st.data_editor(
                df_vendas, 
                num_rows="dynamic",
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status", options=["Em Analise", "Agendado", "Instalado", "Cancelado"], required=True
                    )
                },
                use_container_width=True
            )
            
            if st.button("💾 Salvar Vendas na Nuvem"):
                salvar_no_google(df_editado, "vendas")
                st.success("Planilha atualizada!")
                st.cache_data.clear()

        with tab_users:
            df_users = carregar_dados("usuarios")
            
            # Limpeza visual para evitar erros
            df_users = df_users.fillna("")
            
            df_users_editado = st.data_editor(
                df_users,
                column_config={
                    "Aprovado": st.column_config.CheckboxColumn("Liberado?", default=False),
                    "Senha": st.column_config.TextColumn("Senha")
                },
                disabled=["Usuario"],
                hide_index=True,
                use_container_width=True
            )
            if st.button("💾 Salvar Liberacoes na Nuvem"):
                salvar_no_google(df_users_editado, "usuarios")
                st.success("Permissoes salvas no Google!")
                st.cache_data.clear()

    # --- AFILIADO ---
    else:
        st.title("🚀 Painel do Embaixador")
        if df_vendas.empty:
            meus_dados = pd.DataFrame()
            qtd_validas = 0
        else:
            meus_dados = df_vendas[df_vendas['Afiliado'] == usuario_atual]
            vendas_validas = meus_dados[meus_dados['Status'] == 'Instalado']
            qtd_validas = len(vendas_validas)
            
        nivel, bonus, prox_meta = calcular_nivel(qtd_validas)

        tab1, tab2, tab3 = st.tabs(["📝 Indicar", "📊 Progresso", "🏆 Metas"])
        
        with tab1:
            st.write("### Novo Contrato")
            col1, col2 = st.columns(2)
            nome = col1.text_input("Nome do Cliente")
            tel = col2.text_input("WhatsApp")
            endereco = st.text_input("Endereco Completo")
            st.divider()
            itens_selecionados = st.multiselect("Selecione Produtos:", LISTA_ITENS)
            
            qtd_cameras = 0
            if "Camera de Seguranca (Avulsa)" in itens_selecionados:
                qtd_cameras = st.number_input("Qtd. Cameras", min_value=1, value=1, step=1)
            
            obs = st.text_area("Observacoes")
            
            if st.button("✅ Enviar Indicacao", type="primary"):
                if nome and tel and endereco and itens_selecionados:
                    plano_texto = " + ".join(itens_selecionados)
                    if qtd_cameras > 0: plano_texto += f" (Total {qtd_cameras} Cameras)"
                    
                    salvar_indicacao(usuario_atual, nome, endereco, tel, plano_texto, obs)
                    st.success("Salvo no Google Sheets com sucesso!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Preencha tudo!")

        with tab2:
            col1, col2, col3 = st.columns(3)
            col1.metric("Instaladas", f"{qtd_validas}")
            col2.metric("Nivel", nivel)
            col3.metric("Bonus", f"R$ {bonus}")
            if prox_meta > 0:
                progresso = min(qtd_validas / prox_meta, 1.0)
                st.write(f"Proxima meta: **{qtd_validas}/{prox_meta}**")
                st.progress(progresso)
            st.divider()
            st.dataframe(meus_dados, use_container_width=True)

        with tab3:
             st.markdown("""
             ### ### 🎯 Metas Royal
| Nivel | Vendas (Instaladas) | Bonus |
| :--- | :--- | :--- |
| 👶 Iniciante | 0 a 4 | - |
| 🥉 Bronze | **5** a 9 | R$ 50 |
| 🥈 Prata | **10** a 19 | R$ 100 |
| 🥇 Ouro | **20** a 39 | R$ 200 |
| 💎 Diamante | **40+** | R$ 400 |
             """)