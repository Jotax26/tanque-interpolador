import os
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y TEMA FUTURISTA
# ==========================================
st.set_page_config(
    page_title="VARIGRAL | Sistema de Cubaje",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyección de CSS Personalizado (Glassmorphism & Neon UI)
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Fondo principal y gradiente dark */
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(15, 23, 42, 1) 0%, rgba(9, 14, 26, 1) 90%);
        color: #f8fafc;
    }

    /* Ocultar elementos innecesarios */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Encabezado principal personalizado */
    .header-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    
    .title-text {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.3rem;
        margin: 0;
    }

    /* Cards para la interfaz */
    .custom-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }

    /* Tarjeta de resultado principal */
    .result-card {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(99, 102, 241, 0.15) 100%);
        border: 1px solid rgba(56, 189, 248, 0.4);
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
    }

    .result-val {
        font-size: 2.8rem;
        font-weight: 800;
        color: #38bdf8;
        text-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        margin: 10px 0;
    }

    .result-sub {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Botones y Radio Buttons estilizados */
    .stRadio > label {
        color: #cbd5e1 !important;
        font-weight: 600;
    }

    /* Estilo de la Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.85);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# CARGA Y PROCESAMIENTO DE DATOS
# ==========================================
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "tank-dip-chart-hCylinder.csv")

    df = pd.read_csv(file_path, delimiter=";")

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

# ==========================================
# CABECERA Y DASHBOARD HEADER
# ==========================================
st.markdown(
    """
    <div class="header-card">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h1 class="title-text">VARIGRAL ⚡</h1>
                <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 5px;">Sistema Inteligente de Interpolación y Cubaje de Tanques</p>
            </div>
            <div style="text-align: right; background: rgba(56, 189, 248, 0.1); padding: 8px 16px; border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.3);">
                <span style="color: #38bdf8; font-weight: 600;">● Tanque Cilíndrico Horizontal</span>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# BARRA LATERAL (PARÁMETROS)
# ==========================================
st.sidebar.markdown("### ⚙️ Configuración")

modo = st.sidebar.radio(
    "Dirección del cálculo:",
    ["Pulgadas ➔ Galones", "Galones ➔ Pulgadas"],
)

metodo = st.sidebar.selectbox(
    "Algoritmo de Interpolación:",
    ["Cuadrática (Grado 2)", "Lineal", "Valor Exacto / Más Cercano"],
    help="La interpolación cuadrática ofrece la mayor precisión respetando la geometría del tanque.",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.85rem;">
        VARIGRAL v2.0 • Procesamiento en tiempo real
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# SECCIÓN PRINCIPAL
# ==========================================
col_input, col_result = st.columns([1, 1], gap="large")

if modo == "Pulgadas ➔ Galones":
    with col_input:
        st.markdown(
            '<div class="custom-card">',
            unsafe_allow_html=True,
        )
        st.markdown("### 📏 Ingreso de Nivel")

        tipo_entrada = st.radio(
            "Formato de entrada:",
            ["Por Octavos (Entero + Fracción)", "Decimal directo (ej. 44.375)"],
            horizontal=True,
        )

        if tipo_entrada == "Por Octavos (Entero + Fracción)":
            c1, c2 = st.columns(2)
            with c1:
                pulgadas_enteras = st.number_input(
                    "Pulgadas enteras:",
                    min_value=0,
                    max_value=98,
                    value=44,
                    step=1,
                )
            with c2:
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
            lbl_frac = fraccion_sel.split()[0]
            str_lectura = f'{pulgadas_enteras} {lbl_frac}"' if lbl_frac != '0"' else f'{pulgadas_enteras}"'
        else:
            val_in = st.number_input(
                "Ingrese Nivel en Pulgadas:",
                min_value=0.0,
                max_value=98.0,
                value=44.375,
                step=0.125,
            )
            str_lectura = f'{val_in}"'

        st.markdown("</div>", unsafe_allow_html=True)

    # Cálculo
    if metodo == "Valor Exacto / Más Cercano":
        idx = (df["inches"] - val_in).abs().idxmin()
        res_gal = df.loc[idx, "gallons"]
    elif metodo == "Lineal":
        res_gal = np.interp(val_in, df["inches"], df["gallons"])
    else:
        idx = np.searchsorted(df["inches"], val_in) - 1
        idx = max(0, min(idx, len(df) - 3))
        sub_df = df.iloc[idx : idx + 3]
        poly = np.polyfit(sub_df["inches"], sub_df["gallons"], deg=2)
        res_gal = np.polyval(poly, val_in)

    with col_result:
        pct_lleno = min(100.0, (val_in / df["inches"].max()) * 100)
        st.markdown(
            f"""
            <div class="result-card">
                <span style="color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Volumen Calculado</span>
                <div class="result-val">{res_gal:,.2f}</div>
                <div class="result-sub">Galones Estadounidenses</div>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #cbd5e1;">
                    <span>Nivel Ingresado: <b>{str_lectura}</b></span>
                    <span>Capacidad Tanque: <b>{pct_lleno:.1f}%</b></span>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

else:
    with col_input:
        st.markdown(
            '<div class="custom-card">',
            unsafe_allow_html=True,
        )
        st.markdown("### 🛢️ Ingreso de Volumen")
        val_gal = st.number_input(
            "Ingrese Volumen en Galones:",
            min_value=0.0,
            max_value=float(df["gallons"].max()),
            value=5000.0,
            step=50.0,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # Cálculo
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

    # Formateo a Octavos
    entero = int(res_in)
    resto = res_in - entero
    octavo = round(resto * 8)
    if octavo == 8:
        entero += 1
        str_frac = ""
    elif octavo == 0:
        str_frac = ""
    else:
        gcd_val = math.gcd(octavo, 8)
        num = octavo // gcd_val
        den = 8 // gcd_val
        str_frac = f" {num}/{den}"

    pct_lleno = min(100.0, (val_gal / df["gallons"].max()) * 100)

    with col_result:
        st.markdown(
            f"""
            <div class="result-card">
                <span style="color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Nivel Estimado</span>
                <div class="result-val">{res_in:.3f}"</div>
                <div class="result-sub">Lectura de Vara: <b>{entero}{str_frac}"</b></div>
                <hr style="border-color: rgba(255,255,255,0.1); margin: 15px 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.9rem; color: #cbd5e1;">
                    <span>Volumen: <b>{val_gal:,.2f} Gal</b></span>
                    <span>Capacidad Tanque: <b>{pct_lleno:.1f}%</b></span>
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# GRÁFICO INTERACTIVO DE CURVA DE CALIBRACIÓN
# ==========================================
st.markdown("---")
st.markdown("### 📊 Curva de Calibración del Tanque")

fig = go.Figure()

# Curva principal
fig.add_trace(
    go.Scatter(
        x=df["inches"],
        y=df["gallons"],
        mode="lines",
        name="Curva de Capacidad",
        line=dict(color="#38bdf8", width=3),
        hovertemplate="Nivel: %{x:.2f} in<br>Volumen: %{y:,.2f} Gal",
    )
)

# Marcar punto calculado en la gráfica
p_x = val_in if modo == "Pulgadas ➔ Galones" else res_in
p_y = res_gal if modo == "Pulgadas ➔ Galones" else val_gal

fig.add_trace(
    go.Scatter(
        x=[p_x],
        y=[p_y],
        mode="markers",
        name="Punto Calculado",
        marker=dict(color="#f43f5e", size=14, symbol="diamond-wide"),
        hovertemplate="SELECCIÓN<br>Nivel: %{x:.2f} in<br>Volumen: %{y:,.2f} Gal",
    )
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15, 23, 42, 0.6)",
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(
        title="Nivel (Pulgadas)",
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.1)",
    ),
    yaxis=dict(
        title="Volumen (Galones)",
        gridcolor="rgba(255, 255, 255, 0.05)",
        zerolinecolor="rgba(255, 255, 255, 0.1)",
    ),
    height=400,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
    ),
)

st.plotly_chart(fig, use_container_width=True)