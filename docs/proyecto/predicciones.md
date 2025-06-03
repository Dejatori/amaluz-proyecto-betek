# Documentación del Script de Predicciones (`predicciones.py`)

## 1. Introducción

El script `predicciones.py` está diseñado para realizar un análisis de series temporales y generar predicciones sobre
diversas métricas de negocio de Amaluz. Se conecta a una base de datos MySQL, carga datos históricos, realiza un
Análisis Exploratorio de Datos (EDA), entrena varios modelos predictivos (Regresión Lineal, ARIMA, Prophet) y genera un
informe detallado en formato Markdown con los resultados y gráficos.

El objetivo principal es proporcionar información sobre tendencias pasadas y futuras esperadas para métricas clave como:

* Número de pedidos.
* Ingresos totales.
* Crecimiento de nuevos clientes.
* Volumen de ventas (total y por categoría).

## 2. Funcionamiento del Script

El script sigue un flujo de trabajo estructurado:

### 2.1. Configuración Inicial

* Utiliza la configuración centralizada de la aplicación (`app.core.config`) para obtener la URL de la base de datos (
  `DATABASE_URL_PREDICCIONES`), la cual se define a través de variables de entorno (ver archivo `.env`).
* Define el directorio de salida para los informes y gráficos (`docs/proyecto/analisis_resultados_amaluz`).
* Configura el logging para reducir la verbosidad de algunas librerías (Prophet, CmdStanPy).

### 2.2. Conexión a la Base de Datos

* La función `crear_conexion_db` establece una conexión con la base de datos MySQL utilizando SQLAlchemy.
* La URL de conexión se obtiene automáticamente de la configuración del proyecto (`config.DATABASE_URL_PREDICCIONES`).
  Ya no es necesario ingresarla manualmente.

### 2.3. Selección de Métrica y Carga de Datos

* El script solicita al usuario que seleccione la métrica que desea analizar de una lista predefinida.
* Según la opción elegida, se ejecutan funciones específicas para cargar y preprocesar los datos correspondientes desde
  la base de datos:
    * `cargar_datos_pedidos`: Número de pedidos diarios.
    * `cargar_datos_ingresos`: Suma de ingresos diarios.
    * `cargar_datos_clientes`: Número de nuevos clientes registrados diariamente.
    * `cargar_datos_ventas_categoria`: Volumen total de ventas diarias y desglosado por categoría de producto.
* Los datos se agregan a una frecuencia diaria (`D`) y se formatean en un DataFrame con columnas `ds` (fecha) e `y` (
  valor de la métrica), que es el formato esperado por muchos modelos de series temporales como Prophet.

### 2.4. Análisis Exploratorio de Datos (EDA)

* La función `realizar_eda` toma la serie temporal preparada y genera un análisis visual y descriptivo:
    * Gráfico de la serie temporal original.
    * Gráfico de tendencia (usando media móvil).
    * Cálculo de tasas de crecimiento.
    * Gráfico de descomposición estacional (tendencia, estacionalidad semanal, residuos).
    * Si aplica (para volumen de ventas), gráfico de ventas por categoría.
* Todos los gráficos generados se guardan como imágenes PNG en el directorio de salida.
* Se genera un texto en formato Markdown que resume los hallazgos del EDA, el cual se incluye en el informe final.

### 2.5. Modelado Predictivo

* **División de datos**: La función `dividir_datos` separa la serie temporal en conjuntos de entrenamiento y prueba. Por
  defecto, se utiliza el 20% más reciente de los datos para prueba, sin barajar, para mantener la secuencia temporal.
* **Modelos Implementados**: Se ejecutan varios modelos de series temporales:
    * **Regresión Lineal**: Modela una tendencia lineal simple sobre el tiempo.
    * **ARIMA (Autoregressive Integrated Moving Average)**: Modelo estadístico que utiliza los valores pasados y errores
      de pronóstico para predecir valores futuros. El orden (p,d,q) es configurable en el script (actualmente `(1,1,1)`
      en `main`).
    * **Prophet**: Desarrollado por Facebook, es robusto ante datos faltantes y cambios de tendencia, y maneja bien
      múltiples estacionalidades (anual, semanal).
