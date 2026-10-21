# Importa a biblioteca streamlit para criar a interface do sistema web
import streamlit as st
# Importa a biblioteca pandas para tratamento e estruturação das tabelas de dados
import pandas as pd
# Importa a classe de regressão logística do scikit-learn para classificação
from sklearn.linear_model import LogisticRegression
# Importa o módulo plotly express para plotar o gráfico de dispersão com facilidade
import plotly.express as px
# Importa o módulo de objetos gráficos do plotly para criar o velocímetro customizado
import plotly.graph_objects as go
# Importa a biblioteca os para manipulação de arquivos no sistema operacional
import os

# Configura o layout da página do painel Streamlit para o modo amplo
st.set_page_config(layout='wide')

# Define o título principal do painel na interface do usuário do aplicativo
st.title('Previsão de Inadimplência de Clientes')

# Verifica se o arquivo da planilha excel existe no diretório atual de execução
if not os.path.exists('inadimplencia-clientes.xlsx'):
    # Exibe uma mensagem de erro na tela caso o arquivo de dados não seja localizado
    st.error('Erro: A planilha "inadimplencia-clientes.xlsx" não foi encontrada. Certifique-se de carregar o arquivo.')
    # Interrompe a execução do script do Streamlit de maneira segura
    st.stop()

# Cria uma função cacheada para carregar os dados e treinar o classificador uma única vez
@st.cache_resource
def treinar_modelo_global():
    # Carrega a planilha excel original para um dataframe do pandas
    dados_brutos = pd.read_excel('inadimplencia-clientes.xlsx')
    # Elimina os registros duplicados da base de dados carregada
    dados_limpos = dados_brutos.drop_duplicates()
    # Elimina todas as linhas contendo valores nulos para higienizar a base
    dados_limpos = dados_limpos.dropna()
    # Armazena os nomes originais categóricos de Vínculo e Escolaridade para uso nos filtros
    dados_limpos['Vínculo_Original'] = dados_limpos['Vínculo Empregatício']
    # Salva também a categoria textual da escolaridade para mapeamento do histórico
    dados_limpos['Escolaridade_Original'] = dados_limpos['Escolaridade']
    # Mapeia a coluna Escolaridade usando escala ordinal de nível de instrução
    dados_limpos['Escolaridade'] = dados_limpos['Escolaridade'].map({'Fundamental': 1, 'Médio': 2, 'Superior': 3, 'Pós-graduação': 4})
    # Mapeia a coluna Imóvel Próprio de forma binária com zero e um
    dados_limpos['Imóvel Próprio'] = dados_limpos['Imóvel Próprio'].map({'Não': 0, 'Sim': 1})
    # Mapeia a coluna Situação de inadimplência de forma binária com zero e um
    dados_limpos['Situação'] = dados_limpos['Situação'].map({'Adimplente': 0, 'Inadimplente': 1})
    # Define o mapeamento ideal de estabilidade profissional para otimizar o modelo
    mapeamento_estabilidade = {'Servidor Público': 5, 'CLT': 4, 'Empresário': 3, 'Autônomo': 2, 'Desempregado': 1}
    # Substitui os valores de Vínculo Empregatício pelo mapeamento estruturado
    dados_limpos['Vínculo Empregatício'] = dados_limpos['Vínculo Empregatício'].map(mapeamento_estabilidade)
    # Garante a remoção de qualquer nulo residual que tenha surgido nos mapeamentos
    dados_limpos = dados_limpos.dropna()
    # Isola as variáveis preditoras X removendo identificadores e coluna alvo
    X = dados_limpos.drop(columns=['ID do Cliente', 'Situação', 'Vínculo_Original', 'Escolaridade_Original'])
    # Isola a coluna resposta Y contendo a situação real do cliente
    Y = dados_limpos['Situação']
    # Instancia o classificador de Regressão Logística com limite máximo de iterações
    modelo_lr = LogisticRegression(max_iter=1000)
    # Treina o classificador com toda a base de dados tratada global
    modelo_lr.fit(X, Y)
    # Retorna o modelo treinado, a base tratada com colunas textuais originais e as colunas de treino
    return modelo_lr, dados_limpos, X.columns

# Executa a função de treinamento global e recupera as estruturas montadas
modelo, df_limpo, colunas_preditoras = treinar_modelo_global()

# Divide a tela do aplicativo em duas colunas de proporção idêntica
coluna_esquerda, coluna_direita = st.columns(2)

