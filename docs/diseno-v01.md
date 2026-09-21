# Diseno v0.1 (propuesta)

Base: `docs/decisiones.md` del 2026-09-21 y `docs/api-referencia.md`.
Estado: propuesta original de v0.1. Superada en 0.2 por el cache opt-in y en 0.3 por Polars obligatorio.

## Objetivo

Cliente sync de lectura. Cubre las 4 formas reales. Falla en espanol claro.

## Modelos (Pydantic)

- `Punto`: `fecha: date`, `valor: float`.
- `IndicadorActual`: `codigo: str`, `nombre: str`, `unidad: str`, `fecha: date`, `valor: float`.
- `Serie`: `codigo: str`, `nombre: str`, `unidad: str`, `puntos: list[Punto]`. Orden descendente como la API.
- `Foto`: `fecha: datetime`, `indicadores: dict[str, IndicadorActual]`. 11 llaves (sin dolar_intercambio, excluido por descontinuado).

## Cliente

```python
from datetime import date
import mindicador

cli = mindicador.Client(timeout=10.0)
actual = cli.actual()
serie = cli.historial("uf")
anual = cli.historial_anual("uf", 2024)
punto = cli.puntual("uf", date(2026, 9, 20))
```

Reglas:

- `codigo` se valida contra los 12 fijos. Invalido falla local sin llamar.
- `anio` es `int`. Rango 1900 a anio actual. Futuro como 9999 se permite y retorna serie vacia como la API.
- `fecha` es `date`. Se formatea a `dd-mm-yyyy` dentro. No se acepta string.
- `puntual` retorna `Punto | None`. `None` cuando la serie viene vacia. No es error.
- `serie` y `serie_anio` retornan `Serie` aunque venga vacia.
- `timeout` en segundos. Por defecto 10. Reintento simple solo en falla de red.

## Errores

Base `MindicadorError`. Hijos:

- `CodigoInvalido`: "codigo invalido: {codigo}. Usa uno de: uf, dolar...".
- `FechaInvalida`: "fecha invalida: {detalle}. Usa date valida o anio entre 1900 y {actual}".
- `ErrorRed`: "no se pudo conectar a mindicador.cl: {detalle}".
- `ErrorAPI`: "mindicador.cl respondio con error: {mensaje}".

Los 3 mensajes raros de la API se mapean a estos 2 casos. Serie vacia no es error.

## Pandas en v0.1

Minimo util sin atar Polars:

```python
df = cli.historial_df("uf")
actual_df = cli.actual_df()
```

- `serie_df` columnas: `fecha`, `valor`. `fecha` como fecha.
- `foto_df` columnas: `codigo`, `nombre`, `unidad`, `fecha`, `valor`.
- Polars queda para 1.0. Los modelos Pydantic ya exponen `puntos` e `indicadores` para mapear sin reescribir.

## Lo que no entra

Sin cache, sin CLI, sin async. Solo `httpx`, `pydantic` y `pandas` como runtime.

## Decisiones finas (2026-09-21)

- Nombres largos: `actual`, `historial`, `historial_anual`, `puntual`.
- `puntual` retorna `None` sin dato.
- `pandas` obligatoria en v0.1.
