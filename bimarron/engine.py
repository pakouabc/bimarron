import duckdb
import pandas as pd


class BIEngine:

  def __init__(self, fact_file: str):
    self.conn = duckdb.connect(database=":memory:")
    self.fact_file = fact_file
    self.dims = []
    self.metrics = []
    self.filters = []
    self.sorts = []
    self.joins = []
    self.kpis = []

    # Cargar tabla de hechos principal
    self.conn.execute(
        f"CREATE TABLE fact_table AS SELECT * FROM '{self.fact_file}'"
    )

  # ==========================================
  # 1. MÓDULO ETL (Transformación y Limpieza)
  # ==========================================
  def etl_limpiar_nulos(self, columna: str, valor_por_defecto):
    """Reemplaza valores nulos en una columna, convirtiendo el tipo si es necesario."""
    # Si el valor por defecto es un string, aseguramos que la columna sea de tipo VARCHAR
    if isinstance(valor_por_defecto, str):
      self.conn.execute(
          f"ALTER TABLE fact_table ALTER COLUMN {columna} TYPE VARCHAR"
      )

    self.conn.execute(f"""
          UPDATE fact_table 
          SET {columna} = COALESCE({columna}, '{valor_por_defecto}')
      """)
    return self

  def etl_crear_columna_tiempo(self, columna_fecha: str):
    """Extrae automáticamente Año, Mes y Trimestre para análisis temporal."""
    self.conn.execute(f"""
            ALTER TABLE fact_table ADD COLUMN anio INTEGER;
            ALTER TABLE fact_table ADD COLUMN mes INTEGER;
            ALTER TABLE fact_table ADD COLUMN trimestre INTEGER;

            UPDATE fact_table SET 
                anio = YEAR(CAST({columna_fecha} AS DATE)),
                mes = MONTH(CAST({columna_fecha} AS DATE)),
                trimestre = QUARTER(CAST({columna_fecha} AS DATE));
        """)
    return self

  # ==========================================
  # 2. MÓDULO MODELADO DIMENSIONAL (Star Schema)
  # ==========================================
  def relacionar_dim (
      self,
      dim_file: str,
      alias_dim: str,
      fk_fact: str,
      pk_dim: str,
  ):
    """Realiza un JOIN limpio entre la tabla de Hechos y una Dimensión."""
    self.conn.execute(
        f"CREATE TABLE {alias_dim} AS SELECT * FROM '{dim_file}'"
    )
    self.joins.append(
        f"LEFT JOIN {alias_dim} ON fact_table.{fk_fact} = {alias_dim}.{pk_dim}"
    )
    return self

  # ==========================================
  # 3. MÓDULO ANÁLISIS OLAP (Dimensiones y Métricas)
  # ==========================================
  def dimension(self, *cols):
    self.dims.extend(cols)
    return self

  def metrica(self, nombre: str, expresion: str):
    self.metrics.append(f"{expresion} AS {nombre}")
    return self

  def filtrar(self, condicion: str):
    self.filters.append(condicion)
    return self

  # ==========================================
  # 4. MÓDULO KPIs (Indicadores Clave de Negocio)
  # ==========================================
  def kpi_cumplimiento_meta(
      self, nombre_kpi: str, metrica_real: str, valor_meta: float
  ):
    """Calcula el % de cumplimiento de una meta de negocio."""
    exp = (
        f"ROUND((SUM({metrica_real}) / {valor_meta}) * 100, 2) || '%'"
    )
    self.metrics.append(f"{exp} AS {nombre_kpi}")
    return self

  def kpi_participacion_porcentaje(
      self, nombre_kpi: str, columna_monto: str
  ):
    """Calcula el porcentaje de aporte de cada dimensión al total general."""
    exp = f"ROUND((SUM({columna_monto}) / SUM(SUM({columna_monto})) OVER()) * 100, 2)"
    self.metrics.append(f"{exp} AS {nombre_kpi}_pct")
    return self

  # ==========================================
  # 5. MÓDULO CALIDAD DE DATOS (Data Quality Guardrails)
  # ==========================================
  def validar_regla_negocio(self, condicion_error: str, mensaje_error: str):
    """Comprueba si existen datos corruptos que violen reglas de negocio."""
    conteo = self.conn.execute(
        f"SELECT COUNT(*) FROM fact_table WHERE {condicion_error}"
    ).fetchone()[0]
    if conteo > 0:
      print(f"⚠️ [ALERTA DE CALIDAD]: {mensaje_error} ({conteo} registros infectados)")
    else:
      print("✅ [CALIDAD OK]: Regla de negocio validada correctamente.")
    return self

  # ==========================================
  # EJECUCIÓN Y SALIDA
  # ==========================================
  def ejecutar(self) -> pd.DataFrame:
    select_items = self.dims + self.metrics
    select_clause = ", ".join(select_items) if select_items else "*"

    query = f"SELECT {select_clause} FROM fact_table"

    if self.joins:
      query += " " + " ".join(self.joins)

    if self.filters:
      query += " WHERE " + " AND ".join(self.filters)

    if self.dims:
      group_indices = ", ".join([str(i + 1) for i in range(len(self.dims))])
      query += f" GROUP BY {group_indices}"

    return self.conn.execute(query).df()
