from termcolor import cprint, colored
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import traceback
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import logging

from app.core.config import config

# Configurar logging para Prophet y CmdStanPy (reduce verbosidad)
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

# Configuración de estilo para los gráficos
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("muted") # Usar una paleta de colores de Seaborn

# --- Configuración ---
OUTPUT_DIR = "docs/proyecto/analisis_resultados_amaluz"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Conexión a BD ---
def crear_conexion_db(db_url):
    """Crea una conexión a la base de datos usando SQLAlchemy."""
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            print(f"Conexión exitosa a la base de datos: {engine.url.database}")
            return engine
    except Exception as e:
        print(f"Error al conectar a la base de datos ({db_url}): {e}")
        print(
            "Por favor, verifica la URL de conexión, credenciales, y que el servidor MySQL esté accesible."
        )
        print(
            "Ejemplo de URL: mysql+pymysql://tu_usuario:tu_contraseña@localhost/amaluz"
        )
        return None


# --- Funciones de Carga y Preparación de Datos ---
def cargar_datos_pedidos(engine):
    """Carga el número de pedidos a lo largo del tiempo."""
    query = "SELECT fecha_pedido FROM amaluz.pedido ORDER BY fecha_pedido;"
    df = pd.read_sql(query, engine)
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"])
    df["fecha_pedido"] = pd.to_datetime(df["fecha_pedido"])
    df.set_index("fecha_pedido", inplace=True)
    df_resampled = df.resample("D").size().rename("num_pedidos")
    return df_resampled.reset_index().rename(
        columns={"fecha_pedido": "ds", "num_pedidos": "y"}
    )


def cargar_datos_ingresos(engine):
    """Carga los ingresos totales a lo largo del tiempo."""
    query = "SELECT fecha_pedido, costo_total FROM amaluz.pedido ORDER BY fecha_pedido;"
    df = pd.read_sql(query, engine)
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"])
    df["fecha_pedido"] = pd.to_datetime(df["fecha_pedido"])
    df["costo_total"] = pd.to_numeric(df["costo_total"], errors="coerce").fillna(0)
    df.set_index("fecha_pedido", inplace=True)
    df_resampled = df["costo_total"].resample("D").sum().rename("ingresos_totales")
    return df_resampled.reset_index().rename(
        columns={"fecha_pedido": "ds", "ingresos_totales": "y"}
    )


def cargar_datos_clientes(engine):
    """Carga el crecimiento de nuevos clientes."""
    query = "SELECT fecha_registro FROM amaluz.cliente ORDER BY fecha_registro;"
    df = pd.read_sql(query, engine)
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"])
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    df.set_index("fecha_registro", inplace=True)
    df_resampled = df.resample("D").size().rename("nuevos_clientes")
    return df_resampled.reset_index().rename(
        columns={"fecha_registro": "ds", "nuevos_clientes": "y"}
    )


def cargar_datos_ventas_categoria(engine):
    """Carga el volumen de ventas por categoría de producto."""
    query = """
            SELECT dp.fecha_venta, p.categoria, SUM(dp.cantidad) as cantidad_vendida
            FROM amaluz.detalle_pedido dp
                     JOIN amaluz.productos p ON dp.id_producto = p.id_producto
            GROUP BY dp.fecha_venta, p.categoria
            ORDER BY dp.fecha_venta;
            """ # Se eliminó la barra invertida al final de la consulta
    df = pd.read_sql(query, engine)
    if df.empty:
        return pd.DataFrame(columns=["ds", "y"]), pd.DataFrame()
    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"])
    df["cantidad_vendida"] = pd.to_numeric(
        df["cantidad_vendida"], errors="coerce"
    ).fillna(0)

    df_total_ventas = (
        df.groupby(pd.Grouper(key="fecha_venta", freq="D"))["cantidad_vendida"]
        .sum()
        .reset_index()
    )
    df_total_ventas.columns = ["ds", "y"]

    df_ventas_categoria_pivot = df.pivot_table(
        index=pd.Grouper(key="fecha_venta", freq="D"),
        columns="categoria",
        values="cantidad_vendida",
        aggfunc="sum",
    ).fillna(0)
    return df_total_ventas, df_ventas_categoria_pivot