* **Entrenamiento y Predicción**:
    * Cada modelo se entrena con el conjunto de entrenamiento.
    * Se generan predicciones sobre el conjunto de entrenamiento (para ver el ajuste), sobre el conjunto de prueba (para
      evaluación) y para un período futuro (configurable, por defecto 365 días).
* **Ajuste de Predicciones Negativas**: Para métricas donde los valores negativos no tienen sentido (ej. ingresos,
  número de pedidos), el script ajusta automáticamente las predicciones negativas a cero. Esta corrección se indica en
  el informe final.
* **Visualización de Predicciones**: La función `graficar_predicciones` crea un gráfico para cada modelo, mostrando los
  datos reales, las predicciones de entrenamiento, las predicciones de prueba y las predicciones futuras. Estos gráficos
  también se guardan como archivos PNG.
* **Evaluación del Modelo**: La función `evaluar_modelo` calcula dos métricas de error en el conjunto de prueba:
    * Error Absoluto Medio (MAE).
    * Raíz del Error Cuadrático Medio (RMSE).

### 2.6. Generación de Informe Final

* La función `generar_informe_final` compila todos los resultados en un único archivo Markdown (
  `informe_completo_{metrica}.md`) en el directorio de salida.
* Este informe incluye:
    * Resumen de la métrica analizada y fecha de generación.
    * La sección completa del Análisis Exploratorio de Datos (texto y enlaces a imágenes).
    * Resultados detallados para cada modelo predictivo:
        * Gráfico de predicciones.
        * Métricas MAE y RMSE (si el conjunto de prueba no estaba vacío).
        * Para Prophet, gráfico de componentes (tendencia, estacionalidades).
        * Nota sobre el ajuste de predicciones negativas si se aplicó.

## 3. Interpretación de los Resultados

El script genera un informe en formato Markdown y varios archivos de imagen que ayudan a comprender el comportamiento de
la métrica y la calidad de las predicciones.

### 3.1. Informe en Markdown (`informe_completo_{metrica}.md`)

Este es el principal entregable. Contiene:

* **Sección de EDA**:
    * **Gráfico de Serie Temporal**: Observa la evolución general. ¿Hay picos, valles, patrones repetitivos, valores
      anómalos evidentes?
    * **Gráfico de Tendencia**: ¿La métrica está creciendo, disminuyendo o se mantiene estable a largo plazo? El texto
      indicará la dirección de la tendencia inferida por la media móvil.
    * **Tasas de Crecimiento**: Cuantifican el cambio a lo largo del período analizado. Ayudan a entender la magnitud
      del cambio.
    * **Gráfico de Descomposición Estacional**: Ayuda a identificar patrones que se repiten en intervalos fijos (ej.
      semanalmente).
        * `Observed`: Los datos originales.
        * `Trend`: La tendencia subyacente una vez eliminada la estacionalidad y el ruido.
        * `Seasonal`: El patrón estacional aislado (ej. patrón semanal).
        * `Resid`: El ruido o los componentes irregulares que no son explicados por la tendencia y la estacionalidad. Un
          residuo aleatorio es ideal.
    * **Análisis por Categoría (si aplica)**: Permite comparar el rendimiento entre diferentes categorías de productos.
      Observa qué categorías dominan y cómo evolucionan sus ventas.
