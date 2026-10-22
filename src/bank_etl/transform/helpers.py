import logging

import pandas as pd

logger = logging.getLogger(__name__)


def blank_to_null(s: pd.Series) -> pd.Series:
    """Texto sin espacios; cadenas vacías pasan a NULL real."""
    return s.astype("string").str.strip().replace({"": pd.NA})


def to_number(s: pd.Series, label: str = "") -> pd.Series:
    """Convierte a número; lo que no se pueda (ej. '?') pasa a NULL y se registra."""
    clean = blank_to_null(s)
    result = pd.to_numeric(clean, errors="coerce")
    coerced = int((result.isna() & clean.notna()).sum())
    if coerced:
        logger.warning("%s: %s valores no numéricos convertidos a NULL", label, coerced)
    return result


def parse_yymmdd(s: pd.Series, label: str = "") -> pd.Series:
    """'930101' o '931107 00:00:00' -> fecha. Siempre siglo XX (1900+yy)."""
    clean = blank_to_null(s).str.slice(0, 6)
    parsed = pd.to_datetime("19" + clean, format="%Y%m%d", errors="coerce")
    bad = int((parsed.isna() & clean.notna()).sum())
    if bad:
        logger.warning("%s: %s fechas inválidas convertidas a NULL", label, bad)
    return parsed


def map_values(s: pd.Series, mapping: dict[str, str], label: str = "") -> pd.Series:
    """Traduce valores. Si aparece uno que no está en el diccionario, falla (no se asume nada)."""
    clean = blank_to_null(s)
    unknown = sorted(set(clean.dropna().unique()) - set(mapping))
    if unknown:
        raise ValueError(f"{label}: valores sin traducción definida: {unknown}")
    return clean.map(mapping)