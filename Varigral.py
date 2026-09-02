import io
import math
import os
from datetime import datetime
import altair as alt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import streamlit as st
from supabase import create_client

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="VARIGRAL | Cloud Tank & Fleet System",
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

    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 24px 32px;
        margin-bottom: 24px;
    }

    .hero-title {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0;
    }

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
        margin-bottom: 6px;
    }

    .metric-sub {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 6px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# CONEXIÓN A SUPABASE Y DATOS INICIALES
# ==========================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

INITIAL_EQUIPOS = [
    {"UNIDAD": "A01", "PLACA": "C-125657", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A02", "PLACA": "C-125502", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A03", "PLACA": "C-125609", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A04", "PLACA": "C-125518", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A05", "PLACA": "C-125603", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A06", "PLACA": "C-125721", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A07", "PLACA": "C-125602", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A08", "PLACA": "C-125517", "AÑO": 2013, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A09", "PLACA": "C-125736", "AÑO": 2015, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A10", "PLACA": "C-125501", "AÑO": 2015, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A11", "PLACA": "C-66703", "AÑO": 2015, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A12", "PLACA": "C-125742", "AÑO": 2015, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A13", "PLACA": "C-125611", "AÑO": 2016, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A14", "PLACA": "C-125720", "AÑO": 2016, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A15", "PLACA": "C-125610", "AÑO": 2016, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A16", "PLACA": "C-96846", "AÑO": 2016, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A17", "PLACA": "C-118541", "AÑO": 2012, "MARCA": "FREIGHTLINER"},
    {"UNIDAD": "A18", "PLACA": "C-125745", "AÑO": 2014, "MARCA": "FREIGHTLINER"},
    {"UNIDAD": "A19", "PLACA": "C-119147", "AÑO": 2012, "MARCA": "INTERNATIONAL"},
    {"UNIDAD": "A20", "PLACA": "C-144118", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "A21", "PLACA": "C-144119", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C06", "PLACA": "C-117153", "AÑO": 2013, "MARCA": "FREIGHTLINER CASCADIA"},
    {"UNIDAD": "C07", "PLACA": "C-117060", "AÑO": 2013, "MARCA": "FREIGHTLINER CASCADIA"},
    {"UNIDAD": "C08", "PLACA": "C-116995", "AÑO": 2013, "MARCA": "FREIGHTLINER CASCADIA"},
    {"UNIDAD": "C09", "PLACA": "C-119375", "AÑO": 2012, "MARCA": "FREIGHTLINER BLANCO"},
    {"UNIDAD": "C10", "PLACA": "C-143355", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C11", "PLACA": "C-143356", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C12", "PLACA": "C-143359", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C13", "PLACA": "C-143358", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C14", "PLACA": "C-143357", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C15", "PLACA": "C-143412", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C16", "PLACA": "C-143410", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "C17", "PLACA": "C-143411", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "E03", "PLACA": "CAT0324DCDFP00969", "AÑO": 2011, "MARCA": "CAT 324DL"},
    {"UNIDAD": "E04", "PLACA": "HHKHZ810HE0001476", "AÑO": 2016, "MARCA": "HYUNDAI ROBEX 300LC-9S"},
    {"UNIDAD": "E05", "PLACA": "HHKHZ810HE0001487", "AÑO": 2016, "MARCA": "HYUNDAI ROBEX 300LC-9S"},
    {"UNIDAD": "G01", "PLACA": "RE-1658", "AÑO": 2014, "MARCA": "CARMEX"},
    {"UNIDAD": "G03", "PLACA": "RE-10491", "AÑO": 2014, "MARCA": "CARMEX"},
    {"UNIDAD": "G05", "PLACA": "RE-10482", "AÑO": 2016, "MARCA": "CARMEX"},
    {"UNIDAD": "L01", "PLACA": "P-597222", "AÑO": 2008, "MARCA": "MAZDA BT-50"},
    {"UNIDAD": "L02", "PLACA": "P-339962", "AÑO": 2008, "MARCA": "NISSAN FRONTIER LCV"},
    {"UNIDAD": "M01", "PLACA": "P-199D3", "AÑO": 2011, "MARCA": "MERCEDES L0015/48"},
    {"UNIDAD": "MB01", "PLACA": "P-920975", "AÑO": 2019, "MARCA": "HYUNDAI COUNTY"},
    {"UNIDAD": "MB02", "PLACA": "P-11D28", "AÑO": 2019, "MARCA": "HYUNDAI COUNTY"},
    {"UNIDAD": "MOTO", "PLACA": "M-359043", "AÑO": 2016, "MARCA": "MOTO SUZUKI"},
    {"UNIDAD": "P01", "PLACA": "P-843791", "AÑO": 2019, "MARCA": "KIA K2700"},
    {"UNIDAD": "P02", "PLACA": "C-65671", "AÑO": 2015, "MARCA": "INTERNATIONAL 7600"},
    {"UNIDAD": "P03", "PLACA": "P-697022", "AÑO": 2016, "MARCA": "HYUNDAI H-100"},
    {"UNIDAD": "PL01", "PLACA": "RE-20889", "AÑO": 2007, "MARCA": "FONTAIN"},
    {"UNIDAD": "PL02", "PLACA": "RE-22070", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL03", "PLACA": "RE-22071", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL04", "PLACA": "RE-22074", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL05", "PLACA": "RE-22116", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL06", "PLACA": "RE-22118", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL07", "PLACA": "RE-22119", "AÑO": 2025, "MARCA": "SINOTRUCK"},
    {"UNIDAD": "PL08", "PLACA": "RE-22150", "AÑO": 2025, "MARCA": "SINOTRUCK"}
]

# CRUD Supabase con Manejo de Excepciones
def obtener_equipos():
    try:
        res = supabase.table("equipos").select("*").execute()
        df = pd.DataFrame(res.data)
        if df.empty:
            supabase.table("equipos").upsert(INITIAL_EQUIPOS, on_conflict="UNIDAD").execute()
            res = supabase.table("equipos").select("*").execute()
            df = pd.DataFrame(res.data)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Supabase (equipos): {e}")
        return pd.DataFrame(INITIAL_EQUIPOS)

def obtener_fuleos():
    try:
        res = supabase.table("fuleos").select("*").order("created_at", desc=True).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"⚠️ Error al conectar con Supabase (fuleos): {e}")
        return pd.DataFrame()

def guardar_fuleo(datos):
    try:
        supabase.table("fuleos").insert(datos).execute()
    except Exception as e:
        st.error(f"Error al guardar fuleo: {e}")

def agregar_equipo(datos):
    try:
        supabase.table("equipos").insert(datos).execute()
    except Exception as e:
        st.error(f"Error al agregar equipo: {e}")

def eliminar_equipo(unidad):
    try:
        supabase.table("equipos").delete().eq("UNIDAD", unidad).execute()
    except Exception as e:
        st.error(f"Error al eliminar equipo: {e}")

# ==========================================
# INTERPOLACIÓN Y TABLA DE CUBAJE
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

    f_gallons_quad = interp1d(df["inches"], df["gallons"], kind="quadratic", bounds_error=False, fill_value="extrapolate")
    f_inches_quad = interp1d(df["gallons"], df["inches"], kind="quadratic", bounds_error=False, fill_value="extrapolate")
    return df, f_gallons_quad, f_inches_quad

df_tanque, f_gal_quad, f_in_quad = get_interpolators()
max_inches = float(df_tanque["inches"].max())
max_gallons = float(df_tanque["gallons"].max())

# Cargar Equipos desde Supabase
df_equipos = obtener_equipos()

# Diccionario de Fracciones Exclusivo en Octavos
FRACCIONES_OCTAVOS = {
    "0 (Exacto)": 0.0,
    "1/8": 1 / 8,
    "1/4 (2/8)": 2 / 8,
    "3/8": 3 / 8,
    "1/2 (4/8)": 4 / 8,
    "5/8": 5 / 8,
    "3/4 (6/8)": 6 / 8,
    "7/8": 7 / 8
}

# ==========================================
# HEADER
# ==========================================
st.markdown(
    """
    <div class="hero-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="hero-title">VARIGRAL</h1>
                <p style="color: #64748b; margin: 4px 0 0 0; font-size: 0.95rem;">Sistema Integrado de Cubaje, Fuleos y Flota en Supabase</p>
            </div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["📏 Cubaje de Tanque", "⛽ Registrar Fuleo (Nube)", "🚛 Gestión de Flota"])

# ==========================================
# PESTAÑA 1: CUBAJE (ENTRADA DIRECTA SIN SLIDERS)
# ==========================================
with tab1:
    modo = st.radio(
        "Modo de Operación:",
        ["Pulgadas ➔ Galones", "Galones ➔ Pulgadas"],
        horizontal=True,
        key="modo_cubaje_design"
    )

    st.markdown("---")
    col_inputs, col_results = st.columns([1.1, 0.9], gap="large")

    if modo == "Pulgadas ➔ Galones":
        with col_inputs:
            st.markdown("### 📐 Ingresar Medición de la Varilla")

            col_ent, col_frac = st.columns(2)
            with col_ent:
                pulgadas_enteras = st.number_input(
                    "Pulgadas Enteras:",
                    min_value=0,
                    max_value=int(max_inches),
                    value=44,
                    step=1,
                    key="pulgadas_enteras_inp"
                )
            with col_frac:
                frac_str = st.selectbox(
                    "Fracción (Octavos):",
                    list(FRACCIONES_OCTAVOS.keys()),
                    index=3, # Por defecto 3/8
                    key="fraccion_inp"
                )

            # Suma de la medición exacta ingresada
            nivel_final_in = pulgadas_enteras + FRACCIONES_OCTAVOS[frac_str]

            galones_calc = float(f_gal_quad(nivel_final_in))
            porcentaje = (galones_calc / max_gallons) * 100

        with col_results:
            st.markdown("### 📊 Resultado de Cubaje")

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Lectura Ingresada</div>
                    <div class="metric-value" style="color: #818cf8;">{nivel_final_in:.3f}"</div>
                    <div class="metric-sub">{pulgadas_enteras} in + {frac_str}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Volumen Disponible Calculado</div>
                    <div class="metric-value">{galones_calc:,.2f} GAL</div>
                    <div class="metric-sub">Ocupación del Tanque: {porcentaje:.1f}% ({max_gallons:,.0f} GAL Total)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Espacio Vacío (Ullage)</div>
                    <div class="metric-value" style="color: #f43f5e;">{max_gallons - galones_calc:,.2f} GAL</div>
                    <div class="metric-sub">Faltante para llenar: {max_inches - nivel_final_in:.3f}"</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Gráfica interactiva de nivel
        st.markdown("---")
        st.markdown("#### 📈 Nivel del Tanque en Tiempo Real")
        df_chart = df_tanque.copy()
        chart = alt.Chart(df_chart).mark_line(color="#38bdf8", strokeWidth=2).encode(
            x=alt.X("inches:Q", title="Nivel (Pulgadas)"),
            y=alt.Y("gallons:Q", title="Volumen (Galones)"),
            tooltip=["inches", "gallons"]
        )

        pt = pd.DataFrame([{"inches": nivel_final_in, "gallons": galones_calc}])
        point_chart = alt.Chart(pt).mark_point(color="#f43f5e", size=130, filled=True).encode(
            x="inches:Q",
            y="gallons:Q",
            tooltip=["inches", "gallons"]
        )

        st.altair_chart((chart + point_chart).properties(width="container", height=280), use_container_width=True)

    else:
        # Modo Galones -> Pulgadas
        with col_inputs:
            st.markdown("### 🛢️ Ingresar Galones Objetivo")
            
            galones_final = st.number_input(
                "Cantidad de Galones:",
                min_value=0.0,
                max_value=max_gallons,
                value=5000.0,
                step=10.0,
                format="%.2f",
                key="num_galones_directo"
            )

            inches_calc = float(f_in_quad(galones_final))
            porcentaje = (galones_final / max_gallons) * 100

            # Desglose de pulgadas calculadas expresadas en OCTAVOS
            pulg_int = int(inches_calc)
            pulg_dec = inches_calc - pulg_int
            frac_8 = round(pulg_dec * 8)
            frac_texto = f"{pulg_int} in" if frac_8 == 0 else f"{pulg_int} {frac_8}/8 in"

        with col_results:
            st.markdown("### 📊 Resultado de Nivel Requerido")

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Nivel de Regla Requerido</div>
                    <div class="metric-value" style="color: #818cf8;">{inches_calc:.3f}"</div>
                    <div class="metric-sub">Aproximado en Octavos: {frac_texto}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Volumen Solicitado</div>
                    <div class="metric-value">{galones_final:,.2f} GAL</div>
                    <div class="metric-sub">Porcentaje de Capacidad: {porcentaje:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Gráfica interactiva de curva
        st.markdown("---")
        st.markdown("#### 📈 Nivel del Tanque en Tiempo Real")
        df_chart = df_tanque.copy()
        chart = alt.Chart(df_chart).mark_line(color="#818cf8", strokeWidth=2).encode(
            x=alt.X("inches:Q", title="Nivel (Pulgadas)"),
            y=alt.Y("gallons:Q", title="Volumen (Galones)"),
            tooltip=["inches", "gallons"]
        )

        pt = pd.DataFrame([{"inches": inches_calc, "gallons": galones_final}])
        point_chart = alt.Chart(pt).mark_point(color="#f43f5e", size=130, filled=True).encode(
            x="inches:Q",
            y="gallons:Q",
            tooltip=["inches", "gallons"]
        )

        st.altair_chart((chart + point_chart).properties(width="container", height=280), use_container_width=True)

# ==========================================
# PESTAÑA 2: REGISTRO DE FULEO EN SUPABASE
# ==========================================
with tab2:
    st.markdown("### 🛢️ Registrar Dispensación de Combustible")
    unidades_opts = df_equipos["UNIDAD"].tolist() if not df_equipos.empty else []

    with st.form("form_fuleo_supabase"):
        c1, c2, c3 = st.columns(3)
        with c1:
            unidad_sel = st.selectbox("Unidad:", unidades_opts, key="fuleo_unidad")
            bomba = st.selectbox("Bomba:", ["Bomba Negra", "Bomba Verde"], key="fuleo_bomba")

        with c2:
            val_inicial = st.number_input("Contador Inicial (Gal):", min_value=0.0, step=0.1, format="%.2f", key="fuleo_init")
            val_final = st.number_input("Contador Final (Gal):", min_value=0.0, step=0.1, format="%.2f", key="fuleo_fin")

        with c3:
            operador = st.text_input("Operador/Despachador:", key="fuleo_op")
            despachado = max(0.0, val_final - val_inicial)
            st.text(f"Galones Aprox: {despachado:,.2f} Gal")

        submitted = st.form_submit_button("💾 Guardar Fuleo en Supabase", use_container_width=True)

    if submitted:
        if val_final <= val_inicial:
            st.error("Error: El contador final debe ser mayor que el inicial.")
        elif not unidad_sel:
            st.error("Error: Debe seleccionar una unidad.")
        else:
            eq_row = df_equipos[df_equipos["UNIDAD"] == unidad_sel].iloc[0]
            registro = {
                "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "unidad": unidad_sel,
                "placa": str(eq_row["PLACA"]),
                "marca": str(eq_row["MARCA"]),
                "bomba": bomba,
                "contador_inicial": float(val_inicial),
                "contador_final": float(val_final),
                "galones_dispensados": round(float(despachado), 2),
                "operador": operador,
            }
            guardar_fuleo(registro)
            st.success(f"✅ Fuleo guardado exitosamente para {unidad_sel} ({despachado:.2f} Gal).")

    st.markdown("---")
    st.markdown("### 📊 Registros Guardados en Supabase")
    df_fuleos = obtener_fuleos()
    if not df_fuleos.empty:
        st.dataframe(df_fuleos, use_container_width=True)
        buffer_fuleo = io.BytesIO()
        with pd.ExcelWriter(buffer_fuleo, engine="openpyxl") as writer:
            df_fuleos.to_excel(writer, index=False, sheet_name="Fuleos_Supabase")

        st.download_button(
            label="📊 Descargar Reporte en Excel (.xlsx)",
            data=buffer_fuleo.getvalue(),
            file_name=f"historial_fuleos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_down_fuleos"
        )
    else:
        st.info("No hay registros de fuleo en la base de datos.")

# ==========================================
# PESTAÑA 3: FLOTA EN SUPABASE
# ==========================================
with tab3:
    st.markdown("### 🚛 Base de Datos de Equipos (Supabase)")
    col_add, col_del = st.columns(2, gap="large")

    with col_add:
        st.markdown("#### ➕ Agregar Nuevo Equipo")
        with st.form("form_add_eq"):
            nueva_unidad = st.text_input("Unidad / Código (Ej. A22):", key="add_u").strip().upper()
            nueva_placa = st.text_input("Placa (Ej. C-145000):", key="add_p").strip().upper()
            nuevo_ano = st.number_input("Año:", min_value=1990, max_value=2030, value=2025, key="add_a")
            nueva_marca = st.text_input("Marca / Modelo (Ej. FREIGHTLINER):", key="add_m").strip().upper()
            btn_add = st.form_submit_button("➕ Guardar en Supabase")

        if btn_add:
            if not nueva_unidad or not nueva_placa:
                st.error("Error: Completa los campos requeridos.")
            else:
                agregar_equipo({
                    "UNIDAD": nueva_unidad,
                    "PLACA": nueva_placa,
                    "AÑO": int(nuevo_ano),
                    "MARCA": nueva_marca
                })
                st.success(f"✅ Unidad {nueva_unidad} agregada.")

    with col_del:
        st.markdown("#### 🗑️ Eliminar Equipo")
        with st.form("form_del_eq"):
            unidad_a_eliminar = st.selectbox("Selecciona Unidad:", unidades_opts, key="del_u")
            btn_del = st.form_submit_button("🗑️ Eliminar Registro")

        if btn_del:
            eliminar_equipo(unidad_a_eliminar)
            st.warning(f"❌ Unidad {unidad_a_eliminar} eliminada.")

    st.markdown("---")
    st.markdown(f"#### 📋 Catálogo en Vivo ({len(df_equipos)} Equipos)")
    st.dataframe(df_equipos, use_container_width=True)

    buffer_db = io.BytesIO()
    with pd.ExcelWriter(buffer_db, engine="openpyxl") as writer:
        df_equipos.to_excel(writer, index=False, sheet_name="Flota")

    st.download_button(
        label="📥 Descargar Catálogo (.xlsx)",
        data=buffer_db.getvalue(),
        file_name="catalogo_equipos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="btn_down_flota"
    )