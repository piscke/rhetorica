# Import required libraries
from textwrap import dedent
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import time

# Configuração da página para modo wide
st.set_page_config(layout="wide")

# Load environment variables
load_dotenv()

# Initialize session state
if 'debate_messages' not in st.session_state:
    st.session_state.debate_messages = {'Contra': [], 'Júri': [], 'A Favor': []}
if 'round_scores' not in st.session_state:
    st.session_state.round_scores = {'A Favor': [], 'Contra': []}
if 'debate_finished' not in st.session_state:
    st.session_state.debate_finished = False
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0

# Set up the Streamlit app with centered title and caption
_, title_col, _ = st.columns([1, 2, 1])
with title_col:
    st.markdown("<h1 style='text-align: center;'>Júri Simulado - Debate Retórico 🏛️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Simulação de júri baseada nos princípios retóricos de Aristóteles usando múltiplos agentes</p>", unsafe_allow_html=True)

# Get API key from environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    st.error("Por favor, configure a chave API da OpenAI no arquivo .env")
    st.stop()

# Initialize the agents
pro_agent = Agent(
    name="A Favor",
    role="Argumenta a favor do tópico usando retórica aristotélica e evidências",
    model=OpenAIChat(id="gpt-4-0125-preview", api_key=openai_api_key),
    description=dedent(
        """\
        Você é um especialista em retórica aristotélica, focado em argumentar a favor de um tópico.
        Mantenha suas respostas curtas e diretas, como em um chat.
        Use os três pilares da retórica de Aristóteles e evidências factuais:
        - Logos: Lógica, razão e evidências concretas
        - Ethos: Credibilidade baseada em fatos e fontes confiáveis
        - Pathos: Apelo emocional fundamentado em casos reais
        """
    ),
    instructions=[
        "Baseie seus argumentos em fatos e evidências verificáveis",
        "Use dados e estudos quando possível",
        "Seja conciso e direto, como em um chat",
        "Limite suas respostas a 2-3 frases",
        "Mantenha um tom profissional e factual",
        "Reconheça as limitações dos seus argumentos quando apropriado"
    ],
    add_datetime_to_instructions=True,
    markdown=True,
)

contra_agent = Agent(
    name="Contra",
    role="Argumenta contra o tópico usando retórica aristotélica e evidências",
    model=OpenAIChat(id="gpt-4-0125-preview", api_key=openai_api_key),
    description=dedent(
        """\
        Você é um especialista em retórica aristotélica, focado em argumentar contra um tópico.
        Mantenha suas respostas curtas e diretas, como em um chat.
        Use os três pilares da retórica de Aristóteles e evidências factuais:
        - Logos: Lógica, razão e evidências concretas
        - Ethos: Credibilidade baseada em fatos e fontes confiáveis
        - Pathos: Apelo emocional fundamentado em casos reais
        """
    ),
    instructions=[
        "Baseie seus argumentos em fatos e evidências verificáveis",
        "Use dados e estudos quando possível",
        "Seja conciso e direto, como em um chat",
        "Limite suas respostas a 2-3 frases",
        "Mantenha um tom profissional e factual",
        "Reconheça as limitações dos seus argumentos quando apropriado"
    ],
    add_datetime_to_instructions=True,
    markdown=True,
)

jury_agent = Agent(
    name="Júri",
    role="Analisa os argumentos com foco na busca pela verdade e validação factual",
    model=OpenAIChat(id="gpt-4-0125-preview", api_key=openai_api_key),
    team=[pro_agent, contra_agent],
    description=dedent(
        """\
        Você é um júri imparcial que analisa debates usando princípios da retórica aristotélica e método científico.
        Seu objetivo principal é a busca pela verdade, avaliando a qualidade dos argumentos com base em:
        1. Validação factual e evidências apresentadas
        2. Consistência lógica do argumento
        3. Reconhecimento de potenciais vieses
        4. Uso adequado de fontes e referências
        5. Capacidade de considerar múltiplas perspectivas

        Para cada avaliação:
        1. Analise a veracidade e fundamentação dos argumentos
        2. Identifique pontos fortes e fracos em relação à busca pela verdade
        3. Atribua notas considerando a qualidade da argumentação e seu compromisso com a verdade
        """
    ),
    instructions=[
        "Priorize a verdade e precisão factual acima da retórica pura",
        "Identifique e valorize argumentos baseados em evidências",
        "Penalize afirmações sem fundamentação ou logicamente inconsistentes",
        "Considere o contexto e a complexidade do tema",
        "Use no máximo 3 frases para justificar as notas",
        "Atribua notas de 0 a 10 para cada lado",
        "Mantenha-se imparcial e focado na busca pela verdade",
        "Formate as notas claramente: 'A Favor: X/10, Contra: Y/10'"
    ],
    add_datetime_to_instructions=True,
    markdown=True,
)

def create_typing_placeholder(container, role):
    placeholder = container.empty()
    for _ in range(3):  # Ciclo de animação
        for i in range(4):  # 0 a 3 pontos
            placeholder.markdown(f"_{role} digitando{'.' * i}_")
            time.sleep(0.2)  # Reduzido para 0.2 segundos
    placeholder.empty()

def display_messages(contra_col, jury_col, favor_col):
    # Limpar os containers antes de adicionar novas mensagens
    contra_col.empty()
    jury_col.empty()
    favor_col.empty()
    
    # Exibir todas as mensagens em ordem
    for role in ['A Favor', 'Júri', 'Contra']:
        messages = st.session_state.debate_messages[role]
        container = favor_col if role == 'A Favor' else (jury_col if role == 'Júri' else contra_col)
        
        for msg in messages:
            container.markdown(f"**{role}**\n{msg}")

