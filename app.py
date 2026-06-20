import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Simulador Hidrológico Regional", layout="wide")

st.title("Simulador Regional de Caudales Máximos")

# Controles
st.sidebar.header("Parámetros")
A = st.sidebar.slider("Área (km²)", 0.1, 50.0, 1.0, 0.1)
S = st.sidebar.slider("Pendiente (%)", 1.0, 40.0, 15.0, 0.5)
CN = st.sidebar.slider("Número de Curva (CN)", 50, 98, 80, 1)

# Cálculos
Q100_M1 = 22.41 * (A ** 0.746)
Q100_M2 = 14.82 * (A ** 0.764) * (S ** 0.161)
Q100_M3 = 0.00167 * (A ** 0.8008) * (S ** 0.1353) * (CN ** 2.0351)

Tr_values = [2.33, 5, 10, 25, 50, 100, 500]
data = [{"Periodo (Tr)": str(Tr), 
         "M1": round(Q100_M1 * (np.log(Tr)/np.log(100)), 1),
         "M2": round(Q100_M2 * (np.log(Tr)/np.log(100)), 1),
         "M3": round(Q100_M3 * (np.log(Tr)/np.log(100)), 1)} for Tr in Tr_values]
df = pd.DataFrame(data)

# Tabs
tab1, tab2 = st.tabs(["📊 Gráfica", "📋 Resultados"])

with tab1:
    df_melt = df.melt(id_vars=["Periodo (Tr)"], var_name="Modelo", value_name="Caudal")
    
    fig = px.line(df_melt, x="Periodo (Tr)", y="Caudal", color="Modelo", markers=True)
    
    # AJUSTE MOVIL: Leyenda arriba y márgenes compactos
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Periodo de Retorno (Tr)",
        yaxis_title="m³/s"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # AJUSTE MOVIL: Tabla con scroll si es necesario
    st.dataframe(df, hide_index=True, use_container_width=True)
