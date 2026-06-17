import pandas as pd
import os
import re

# =====================================================
# CONFIGURAÇÕES
# =====================================================

arquivo_excel = "SINTEF datasheet.xlsx"

abas = [
    "Data-3mm",
    "Data-2mm",
    "Data-2mm-gas"
]

os.makedirs("resultados", exist_ok=True)

# =====================================================
# LISTA FINAL
# =====================================================

dados_finais = []

# =====================================================
# LEITURA DAS ABAS
# =====================================================

for aba in abas:

    print(f"Lendo {aba}")

    df = pd.read_excel(
        arquivo_excel,
        sheet_name=aba,
        header=None
    )

    # Dados começam na linha 11
    dados = df.iloc[11:].copy()

    dados = dados[[0,1,2,3,4,5,6]]

    dados.columns = [
        "Pred_d50",
        "Experimento",
        "Meas_d50",
        "IFT",
        "Nozzle_D",
        "Qoil",
        "Qgas"
    ]

    dados["Dataset"] = aba
    
    if aba == "Data-3mm":
      dados["Nozzle_Type"] = "3 mm"

    elif aba == "Data-2mm":
     dados["Nozzle_Type"] = "2 mm"

    elif aba == "Data-2mm-gas":
     dados["Nozzle_Type"] = "2 mm + gas"

    oil_ids = []
    tratamentos = []

    ultimo_oleo = None

    for item in dados["Experimento"]:

        texto = str(item)

        if "-" in texto and texto[:4].isdigit():

            partes = texto.split("-",1)

            ultimo_oleo = partes[0]

            oil_ids.append(ultimo_oleo)
            tratamentos.append(partes[1])

        else:

            oil_ids.append(ultimo_oleo)
            tratamentos.append(texto)

    dados["Oil_ID"] = oil_ids
    dados["Treatment"] = tratamentos

    dados_finais.append(dados)

# =====================================================
# UNIR TUDO
# =====================================================

master = pd.concat(
    dados_finais,
    ignore_index=True
)

master = master[
    [
        "Nozzle_Type",
        "Oil_ID",
        "Treatment",
        "Pred_d50",
        "Meas_d50",
        "IFT",
        "Nozzle_D",
        "Qoil",
        "Qgas"
    ]
]

# =====================================================
# LIMPEZA
# =====================================================

master = master.dropna(
    subset=["Pred_d50"],
    how="all"
)
master = master.sort_values(
    by=[
        "Nozzle_Type",
        "Oil_ID",
        "Treatment"
    ]
)
master["Oil_ID"] = pd.to_numeric(
    master["Oil_ID"],
    errors="coerce"
)

# =====================================================
# SALVAR
# =====================================================

arquivo_saida = "resultados/SINTEF_Master_Dataset.xlsx"

master.to_excel(
    arquivo_saida,
    index=False
)
with pd.ExcelWriter(
    arquivo_saida,
    engine="openpyxl"
) as writer:

    # Aba principal
    master.to_excel(
        writer,
        sheet_name="Master",
        index=False
    )

    # Filtro automático
    ws = writer.sheets["Master"]
    ws.auto_filter.ref = ws.dimensions

    # Resumo por nozzle
    resumo_nozzle = (
        master.groupby("Nozzle_Type")
        .size()
        .reset_index(name="N_Experimentos")
    )

    resumo_nozzle.to_excel(
        writer,
        sheet_name="Resumo_Nozzles",
        index=False
    )

    # Resumo dos óleos
    resumo_oleos = pd.DataFrame({
        "Oil_ID": sorted(
            master["Oil_ID"]
            .dropna()
            .unique()
        )
    })

    resumo_oleos.to_excel(
        writer,
        sheet_name="Resumo_Oleos",
        index=False
    )

    # Resumo tratamentos
    resumo_tratamentos = pd.DataFrame({
        "Treatment": sorted(
            master["Treatment"]
            .dropna()
            .unique()
        )
    })

    resumo_tratamentos.to_excel(
        writer,
        sheet_name="Resumo_Tratamentos",
        index=False
    )

print("\n")
print("="*60)
print("CONSOLIDAÇÃO FINALIZADA")
print("="*60)

print("Total de experimentos:", len(master))
print("Arquivo salvo em:")
print(arquivo_saida)