def extract_scores(verdict_text):
    import re
    defense_score = 7  # default
    prosecution_score = 7  # default
    
    # Procurar por padrões como "A Favor: 8/10" ou "Contra: 7/10"
    defense_match = re.search(r"A Favor:\s*(\d+)[/\d]*", verdict_text)
    prosecution_match = re.search(r"Contra:\s*(\d+)[/\d]*", verdict_text)
    
    if defense_match:
        defense_score = int(defense_match.group(1))
    if prosecution_match:
        prosecution_score = int(prosecution_match.group(1))
    
    return defense_score, prosecution_score

def plot_scores():
    if len(st.session_state.round_scores['A Favor']) > 0:
        rounds = list(range(1, len(st.session_state.round_scores['A Favor']) + 1))
        
        # Criar o gráfico com as pontuações atualizadas
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=rounds,
            y=st.session_state.round_scores['A Favor'],
            name='A Favor',
            line=dict(color='blue', width=3),
            mode='lines+markers'
        ))
        fig.add_trace(go.Scatter(
            x=rounds,
            y=st.session_state.round_scores['Contra'],
            name='Contra',
            line=dict(color='red', width=3),
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Pontuação por Rodada',
            xaxis_title='Rodada',
            yaxis_title='Pontuação',
            yaxis=dict(range=[0, 10], tickmode='linear', dtick=1),
            xaxis=dict(tickmode='linear', dtick=1),
            showlegend=True,
            height=300,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True, clear_figure=True)

# Interface do usuário - Controles em uma linha e alinhados
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        topic = st.text_input("Digite o tópico para debate:", label_visibility="visible")
    with col2:
        max_rounds = st.slider("Rodadas:", min_value=1, max_value=5, value=2, label_visibility="visible")
    with col3:
        # Adiciona um espaço vazio para alinhar o botão com os outros elementos
        st.write("")  # Isso empurra o botão para baixo
        start_debate = st.button("Iniciar Debate")

    if start_debate:
        st.session_state.debate_messages = {'Contra': [], 'Júri': [], 'A Favor': []}
        st.session_state.round_scores = {'A Favor': [], 'Contra': []}
        st.session_state.debate_finished = False
        st.session_state.current_round = 0
        st.rerun()

# Criar colunas para o debate com proporções iguais
favor_col, jury_col, contra_col = st.columns(3)

# Adicionar títulos às colunas
with favor_col:
    st.markdown("<h3 style='text-align: center;'>A Favor 👨‍⚖️</h3>", unsafe_allow_html=True)
with jury_col:
    st.markdown("<h3 style='text-align: center;'>Júri ⚖️</h3>", unsafe_allow_html=True)
with contra_col:
    st.markdown("<h3 style='text-align: center;'>Contra 👨‍💼</h3>", unsafe_allow_html=True)

# Criar containers para cada coluna
favor_container = favor_col.container()
jury_container = jury_col.container()
contra_container = contra_col.container()

# Container para o gráfico abaixo das colunas de debate
chart_container = st.container()

if topic and not st.session_state.debate_finished:
    for round_num in range(max_rounds):
        st.session_state.current_round = round_num + 1
        
        # A Favor inicia
        create_typing_placeholder(favor_container, "A Favor")
        pro_prompt = f"Round {round_num + 1}: {'Apresente seu argumento inicial sobre' if round_num == 0 else 'Responda à última mensagem do oponente sobre'} {topic}. Seja breve e direto."
        pro_response = pro_agent.run(pro_prompt)
        st.session_state.debate_messages['A Favor'].append(pro_response.content)
        favor_container.markdown(f"**A Favor**\n{pro_response.content}")
        
        # Contra responde
        create_typing_placeholder(contra_container, "Contra")
        contra_prompt = f"Round {round_num + 1}: Responda ao argumento a favor: {pro_response.content}"
        contra_response = contra_agent.run(contra_prompt)
        st.session_state.debate_messages['Contra'].append(contra_response.content)
        contra_container.markdown(f"**Contra**\n{contra_response.content}")
        
        # Júri avalia a rodada
        create_typing_placeholder(jury_container, "Júri")
        jury_prompt = f"""Avalie brevemente a rodada {round_num + 1} com foco na busca pela verdade:

        A Favor: {pro_response.content}
        Contra: {contra_response.content}
        
        Analise:
        1. A validação factual e evidências apresentadas
        2. A consistência lógica dos argumentos
        3. O reconhecimento de vieses
        4. O uso de fontes e referências
        5. A consideração de múltiplas perspectivas

        Forneça uma avaliação concisa e atribua notas (ex: A Favor: 8/10, Contra: 7/10) baseadas na qualidade e veracidade dos argumentos."""
        
        verdict = jury_agent.run(jury_prompt)
        st.session_state.debate_messages['Júri'].append(verdict.content)
        jury_container.markdown(f"**Júri**\n{verdict.content}")
        
        # Extrair e armazenar pontuações
        defense_score, prosecution_score = extract_scores(verdict.content)
        st.session_state.round_scores['A Favor'].append(defense_score)
        st.session_state.round_scores['Contra'].append(prosecution_score)
    
    # Atualizar o gráfico apenas uma vez, após todas as rodadas
    with chart_container:
        st.empty()  # Limpa o container antes de plotar
        plot_scores()
    
    st.session_state.debate_finished = True