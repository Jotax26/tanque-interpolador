import math
import os
import altair as alt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="VARIGRAL | Tank Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: #0b0f19;
        color: #f8fafc;
    }
    
    #MainMenu, footer, header {visibility: hidden;}

    /* Banner Principal */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    }

    .hero-title {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }

    /* Cards Informativas */
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(12px);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #38bdf8;
        line-height: 1.1;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# Carga e Interpolación Pre-calculada
# ==========================================
@st.cache_resource
def get_interpolators():
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
    df["gallons"] = df["Volumen lleno (galones estadounidenses)"]

    f_gallons_quad = interp1d(
        df["inches"], df["gallons"], kind="quadratic", bounds_error=False, fill_value="extrapolate"
    )
    f_gallons_lin = interp1d(
        df["inches"], df["gallons"], kind="linear", bounds_error=False, fill_value="extrapolate"
    )

    f_inches_quad = interp1d(
        df["gallons"], df["inches"], kind="quadratic", bounds_error=False, fill_value="extrapolate"
    )
    f_inches_lin = interp1d(
        df["gallons"], df["inches"], kind="linear", bounds_error=False, fill_value="extrapolate"
    )

    return df, f_gallons_quad, f_gallons_lin, f_inches_quad, f_inches_lin


df, f_gal_quad, f_gal_lin, f_in_quad, f_in_lin = get_interpolators()
max_inches = float(df["inches"].max())
max_gallons = float(df["gallons"].max())

