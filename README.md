<div align="center">

<img src="https://raw.githubusercontent.com/tu-usuario/bimarron/main/assets/logo.jpeg" alt="BiMarrón Logo" width="120" />
  # BiMarrón
  ### Business Intelligence Toolkit

  ---

  *De los datos a las decisiones.*  
  *Inspirado en el espíritu analítico del Cimarrón.*

  ---

</div>

## 📌 ¿Qué es BiMarrón?

**BiMarrón** es un toolkit educativo en Python diseñado específicamente para estudiantes y profesionales de **Inteligencia de Negocios**. 

Proporciona un DSL (*Domain-Specific Language*) con sintaxis fluida y expresiva sobre el motor ultra rápido de **DuckDB**, permitiendo enfocarse 100% en el **razonamiento analítico, la calidad de datos, el modelado dimensional y los KPIs**, sin lidiar con sintaxis complejas o configuraciones pesadas de servidores.

---

## 🚀 Características Clave

* 🛠️ **Módulo ETL Express:** Limpieza de nulos, formateo de tipos y derivación de dimensiones temporales (Año, Mes, Trimestre) en una sola línea.
* 🛡️ **Guardrails de Calidad de Datos:** Reglas de negocio pre-ejecución para detectar inconsistencias antes de analizar.
* ⭐️ **Modelado Dimensional (Star Schema):** Relaciones directas entre tablas de Hechos (*Fact*) y Dimensiones (*Dim*).
* 📈 **Métricas y KPIs Automatizados:** Cálculo fluido de % de cumplimiento de metas y aportación/share sobre el total.
* ⚡ **Motor DuckDB en Memoria:** Procesa archivos `.csv`, `.parquet` y `.json` locales a velocidad relámpago.

---

## 📦 Instalación

Puedes instalar **BiMarrón** directamente desde GitHub usando `pip`:

```bash
pip install git+https://github.com/pakouabc/bimarron.git
```

## Ejemplo de Uso
Un pipeline completo de Inteligencia de Negocios en unos pocos pasos:

```python
from bimarron import BiEngine

# 1. Inicializar con la tabla de hechos
analisis = (
    BiEngine("ventas_fact.csv")
    
    # 2. ETL y Calidad de Datos
    .etl_limpiar_nulos("sucursal_id", "DESCONOCIDA")
    .etl_crear_columna_tiempo("fecha_venta")
    .validar_regla_negocio("monto_venta < 0", "Se detectaron ventas con montos negativos")
    
    # 3. Modelado Dimensional (Star Schema)
    .relacionar_dim("dim_productos.csv", "prod", "producto_id", "id")
    
    # 4. Análisis OLAP y KPIs
    .dimension("anio", "prod.categoria_nombre")
    .metrica("total_ventas", "SUM(monto_venta)")
    .kpi_cumplimiento_meta(nombre_kpi="meta_anual", metrica_real="monto_venta", valor_meta=500000.0)
    .kpi_participacion_porcentaje("share_categoria", "monto_venta")
    
    # 5. Ejecutar
    .ejecutar()
)

print(analisis)


```


## Contenido de archivos CSV 
- ventas_fact.csv
```csv
id,fecha_venta,sucursal_id,producto_id,monto_venta,cantidad
1001,2026-01-15,1,101,150.50,1
1002,2026-01-16,1,102,450.00,3
1003,2026-01-20,2,103,1200.00,1
1004,2026-02-01,1,101,300.00,2
1005,2026-02-05,3,104,80.00,4
1006,2026-02-12,,102,150.00,1
1007,2026-02-18,2,105,-50.00,1
1008,2026-03-02,3,103,2400.00,2
1009,2026-03-10,1,104,40.00,2
1010,2026-03-15,2,101,150.50,1
1011,2026-03-22,3,102,600.00,4
1012,2026-03-28,1,105,850.00,2

```

- dim_productos.csv
```csv
id,producto_nombre,categoria_nombre,precio_lista
101,Teclado Mecánico,Periféricos,150.50
102,Mouse Inalámbrico,Periféricos,150.00
103,Monitor 27 Pulgadas,Pantallas,1200.00
104,Cable HDMI 2m,Accesorios,20.00
105,Silla Ergonómica,Mobiliario,425.00

```