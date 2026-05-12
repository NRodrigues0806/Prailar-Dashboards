import streamlit as st # pip install streamlit
import datetime
from streamlit_autorefresh import st_autorefresh # pip install streamlit-autorefresh
import plotly.express as px # pip install plotly / graficos mais bonitos e interativos

import etl_praialar # arquivo com as funções de limpeza dos dados, que já devolve os DataFrames prontos pra usar

# python -m streamlit run app.py pra rodar o Streamlit

# Refresh automático a cada 10min para teste
st.write(f"⏳ Última atualização da tela: {datetime.datetime.now().strftime('%H:%M:%S')}")
st.set_page_config(layout="wide", page_title="Dashboard PraiaLar")
st_autorefresh(interval=600000, key="atualizacao_painel")

st.title("📊 Dashboard Experimental - Praialar")





# BLOCO DE VISITAS
# chama a função do ETL, que já fez a limpeza e devolve o DataFrame pronto pra usar
df_visitas = etl_praialar.limpar_visitas()

st.subheader("Tabela de Visitas (12/04 até 12/05)")
st.dataframe(df_visitas) # dataframe serve pra mostrar a tabela

contagem_origem_visitas = df_visitas['Origem'].value_counts()
colunas = st.columns(6)

with colunas[0]:
    st.metric(label="Total Realizadas", value=len(df_visitas))

for i in range(min(5, len(contagem_origem_visitas))):
    nome_portal = contagem_origem_visitas.index[i]
    quantidade = contagem_origem_visitas.iloc[i]
    with colunas[i+1]:
        st.metric(label=f"{nome_portal}", value=quantidade)

st.divider()





# BLOCO DE VENDAS
# Só chama a função, o ETL já tirou a última linha e converteu pra número

df_vendasOrigem = etl_praialar.limpar_vendas()

total_vendas_calculado = int(df_vendasOrigem['Total Convertidos'].sum())

st.subheader("📊 Origem das Vendas e Conversão (12/04 até 12/05)")
st.metric(label="Total de Vendas Convertidas", value=total_vendas_calculado)

st.write("📈 Conversão por Origem:")
df_conversao = df_vendasOrigem[['Portal', 'Total recebidos', 'Total Convertidos', 'Conversão']]
st.dataframe(df_conversao, hide_index=True)

st.divider()

st.write("Distribuição de Leads por Canal:")

# Tirei 'Portal' da lista, pois ela é uma coluna de texto
canais = ['Internet', 'Showroom', 'Telefone', 'Rede social', 'Planilha', 'WhatsApp']

# Pega a soma dos canais
contagem_para_grafico = df_vendasOrigem[canais].sum()

# Filtra apenas os canais que tiveram mais de 0 leads
contagem_para_grafico = contagem_para_grafico[contagem_para_grafico > 0]

# O Plotly gosta de ler DataFrames em vez de Séries, então converti
# Plotly é bidimensional, então precisa de uma coluna pra nome do canal e outra pra quantidade. O reset_index() transforma o nome do canal em uma coluna normal, e a linha abaixo renomeia as colunas pra ficar mais fácil de usar no gráfico
df_pizza = contagem_para_grafico.reset_index()
df_pizza.columns = ['Canal', 'Quantidade']

# Cria o gráfico de Pizza (Rosca)
fig = px.pie(
    df_pizza, 
    values='Quantidade', 
    names='Canal', 
    hole=0.4 # Deixa o gráfico em formato de rosca, se quiser pizza normal é só tirar essa linha
)

# Renderiza o gráfico na tela
st.plotly_chart(fig, use_container_width=True)





# BLOCO DO RANKING
# Só chama a função 

st.subheader("🏆 Gráfico: Ranking Corretores - Imóveis ativos / vendas (12/04 até 12/05)")

df_rankingImoveis = etl_praialar.limpar_ranking()


# (ascending=True) - O gráfico desenha de baixo para cima, empurrando os maiores pro alto
df_rankingImoveis = df_rankingImoveis.sort_values(by='TOTAL DE IMÓVEIS', ascending=True)

# Cria o gráfico de barras horizontal com Plotly
fig_ranking = px.bar(
    df_rankingImoveis,
    x='TOTAL DE IMÓVEIS',
    y='CORRETOR',
    orientation='h', # 'h' avisa que é horizontal
    height=500
)

# Renderiza na tela
st.plotly_chart(fig_ranking, use_container_width=True)




# BLOCO NEGÓCIOS FECHADOS

st.divider()
st.subheader("💰 Desempenho Financeiro (Negócios Fechados - 12/04 até 12/05)")

# Chama a função do ETL
df_negocios = etl_praialar.limpar_negocios_fechados()

# Tabela das vendas
st.write("📋 Maiores Vendas do Período:")

# Seleciona as colunas e ordena
df_resumo_vendas = df_negocios[['Data de fechamento', 'Nome', 'Vendedor', 'Preço Formatado']]
df_resumo_vendas = df_resumo_vendas.sort_values(by='Preço Formatado', ascending=False)

# 2. Renomeia as colunas pra UX
df_resumo_vendas = df_resumo_vendas.rename(columns={
    "Data de fechamento": "Data de Fechamento",
    "Nome": "Cliente",
    "Vendedor": "Corretor",
    "Preço Formatado": "Valor da Venda"
})

# Criar estilização dos valores em BRL e formatação da data usando lambda pra não dar erro caso o valor não seja uma data válida (ex: célula vazia)
df_estilizado = df_resumo_vendas.style.format({
    # Formata a data (Verifica se é uma data válida antes pra não dar erro)
    "Data de Fechamento": lambda x: x.strftime("%d/%m/%Y %H:%M") if hasattr(x, 'strftime') else "", # Se for uma data, formata. Se não, deixa vazio
    
    # trocar vírgulas e pontos para BRL
    "Valor da Venda": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
})

# 4. Mostramos a tabela estilizada na tela
st.dataframe(df_estilizado, hide_index=True)