# ==========================================
# HEADER
# ==========================================
st.markdown(
    """
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="hero-title">VARIGRAL</h1>
                <p style="color: #64748b; margin: 4px 0 0 0; font-size: 0.95rem;">Sistema Avanzado de Cubaje y Análisis de Tanques</p>
            </div>
            <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 99px; padding: 6px 16px;">
                <span style="color: #38bdf8; font-size: 0.85rem; font-weight: 600;">● Online</span>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("### ⚙️ Parámetros")
modo = st.sidebar.radio("Modo de Operación:", ["Pulgadas ➔ Galones", "Galones ➔ Pulgadas"])
algoritmo = st.sidebar.selectbox("Algoritmo:", ["Cuadrático (Recomendado)", "Lineal", "Más Cercano"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📐 Capacidades")
st.sidebar.metric("Altura Máxima", f'{max_inches:.2f}"')
st.sidebar.metric("Volumen Máximo", f"{max_gallons:,.2f} Gal")

# ==========================================
# PANEL PRINCIPAL
# ==========================================
col_in, col_out = st.columns([1.1, 0.9], gap="large")

if modo == "Pulgadas ➔ Galones":
    with col_in:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 📏 Entrada de Nivel")
        fmt = st.radio("Formato:", ["Por Octavos", "Decimal Directo"], horizontal=True)

        if fmt == "Por Octavos":
            c1, c2 = st.columns(2)
            with c1:
                p_entera = st.number_input("Pulgadas:", min_value=0, max_value=int(max_inches), value=44)
            with c2:
                octavos_dict = {
                    '0"': 0.0, '1/8"': 0.125, '1/4"': 0.25, '3/8"': 0.375,
                    '1/2"': 0.5, '5/8"': 0.625, '3/4"': 0.75, '7/8"': 0.875,
                }
                p_frac_str = st.selectbox("Octavo:", list(octavos_dict.keys()), index=3)
                p_frac = octavos_dict[p_frac_str]

            val_input = float(p_entera + p_frac)
            readout = f'{p_entera} {p_frac_str}' if p_frac_str != '0"' else f'{p_entera}"'
        else:
            val_input = st.slider("Nivel (in):", 0.0, max_inches, 44.375, step=0.0625)
            readout = f'{val_input:.3f}"'
        st.markdown("</div>", unsafe_allow_html=True)

    if algoritmo == "Más Cercano":
        idx = (df["inches"] - val_input).abs().idxmin()
        res_val = float(df.loc[idx, "gallons"])
    elif algoritmo == "Lineal":
        res_val = float(f_gal_lin(val_input))
    else:
        res_val = float(f_gal_quad(val_input))

    pct_lleno = min(100.0, (val_input / max_inches) * 100)

    with col_out:
        st.markdown(
            f"""
            <div class="metric-card" style="border-color: rgba(56, 189, 248, 0.3); background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(14,165,233,0.1)); margin-bottom: 20px;">
                <div class="metric-label">Volumen Estimado</div>
                <div class="metric-value">{res_val:,.2f} <span style="font-size: 1rem; color: #94a3b8;">GAL</span></div>
                <div style="margin-top: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; font-size: 0.9rem; color: #cbd5e1;">
                    📍 Nivel Medido: <b>{readout}</b> ({val_input:.3f} in)
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="width: 150px; height: 150px; border-radius: 50%; border: 4px solid #38bdf8; position: relative; overflow: hidden; margin: 0 auto; background: rgba(15,23,42,0.8); box-shadow: 0 0 20px rgba(56,189,248,0.2);">
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: {pct_lleno}%; background: linear-gradient(180deg, rgba(56,189,248,0.8) 0%, rgba(2,132,199,0.9) 100%); transition: height 0.5s ease-in-out;"></div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 800; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                        {pct_lleno:.1f}%
                    </div>
                </div>
                <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem; font-weight: 600;">VISTA FRONTAL DEL TANQUE</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

else:
    with col_in:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("#### 🛢️ Entrada de Volumen")
        val_input = st.number_input("Volumen (Galones):", min_value=0.0, max_value=max_gallons, value=5000.0, step=50.0)
        st.markdown("</div>", unsafe_allow_html=True)

    if algoritmo == "Más Cercano":
        idx = (df["gallons"] - val_input).abs().idxmin()
        res_val = float(df.loc[idx, "inches"])
    elif algoritmo == "Lineal":
        res_val = float(f_in_lin(val_input))
    else:
        res_val = float(f_in_quad(val_input))

    entero = int(res_val)
    resto = res_val - entero
    octavo = round(resto * 8)
    if octavo == 8:
        entero += 1
        str_frac = ""
    elif octavo == 0:
        str_frac = ""
    else:
        gcd_v = math.gcd(octavo, 8)
        str_frac = f" {octavo//gcd_v}/{8//gcd_v}"

    pct_lleno = min(100.0, (val_input / max_gallons) * 100)

    with col_out:
        st.markdown(
            f"""
            <div class="metric-card" style="border-color: rgba(129, 140, 248, 0.3); background: linear-gradient(145deg, rgba(15,23,42,0.9), rgba(129,140,248,0.1)); margin-bottom: 20px;">
                <div class="metric-label">Nivel de Vara Requerido</div>
                <div class="metric-value" style="color: #818cf8;">{entero}{str_frac}"</div>
                <div style="margin-top: 15px; background: rgba(255,255,255,0.05); border-radius: 8px; padding: 10px; font-size: 0.9rem; color: #cbd5e1;">
                    📏 Valor Decimal Exacto: <b>{res_val:.4f} pulgadas</b>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="width: 150px; height: 150px; border-radius: 50%; border: 4px solid #818cf8; position: relative; overflow: hidden; margin: 0 auto; background: rgba(15,23,42,0.8); box-shadow: 0 0 20px rgba(129,140,248,0.2);">
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: {pct_lleno}%; background: linear-gradient(180deg, rgba(129,140,248,0.8) 0%, rgba(79,70,229,0.9) 100%); transition: height 0.5s ease-in-out;"></div>
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-weight: 800; font-size: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                        {pct_lleno:.1f}%
                    </div>
                </div>
                <div style="margin-top: 10px; color: #94a3b8; font-size: 0.85rem; font-weight: 600;">VISTA FRONTAL DEL TANQUE</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

# ==========================================
# HISTORIAL DE MEDICIONES
# ==========================================
st.markdown("---")
st.markdown("### 📋 Historial de Turno")

if "historial" not in st.session_state:
    st.session_state.historial = []

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("💾 Guardar Medición", use_container_width=True):
        registro = {
            "Modo": modo,
            "Nivel (Pulgadas)": round(val_input if modo == "Pulgadas ➔ Galones" else res_val, 3),
            "Volumen (Galones)": round(res_val if modo == "Pulgadas ➔ Galones" else val_input, 2),
            "Capacidad %": round(pct_lleno, 1)
        }
        st.session_state.historial.insert(0, registro)
        st.toast("✅ Registro guardado exitosamente.")

if st.session_state.historial:
    df_historial = pd.DataFrame(st.session_state.historial)
    st.dataframe(df_historial, use_container_width=True)
    
    csv_data = df_historial.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Reporte (CSV)",
        data=csv_data,
        file_name="reporte_tanque.csv",
        mime="text/csv",
    )

# ==========================================
# GRÁFICO ALTAIR
# ==========================================
st.markdown("---")
st.markdown("### 📈 Curva de Capacidad")

pt_x = val_input if modo == "Pulgadas ➔ Galones" else res_val
pt_y = res_val if modo == "Pulgadas ➔ Galones" else val_input
point_df = pd.DataFrame({"inches": [pt_x], "gallons": [pt_y]})

line_chart = (
    alt.Chart(df)
    .mark_line(color="#38bdf8", strokeWidth=3)
    .encode(
        x=alt.X("inches:Q", title="Nivel (Pulgadas)"),
        y=alt.Y("gallons:Q", title="Volumen (Galones)"),
        tooltip=[alt.Tooltip("inches:Q", format=".2f"), alt.Tooltip("gallons:Q", format=",.2f")],
    )
)

point_chart = (
    alt.Chart(point_df)
    .mark_point(color="#f43f5e", size=200, filled=True)
    .encode(x="inches:Q", y="gallons:Q")
)

chart = (line_chart + point_chart).properties(height=350).interactive()
st.altair_chart(chart, use_container_width=True)