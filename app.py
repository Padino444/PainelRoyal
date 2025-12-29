import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema Royal", page_icon="👑", layout="wide")

# --- ARQUIVOS DE DADOS ---
FILE_DB = 'dados_royal.csv'
FILE_USERS = 'usuarios.csv'

# --- LISTA DE PRODUTOS ---
# Mudei "Ponto Adicional" para "Ponto Extra" para sumir o erro de texto
LISTA_ITENS = [
    "Internet 300 MEGA",
    "Internet 500 MEGA",
    "Internet 600 MEGA",
    "Internet 800 MEGA",
    "Internet 1 GIGA",
    "TV Basico",
    "TV Full",
    "Chip 20GB",
    "Chip 25GB",
    "Chip 30GB",
    "Camera de Seguranca (Avulsa)",
    "Ponto Extra",
    "Telefone Fixo VoIP",
    "Wi-Fi 6 (Roteador Extra)",
    # COMBOS
    "Combo 1 (300MB + TV Basico)",
    "Combo 2 (500MB + Chip 20GB + TV Basico)",
    "Combo 3 (600MB + Chip 25GB + TV Basico + Wi-Fi 6)",
    "Combo 4 (800MB + Chip 30GB + TV Full + Wi-Fi 6)",
    "Combo 5 (1GB + Chip 30GB + 2 Cameras + Wi-Fi 6)"
]

# --- FUNÇÕES ---
def carregar_dados():
    if not os.path.exists(FILE_DB):
        df = pd.DataFrame(columns=["Data", "Afiliado", "Cliente", "Endereco", "Telefone", "Plano", "Status", "Obs"])
        df.to_csv(FILE_DB, index=False, encoding='utf-8-sig')
        return df
    return pd.read_csv(FILE_DB, encoding='utf-8-sig')

def carregar_usuarios():
    if not os.path.exists(FILE_USERS):
        df = pd.DataFrame([["admin", "admin123", "Admin Royal", True]], columns=["Usuario", "Senha", "Nome", "Aprovado"])
        df.to_csv(FILE_USERS, index=False, encoding='utf-8-sig')
        return df
    return pd.read_csv(FILE_USERS, encoding='utf-8-sig')

def salvar_usuarios(df):
    df.to_csv(FILE_USERS, index=False, encoding='utf-8-sig')

def cadastrar_novo_usuario(usuario, senha, nome):
    df = carregar_usuarios()
    if usuario in df['Usuario'].astype(str).values:
        return False, "Usuario ja existe."
    novo_usuario = {"Usuario": usuario, "Senha": senha, "Nome": nome, "Aprovado": False}
    df = pd.concat([df, pd.DataFrame([novo_usuario])], ignore_index=True)
    salvar_usuarios(df)
    return True, "Cadastro realizado! Aguarde a aprovacao do Admin."

def salvar_indicacao(afiliado, cliente, endereco, telefone, plano_final, obs):
    df = carregar_dados()
    novo_dado = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Afiliado": afiliado,
        "Cliente": cliente,
        "Endereco": endereco,
        "Telefone": telefone,
        "Plano": plano_final,
        "Status": "Em Analise",
        "Obs": obs
    }
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(FILE_DB, index=False, encoding='utf-8-sig')
    return True