# --- Análisis Exploratorio de Datos (EDA) ---
def realizar_eda(df_serie_temporal, metrica_nombre, df_categorias=None):
    informe_eda = f"## Análisis Exploratorio de Datos (EDA) para: {metrica_nombre}\n\n"
    informe_eda += "El Análisis Exploratorio de Datos nos ayuda a entender las características principales de los datos antes de aplicar modelos predictivos.\n\n"

    # Asegurar que 'ds' es datetime
    df_serie_temporal["ds"] = pd.to_datetime(df_serie_temporal["ds"])
    df_serie_temporal_eda = df_serie_temporal.set_index("ds")

    # 1. Gráfico de la serie temporal original
    plt.figure(figsize=(12, 6))
    plt.plot(
        df_serie_temporal_eda.index, # Usar el índice para el eje x
        df_serie_temporal_eda["y"],
        label=f"{metrica_nombre} (Valores Diarios)",
        linewidth=1.5
    )
    plt.title(f"Serie Temporal de {metrica_nombre}", fontsize=16)
    plt.xlabel("Fecha", fontsize=12)
    plt.ylabel(metrica_nombre, fontsize=12)
    plt.legend(fontsize=10)
    plt.tight_layout()
    nombre_archivo_serie = f'serie_temporal_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
    ruta_grafico_serie = os.path.join(OUTPUT_DIR, nombre_archivo_serie)
    plt.savefig(ruta_grafico_serie)
    plt.close()
    informe_eda += f"### 1. Visualización de la Serie Temporal\n"
    informe_eda += f"El siguiente gráfico muestra la evolución de '{metrica_nombre}' a lo largo del tiempo. Permite observar patrones generales, picos, valles y posibles anomalías.\n"
    informe_eda += f"![Serie Temporal de {metrica_nombre}]({nombre_archivo_serie})\n\n"

    # 2. Tendencia (media móvil 30 días)
    window_size = 30
    df_serie_temporal_eda["tendencia"] = (
        df_serie_temporal_eda["y"].rolling(window=window_size, center=True, min_periods=1).mean()
    )
    plt.figure(figsize=(12, 6))
    plt.plot(
        df_serie_temporal_eda.index,
        df_serie_temporal_eda["y"],
        label=f"{metrica_nombre} (Valores Diarios)",
        alpha=0.6,
        linewidth=1
    )
    plt.plot(
        df_serie_temporal_eda.index,
        df_serie_temporal_eda["tendencia"],
        label=f"Tendencia (Media Móvil {window_size} días)",
        color="red", # Usar un color distintivo para la tendencia
        linewidth=2,
    )
    plt.title(f"Tendencia de {metrica_nombre}", fontsize=16)
    plt.xlabel("Fecha", fontsize=12)
    plt.ylabel(metrica_nombre, fontsize=12)
    plt.legend(fontsize=10)
    plt.tight_layout()
    nombre_archivo_tendencia = f'tendencia_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
    ruta_grafico_tendencia = os.path.join(OUTPUT_DIR, nombre_archivo_tendencia)
    plt.savefig(ruta_grafico_tendencia)
    plt.close()
    informe_eda += f"### 2. Análisis de Tendencia\n"
    informe_eda += f"Se calcula una media móvil de {window_size} días para suavizar las fluctuaciones a corto plazo y visualizar la dirección general de la serie. Una media móvil representa el promedio de los datos sobre una ventana de tiempo deslizante.\n"
    informe_eda += f"![Tendencia de {metrica_nombre}]({nombre_archivo_tendencia})\n\n"

    if not df_serie_temporal_eda["tendencia"].dropna().empty:
        tendencia_vals = df_serie_temporal_eda["tendencia"].dropna()
        if len(tendencia_vals) > 1:
            cambio_tendencia = tendencia_vals.iloc[-1] - tendencia_vals.iloc[0]
            if cambio_tendencia > 0.01 * abs(tendencia_vals.iloc[0]) if tendencia_vals.iloc[0] != 0 else cambio_tendencia > 0: # Manejar división por cero
                informe_eda += "**Conclusión de Tendencia**: La tendencia general observada es **ascendente**.\n"
            elif cambio_tendencia < -0.01 * abs(tendencia_vals.iloc[0]) if tendencia_vals.iloc[0] != 0 else cambio_tendencia < 0:
                informe_eda += "**Conclusión de Tendencia**: La tendencia general observada es **descendente**.\n"
            else:
                informe_eda += "**Conclusión de Tendencia**: La tendencia general observada es **estable o con cambios menores**.\n"
        else:
            informe_eda += "No hay suficientes puntos en la tendencia para determinar su dirección de forma concluyente.\n"
    else:
        informe_eda += "No se pudo determinar la tendencia (datos insuficientes para la media móvil).\n"
    informe_eda += "\n"

    # 3. Tasa de crecimiento
    informe_eda += f"### 3. Tasas de Crecimiento\n"
    if len(df_serie_temporal_eda["y"]) >= 2:
        val_inicial = df_serie_temporal_eda["y"].iloc[0]
        val_final = df_serie_temporal_eda["y"].iloc[-1]
        crecimiento_total = val_final - val_inicial

        informe_eda += f"- **Valor Inicial**: {val_inicial:.2f}\n"
        informe_eda += f"- **Valor Final**: {val_final:.2f}\n"
        informe_eda += f"- **Crecimiento Total en el Período**: {crecimiento_total:.2f} unidades.\n"

        if val_inicial != 0:
            crecimiento_porcentual_total = (crecimiento_total / abs(val_inicial)) * 100
            informe_eda += f"- **Crecimiento Porcentual Total**: {crecimiento_porcentual_total:.2f}%.\n"
        else:
            informe_eda += "- Crecimiento Porcentual Total: No aplicable (valor inicial es cero).\n"

        num_dias = (df_serie_temporal_eda.index.max() - df_serie_temporal_eda.index.min()).days
        if num_dias > 0:
            num_meses = num_dias / 30.44 # Promedio de días en un mes
            if num_meses >= 1:
                try:
                    if val_inicial > 0 and val_final > 0: # Para tasa compuesta geométrica
                        tasa_crecimiento_mensual_compuesta = ((val_final / val_inicial) ** (1 / num_meses) - 1) * 100
                        if not (np.isnan(tasa_crecimiento_mensual_compuesta) or np.isinf(tasa_crecimiento_mensual_compuesta)):
                            informe_eda += f"- **Tasa de Crecimiento Mensual Promedio (Compuesta)**: {tasa_crecimiento_mensual_compuesta:.2f}%. Esta tasa indica el crecimiento promedio mensual si el crecimiento se reinvirtiera cada mes.\n"
                        else:
                            raise ValueError("Resultado no válido para tasa compuesta")
                    else: # Usar lineal si no se puede calcular compuesta
                        raise ValueError("Valores no positivos para tasa compuesta")
                except (ZeroDivisionError, ValueError, OverflowError):
                    crecimiento_promedio_mensual_lineal = (crecimiento_total / num_meses) if num_meses > 0 else 0
                    informe_eda += f"- **Crecimiento Promedio Mensual (Lineal)**: {crecimiento_promedio_mensual_lineal:.2f} unidades/mes. Esta es la variación promedio simple por mes.\n"
    else:
        informe_eda += "Datos insuficientes para calcular tasas de crecimiento.\n"
    informe_eda += "\n"

    # 4. Descomposición Estacional
    informe_eda += f"### 4. Descomposición Estacional\n"
    periodo_estacional = 7  # Asumimos estacionalidad semanal para datos diarios
    if len(df_serie_temporal_eda) >= 2 * periodo_estacional:
        try:
            # Usar df_serie_temporal_eda['y'] que es una Serie con índice DatetimeIndex
            descomposicion = seasonal_decompose(
                df_serie_temporal_eda["y"],
                model="additive", # 'additive' es común, 'multiplicative' si la estacionalidad crece con la tendencia
                period=periodo_estacional,
                extrapolate_trend="freq",
            )
            fig_desc = descomposicion.plot()
            fig_desc.set_size_inches(12, 10)
            fig_desc.suptitle(f"Descomposición Estacional de {metrica_nombre}", fontsize=16, y=1.02)
            # Traducir títulos de subplots si es posible (difícil con el plot directo de seasonal_decompose)
            axes = fig_desc.get_axes()
            if len(axes) >=4: # Observed, Trend, Seasonal, Residual
                axes[0].set_ylabel("Observado")
                axes[1].set_ylabel("Tendencia")
                axes[2].set_ylabel("Estacionalidad")
                axes[3].set_ylabel("Residuos")
                axes[3].set_xlabel("Fecha")

            plt.tight_layout(rect=[0, 0, 1, 0.98]) # Ajustar para el supertítulo
            nombre_archivo_descomposicion = f'descomposicion_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
            ruta_grafico_descomposicion = os.path.join(OUTPUT_DIR, nombre_archivo_descomposicion)
            plt.savefig(ruta_grafico_descomposicion)
            plt.close(fig_desc)
            informe_eda += "La descomposición de series temporales separa los datos en varios componentes:\n"
            informe_eda += "- **Tendencia**: La dirección general a largo plazo de los datos.\n"
            informe_eda += "- **Estacionalidad**: Patrones que se repiten en intervalos fijos (ej. semanalmente, anualmente).\n"
            informe_eda += "- **Residuos**: La parte de los datos que queda después de remover la tendencia y la estacionalidad (ruido aleatorio).\n"
            informe_eda += f"Se ha realizado una descomposición asumiendo un ciclo estacional de {periodo_estacional} días (semanal).\n"
            informe_eda += f"![Descomposición Estacional de {metrica_nombre}]({nombre_archivo_descomposicion})\n\n"
        except Exception as e:
            informe_eda += f"No se pudo realizar la descomposición estacional: {e}. Puede ser debido a datos insuficientes o falta de variabilidad.\n"
    else:
        informe_eda += f"Datos insuficientes para una descomposición estacional detallada (se necesitan al menos dos ciclos completos, es decir, {2*periodo_estacional} días para un periodo de {periodo_estacional}).\n"
    informe_eda += "\n"

    # 5. Análisis Categórico (si aplica)
    if df_categorias is not None and not df_categorias.empty:
        informe_eda += f"### 5. Análisis por Categoría (para '{metrica_nombre}')\n"
        df_categorias.index = pd.to_datetime(df_categorias.index)

        plt.figure(figsize=(14, 8))
        for categoria in df_categorias.columns:
            plt.plot(df_categorias.index, df_categorias[categoria], label=categoria, linewidth=1.5)
        plt.title(f"{metrica_nombre} por Categoría de Producto", fontsize=16)
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Valor de la Métrica (ej. Cantidad Vendida)", fontsize=12)
        plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0.0, fontsize=10)
        plt.tight_layout(rect=[0, 0, 0.85, 1]) # Ajustar para leyenda externa
        nombre_archivo_categorias = f'metricas_por_categoria_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
        ruta_grafico_categorias = os.path.join(OUTPUT_DIR, nombre_archivo_categorias)
        plt.savefig(ruta_grafico_categorias)
        plt.close()
        informe_eda += f"El siguiente gráfico muestra la evolución de '{metrica_nombre}' desglosada por categoría de producto. Esto ayuda a identificar qué categorías son más significativas y cómo evoluciona su contribución.\n"
        informe_eda += f"![{metrica_nombre} por Categoría]({nombre_archivo_categorias})\n\n"

        total_por_categoria = df_categorias.sum().sort_values(ascending=False)
        informe_eda += "**Total Acumulado por Categoría (ordenado de mayor a menor):**\n"
        for cat, total in total_por_categoria.items():
            informe_eda += f"- **{cat}**: {total:.0f}\n"
        informe_eda += "\nObservar este desglose puede revelar categorías dominantes, con mayor crecimiento o aquellas que podrían requerir atención.\n"
    return informe_eda