# Inicia o bloco de construção dos componentes da coluna esquerda
with coluna_esquerda:
    # Define o cabeçalho para a seção de simulação dos dados cadastrais
    st.subheader('Simulador de Dados do Cliente')
    # Cria o controle numérico para coletar a idade do cliente simulado
    idade = st.number_input('Idade do Cliente', min_value=18, max_value=100, value=35)
    # Cria a caixa de seleção contendo as opções de escolaridade do cliente simulado
    escolaridade_nome = st.selectbox('Nível de Escolaridade', ['Fundamental', 'Médio', 'Superior', 'Pós-graduação'])
    # Cria a caixa de seleção contendo as categorias de vínculo do cliente simulado
    vinculo_nome = st.selectbox('Vínculo Empregatício', ['Servidor Público', 'CLT', 'Empresário', 'Autônomo', 'Desempregado'])
    # Cria o controle de entrada de renda mensal declarada em reais
    renda = st.number_input('Renda Mensal (R$)', min_value=0.0, value=5000.0, step=100.0)
    # Cria o campo de inserção do valor pretendido de empréstimo em reais
    emprestimo = st.number_input('Valor do Empréstimo (R$)', min_value=0.0, value=15000.0, step=500.0)
    # Cria o controle para coletar o valor estimado da parcela mensal
    parcela = st.number_input('Valor da Parcela (R$)', min_value=0.0, value=600.0, step=50.0)
    # Cria o controle numérico para definir o prazo de parcelamento em meses
    prazo = st.number_input('Prazo (meses)', min_value=1, max_value=360, value=24)
    # Cria a caixa de seleção para indicar a posse de imóvel residencial próprio
    imovel_nome = st.selectbox('Possui Imóvel Próprio?', ['Não', 'Sim'])
    # Cria o controle numérico para obter o tempo de relacionamento bancário
    relacionamento = st.number_input('Tempo de Relacionamento (anos)', min_value=0, max_value=50, value=5)
    # Cria o controle numérico para indicar quantidade de atrasos anteriores do cliente
    atrasos = st.number_input('Quantidade de Atrasos Anteriores', min_value=0, max_value=100, value=0)
    
    # Adiciona divisor visual para os filtros do histórico
    st.write('---')
    # Define o cabeçalho dos filtros do histórico de clientes
    st.subheader('Filtros para Gráfico do Histórico')
    # Recupera a lista de opções de vínculos exclusivos presentes na base
    opcoes_vinculo = sorted(df_limpo['Vínculo_Original'].unique())
    # Cria o filtro multisseleção de vínculo com todas as opções selecionadas por padrão
    filtro_vinculo = st.multiselect('Filtrar Vínculo Empregatício (Histórico)', opcoes_vinculo, default=opcoes_vinculo)
    # Recupera a lista de opções de escolaridades exclusivas presentes na base
    opcoes_escolaridade = ['Fundamental', 'Médio', 'Superior', 'Pós-graduação']
    # Cria o filtro multisseleção de escolaridade com todas as opções selecionadas por padrão
    filtro_escolaridade = st.multiselect('Filtrar Escolaridade (Histórico)', opcoes_escolaridade, default=opcoes_escolaridade)

# Converte a escolaridade textual selecionada no dígito ordinal correspondente
escolaridade_valor = {'Fundamental': 1, 'Médio': 2, 'Superior': 3, 'Pós-graduação': 4}[escolaridade_nome]
# Converte o vínculo de emprego textual na nota de estabilidade econômica correspondente
vinculo_valor = {'Servidor Público': 5, 'CLT': 4, 'Empresário': 3, 'Autônomo': 2, 'Desempregado': 1}[vinculo_nome]
# Converte a opção de imóvel próprio para a representação binária correspondente
imovel_valor = {'Não': 0, 'Sim': 1}[imovel_nome]

# Agrupa os valores inseridos pelo usuário em um dataframe idêntico ao treino
dados_cliente = pd.DataFrame([[idade, escolaridade_valor, vinculo_valor, renda, emprestimo, parcela, prazo, imovel_valor, relacionamento, atrasos]], columns=colunas_preditoras)

