import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Embaixador Royal", page_icon="👑", layout="wide")

# --- CSS PARA DEIXAR BONITO (Personalização) ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        color: #1E90FF;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
FILE_DB = 'dados_royal.csv'

def carregar_dados():
    if not os.path.exists(FILE_DB):
        # Cria o arquivo se não existir
        df = pd.DataFrame(columns=["Data", "Afiliado", "Cliente", "Telefone", "Plano", "Status"])
        df.to_csv(FILE_DB, index=False)
        return df
    return pd.read_csv(FILE_DB)

def salvar_indicacao(afiliado, cliente, telefone, plano):
    df = carregar_dados()
    novo_dado = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Afiliado": afiliado,
        "Cliente": cliente,
        "Telefone": telefone,
        "Plano": plano,
        "Status": "Em Análise"
    }
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
    df.to_csv(FILE_DB, index=False)
    return True

def calcular_nivel(qtd_vendas):
    if qtd_vendas >= 21:
        return "💎 Diamante", 1000
    elif qtd_vendas >= 11:
        return "🥇 Ouro", 400
    elif qtd_vendas >= 5:
        return "🥈 Prata", 150
    elif qtd_vendas >= 1:
        return "🥉 Bronze", 50
    else:
        return "👶 Iniciante", 0

# --- LÓGICA DO APP ---

# Simulação de Login (Pode melhorar depois)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/6159/6159578.png", width=100)
st.sidebar.title("Área do Parceiro")
usuario_logado = st.sidebar.text_input("Seu Código/Email de Afiliado", key="login")

if usuario_logado:
    st.sidebar.success(f"Logado como: {usuario_logado}")
    
    # Carrega dados
    df = carregar_dados()
    
    # Filtra dados do usuário logado
    meus_dados = df[df['Afiliado'] == usuario_logado]
    total_indicacoes = len(meus_dados)
    
    # Gamificação
    nivel, bonus = calcular_nivel(total_indicacoes)
    
    # --- TELA PRINCIPAL ---
    st.markdown("<h1 class='main-header'>👑 Painel Embaixador Royal</h1>", unsafe_allow_html=True)
    
    # Abas
    tab1, tab2, tab3 = st.tabs(["📝 Indicar", "📊 Meu Desempenho", "🏆 Metas"])
    
    with tab1:
        st.subheader("Nova Indicação")
        with st.form("form_indicacao"):
            col1, col2 = st.columns(2)
            nome_cliente = col1.text_input("Nome do Cliente")
            tel_cliente = col2.text_input("WhatsApp do Cliente")
            plano = st.selectbox("Plano de Interesse", ["Internet 600 MEGA", "Kit Câmeras", "TV por Assinatura"])
            
            submitted = st.form_submit_button("✅ Enviar Indicação")
            if submitted:
                if nome_cliente and tel_cliente:
                    salvar_indicacao(usuario_logado, nome_cliente, tel_cliente, plano)
                    st.success(f"Sucesso! {nome_cliente} foi enviado para o time comercial.")
                    st.rerun() # Atualiza a tela
                else:
                    st.error("Preencha todos os campos!")

    with tab2:
        st.subheader(f"Olá, {usuario_logado}!")
        
        # Métricas (KPIs)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Indicações", total_indicacoes)
        col2.metric("Nível Atual", nivel)
        col3.metric("Bônus Acumulado", f"R$ {bonus},00")
        
        st.divider()
        st.write("📜 **Histórico de Indicações**")
        st.dataframe(meus_dados, use_container_width=True)

    with tab3:
        st.subheader("Escalada de Prêmios 🚀")
        st.info("O ciclo zera todo dia 01 do mês. Acelera!")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.success("🥉 **Bronze**\n\n1 a 4 indicações\n\n**+ R$ 50**")
        col2.warning("🥈 **Prata**\n\n5 a 10 indicações\n\n**+ R$ 150**")
        col3.warning("🥇 **Ouro**\n\n11 a 20 indicações\n\n**+ R$ 400**")
        col4.info("💎 **Diamante**\n\n21+ indicações\n\n**+ R$ 1.000**")
        
        # Barra de progresso para o próximo nível
        proxima_meta = 0
        if total_indicacoes < 5: proxima_meta = 5
        elif total_indicacoes < 11: proxima_meta = 11
        elif total_indicacoes < 21: proxima_meta = 21
        else: proxima_meta = 40
        
        if proxima_meta > 0:
            progresso = total_indicacoes / proxima_meta
            st.write(f"Progresso para o próximo nível: {int(progresso*100)}%")
            st.progress(progresso)

else:
    st.info("👈 Digite seu código de afiliado na barra lateral para entrar.")
    st.image("https://img.freepik.com/free-vector/affiliate-marketing-concept-illustration_114360-5858.jpg", width=400)