# --- Modelado Predictivo ---
def dividir_datos(df, test_size=0.2, min_train_size=20):
    if len(df) < min_train_size + 5: # Un mínimo para tener algo en test si es posible
        print(f"Advertencia: Datos insuficientes ({len(df)} puntos) para una división estándar en entrenamiento/prueba. Se usarán todos los datos para entrenamiento.")
        return df.copy(), pd.DataFrame(columns=df.columns) # Devuelve un df_test vacío
    train, test = train_test_split(df, test_size=test_size, shuffle=False) # shuffle=False es crucial para series temporales
    return train.copy(), test.copy()


def evaluar_modelo(y_true, y_pred, nombre_modelo):
    if y_true.empty or y_pred.empty or len(y_true) != len(y_pred):
        print(f"No se puede evaluar el modelo {nombre_modelo}: los datos reales o las predicciones están vacíos o tienen longitudes desiguales.")
        return np.nan, np.nan

    y_true_val = y_true.values.astype(float)
    y_pred_val = y_pred.values.astype(float)

    nan_mask = np.isnan(y_pred_val)
    if np.all(nan_mask):
        print(f"Todas las predicciones para el modelo {nombre_modelo} son NaN. No se puede evaluar.")
        return np.nan, np.nan

    y_true_filt = y_true_val[~nan_mask]
    y_pred_filt = y_pred_val[~nan_mask]

    if len(y_true_filt) == 0:
        print(f"No hay predicciones válidas para el modelo {nombre_modelo} después de filtrar NaNs.")
        return np.nan, np.nan

    mae = mean_absolute_error(y_true_filt, y_pred_filt)
    rmse = np.sqrt(mean_squared_error(y_true_filt, y_pred_filt))
    print(f"Evaluación del modelo {nombre_modelo} (sobre {len(y_true_filt)} puntos de prueba): MAE = {mae:.2f}, RMSE = {rmse:.2f}")
    return mae, rmse


