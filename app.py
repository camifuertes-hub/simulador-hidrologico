import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Simulador Hidrológico Regional", layout="wide")

st.title("Simulador Regional de Caudales Máximos - Valle de Aburrá")
st.markdown("""
Esta herramienta permite estimar caudales de diseño ($Q_{Tr}$) comparando tres modelos empíricos regionales.
""")

# Panel Explicativo Visual
st.info("""
**Dependencia de Variables por Modelo:**
* **Modelo 1 (Univariado):** Sensible ÚNICAMENTE al **Área** de la cuenca.
* **Modelo 2 (Bivariado):** Sensible al **Área** y a la **Pendiente** del cauce.
* **Modelo 3 (Multivariado):** Sensible al **Área**, **Pendiente** y **Número de Curva (CN)**.
""")

# Controles en la barra lateral
st.sidebar.header("Parámetros de la Cuenca")
# AJUSTE: Área mínima desde 0.1
A = st.sidebar.slider("Área de la Cuenca (km²)", min_value=0.1, max_value=50.0, value=1.0, step=0.1)
S = st.sidebar.slider("Pendiente del Cauce (%)", min_value=1.0, max_value=40.0, value=15.0, step=0.5)
CN = st.sidebar.slider("Número de Curva (CN)", min_value=50, max_value=98, value=80, step=1)

# Cálculo de Q100 para los 3 modelos
Q100_M1 = 22.41 * (A ** 0.746)
Q100_M2 = 14.82 * (A ** 0.764) * (S ** 0.161)
Q100_M3 = 0.00167 * (A ** 0.8008) * (S ** 0.1353) * (CN ** 2.0351)

# Periodos de Retorno y factor de escala Gumbel
Tr_values = [2.33, 5, 10, 25, 50, 100, 500]
ln_100 = np.log(100)

data = []
for Tr in Tr_values:
    factor = np.log(Tr) / ln_100
    data.append({
        "Periodo de Retorno (Años)": str(Tr),
        "Tr_num": Tr,
        "Modelo 1 (Solo Área)": round(Q100_M1 * factor, 2),
        "Modelo 2 (Área + Pendiente)": round(Q100_M2 * factor, 2),
        "Modelo 3 (Multivariado)": round(Q100_M3 * factor, 2)
    })

df = pd.DataFrame(data)

# Visualización
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Comparativa de Curvas de Frecuencia")
    df_melt = df.melt(id_vars=["Periodo de Retorno (Años)", "Tr_num"], 
                      value_vars=["Modelo 1 (Solo Área)", "Modelo 2 (Área + Pendiente)", "Modelo 3 (Multivariado)"],
                      var_name="Modelo", value_name="Caudal (m³/s)")
    
    fig = px.line(df_melt, x="Periodo de Retorno (Años)", y="Caudal (m³/s)", color="Modelo",
                  markers=True, title=f"Caudal estimado para Área: {A} km², Pendiente: {S}%, CN: {CN}")
    fig.update_layout(yaxis_title="Caudal Estimado (m³/s)")
    fig.update_xaxes(type='category', categoryorder='array', categoryarray=[str(t) for t in Tr_values])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # AJUSTE: Título explicativo
    st.subheader("Resultados de Caudal por Periodo de Retorno")
    st.write("Valores expresados en metros cúbicos por segundo (m³/s)")
    st.dataframe(df.drop(columns=["Tr_num"]), hide_index=True)
