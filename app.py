import streamlit as st # pip install streamlit
import datetime # biblioteca usada pra mostrar a hora da última atualização do painel
from streamlit_autorefresh import st_autorefresh # pip install streamlit-autorefresh
import plotly.express as px # pip install plotly / graficos mais bonitos e interativos

import etl_praialar # arquivo com as funções de limpeza dos dados, que já devolve os 
# DataFrames prontos pra usar

# python -m streamlit run app.py pra rodar o Streamlit

# SISTEMA DE LOGIN

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Se não tiver autenticado, mostra a tela de login e para o resto do código
if not st.session_state.autenticado:
    st.markdown("### 🔒 Acesso Restrito - PraiaLar Dashboards")
    senha_digitada = st.text_input("Digite a senha de acesso:", type="password")
    
    if st.button("Entrar"):
        # comparar com a senha no cofre do Streamlit
        if senha_digitada == st.secrets["SENHA_DO_PAINEL"]:
            st.session_state.autenticado = True
            st.rerun() # Recarrega a página liberando o painel
        else:
            st.error("Senha incorreta. Tente novamente.")
            
    st.stop() # O st.stop() impede que o Python leia o resto do código abaixo


# Refresh automático a cada 10min para teste
st.write(f"⏳ Última atualização da tela: {datetime.datetime.now().strftime('%H:%M:%S')}")
st.set_page_config(layout="wide", page_title="Dashboard PraiaLar")
st_autorefresh(interval=600000, key="atualizacao_painel")

st.title("📊 Dashboard - Praialar") # Como se fosse o H1 do HTML





# BLOCO DE VISITAS
# chama a função do ETL, que já fez a limpeza e devolve o DataFrame pronto pra usar
df_visitas = etl_praialar.limpar_visitas()

st.subheader("Tabela de Visitas (12/04 até 12/05)") # subheader é tipo um título menor 
# pra separar os blocos
st.dataframe(df_visitas) # dataframe serve pra mostrar a tabela

contagem_origem_visitas = df_visitas['Origem'].value_counts() # value_counts() conta 
#quantas vezes cada valor aparece na coluna 'Origem', 
# devolvendo uma Série onde o índice é a origem e o valor é a contagem

# Criar as colunas pro layout dos KPIs
colunas = st.columns(6)

# O primeiro KPI é o total de visitas realizadas, que é o número 
# de linhas do DataFrame (len(df_visitas))
with colunas[0]:
    st.metric(label="Total Realizadas", value=len(df_visitas))

# Os próximos KPIs são as 5 origens mais comuns, que a gente pega do value_counts() 
# e mostra usando um loop pra não precisar repetir o código 5 vezes
# O loop vai de 0 a 4 (min(5, len(contagem_origem_visitas)) garante que se tiver 
# menos de 5 origens, o loop só vai até o número de origens disponíveis)
for i in range(min(5, len(contagem_origem_visitas))):
    nome_portal = contagem_origem_visitas.index[i]
    quantidade = contagem_origem_visitas.iloc[i]
    with colunas[i+1]:
        st.metric(label=f"{nome_portal}", value=quantidade)

st.divider() # linha divisória pra separar os blocos, visual mais organizado





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

# O Plotly é melhor para ler DataFrames em vez de Séries, então converti
# Plotly é bidimensional, então precisa de uma coluna pra nome do canal e 
# outra pra quantidade 
# O reset_index() transforma o nome do canal em uma coluna normal, e a linha 
# abaixo renomeia as colunas pra ficar mais fácil de usar no gráfico
df_pizza = contagem_para_grafico.reset_index()
df_pizza.columns = ['Canal', 'Quantidade']

# Cria o gráfico de Pizza (Rosca)
fig = px.pie(
    df_pizza, 
    values='Quantidade', 
    names='Canal', 
    hole=0.4 # Deixa o gráfico em formato de rosca, se quiser pizza 
    # normal é só tirar essa linha
)

# Renderiza o gráfico na tela
st.plotly_chart(fig, use_container_width=True) # use_container_width=True faz o gráfico usar toda a largura disponível, deixando mais bonito e responsivo em telas menores





# BLOCO DO RANKING
# Só chama a função 

st.subheader("🏆 Gráfico: Ranking Corretores - Imóveis ativos / vendas (12/04 até 12/05)")

df_rankingImoveis = etl_praialar.limpar_ranking()


# (ascending=True) - O gráfico desenha de baixo para cima, empurrando os maiores pro alto
df_rankingImoveis = df_rankingImoveis.sort_values(by='TOTAL DE IMÓVEIS', ascending=True)

# Cria o gráfico de barras horizontal com Plotly
fig_ranking = px.bar(
    df_rankingImoveis,
    x='TOTAL DE IMÓVEIS', # x fica na horizontal, y na vertical
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

# Criar estilização dos valores em BRL e formatação da data usando lambda pra não dar 
# erro caso o valor não seja uma data válida (ex: célula vazia)
df_estilizado = df_resumo_vendas.style.format({
    # Formata a data (Verifica se é uma data válida antes pra não dar erro)
    # hasattr = has attribute - verifica se o objeto tem um atributo específico, 
    # no caso o método strftime que é usado pra formatar datas
    # Se tiver, formata a data 
    # Se não tiver (ex: valor vazio ou inválido), deixa a célula vazia

    "Data de Fechamento": lambda x: x.strftime("%d/%m/%Y %H:%M") if hasattr(x, 'strftime') else "", # Se for uma data, formata. Se não, deixa vazio
    
    "Valor da Venda": lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") 
    # Formata o número com 2 casas decimais
    # troca os pontos pelos temporários "X", depois troca as vírgulas por pontos 
    # e os "X" por vírgulas, pra ficar no formato brasileiro de moeda
})

# 4. Mostramos a tabela estilizada na tela
st.dataframe(df_estilizado, hide_index=True) #hide_index=True esconde a coluna do índice, 
# deixando só as colunas que a gente quer mostrar pra ficar mais limpo