def modelo_regresion_lineal(df_train, df_test, n_futuro=365):
    df_train_copy = df_train.copy()
    df_train_copy["time"] = np.arange(len(df_train_copy.index))

    X_train = df_train_copy[["time"]]
    y_train = df_train_copy["y"]

    model = LinearRegression()
    model.fit(X_train, y_train)

    pred_train_vals = model.predict(X_train)
    pred_train_series = pd.Series(pred_train_vals, index=df_train["ds"])

    pred_test_series = pd.Series(dtype='float64')
    if not df_test.empty:
        df_test_copy = df_test.copy()
        df_test_copy['time'] = np.arange(len(df_train_copy), len(df_train_copy) + len(df_test_copy))
        X_test = df_test_copy[['time']]
        pred_test_vals = model.predict(X_test)
        pred_test_series = pd.Series(pred_test_vals, index=df_test["ds"])

    ultima_fecha_conocida = df_test["ds"].iloc[-1] if not df_test.empty else df_train["ds"].iloc[-1]
    ultimo_tiempo_conocido = (len(df_train) + len(df_test) - 1) if not df_test.empty else (len(df_train) - 1)

    tiempos_futuros_vals = np.arange(ultimo_tiempo_conocido + 1, ultimo_tiempo_conocido + 1 + n_futuro)
    X_futuro = pd.DataFrame(tiempos_futuros_vals, columns=['time'])
    pred_futuro_vals = model.predict(X_futuro)
    fechas_futuras = pd.date_range(start=ultima_fecha_conocida + pd.Timedelta(days=1), periods=n_futuro)
    pred_futuro_series = pd.Series(pred_futuro_vals, index=fechas_futuras)

    return pred_train_series, pred_test_series, pred_futuro_series


def modelo_arima(df_train, df_test, order, n_futuro):
    historial = [x for x in df_train["y"]]
    pred_train_series = pd.Series(dtype='float64')

    try:
        model_fit_train = ARIMA(historial, order=order, enforce_stationarity=False, enforce_invertibility=False).fit()
        fitted_vals = model_fit_train.fittedvalues
        start_index_fitted = len(historial) - len(fitted_vals)
        temp_pred_train_vals = [np.nan] * start_index_fitted + list(fitted_vals)
        pred_train_series = pd.Series(temp_pred_train_vals, index=df_train["ds"])
    except Exception as e:
        print(f"Error al ajustar ARIMA en datos de entrenamiento: {e}. Se devolverán NaNs para el entrenamiento.")
        pred_train_series = pd.Series([np.nan] * len(df_train), index=df_train["ds"])

    pred_test_list = []
    if not df_test.empty:
        current_hist = list(historial)
        for t in range(len(df_test)):
            try:
                model = ARIMA(current_hist, order=order, enforce_stationarity=False, enforce_invertibility=False)
                model_fit = model.fit()
                yhat = model_fit.forecast()[0]
                pred_test_list.append(yhat)
                current_hist.append(df_test["y"].iloc[t])
            except Exception as e:
                print(f"Error en la predicción ARIMA para el paso de prueba {t+1}/{len(df_test)}: {e}. Se usará NaN.")
                pred_test_list.append(np.nan)
                current_hist.append(df_test["y"].iloc[t]) # Añadir valor real para el siguiente paso

    pred_test_vals = np.array(pred_test_list, dtype=float)
    pred_test_series = pd.Series(pred_test_vals, index=df_test["ds"] if not df_test.empty else None)

    full_historial = list(df_train["y"]) + (list(df_test["y"]) if not df_test.empty else [])
    pred_futuro_series = pd.Series(dtype='float64')
    ultima_fecha_conocida = df_test["ds"].iloc[-1] if not df_test.empty else df_train["ds"].iloc[-1]
    fechas_futuras = pd.date_range(start=ultima_fecha_conocida + pd.Timedelta(days=1), periods=n_futuro)

    if len(full_historial) > max(order): # Asegurar suficientes datos
        try:
            model_final = ARIMA(full_historial, order=order, enforce_stationarity=False, enforce_invertibility=False)
            model_fit_final = model_final.fit()
            pred_futuro_vals = model_fit_final.forecast(steps=n_futuro)
            pred_futuro_series = pd.Series(pred_futuro_vals, index=fechas_futuras)
        except Exception as e:
            print(f"Error al generar predicciones futuras con ARIMA: {e}. Se devolverán NaNs para el futuro.")
            pred_futuro_series = pd.Series([np.nan] * n_futuro, index=fechas_futuras)
    else:
        print("No hay suficientes datos en el historial completo para predicciones futuras con ARIMA.")
        pred_futuro_series = pd.Series([np.nan] * n_futuro, index=fechas_futuras)

    return pred_train_series, pred_test_series, pred_futuro_series