# Inicia o bloco de construção dos componentes da coluna direita
with coluna_direita:
    # Define o cabeçalho para exibição do diagnóstico em tempo real
    st.subheader('Diagnóstico de Risco em Tempo Real')
    # Executa a classificação final da situação financeira do cliente simulado
    classe_prevista = modelo.predict(dados_cliente)[0]
    # Calcula as probabilidades estimadas para cada classe do problema
    probabilidades = modelo.predict_proba(dados_cliente)[0]
    # Extrai a probabilidade percentual de inadimplência do cliente simulado
    probabilidade_inadimplencia = probabilidades[1] * 100
    # Extrai a probabilidade percentual de adimplência do cliente simulado
    probabilidade_adimplencia = probabilidades[0] * 100

    # Verifica se o modelo detectou classificação de inadimplência
    if classe_prevista == 1:
        # Exibe banner vermelho indicando situação prevista como Inadimplente
        st.error(f'SITUAÇÃO PREVISTA: Inadimplente (Probabilidade de Inadimplência: {probabilidade_inadimplencia:.2f}%)')
    else:
        # Exibe banner verde indicando situação prevista como Adimplente
        st.success(f'SITUAÇÃO PREVISTA: Adimplente (Probabilidade de Inadimplência: {probabilidade_inadimplencia:.2f}%)')

    # Cria a figura para o velocímetro utilizando Plotly
    fig_velocimetro = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probabilidade_inadimplencia,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Probabilidade de Inadimplência (%)"},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#FF4B4B" if classe_prevista == 1 else "#00F294"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0, 255, 0, 0.1)'},
                {'range': [30, 70], 'color': 'rgba(255, 255, 0, 0.1)'},
                {'range': [70, 100], 'color': 'rgba(255, 0, 0, 0.1)'}
            ]
        }
    ))
    # Define configurações de tamanho e layout do gráfico de velocímetro
    fig_velocimetro.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
    # Exibe o gráfico de velocímetro interativo na tela do aplicativo
    st.plotly_chart(fig_velocimetro, use_container_width=True)

    # Adiciona divisor visual para a seção de dispersão do histórico
    st.write('---')
    # Define o cabeçalho para o gráfico comparativo de dispersão do histórico
    st.subheader('Análise de Dispersão do Histórico de Clientes')

    # Aplica os filtros selecionados pelo usuário no dataframe limpo para plotagem histórica
    df_filtrado = df_limpo[
        (df_limpo['Vínculo_Original'].isin(filtro_vinculo)) &
        (df_limpo['Escolaridade_Original'].isin(filtro_escolaridade))
    ]

    # Verifica se as multisseleções estão vazias ou não retornaram nenhum registro histórico
    if len(filtro_vinculo) == 0 or len(filtro_escolaridade) == 0:
        # Exibe uma caixa informativa de aviso para o usuário preencher os filtros
        st.warning('Aviso: Selecione pelo menos uma opção em cada filtro do Histórico na coluna esquerda para exibir o gráfico de dispersão.')
    else:
        # Cria uma cópia temporária do histórico filtrado para aplicar formatação legível de situação
        df_plot = df_filtrado.copy()
        # Mapeia os códigos numéricos da situação de inadimplência de volta para strings visíveis
        df_plot['Situação Real'] = df_plot['Situação'].map({0: 'Adimplente', 1: 'Inadimplente'})
        
        # Cria o gráfico de dispersão com base na renda mensal e valor de parcela
        fig_dispersao = px.scatter(
            df_plot,
            x='Renda Mensal (R$)',
            y='Valor da Parcela (R$)',
            color='Situação Real',
            color_discrete_map={'Adimplente': '#0068C9', 'Inadimplente': '#FF4B4B'},
            title='Relação Renda Mensal vs Valor da Parcela',
            labels={'Renda Mensal (R$)': 'Renda Mensal (R$)', 'Valor da Parcela (R$)': 'Valor da Parcela (R$)'},
            hover_data=['Idade', 'Tempo de Relacionamento (anos)']
        )
        
        # Cria o marcador destacado em formato de estrela amarela para representar o cliente simulado atual
        fig_dispersao.add_trace(go.Scatter(
            x=[renda],
            y=[parcela],
            mode='markers',
            marker=dict(symbol='star', size=16, color='yellow', line=dict(color='black', width=1.5)),
            name='Cliente Simulado'
        ))
        
        # Configura as propriedades do layout do gráfico de dispersão interativo do Plotly
        fig_dispersao.update_layout(legend_title_text='Situação',
                                    margin=dict(l=20, r=20, t=40, b=20))
        # Renderiza o gráfico de dispersão completo e responsivo na tela
        st.plotly_chart(fig_dispersao, use_container_width=True)
