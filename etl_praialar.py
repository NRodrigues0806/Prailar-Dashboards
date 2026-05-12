import pandas as pd
import os
import glob # biblioteca pra procurar arquivos no computador, usando padrões de nome, tipo, etc


# FUNÇÃO DE AUTOMAÇÃO 

def pegar_arquivo_mais_recente(palavra_chave):
    # Procura na pasta 'planilhas' qualquer arquivo que tenha a palavra-chave e termine em .xlsx
    # O asterisco serve como "qualquer coisa antes" e "qualquer coisa depois"
    padrao = f"planilhas/*{palavra_chave}*.xlsx"
    arquivos_encontrados = glob.glob(padrao)
    
    # Se não achar nada, o código avisa o erro
    if not arquivos_encontrados: 
        raise FileNotFoundError(f"Erro: Nenhum arquivo com a palavra '{palavra_chave}' encontrado na pasta 'planilhas'.")
    
    # os.path.getmtime verifica a "data de modificação" do windows
    # O max() pega o arquivo com a data mais recente
    arquivo_mais_recente = max(arquivos_encontrados, key=os.path.getmtime)
    
    return arquivo_mais_recente



# FUNÇÕES DE LIMPEZA


def limpar_visitas():
    # Usa a automação no lugar do arquivo com nome fixo
    arquivo_visitas = pegar_arquivo_mais_recente("visitas") # palavra chave
    df = pd.read_excel(arquivo_visitas)
    
    # Faz a limpeza
    df = df[df['Status visita'] == 'Realizada'] # Só deixa as visitas realizadas
    df = df.drop_duplicates(subset=['ID do lead']) #subset é a coluna que ele vai olhar pra ver se tem repetido ou não
    df = df.drop(columns=['Telefone apenas dígitos', 'Email do cliente'], errors='ignore')
    
    return df

def limpar_vendas():
    # Usa a automação no lugar do arquivo com nome fixo
    arquivo_vendas = pegar_arquivo_mais_recente("sales") # palavra chave
    df = pd.read_excel(arquivo_vendas)
    
    # Faz a limpeza
    df = df.iloc[:-1] # Remove a última linha
    
    # Converte as colunas que sao numeros
    df['Total Convertidos'] = pd.to_numeric(df['Total Convertidos'], errors='coerce').fillna(0)
    df['Total recebidos'] = pd.to_numeric(df['Total recebidos'], errors='coerce').fillna(0)
    
    canais = ['Internet', 'Showroom', 'Telefone', 'Rede social', 'Planilha', 'WhatsApp'] # Removido a coluna 'Portal' por ter valores de texto que não podem virar numéricos
    for canal in canais:
        if canal in df.columns: # If de Proteção se a coluna não existir
            df[canal] = pd.to_numeric(df[canal], errors='coerce').fillna(0) 
            #coerce - coagir/forçar
            # fillna(0) - preencher com 0 os valores que não puderam ser convertidos
        
    return df

def limpar_ranking():
    # Usa a automação no lugar do arquivo com nome fixo
    arquivo_ranking = pegar_arquivo_mais_recente("ranking") # palavra chave
    df = pd.read_excel(arquivo_ranking)
    
    # Faz a limpeza
    df = df.iloc[:-1]
    
    return df


# Se rodar esse arquivo direto, ele só testa as funções
if __name__ == "__main__":
    print("Testando a limpeza dos dados...")
    
    # os Prints são apenas pra conferência do arquivo separadamente
    # Pra rodar e ver o resultado, se deu certo ou não
    teste_visitas = limpar_visitas()
    print(f"Sucesso! {len(teste_visitas)} visitas prontas para o painel.")
    
    teste_vendas = limpar_vendas()
    print(f"Sucesso! Tabela de vendas carregada com {len(teste_vendas)} origens.")