* **Sección de Resultados de Modelos Predictivos**:
    * Para cada modelo (Regresión Lineal, ARIMA, Prophet):
        * **Gráfico de Predicciones**: Es crucial para una evaluación visual.
            * **Ajuste en Entrenamiento (naranja)**: ¿Qué tan bien sigue el modelo los datos con los que fue entrenado?
              Un ajuste perfecto puede indicar sobreajuste.
            * **Ajuste en Prueba (verde)**: ¿Qué tan bien predice el modelo datos que no ha visto? Esta es una medida
              clave de generalización.
            * **Predicciones Futuras (rojo)**: ¿Son lógicas las predicciones? ¿Siguen la tendencia y estacionalidad
              observadas? ¿Hay valores extraños (ej. negativos para ingresos, si no se hubieran ajustado)?
            * Compara la forma de las predicciones con los datos reales. ¿Captura el modelo los picos y valles
              importantes?
        * **Métricas MAE y RMSE**: Explicadas en la siguiente sección.
        * **Gráfico de Componentes de Prophet**: Muestra la tendencia general detectada por Prophet, así como las
          estacionalidades (anual, semanal) que el modelo ha identificado. Es útil para entender qué patrones está
          usando Prophet para predecir.
        * **Nota sobre ajuste de predicciones negativas**: Si se aplicó, se mencionará aquí.

### 3.2. Métricas de Evaluación: MAE y RMSE

Estas métricas se calculan sobre el **conjunto de prueba** y miden el error promedio de las predicciones del modelo en
datos que no utilizó para entrenar. Valores más bajos indican un mejor rendimiento.

* **Error Absoluto Medio (MAE)**:
    * **Qué es**: Es el promedio de las diferencias absolutas entre los valores predichos y los valores reales.
    * **Interpretación**: Indica, en promedio, cuánto se equivocan las predicciones del modelo, en las mismas unidades
      que la variable original. Por ejemplo, si el MAE para "Ingresos Totales" es 1000, significa que las predicciones
      de ingresos se desvían, en promedio, en 1000 unidades monetarias del valor real.
    * **Ventaja**: Fácil de interpretar. Menos sensible a errores grandes puntuales.
    * **Desventaja**: No penaliza más los errores grandes que los pequeños.

* **Raíz del Error Cuadrático Medio (RMSE)**:
    * **Qué es**: Es la raíz cuadrada del promedio de las diferencias al cuadrado entre los valores predichos y los
      valores reales.
    * **Interpretación**: Similar al MAE, mide el error promedio en las unidades de la variable original. Sin embargo,
      al elevar al cuadrado los errores antes de promediarlos, el RMSE penaliza más los errores grandes.
    * **Ventaja**: Penaliza errores grandes, lo cual puede ser útil si estos son particularmente indeseables.
    * **Desventaja**: Más sensible a valores atípicos (outliers) que el MAE. Si el RMSE es considerablemente mayor que
      el MAE, sugiere que el modelo está cometiendo algunos errores grandes.

**Cómo usar MAE y RMSE para comparar modelos:**

1. **Comparar entre modelos para la misma métrica**: El modelo con el MAE y RMSE más bajos generalmente se considera el
   mejor en términos de precisión predictiva en el conjunto de prueba.
2. **Relacionar con la escala de los datos**: Un MAE de 100 es diferente si los valores típicos de la métrica son 200 (
   error del 50%) o 10,000 (error del 1%). Observa la gráfica de la serie temporal para entender la magnitud de tus
   datos y contextualizar el error.
3. **Analizar la diferencia entre RMSE y MAE**:
    * Si RMSE ≈ MAE: Todos los errores tienden a ser de una magnitud similar.
    * Si RMSE > MAE: Hay algunos errores grandes que inflan el RMSE. Investiga en los gráficos de predicción cuándo
      ocurren estos errores.

### 3.3. Consideraciones Adicionales para la Interpretación

* **Advertencias del Modelo**: Presta atención a cualquier advertencia impresa en la consola durante la ejecución del
  script (ej. `ConvergenceWarning` para ARIMA). Estas pueden indicar que el modelo no se ajustó correctamente y las
  predicciones podrían no ser confiables, incluso si el MAE/RMSE parece bueno.
* **Lógica del Negocio**: Las predicciones deben tener sentido en el contexto del negocio.
    * El script ahora ajusta predicciones negativas a cero para métricas como ingresos o volumen de ventas. El informe
      indicará si se realizó este ajuste. Es importante ser consciente de esta corrección automática.
    * Si las predicciones, incluso después del ajuste, parecen ilógicas (ej. un crecimiento explosivo sin
      justificación), el modelo debe ser revisado.
