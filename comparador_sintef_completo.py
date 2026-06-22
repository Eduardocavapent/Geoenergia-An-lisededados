
# ==========================================================
# COMPARADOR COMPLETO SINTEF
# Compara o SINTEF datasheet com o Master Dataset
# ==========================================================

import pandas as pd
import numpy as np
from pathlib import Path

INPUT_DIR = Path("entrada")
OUTPUT_DIR = Path("saida")

OUTPUT_DIR.mkdir(exist_ok=True)

DATASHEET = INPUT_DIR / "SINTEF datasheet.xlsx"
MASTER = INPUT_DIR / "SINTEF_Master_Dataset.xlsx"

# ----------------------------------------------------------
# LEITURA
# ----------------------------------------------------------

xls_data = pd.ExcelFile(DATASHEET)
xls_master = pd.ExcelFile(MASTER)

print("="*80)
print("ABAS DATASHEET")
print(xls_data.sheet_names)
print("="*80)

print("ABAS MASTER")
print(xls_master.sheet_names)
print("="*80)

# ----------------------------------------------------------
# EXTRAI LINHAS EXPERIMENTAIS
# ----------------------------------------------------------

abas_exp = ["Data-3mm","Data-2mm","Data-2mm-gas"]

dados = []

for aba in abas_exp:

    df = pd.read_excel(
        DATASHEET,
        sheet_name=aba,
        header=10
    )

    df = df.dropna(how="all")

    df["Origem_Aba"] = aba

    dados.append(df)

dados = pd.concat(dados, ignore_index=True)

dados.to_excel(
    OUTPUT_DIR/"01_dados_extraidos.xlsx",
    index=False
)

print("Linhas extraídas:", len(dados))

# ----------------------------------------------------------
# MASTER
# ----------------------------------------------------------

master = pd.read_excel(
    MASTER,
    sheet_name="Master"
)

print("Linhas Master:", len(master))

# ----------------------------------------------------------
# RELATÓRIO ESTRUTURAL
# ----------------------------------------------------------

with open(
    OUTPUT_DIR/"02_relatorio_estrutura.txt",
    "w",
    encoding="utf-8"
) as arq:

    arq.write("ESTRUTURA DATASHEET\n")
    arq.write("="*80 + "\n")

    for c in dados.columns:
        arq.write(str(c) + "\n")

    arq.write("\n\n")

    arq.write("ESTRUTURA MASTER\n")
    arq.write("="*80 + "\n")

    for c in master.columns:
        arq.write(str(c) + "\n")

# ----------------------------------------------------------
# ESTATÍSTICAS
# ----------------------------------------------------------

stats = []

for col in master.columns:

    if pd.api.types.is_numeric_dtype(master[col]):

        stats.append([
            col,
            master[col].count(),
            master[col].mean(),
            master[col].std(),
            master[col].min(),
            master[col].max()
        ])

stats = pd.DataFrame(
    stats,
    columns=[
        "Coluna",
        "N",
        "Media",
        "Std",
        "Min",
        "Max"
    ]
)

stats.to_excel(
    OUTPUT_DIR/"03_estatisticas_master.xlsx",
    index=False
)

# ----------------------------------------------------------
# DUPLICADOS
# ----------------------------------------------------------

dup = master[master.duplicated()]

dup.to_excel(
    OUTPUT_DIR/"04_duplicados.xlsx",
    index=False
)

# ----------------------------------------------------------
# NULOS
# ----------------------------------------------------------

nulos = pd.DataFrame({
    "Coluna": master.columns,
    "Nulos": master.isnull().sum().values,
    "Percentual": (
        master.isnull().sum().values
        / len(master)
    ) * 100
})

nulos.to_excel(
    OUTPUT_DIR/"05_nulos.xlsx",
    index=False
)

# ----------------------------------------------------------
# TIPOS
# ----------------------------------------------------------

tipos = pd.DataFrame({
    "Coluna": master.columns,
    "Tipo": master.dtypes.astype(str).values
})

tipos.to_excel(
    OUTPUT_DIR/"06_tipos.xlsx",
    index=False
)

# ----------------------------------------------------------
# CONSISTÊNCIA NUMÉRICA
# ----------------------------------------------------------

anomalias = []

for col in master.columns:

    if pd.api.types.is_numeric_dtype(master[col]):

        media = master[col].mean()
        std = master[col].std()

        lim_inf = media - 3*std
        lim_sup = media + 3*std

        fora = master[
            (master[col] < lim_inf)
            |
            (master[col] > lim_sup)
        ]

        for idx in fora.index:

            anomalias.append([
                idx,
                col,
                master.loc[idx,col],
                lim_inf,
                lim_sup
            ])

anomalias = pd.DataFrame(
    anomalias,
    columns=[
        "Linha",
        "Coluna",
        "Valor",
        "Limite_Inferior",
        "Limite_Superior"
    ]
)

anomalias.to_excel(
    OUTPUT_DIR/"07_anomalias.xlsx",
    index=False
)

# ----------------------------------------------------------
# RESUMO FINAL
# ----------------------------------------------------------

with open(
    OUTPUT_DIR/"08_resumo_final.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write("RESUMO GERAL\n")
    f.write("="*80 + "\n")

    f.write(f"Experimentos extraídos: {len(dados)}\n")
    f.write(f"Experimentos master: {len(master)}\n")
    f.write(f"Duplicados: {len(dup)}\n")
    f.write(f"Anomalias: {len(anomalias)}\n")

print("\\nANÁLISE CONCLUÍDA")
print("Resultados em ./saida")
