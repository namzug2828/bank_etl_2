# Berka Credit Risk ETL

Pipeline ETL en Python orientado a objetos, sobre PostgreSQL, que carga el dataset
bancario público **Berka** (banco checo, ~1,06 millones de transacciones), lo valida
y lo deja listo para análisis de cartera de crédito.

## Arquitectura

```
CSV ──► raw (texto, copia fiel) ──► core (tipado, limpio, PK/FK) ──► analytics (vistas)
                                        │
                                        └──► audit (ejecuciones y resultado de cada regla)
```

| Esquema | Función |
|---|---|
| `raw` | Copia fiel de los CSV, todo como texto. Carga masiva con `COPY`. |
| `core` | Datos tipados con PK, FK y `CHECK`. Montos en `NUMERIC(14,2)`. |
| `audit` | `etl_run` (cada ejecución) y `validation_result` (cada regla por ejecución). |
| `analytics` | Vistas para consultas de cartera. |

## Estructura del paquete

```
src/bank_etl/
├── config.py, db.py          configuración y conexión
├── extract/                  CsvExtractor, RawReader
├── transform/                BaseTransformer (ABC) + un transformer por tabla
├── load/                     RawLoader, CoreLoader (TRUNCATE + COPY atómico)
├── validation/               BaseRule, reglas, Validator
├── audit.py                  AuditLog
└── pipeline.py               Pipeline: orquesta todo y registra la ejecución
sql/                          DDL, vistas y consultas analíticas
tests/                        pytest
```

## Transformaciones destacadas

- Fechas `YYMMDD` a `DATE`.
- `birth_number` decodificado en fecha de nacimiento y género (en mujeres el mes trae +50).
- Valores en checo traducidos con diccionarios explícitos. **Un valor desconocido
  detiene el proceso** en lugar de cargarse en silencio.
- Espacios en blanco a `NULL`; valores no numéricos (`?`) a `NULL` con warning en el log.

## Validaciones (39 reglas por ejecución)

Conciliación de conteos raw vs. core, sumas de control de montos, duplicados de clave,
integridad referencial, nulos en columnas obligatorias, rangos y reglas de negocio
(por ejemplo, un préstamo no puede ser anterior a la cuenta; un titular por cuenta).
Los resultados quedan en `audit.validation_result`. El script termina con código 1
si alguna regla falla.

## Cómo reproducirlo

1. Descarga el dataset Berka (Kaggle, "Berka dataset") y deja los CSV en `data/raw/`.
   Los datos no se versionan.
2. Crea una base en PostgreSQL y ejecuta `sql/01_schema.sql` y `sql/02_audit_error_message.sql`.
3. Copia `.env.example` a `.env` y completa tus credenciales.
4. Instala y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -v
python scripts/run_pipeline.py
```

5. Para el análisis, ejecuta `sql/03_analytics_views.sql` y las consultas de `sql/queries/`.

## Hallazgos del análisis exploratorio

- Mala cartera (estados B o D): ~11% por número de préstamos y ~15% por monto.
- Las diferencias por región, plazo y edad no son concluyentes: son pocos préstamos por grupo.
- Los préstamos B y D tuvieron saldos previos más bajos que A y C. Es una asociación
  exploratoria que requeriría más datos para confirmarse.

## Limitaciones

- Los estados A/B/C/D de `loan.status` se parecen, por analogía, a etapas de riesgo,
  pero no equivalen a las etapas de IFRS 9.
- Recarga completa en cada ejecución (sin cargas incrementales).
- El dataset es histórico (1993-1998) y anonimizado.