import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
A = st.sidebar.slider("Área de la Cuenca (km²)", 0.01, 25.00, 1.00, 0.01)
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
tab1, tab2, tab3 = st.tabs(["📈 Análisis Gráfico", "📋 Tabla de Caudales", "🌊 Sección Hidráulica (Manning)"])

with tab1:
    df_melt = df.melt(id_vars=["Tr"], var_name="Modelo", value_name="Caudal")
    fig = px.line(df_melt, x="Tr", y="Caudal", color="Modelo", markers=True)
    fig.update_layout(
        template="plotly_white",
        title=f"Respuesta Hidrológica: A={A}km², S={S}%, CN={CN}",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=12)),
        margin=dict(l=40, r=40, t=80, b=40),
        xaxis=dict(title="Periodo de Retorno (Años)", showgrid=True, gridcolor='lightgray'),
        yaxis=dict(title="Caudal (m³/s)", showgrid=True, gridcolor='lightgray'),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(df, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Simulador Geométrico: Ecuación de Manning")
    st.markdown("Ajuste la geometría para que la **Capacidad del Canal** supere al **Caudal de Diseño**.")
    
    # Dividimos la pantalla
    col_geom, col_plot = st.columns([1, 2.5])
    
    with col_geom:
        st.write("**1. Meta Hidráulica**")
        # El valor por defecto es el M3, pero el usuario puede borrarlo e ingresar el que quiera
        Q_ref = st.number_input("Caudal de Diseño (m³/s)", min_value=0.1, max_value=5000.0, value=float(Q100_M3), step=1.0, help="Puede usar el valor calculado o escribir su propio caudal.")
        
        st.write("**2. Geometría del Canal**")
        b = st.number_input("Ancho de Solera, b (m)", min_value=0.5, max_value=20.0, value=3.0, step=0.5)
        z = st.number_input("Talud lateral, z (H:V)", min_value=0.0, max_value=3.0, value=1.0, step=0.5)
        y = st.number_input("Tirante de agua, Y (m)", min_value=0.1, max_value=10.0, value=1.5, step=0.1)
        
        st.write("**3. Propiedades del Flujo**")
        n = st.number_input("Rugosidad (n)", min_value=0.010, max_value=0.100, value=0.015, step=0.001, format="%.3f")
        S_m = st.number_input("Pendiente longitudinal (m/m)", min_value=0.001, max_value=0.200, value=0.010, step=0.001, format="%.3f")

        # Cálculos de Manning
        Area = y * (b + z * y)
        Perimetro = b + 2 * y * np.sqrt(1 + z**2)
        Radio_H = Area / Perimetro
        Velocidad = (1 / n) * (Radio_H ** (2/3)) * (S_m ** 0.5)
        Caudal_cap = Velocidad * Area
        
        # Cálculo del Borde Libre requerido normativo
        borde_libre = max(0.3, y * 0.2)

    with col_plot:
        Y_max = y + borde_libre + 0.5 
        
        x_canal = [-b/2 - z*Y_max, -b/2, b/2, b/2 + z*Y_max]
        y_canal = [Y_max, 0, 0, Y_max]
        
        x_agua = [-b/2 - z*y, -b/2, b/2, b/2 + z*y]
        y_agua = [y, 0, 0, y]

        fig_manning = go.Figure()

        fig_manning.add_trace(go.Scatter(
            x=x_agua, y=y_agua, fill='toself', mode='lines', 
            fillcolor='rgba(0, 191, 255, 0.4)', line=dict(color='blue', width=2),
            name='Lámina de Agua'
        ))
        
        fig_manning.add_trace(go.Scatter(
            x=x_canal, y=y_canal, mode='lines', 
            line=dict(color='black', width=4), name='Perfil del Canal'
        ))

        fig_manning.update_layout(
            template="plotly_white",
            title=f"Geometría Transversal (Tirante ingresado: {y} m)",
            xaxis=dict(title="Ancho transversal (m)", range=[-b/2 - z*Y_max - 1, b/2 + z*Y_max + 1], scaleanchor="y", scaleratio=1),
            yaxis=dict(title="Elevación (m)", range=[-0.5, Y_max + 0.5]),
            margin=dict(l=40, r=40, t=60, b=40),
            showlegend=False
        )
        st.plotly_chart(fig_manning, use_container_width=True)
        
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Caudal de Diseño (Meta)", f"{Q_ref:.2f} m³/s")
    
    margen = Caudal_cap - Q_ref
    c2.metric("Capacidad del Canal", f"{Caudal_cap:.2f} m³/s", delta=f"{margen:.2f} m³/s (Margen)", delta_color="normal")
    
    c3.metric("Velocidad de Flujo", f"{Velocidad:.2f} m/s")
    
    Froude = Velocidad / np.sqrt(9.81 * (Area / (b + 2*z*y)))
    estado_flujo = "Subcrítico" if Froude < 1 else ("Crítico" if Froude == 1 else "Supercrítico")
    c4.metric("Régimen (Froude)", f"{Froude:.2f} ({estado_flujo})")

st.divider()
st.caption("Nota técnica: El modelo 3 (Multivariado) integra el uso del suelo mediante el Número de Curva. Valores validados para la región andina.")
