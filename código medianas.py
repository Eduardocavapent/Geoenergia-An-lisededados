# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. LEITURA E PREPARAÇÃO DOS DADOS


# Lembre-se do 'r' antes das aspas!
caminho_arquivo = r'C:\Users\09095340988\Desktop\Bolsa\Tabelas histogramas\distributions\3mm all experiments-4667.xlsx'
df = pd.read_excel(caminho_arquivo)

# Renomeando a primeira coluna
df.rename(columns={'Unnamed: 0': 'Tamanho_da_Gota_um'}, inplace=True)

# Extração automática do diâmetro e do óleo
nome_arquivo = os.path.basename(caminho_arquivo) 
diametro = nome_arquivo.split(' ')[0] 
tipo_oleo = nome_arquivo.split('-')[1].split('.')[0] 

# 🔥 CONVERSÃO PARA MILÍMETROS (mm) 🔥
tamanho_gota_mm = df['Tamanho_da_Gota_um'] / 1000

# Separando as colunas de tratamentos
tratamentos = df.columns[1:] 

# 2. CÁLCULO DA MEDIANA (d50) EM mm

print(f"--- Calculando Medianas (d50) para o Óleo {tipo_oleo} ({diametro}) ---")

# Dicionário para guardar os resultados
resultados_mediana = {}

for tratamento in tratamentos:
    soma_total = df[tratamento].sum()
    
    if soma_total > 0: 
        # Calcula a frequência acumulada normalizada (escala de 0 a 1)
        freq_acumulada = df[tratamento].cumsum() / soma_total
        
        # Interpolação usando os tamanhos já convertidos para mm
        mediana = np.interp(0.5, freq_acumulada, tamanho_gota_mm)
    else:
        mediana = 0
        
    resultados_mediana[tratamento] = mediana
    print(f"Tratamento {tratamento}: {mediana:.3f} mm")

# Convertendo os resultados para uma nova tabela e exportando
df_medianas = pd.DataFrame(list(resultados_mediana.items()), columns=['Tratamento', 'Mediana_d50_mm'])
nome_planilha_saida = f'Medianas_Gotas_{diametro}_oleo{tipo_oleo}.xlsx'
df_medianas.to_excel(nome_planilha_saida, index=False)

print(f"\n✅ Tabela de medianas salva com sucesso: {nome_planilha_saida}\n")


# ==========================================
# 3. GERAÇÃO DOS GRÁFICOS (LOOP AUTOMÁTICO)
# ==========================================

print("Gerando gráficos de distribuição...")

for tratamento in tratamentos:
    plt.figure(figsize=(8, 5))
    
    # Plotando os gráficos com o eixo X já em mm
    plt.fill_between(tamanho_gota_mm, df[tratamento], color='royalblue', alpha=0.4)
    plt.plot(tamanho_gota_mm, df[tratamento], color='darkblue', linewidth=2)
    
    plt.xscale('log') 
    
    # Adicionando a MEDIANA em mm no título do gráfico
    mediana_atual = resultados_mediana[tratamento]
    plt.title(f'Distribuição {diametro} - Óleo {tipo_oleo} | {tratamento} (Mediana: {mediana_atual:.3f} mm)', fontsize=13, pad=10)
    
    # Atualizando o rótulo do Eixo X para mm
    plt.xlabel('Tamanho da Gota (mm)', fontsize=12)
    plt.ylabel('Porcentagem (%)', fontsize=12)
    
    plt.grid(True, which="both", ls="--", alpha=0.5) 
    plt.tight_layout()
    
    nome_imagem = f'histograma_{diametro}_oleo{tipo_oleo}_{tratamento}'.replace('%', 'pct')
    
    plt.savefig(f'{nome_imagem}.png', dpi=300)
    plt.show()

print("Todos os gráficos foram gerados e salvos com sucesso!")