* **Coherencia con el EDA**: Las predicciones futuras deben ser, en general, coherentes con las tendencias y
  estacionalidades identificadas en el EDA. Si el EDA muestra una fuerte tendencia descendente, pero un modelo predice
  un aumento repentino sin una justificación clara (ej. una estacionalidad anual muy fuerte que el EDA también muestre),
  el modelo podría ser sospechoso.
* **Cantidad de Datos**: La fiabilidad de las predicciones depende de la cantidad y calidad de los datos históricos. Con
  pocos datos (ej. menos de dos ciclos estacionales completos), los modelos pueden tener dificultades para aprender
  patrones complejos o generalizar bien. El script indica si los datos son insuficientes para ciertos análisis o
  modelos.

## 4. Uso del Script

### 4.1. Requisitos

* Python 3.8 o superior (recomendado 3.11+).
* Las librerías listadas en los `import` al inicio del script (`pandas`, `numpy`, `sqlalchemy`, `statsmodels`,
  `scikit-learn`, `prophet`, `matplotlib`, `pymysql`, `seaborn`, `termcolor`, `etc`). Puedes instalarlas usando pip:
  ```bash
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```
* Acceso a una base de datos MySQL con el esquema y datos de Amaluz.
* Archivo `.env` configurado correctamente con la variable `DEV_DATABASE_URL_PREDICCIONES` (o
  `PROD_DATABASE_URL_PREDICCIONES` según el `ENV_STATE`) apuntando a tu base de datos de predicciones. Ejemplo:
  `DEV_DATABASE_URL_PREDICCIONES=mysql+pymysql://tu_usuario:tu_contraseña@localhost:3308/amaluz`

### 4.2. Ejecución

1. Asegúrate de que tu archivo `.env` esté configurado con la URL correcta para `DATABASE_URL_PREDICCIONES`
   correspondiente a tu `ENV_STATE`.
2. Navega al directorio raíz de tu proyecto (donde se encuentra el script `predicciones.py`, usualmente en una
   subcarpeta como `scripts/` o similar, o ajústalo si está en la raíz).
3. Ejecuta el script desde la terminal:
   ```bash
   python predicciones.py 
   ```
   (O `python app/scripts/predicciones.py` si está dentro de `app/scripts` y lo ejecutas desde la raíz del proyecto,
   ajusta la ruta según tu estructura).
4. El script te pedirá que selecciones la métrica a analizar ingresando un número.
5. El script procesará los datos, ejecutará los modelos y generará el informe. Los resultados se guardarán en la carpeta
   `docs/proyecto/analisis_resultados_amaluz/`.

### 4.3. Modificación de Parámetros

El script está diseñado para ser configurable directamente en el código fuente (`predicciones.py`), principalmente
dentro de la función `main()`:

* **URL de la Base de Datos**: Se configura a través del archivo `.env` y `app.core.config.py` (variable
  `DATABASE_URL_PREDICCIONES`).
* **Horizonte de Predicción**: La variable `n_futuro_pred` en la función `main` controla cuántos días hacia el futuro se
  predicen (por defecto 365).
* **Parámetros de ARIMA**: El `order` de ARIMA (p,d,q) se define en el diccionario `modelos_a_ejecutar` dentro de
  `main`. Puedes cambiar `(1,1,1)` a otros valores si deseas experimentar.
* **Modelos a Ejecutar**: Puedes comentar o descomentar líneas en el diccionario `modelos_a_ejecutar` para incluir o
  excluir modelos del análisis.
* **Ajuste de Predicciones No Negativas**: La lógica para decidir qué métricas requieren este ajuste está en `main()` en
  el diccionario `metrica_info`.
* **Directorio de Salida**: La variable `OUTPUT_DIR` al inicio del script define dónde se guardan los informes.