import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Simulador Hidrológico Medellín", layout="wide")

st.title("💧 Simulador Hidrológico de Caudales Máximos")

# Panel Técnico Explicativo (Fijo y limpio)
st.markdown("""
Esta herramienta utiliza regresiones multivariadas calibradas para Medellín. 
Seleccione los parámetros de la cuenca en la barra lateral para observar la respuesta del sistema.
""")

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Modelo 1", "Univariado", "Sensible: Área")
col_m2.metric("Modelo 2", "Bivariado", "Sensible: Área + Pendiente")
col_m3.metric("Modelo 3", "Multivariado", "Sensible: A + S + CN")

# Sidebar
st.sidebar.header("Parámetros de entrada")
A = st.sidebar.slider("Área de la Cuenca (km²)", 0.01, 50.0, 1.0, 0.01)
S = st.sidebar.slider("Pendiente del Cauce (%)", 1.0, 70.0, 25.0, 0.1)
CN = st.sidebar.slider("Número de Curva (CN)", 50, 98, 80, 1)

# Lógica
Q100_M1 = 22.41 * (A ** 0.746)
Q100_M2 = 14.82 * (A ** 0.764) * (S ** 0.161)
Q100_M3 = 0.00167 * (A ** 0.8008) * (S ** 0.1353) * (CN ** 2.0351)

Tr_values = [2.33, 5, 10, 25, 50, 100, 500]
data = [{"Tr": str(Tr), 
         "M1 (Base)": round(Q100_M1 * (np.log(Tr)/np.log(100)), 1),
         "M2 (Pend)": round(Q100_M2 * (np.log(Tr)/np.log(100)), 1),
         "M3 (Mult)": round(Q100_M3 * (np.log(Tr)/np.log(100)), 1)} for Tr in Tr_values]
df = pd.DataFrame(data)

# Visualización Científica
tab1, tab2 = st.tabs(["📈 Análisis Gráfico", "📋 Resultados Numéricos"])

with tab1:
    df_melt = df.melt(id_vars=["Tr"], var_name="Modelo", value_name="Caudal")
    
    fig = px.line(df_melt, x="Tr", y="Caudal", color="Modelo", markers=True)
    
    # Ajustes de estilo científico
    fig.update_layout(
        template="plotly_white", # Fondo blanco, estilo académico
        title=f"Respuesta Hidrológica: A={A}km², S={S}%, CN={CN}",
        legend=dict(
            orientation="h", 
            yanchor="bottom", y=1.05, 
            xanchor="center", x=0.5,
            font=dict(size=12)
        ),
        margin=dict(l=40, r=40, t=80, b=40), # Espacio para evitar superposición
        xaxis=dict(title="Periodo de Retorno (Años)", showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title="Caudal (m³/s)", showgrid=True, gridcolor='lightgray'),
        hovermode='x unified' # Panel de información limpio al lado del cursor
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df, hide_index=True, use_container_width=True)

st.divider()
st.caption("Nota técnica: El modelo 3 (Multivariado) integra el uso del suelo mediante el Número de Curva. Valores validados para la región andina.")