def modelo_prophet(df_train, df_test, n_futuro=365):
    model = Prophet(
        daily_seasonality=False, # Generalmente no es tan útil como semanal o anual para datos diarios de negocio
        weekly_seasonality='auto', # Prophet decide si hay suficiente data
        yearly_seasonality='auto', # Prophet decide si hay suficiente data
        changepoint_prior_scale=0.05, # Valor por defecto, ajustar si hay muchos/pocos cambios de tendencia
    )
    # Prophet puede añadir estacionalidades si hay suficientes datos
    # No es necesario deshabilitarlas manualmente a menos que se sepa que no aplican o causan problemas
    # if len(df_train) < 14: model.weekly_seasonality = False
    # if len(df_train) < 365 * 2: model.yearly_seasonality = False

    model.fit(df_train[["ds", "y"]])

    pred_train_df = model.predict(df_train[["ds"]]) # No pasar 'y' para predicción
    pred_train_vals = pred_train_df["yhat"].values
    pred_train_series = pd.Series(pred_train_vals, index=df_train["ds"])

    pred_test_series = pd.Series(dtype='float64')
    if not df_test.empty:
        pred_test_df = model.predict(df_test[["ds"]]) # No pasar 'y' para predicción
        pred_test_vals = pred_test_df["yhat"].values
        pred_test_series = pd.Series(pred_test_vals, index=df_test["ds"])

    future_dates_df = model.make_future_dataframe(periods=n_futuro, freq='D') # Asegurar frecuencia diaria
    forecast_df = model.predict(future_dates_df)

    # Filtrar solo las predicciones futuras (posteriores a la última fecha de entrenamiento)
    pred_futuro_df_filtered = forecast_df[forecast_df['ds'] > df_train['ds'].max()]
    pred_futuro_vals = pred_futuro_df_filtered['yhat'].values

    # Asegurar que tomamos n_futuro periodos desde la última fecha conocida (entrenamiento o prueba)
    ultima_fecha_conocida = df_test["ds"].max() if not df_test.empty else df_train["ds"].max()
    fechas_futuras_correctas = pd.date_range(start=ultima_fecha_conocida + pd.Timedelta(days=1), periods=n_futuro, freq='D')

    # Alinear predicciones futuras con las fechas correctas
    # Esto es importante si make_future_dataframe generó más fechas de las necesarias o si hubo un gap
    pred_futuro_series = pd.Series(pred_futuro_vals[:n_futuro], index=fechas_futuras_correctas)


    return pred_train_series, pred_test_series, pred_futuro_series, model, forecast_df # Devolver forecast_df completo para componentes


# --- Visualización de Resultados de Modelos ---
def graficar_predicciones(
        df_serie_temporal, df_train, df_test, predicciones, nombre_modelo, metrica_nombre
):
    plt.figure(figsize=(14, 7))
    # Datos reales
    plt.plot(
        df_serie_temporal["ds"],
        df_serie_temporal["y"],
        label="Datos Reales",
        color="royalblue", # Un azul más distintivo
        linewidth=2, # Hacerla más prominente
        alpha=0.8
    )

    # Predicciones de entrenamiento
    if "train" in predicciones and not predicciones["train"].empty:
        plt.plot(
            predicciones["train"].index,
            predicciones["train"].values,
            label=f"Pred. {nombre_modelo} (Entrenamiento)",
            linestyle="--",
            color="darkorange", # Naranja oscuro
            linewidth=1.5
        )

    # Predicciones de prueba
    if "test" in predicciones and not predicciones["test"].empty and not df_test.empty:
        plt.plot(
            predicciones["test"].index,
            predicciones["test"].values,
            label=f"Pred. {nombre_modelo} (Prueba)",
            linestyle="--",
            color="forestgreen", # Verde bosque
            linewidth=1.5
        )

    # Predicciones futuras
    if "future" in predicciones and not predicciones["future"].empty:
        plt.plot(
            predicciones["future"].index,
            predicciones["future"].values,
            label=f"Pred. {nombre_modelo} (Futuro)",
            linestyle=":",
            color="crimson", # Rojo carmesí
            linewidth=2
        )

    plt.title(f"{metrica_nombre}: Datos Reales vs. Predicciones del Modelo {nombre_modelo}", fontsize=16)
    plt.xlabel("Fecha", fontsize=12)
    plt.ylabel(metrica_nombre, fontsize=12)
    plt.legend(loc="best", fontsize=10) # 'best' para mejor ubicación automática
    plt.tight_layout()

    nombre_archivo_pred = f'predicciones_{nombre_modelo.lower().replace(" ", "_")}_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
    ruta_grafico = os.path.join(OUTPUT_DIR, nombre_archivo_pred)
    plt.savefig(ruta_grafico)
    plt.close()
    return nombre_archivo_pred # Devolver solo el nombre base para el informe