def calcular_nivel(qtd_vendas_validas):
    if qtd_vendas_validas >= 40: return "💎 Diamante", 1000, 100
    elif qtd_vendas_validas >= 20: return "🥇 Ouro", 400, 40
    elif qtd_vendas_validas >= 10: return "🥈 Prata", 150, 20
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
                df_users = carregar_usuarios()
                df_users['Usuario'] = df_users['Usuario'].astype(str)
                df_users['Senha'] = df_users['Senha'].astype(str)
                user_match = df_users[(df_users['Usuario'] == login_user) & (df_users['Senha'] == login_pass)]
                
                if not user_match.empty:
                    esta_aprovado = user_match.iloc[0]['Aprovado']
                    if str(esta_aprovado).lower() == 'true':
                        st.session_state['logado'] = True
                        st.session_state['usuario'] = login_user
                        st.session_state['nome'] = user_match.iloc[0]['Nome']
                        st.rerun()
                    else:
                        st.warning("🔒 Seu cadastro ainda esta em analise.")
                else:
                    st.error("Usuario ou senha incorretos.")

        with tab_cadastro:
            st.info("Crie sua conta. Voce so podera entrar apos aprovacao.")
            new_nome = st.text_input("Nome Completo")
            new_user = st.text_input("Usuario desejado")
            new_pass = st.text_input("Senha desejada", type="password")
            if st.button("SOLICITAR CADASTRO", use_container_width=True):
                if new_nome and new_user and new_pass:
                    sucesso, msg = cadastrar_novo_usuario(new_user, new_pass, new_nome)
                    if sucesso: st.success(msg)
                    else: st.error(msg)
                else: st.error("Preencha tudo!")

# ==========================================
# ÁREA LOGADA
# ==========================================
else:
    usuario_atual = st.session_state['usuario']
    nome_atual = st.session_state['nome']
    
    st.sidebar.title(f"Ola, {nome_atual}!")
    if st.sidebar.button("Sair"):
        st.session_state['logado'] = False
        st.rerun()
    
    df_vendas = carregar_dados()

    # --- ADMIN ---
    if usuario_atual == 'admin':
        st.title("🛠️ Painel do Chefe")
        tab_vendas, tab_users = st.tabs(["💰 Aprovar Vendas", "👥 Aprovar Usuarios"])
        
        with tab_vendas:
            st.warning("Gerencie as comissoes aqui.")
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
            if st.button("💾 Salvar Vendas"):
                df_editado.to_csv(FILE_DB, index=False, encoding='utf-8-sig')
                st.success("Vendas atualizadas!")

        with tab_users:
            st.warning("Libere ou bloqueie o acesso dos afiliados.")
            df_users = carregar_usuarios()
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
            if st.button("💾 Salvar Liberacoes"):
                salvar_usuarios(df_users_editado)
                st.success("Permissoes atualizadas!")

    # --- AFILIADO ---
    else:
        st.title("🚀 Painel do Embaixador")
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
            st.write("### Monte o Pedido 🛒")
            
            itens_selecionados = st.multiselect(
                "Selecione o que o cliente quer (Pode marcar varios):", 
                LISTA_ITENS,
                placeholder="Clique aqui para adicionar produtos..."
            )
            
            qtd_cameras = 0
            if "Camera de Seguranca (Avulsa)" in itens_selecionados:
                st.info("📷 Voce selecionou camera avulsa. Quantas unidades?")
                qtd_cameras = st.number_input("Qtd. Cameras", min_value=1, value=1, step=1)
            
            obs = st.text_area("Observacoes")
            
            if st.button("✅ Enviar Indicacao", type="primary"):
                if nome and tel and endereco and itens_selecionados:
                    plano_texto = " + ".join(itens_selecionados)
                    
                    if qtd_cameras > 0:
                        plano_texto += f" (Total {qtd_cameras} Cameras)"
                    
                    salvar_indicacao(usuario_atual, nome, endereco, tel, plano_texto, obs)
                    st.success("Indicacao enviada com sucesso!")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Preencha Nome, Endereco e selecione pelo menos 1 produto!")

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
             ### 🎯 Metas Royal
             | Nivel | Vendas (Instaladas) | Bonus |
             | :--- | :--- | :--- |
             | 👶 Iniciante | 0 a 4 | - |
             | 🥉 Bronze | **5** a 9 | R$ 50 |
             | 🥈 Prata | **10** a 19 | R$ 100 |
             | 🥇 Ouro | **20** a 39 | R$ 200 |
             | 💎 Diamante | **40+** | R$ 400 |
             """)