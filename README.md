# Júri Simulado - Debate Retórico

Uma aplicação de simulação de júri que utiliza princípios da retórica aristotélica para conduzir debates estruturados usando múltiplos agentes de IA.

## Características

- Debate estruturado com agentes a favor e contra
- Análise baseada nos três pilares da retórica de Aristóteles (Ethos, Pathos, Logos)
- Interface intuitiva usando Streamlit
- Veredicto imparcial baseado na qualidade dos argumentos

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Copie o arquivo `.env.example` para `.env` e adicione sua chave API da OpenAI:
   ```bash
   cp .env.example .env
   ```

## Uso

1. Execute a aplicação:
   ```bash
   streamlit run src/app.py
   ```
2. Digite um tópico para debate no campo de texto
3. Clique em "Iniciar Debate"
4. Observe o desenvolvimento do debate e o veredicto final

## Estrutura do Debate

1. Argumento inicial (Agente Pró)
2. Contra-argumento (Agente Contra)
3. Réplica (Agente Pró)
4. Tréplica (Agente Contra)
5. Veredicto final (Agente Júri)

## Princípios Retóricos

- **Ethos**: Credibilidade e autoridade moral
- **Pathos**: Apelo emocional e conexão com a audiência
- **Logos**: Lógica, razão e evidências