# --- Generación de Informe ---
def generar_informe_final(
        metrica_nombre,
        informe_eda_txt,
        resultados_modelos,
        df_serie_temporal
):
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nombre_archivo_informe = f'informe_completo_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.md'
    ruta_informe = os.path.join(OUTPUT_DIR, nombre_archivo_informe)

    informe_md = f"# Informe de Análisis y Predicción: {metrica_nombre}\n"
    informe_md += f"**Fecha de Generación**: {fecha_actual}\n\n"
    informe_md += f"## 1. Introducción\n"
    informe_md += f"Este informe detalla el análisis exploratorio y los resultados de los modelos predictivos para la métrica: **{metrica_nombre}**. El objetivo es comprender las tendencias históricas y proyectar valores futuros para apoyar la toma de decisiones.\n\n"

    if df_serie_temporal.empty or len(df_serie_temporal["y"].dropna()) < 10:
        informe_md += "## Advertencia: Datos Insuficientes\n"
        informe_md += f"No se encontraron suficientes datos ({len(df_serie_temporal['y'].dropna())} puntos válidos) para la métrica '{metrica_nombre}' para realizar un análisis completo o generar predicciones confiables. El informe se limitará a la información disponible.\n\n"

    informe_md += informe_eda_txt # Ya incluye el título "## Análisis Exploratorio de Datos..."

    informe_md += "\n## 3. Modelado Predictivo y Resultados\n"
    if not df_serie_temporal.empty and len(df_serie_temporal["y"].dropna()) >= 10 :
        informe_md += f"Se han aplicado varios modelos de series temporales para predecir los próximos **{resultados_modelos.get('n_futuro', 'N/A')} días** de '{metrica_nombre}'.\n"
        informe_md += "Los modelos se evalúan utilizando el Error Absoluto Medio (MAE) y la Raíz del Error Cuadrático Medio (RMSE) sobre un conjunto de datos de prueba (típicamente el 20% más reciente de los datos históricos, no utilizado durante el entrenamiento del modelo).\n"
        informe_md += "- **MAE**: Mide el promedio de los errores absolutos. Un MAE de X significa que, en promedio, las predicciones del modelo se desvían en X unidades del valor real.\n"
        informe_md += "- **RMSE**: Similar al MAE, pero penaliza más los errores grandes. Si el RMSE es significativamente mayor que el MAE, indica la presencia de algunos errores de predicción grandes.\n"
        informe_md += "**Valores más bajos de MAE y RMSE indican un mejor rendimiento del modelo en el conjunto de prueba.**\n\n"
    else:
        informe_md += "No se procedió con el modelado predictivo debido a la insuficiencia de datos.\n\n"

    for nombre_modelo, data in resultados_modelos.items():
        if nombre_modelo == "n_futuro":
            continue
        informe_md += f"### 3.{list(resultados_modelos.keys()).index(nombre_modelo)} Modelo: {nombre_modelo.replace('_', ' ')}\n" # Numeración
        if "ruta_grafico" in data and data["ruta_grafico"]:
            informe_md += f"**Gráfico de Predicciones ({nombre_modelo.replace('_', ' ')})**:\n"
            informe_md += f"El gráfico muestra los datos reales (azul), las predicciones sobre el conjunto de entrenamiento (naranja), las predicciones sobre el conjunto de prueba (verde) y las predicciones futuras (rojo).\n"
            informe_md += f"![Predicciones {nombre_modelo.replace('_', ' ')}]({data['ruta_grafico']})\n\n"

        if "mae" in data and "rmse" in data and not (np.isnan(data["mae"]) or np.isnan(data["rmse"])):
            informe_md += f"**Métricas de Evaluación en Conjunto de Prueba**:\n"
            informe_md += f"- Error Absoluto Medio (MAE): **{data['mae']:.2f}**\n"
            informe_md += f"- Raíz del Error Cuadrático Medio (RMSE): **{data['rmse']:.2f}**\n"
            informe_md += f"  (Contextualizar estos valores con la escala de '{metrica_nombre}' observada en el EDA).\n\n"
        elif "error_evaluacion" in data:
            informe_md += f"- **Nota sobre Evaluación**: {data['error_evaluacion']}\n\n"
        else:
            informe_md += "- No se pudo evaluar el modelo en un conjunto de prueba o la evaluación no fue aplicable/posible.\n\n"

        if nombre_modelo == "Prophet" and "ruta_grafico_componentes" in data and data["ruta_grafico_componentes"]:
            informe_md += f"**Análisis de Componentes (Prophet)**:\n"
            informe_md += "Prophet descompone la serie temporal en tendencia, estacionalidad anual y semanal (si se detectan y activan). Esto ayuda a entender los factores que impulsan las predicciones.\n"
            informe_md += f"![Componentes Prophet para {metrica_nombre}]({data['ruta_grafico_componentes']})\n"
            informe_md += "- **Tendencia**: Muestra la dirección general a largo plazo.\n"
            informe_md += "- **Estacionalidad Semanal**: Patrones que se repiten cada semana (ej. picos los fines de semana).\n"
            informe_md += "- **Estacionalidad Anual**: Patrones que se repiten cada año (ej. aumento de ventas en ciertas temporadas).\n\n"
        informe_md += "\n"

    informe_md += "## 4. Conclusiones Generales e Interpretación\n"
    if not df_serie_temporal.empty and len(df_serie_temporal["y"].dropna()) >= 10:
        informe_md += "Al interpretar estos resultados, considera lo siguiente:\n"
        informe_md += "- **Comparación de Modelos**: El modelo con los valores MAE y RMSE más bajos en el conjunto de prueba generalmente se considera el más preciso para los datos históricos recientes. Sin embargo, la simplicidad del modelo y su interpretabilidad también son importantes.\n"
        informe_md += "- **Coherencia con el EDA**: Las predicciones futuras deben ser lógicas y, en general, coherentes con las tendencias y estacionalidades identificadas en el Análisis Exploratorio de Datos. Desviaciones significativas deben ser investigadas.\n"
        informe_md += "- **Incertidumbre de las Predicciones**: Las predicciones futuras siempre conllevan incertidumbre, que tiende a aumentar cuanto más lejano es el horizonte de predicción. Los gráficos de predicción pueden dar una idea visual de esta incertidumbre (ej. si los modelos divergen mucho).\n"
        informe_md += "- **Advertencias del Modelo**: Presta atención a cualquier advertencia impresa en la consola durante la ejecución del script (ej. `ConvergenceWarning` para ARIMA), ya que pueden indicar problemas con el ajuste del modelo.\n"
        informe_md += "- **Contexto del Negocio**: Finalmente, las predicciones deben ser evaluadas en el contexto del negocio. ¿Tienen sentido? ¿Son accionables?\n\n"
        informe_md += "Se recomienda revisar este informe periódicamente con datos actualizados para refinar los modelos y las predicciones.\n"
    else:
        informe_md += "Debido a la insuficiencia de datos, no se pueden extraer conclusiones detalladas del modelado predictivo.\n"

    informe_md += f"\n---\n*Fin del informe. Los gráficos y este archivo Markdown se encuentran en la carpeta: `./{OUTPUT_DIR}`*"

    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write(informe_md)
    print(f"Informe final detallado guardado en: {ruta_informe}")


