import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px # type: ignore

# Definir as configurações da página
# Definir o título e o ícone da página
set_page_config = st.set_page_config(
    page_title="Dashbord de salários na Área de Dados",
    page_icon="🦝",
    layout="wide"
)

# Carregar os dados
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# Barra lateral (Filtros)
st.sidebar.header("🔍 Filtros")

# Filtro por ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

# Filtro por senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect('Nível de Senioridade', senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect('Tipo de Contrato', contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect('Tamanho da Empresa', tamanhos_disponiveis, default=tamanhos_disponiveis)

# Aplicar os filtros
# O dataframe é filtrado com base nas seleções feitas na barra lateral
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# Conteudo principal
st.title('🦝 Dashboard de Análise de Salários na Área de Dados')
st.markdown('Este dashboard permite analisar os salários na área de dados com base em diferentes filtros, como ano, nível de senioridade, tipo de contrato e tamanho da empresa.')

#Metricas principais
st.subheader('📊 Métricas Principais (Salário em USD)')

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    carga_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, carga_mais_frequente = 0, 0 , 0, ''

col1, col2, col3, col4 = st.columns(4)
col1.metric('Salário Médio', f'${salario_medio:,.0f}')
col2.metric('Salário Máximo', f'${salario_maximo:,.0f}')
col3.metric('Total de Registros', f'{total_registros:,}')
col4.metric('Carga Mais Frequente', carga_mais_frequente)

st.markdown('---')

# Análise visual com o Plotly
st.subheader('📈 Gráficos')

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
        top_cargos,
        x='usd',
        y='cargo',
        orientation='h',
        title='Top 10 Cargos por Média Salarial',
        labels={'usd': 'Média Salarial atual (USD)', 'cargo':''}    
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning('Nenhum dado disponível para exibir o gráfico de cargos.')

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição de Salários Anuais',
            labels={'usd': 'Faixa Salarial (USD)', 'count': ''}   
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning('Nenhum dado disponível para exibir o gráfico de distribuição.')

col_graft3, col_graf4 = st.columns(2)

with col_graft3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção de tipos de Trabalho',
            hole= 0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning('Nenhum dado disponível para exibir o gráfico de tipos de trabalho.')

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Média Salarial de Data Scientists por País',
            labels={'usd': 'Média Salarial (USD)', 'residencia_iso3': 'País'})
        st.plotly_chart(grafico_paises, use_container_width=True)                             
    else:
        st.warning('Nenhum dado disponível para exibir o mapa salarial.')

# Tabela de Dados Detalhados
st.subheader('📋 Tabela de Dados Detalhados')
st.dataframe(df_filtrado)