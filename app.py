import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Simulador Hidrológico Aburrá", layout="centered")

# CABECERA: Título técnico y profesional
st.title("💧 Simulador Hidrológico: Valle de Aburrá")
st.markdown("Cálculo regional de caudales de diseño ($Q_{Tr}$) basado en regresiones multivariadas.")

# PANEL EXPLICATIVO: Siempre visible, estilo manual técnico
with st.container():
    st.markdown("### ⚙️ Motor de Cálculo")
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    col_exp1.info("**Modelo 1**\n\nSensible al **Área**.")
    col_exp2.info("**Modelo 2**\n\nSensible al **Área + Pendiente**.")
    col_exp3.info("**Modelo 3**\n\nSensible al **Área + Pendiente + CN**.")

# SIDEBAR: Entrada de datos
st.sidebar.header("Parámetros de entrada")
A = st.sidebar.slider("Área (km²)", 0.1, 50.0, 1.0, 0.1)
S = st.sidebar.slider("Pendiente (%)", 1.0, 40.0, 15.0, 0.5)
CN = st.sidebar.slider("Número de Curva (CN)", 50, 98, 80, 1)

# Lógica de cálculo
Q100_M1 = 22.41 * (A ** 0.746)
Q100_M2 = 14.82 * (A ** 0.764) * (S ** 0.161)
Q100_M3 = 0.00167 * (A ** 0.8008) * (S ** 0.1353) * (CN ** 2.0351)

Tr_values = [2.33, 5, 10, 25, 50, 100, 500]
data = [{"Tr (Años)": str(Tr), 
         "M1 (Base)": round(Q100_M1 * (np.log(Tr)/np.log(100)), 1),
         "M2 (Pend)": round(Q100_M2 * (np.log(Tr)/np.log(100)), 1),
         "M3 (Multivar)": round(Q100_M3 * (np.log(Tr)/np.log(100)), 1)} for Tr in Tr_values]
df = pd.DataFrame(data)

# PESTAÑAS: Estructura clara
tab1, tab2 = st.tabs(["📈 Análisis Gráfico", "📋 Tabla de Caudales"])

with tab1:
    df_melt = df.melt(id_vars=["Tr (Años)"], var_name="Modelo", value_name="Caudal")
    fig = px.line(df_melt, x="Tr (Años)", y="Caudal", color="Modelo", markers=True)
    fig.update_layout(
        title=f"Resultados para A={A}km², S={S}%, CN={CN}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Periodo de Retorno (Años)",
        yaxis_title="m³/s"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df, hide_index=True, use_container_width=True)

# PIE DE PÁGINA: Nota técnica final (Rigor)
st.divider()
st.caption("Nota técnica: El Modelo 3 es el más robusto para cuencas con alta urbanización. Para diseños críticos, utilice el Q500 como evento de verificación.")
