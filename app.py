import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Simulador Hidrológico Regional", layout="wide")

st.title("Simulador Regional de Caudales Máximos - Valle de Aburrá")
st.markdown("""
Esta herramienta calcula y escala caudales de diseño ($Q_{Tr}$) comparando tres modelos empíricos regionales.
""")

# Panel Explicativo Visual (Dependencias)
st.info("""
**Dependencia de Variables por Modelo:**
* **Modelo 1 (Univariado):** Sensible ÚNICAMENTE al **Área**.
* **Modelo 2 (Bivariado):** Sensible al **Área** y a la **Pendiente**.
* **Modelo 3 (Multivariado):** Sensible al **Área**, **Pendiente** y **Número de Curva (CN)**.
""")

# Controles en la barra lateral
st.sidebar.header("Parámetros de la Cuenca")
A = st.sidebar.slider("Área de la Cuenca (km²)", min_value=1.0, max_value=50.0, value=9.6, step=0.1)
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
        "Tr_num": Tr, # Para ordenar internamente
        "Modelo 1": round(Q100_M1 * factor, 1),
        "Modelo 2": round(Q100_M2 * factor, 1),
        "Modelo 3": round(Q100_M3 * factor, 1)
    })

df = pd.DataFrame(data)

# Crear columnas para dividir la pantalla (Gráfico y Tabla)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Curvas de Frecuencia (Caudal vs. Tr)")
    # Transformar datos para Plotly (Formato largo)
    df_melt = df.melt(id_vars=["Periodo de Retorno (Años)", "Tr_num"], 
                      value_vars=["Modelo 1", "Modelo 2", "Modelo 3"],
                      var_name="Modelo", value_name="Caudal (m³/s)")
    
    # Gráfica interactiva
    fig = px.line(df_melt, x="Periodo de Retorno (Años)", y="Caudal (m³/s)", color="Modelo",
                  markers=True, title=f"Área: {A} km² | Pendiente: {S}% | CN: {CN}")
    # Forzar el orden categórico en el eje X
    fig.update_xaxes(type='category', categoryorder='array', categoryarray=[str(t) for t in Tr_values])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Resultados (m³/s)")
    # Mostrar tabla limpia sin la columna de ordenamiento interno
    st.dataframe(df.drop(columns=["Tr_num"]), hide_index=True)