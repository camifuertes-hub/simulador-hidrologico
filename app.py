import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Simulador Hidrológico Aburrá", layout="centered")

st.title("Simulador de Caudales Máximos")
st.markdown("Cálculo regional de caudales de diseño ($Q_{Tr}$) para el Valle de Aburrá.")

# Sección explicativa compacta pero informativa
with st.expander("ℹ️ ¿Cómo funcionan los modelos? (Clic para expandir)"):
    st.markdown("""
    * **Modelo 1 (Univariado):** Basado solo en el **Área** ($A$). Es nuestra línea base.
    * **Modelo 2 (Bivariado):** Integra **Área** ($A$) y **Pendiente** ($S$) del cauce.
    * **Modelo 3 (Multivariado):** Integra **Área** ($A$), **Pendiente** ($S$) y **Uso del suelo** ($CN$). 
    
    *El Modelo 3 es el más preciso para cuencas urbanizadas.*
    """)

# Sidebar optimizado
st.sidebar.header("Parámetros de entrada")
A = st.sidebar.slider("Área (km²)", 0.1, 50.0, 1.0, 0.1)
S = st.sidebar.slider("Pendiente (%)", 1.0, 40.0, 15.0, 0.5)
CN = st.sidebar.slider("Número de Curva (CN)", 50, 98, 80, 1)

# Cálculos
Q100_M1 = 22.41 * (A ** 0.746)
Q100_M2 = 14.82 * (A ** 0.764) * (S ** 0.161)
Q100_M3 = 0.00167 * (A ** 0.8008) * (S ** 0.1353) * (CN ** 2.0351)

Tr_values = [2.33, 5, 10, 25, 50, 100, 500]
data = [{"Tr (Años)": str(Tr), 
         "M1 (Solo Área)": round(Q100_M1 * (np.log(Tr)/np.log(100)), 1),
         "M2 (Área+Pend)": round(Q100_M2 * (np.log(Tr)/np.log(100)), 1),
         "M3 (Multivar)": round(Q100_M3 * (np.log(Tr)/np.log(100)), 1)} for Tr in Tr_values]
df = pd.DataFrame(data)

# Visualización con pestañas
tab1, tab2 = st.tabs(["📈 Gráfica Comparativa", "📊 Resultados (m³/s)"])

with tab1:
    df_melt = df.melt(id_vars=["Tr (Años)"], var_name="Modelo", value_name="Caudal")
    fig = px.line(df_melt, x="Tr (Años)", y="Caudal", color="Modelo", markers=True)
    fig.update_layout(
        title=f"Estimación para A={A}km², S={S}%, CN={CN}",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=60, b=10),
        xaxis_title="Periodo de Retorno (Años)",
        yaxis_title="Caudal (m³/s)"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df, hide_index=True, use_container_width=True)
