import os
import numpy as np
import pandas as pd
import streamlit as st


# Cargar los datos evitando el error FileNotFoundError
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "tank-dip-chart-hCylinder.csv")

    df = pd.read_csv(file_path, delimiter=";")

    # Función para convertir fracciones a decimales
    def parse_frac(val):
        parts = str(val).strip().split()
        if len(parts) == 2:
            num, den = parts[1].split("/")
            return float(parts[0]) + float(num) / float(den)
        elif "/" in parts[0]:
            num, den = parts[0].split("/")
            return float(num) / float(den)
        return float(parts[0])

    df["inches"] = df["Nivel (pulgadas fraccionarias)"].apply(parse_frac)
    df.rename(
        columns={"Volumen lleno (galones estadounidenses)": "gallons"},
        inplace=True,
    )
    return df


df = load_data()

st.title("🛢️ Calculadora de Tanque Cilíndrico")

modo = st.radio(
    "Dirección de cálculo:", ["Pulgadas ➔ Galones", "Galones ➔ Pulgadas"]
)
metodo = st.selectbox(
    "Método de Interpolación:",
    ["Cuadrática (Grado 2)", "Lineal", "Valor Exacto / Más Cercano"],
)

if modo == "Pulgadas ➔ Galones":
    st.subheader("Ingreso de Nivel")

    # Selección del modo de entrada (Decimal o Por Octavos)
    tipo_entrada = st.radio(
        "Formato de entrada:",
        ["Por Octavos (Entero + Fracción)", "Decimal directo (ej. 44.375)"],
        horizontal=True,
    )

    if tipo_entrada == "Por Octavos (Entero + Fracción)":
        col1, col2 = st.columns(2)
        with col1:
            pulgadas_enteras = st.number_input(
                "Pulgadas enteras:",
                min_value=0,
                max_value=98,
                value=44,
                step=1,
            )
        with col2:
            opciones_octavos = {
                '0" (0.000)': 0.0,
                '1/8" (0.125)': 0.125,
                '1/4" (0.250)': 0.25,
                '3/8" (0.375)': 0.375,
                '1/2" (0.500)': 0.5,
                '5/8" (0.625)': 0.625,
                '3/4" (0.750)': 0.75,
                '7/8" (0.875)': 0.875,
            }
            fraccion_sel = st.selectbox(
                "Octavos de pulgada:", list(opciones_octavos.keys())
            )
            val_frac = opciones_octavos[fraccion_sel]

        val_in = pulgadas_enteras + val_frac
        st.info(
            f"**Nivel total ingresado:** `{val_in}` (o `{pulgadas_enteras}"
            f" {fraccion_sel.split()[0]}`)"
        )
    else:
        val_in = st.number_input(
            "Ingrese Nivel en Pulgadas:",
            min_value=0.0,
            max_value=98.0,
            value=44.375,
            step=0.125,
        )

    # Cálculo según el método seleccionado
    if metodo == "Valor Exacto / Más Cercano":
        idx = (df["inches"] - val_in).abs().idxmin()
        res_gal = df.loc[idx, "gallons"]
    elif metodo == "Lineal":
        res_gal = np.interp(val_in, df["inches"], df["gallons"])
    else:
        # Interpolación polinómica cuadrática (3 puntos)
        idx = np.searchsorted(df["inches"], val_in) - 1
        idx = max(0, min(idx, len(df) - 3))
        sub_df = df.iloc[idx : idx + 3]
        poly = np.polyfit(sub_df["inches"], sub_df["gallons"], deg=2)
        res_gal = np.polyval(poly, val_in)

    st.success(f"🛢️ **Volumen estimado:** **{res_gal:,.2f} Galones**")

else:
    val_gal = st.number_input(
        "Ingrese Volumen en Galones:",
        min_value=0.0,
        max_value=11004.24,
        value=5000.0,
        step=10.0,
    )

    if metodo == "Valor Exacto / Más Cercano":
        idx = (df["gallons"] - val_gal).abs().idxmin()
        res_in = df.loc[idx, "inches"]
    elif metodo == "Lineal":
        res_in = np.interp(val_gal, df["gallons"], df["inches"])
    else:
        idx = np.searchsorted(df["gallons"], val_gal) - 1
        idx = max(0, min(idx, len(df) - 3))
        sub_df = df.iloc[idx : idx + 3]
        poly = np.polyfit(sub_df["gallons"], sub_df["inches"], deg=2)
        res_in = np.polyval(poly, val_gal)

    # Convertir el resultado a pulgadas enteras + octavo aproximado
    entero = int(res_in)
    resto = res_in - entero
    octavo = round(resto * 8)
    if octavo == 8:
        entero += 1
        str_frac = ""
    elif octavo == 0:
        str_frac = ""
    else:
        # Simplificar fracción
        from math import gcd

        num = octavo // gcd(octavo, 8)
        den = 8 // gcd(octavo, 8)
        str_frac = f" {num}/{den}"

    st.success(
        f'📏 **Nivel estimado:** **{res_in:.4f} Pulgadas** ({entero}{str_frac}")'
    )