# --- Flujo Principal (main) ---
def main():
    cprint("===================================================", 'cyan', attrs=['bold'])
    cprint("Script de Análisis y Predicción de Datos de Amaluz", 'cyan', attrs=['bold'])
    cprint("===================================================", 'cyan', attrs=['bold'])

    # Definición de métricas
    metricas_info = {
        1: {"nombre": "Número de Pedidos", "loader": cargar_datos_pedidos, "df_categorias_loader": None},
        2: {"nombre": "Ingresos Totales", "loader": cargar_datos_ingresos, "df_categorias_loader": None},
        3: {"nombre": "Nuevos Clientes Registrados", "loader": cargar_datos_clientes, "df_categorias_loader": None},
        4: {"nombre": "Volumen de Ventas (Total Unidades)", "loader": cargar_datos_ventas_categoria, "df_categorias_loader": True}
    }

    cprint("\nSeleccione la métrica a analizar:", 'yellow')
    for key, value in metricas_info.items():
        print(f"{key}. {colored(value['nombre'], 'yellow')}")

    opcion = 0
    while True:
        try:
            opcion_str = input(f"Ingrese el número de la opción (1-{len(metricas_info)}): ")
            opcion = int(opcion_str)
            if opcion in metricas_info:
                break
            else:
                cprint(f"Opción no válida. Por favor, ingrese un número entre 1 y {len(metricas_info)}.", 'red')
        except ValueError:
            cprint("Entrada no válida. Por favor, ingrese un número.", 'red')

    seleccion_metrica = metricas_info[opcion]
    metrica_nombre = seleccion_metrica["nombre"]
    funcion_carga_datos = seleccion_metrica["loader"]
    carga_categorias = seleccion_metrica["df_categorias_loader"]

    db_url = config.DATABASE_URL_PREDICCIONES
    if not db_url:
        cprint("Error: La URL de la base de datos no está configurada (DATABASE_URL_PREDICCIONES).", 'red', attrs=['bold'])
        cprint("Por favor, configurela en su archivo .env o en la configuración del proyecto.", 'red')
        return

    engine = crear_conexion_db(db_url)
    if engine is None:
        return # Mensaje de error ya impreso en crear_conexion_db

    df_serie_temporal = pd.DataFrame()
    df_categorias_ventas = None # Inicializar

    cprint(f"\nCargando datos para: {colored(metrica_nombre, 'cyan')}...", 'green')
    try:
        if carga_categorias:
            df_serie_temporal, df_categorias_ventas = funcion_carga_datos(engine)
        else:
            df_serie_temporal = funcion_carga_datos(engine)
    except Exception as e:
        cprint(f"Error crítico al cargar datos de la base de datos para '{colored(metrica_nombre, 'cyan')}': {e}", 'red', attrs=['bold'])
        cprint("Asegúrese de que las tablas necesarias (ej. PEDIDO, CLIENTE, PRODUCTOS, DETALLE_PEDIDO) existan, tengan datos y la consulta SQL sea correcta.", 'red')
        if engine: engine.dispose()
        return
    finally:
        if engine:
            engine.dispose()
            cprint("Conexión a la base de datos cerrada.", 'blue')

    if df_serie_temporal.empty or len(df_serie_temporal["y"].dropna()) < 10: # Umbral mínimo de datos
        cprint(f"Datos insuficientes para '{colored(metrica_nombre, 'cyan')}' ({len(df_serie_temporal['y'].dropna())} puntos válidos después de la carga y agregación).", 'red')
        cprint("Se requiere un mínimo de 10 puntos de datos para proceder con el análisis y modelado.", 'red')
        informe_eda_txt = f"## 2. Análisis Exploratorio de Datos para: {metrica_nombre}\n\n**No hay suficientes datos para realizar el análisis exploratorio detallado.**\n"
        generar_informe_final(metrica_nombre, informe_eda_txt, {}, df_serie_temporal)
        return

    cprint(f"Datos cargados exitosamente para: {colored(metrica_nombre, 'cyan')}. Total de registros diarios agregados: {len(df_serie_temporal)}", 'green')

    cprint("\nRealizando Análisis Exploratorio de Datos (EDA)...", 'magenta')
    informe_eda_txt = realizar_eda(df_serie_temporal.copy(), metrica_nombre, df_categorias_ventas)
    cprint("Análisis Exploratorio de Datos completado.", 'magenta')

    cprint("\nIniciando Modelado Predictivo...", 'magenta', attrs=['bold'])
    min_datos_para_split_test = 30
    test_size_prop = 0.2
    n_futuro_pred = 365 # Días a predecir en el futuro

    df_train, df_test = dividir_datos(
        df_serie_temporal,
        test_size=test_size_prop,
        min_train_size=min_datos_para_split_test - int(min_datos_para_split_test * test_size_prop) # Asegurar que min_train_size es para el set de entrenamiento
    )

    if not df_test.empty:
        cprint(f"Datos divididos: {colored(len(df_train), 'blue')} puntos para entrenamiento, {colored(len(df_test), 'blue')} puntos para prueba.", 'green')
    else:
        cprint(f"Se usarán todos los {colored(len(df_train), 'blue')} puntos de datos para entrenamiento (no hay suficientes datos para un conjunto de prueba separado).", 'yellow')

    resultados_modelos = {"n_futuro": n_futuro_pred}
    # Ajustar el orden de ARIMA si es necesario, (1,1,1) es un buen punto de partida para datos con tendencia.
    # (p,d,q): p=periodos auto-regresivos, d=diferenciaciones, q=periodos de media móvil
    modelos_a_ejecutar = {
        "Regresion_Lineal": lambda tr, te, n_futuro: modelo_regresion_lineal(tr, te, n_futuro),
        "ARIMA": lambda tr, te, n_futuro: modelo_arima(tr, te, order=(1,0,1), n_futuro=n_futuro),
        "Prophet": lambda tr, te, n_futuro: modelo_prophet(tr, te, n_futuro),
    }

    # Requisitos mínimos de longitud de datos de entrenamiento para cada modelo
    min_train_len_req = {"Regresion_Lineal": 2, "ARIMA": 10, "Prophet": 10} # Prophet necesita más para estacionalidades

    for nombre_modelo_fn, func_modelo in modelos_a_ejecutar.items():
        cprint(f"\n--- Procesando Modelo: {colored(nombre_modelo_fn.replace('_', ' '), 'cyan')} ---", 'yellow')
        resultados_modelos[nombre_modelo_fn] = {}

        if len(df_train) < min_train_len_req.get(nombre_modelo_fn, 2):
            msg_error = f"Datos de entrenamiento insuficientes ({len(df_train)} puntos) para el modelo {nombre_modelo_fn}. Se requieren al menos {min_train_len_req.get(nombre_modelo_fn, 2)}."
            cprint(msg_error, 'red')
            resultados_modelos[nombre_modelo_fn]["error_evaluacion"] = msg_error
            continue
        try:
            if nombre_modelo_fn == "Prophet":
                pred_train, pred_test, pred_futuro, prophet_model_obj, prophet_forecast_obj = func_modelo(
                    df_train.copy(), df_test.copy(), n_futuro=n_futuro_pred
                )
                # Graficar componentes de Prophet
                fig_comp = prophet_model_obj.plot_components(prophet_forecast_obj)
                # Personalizar títulos de componentes de Prophet si es posible (requiere acceder a los ejes)
                axes_comp = fig_comp.get_axes()
                if axes_comp:
                    axes_comp[0].set_title("Tendencia", fontsize=12) # El primer subplot suele ser la tendencia
                    # Los siguientes dependen de las estacionalidades activadas
                    # Ejemplo: if prophet_model_obj.weekly_seasonality: axes_comp[1].set_title("Estacionalidad Semanal", fontsize=12)
                fig_comp.suptitle(f"Componentes del Modelo Prophet para {metrica_nombre}", fontsize=14, y=1.03)
                plt.tight_layout(rect=[0,0,1,0.97])

                nombre_g_comp_prophet = f'componentes_prophet_{metrica_nombre.lower().replace(" ", "_").replace("(", "").replace(")", "")}.png'
                ruta_g_comp_prophet = os.path.join(OUTPUT_DIR, nombre_g_comp_prophet)
                fig_comp.savefig(ruta_g_comp_prophet)
                plt.close(fig_comp)
                resultados_modelos[nombre_modelo_fn]["ruta_grafico_componentes"] = nombre_g_comp_prophet
            else:
                pred_train, pred_test, pred_futuro = func_modelo(
                    df_train.copy(), df_test.copy(), n_futuro=n_futuro_pred
                )

            nombre_g_pred = graficar_predicciones(
                df_serie_temporal, # Serie completa para el fondo
                df_train, # Datos de entrenamiento para contexto
                df_test, # Datos de prueba para contexto
                {"train": pred_train, "test": pred_test, "future": pred_futuro},
                nombre_modelo_fn,
                metrica_nombre,
            )
            resultados_modelos[nombre_modelo_fn]["ruta_grafico"] = nombre_g_pred

            if not df_test.empty and not pred_test.empty:
                mae, rmse = evaluar_modelo(df_test["y"], pred_test, nombre_modelo_fn)
                resultados_modelos[nombre_modelo_fn].update({"mae": mae, "rmse": rmse})
            elif df_test.empty:
                msg_eval_skip = "No se realizó evaluación en conjunto de prueba (no hay datos de prueba)."
                cprint(msg_eval_skip, 'yellow')
                resultados_modelos[nombre_modelo_fn]["error_evaluacion"] = msg_eval_skip
            else: # pred_test está vacío
                msg_eval_skip_pred = "No se generaron predicciones para el conjunto de prueba."
                cprint(msg_eval_skip_pred, 'yellow')
                resultados_modelos[nombre_modelo_fn]["error_evaluacion"] = msg_eval_skip_pred

        except Exception as e:
            error_msg = f"Error crítico durante el modelado con {colored(nombre_modelo_fn, 'red')}: {e}"
            cprint(error_msg, 'red', attrs=['bold'])
            traceback.print_exc() # Imprimir traceback para depuración
            resultados_modelos[nombre_modelo_fn]["error_evaluacion"] = error_msg

    cprint("\nGenerando informe final detallado...", 'magenta')
    generar_informe_final(
        metrica_nombre, informe_eda_txt, resultados_modelos, df_serie_temporal
    )
    cprint(f"\nProceso completado. Los resultados se encuentran en la carpeta: ./{OUTPUT_DIR}", 'green', attrs=['bold'])


if __name__ == "__main__":
    main()