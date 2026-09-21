# mindicador

SDK simple en Python para consultar mindicador.cl.

Lee indicadores económicos chilenos desde Python. Pensado para uso directo en scripts y análisis.

Estado: versión `0.x` en desarrollo. Aún no está en PyPI. Se instala desde GitHub.

Fuente de datos: mindicador.cl. Proyecto independiente, sin afiliación con este SDK ni con el Banco Central de Chile. Los datos pertenecen a sus fuentes. Cita la fuente cuando uses los valores.

## Instalación

Con `uv`:

```bash
uv add "mindicador @ git+https://github.com/LuisFigueroaG/mindicador.git"
```

Con `pip`:

```bash
pip install "mindicador @ git+https://github.com/LuisFigueroaG/mindicador.git"
```

Requiere Python 3.12 o más. Incluye `httpx`, `pydantic` y `pandas`.

## Uso rápido

```python
from mindicador import Client

with Client() as cli:
    foto = cli.actual()
    print(foto.indicadores["uf"].valor)
```

Salidas reales de cada método: ver `docs/ejemplos.md`.

## Métodos

### Foto actual

Trae los 11 indicadores con su último valor.

```python
foto = cli.actual()
print(foto.fecha)
for codigo, ind in foto.indicadores.items():
    print(codigo, ind.valor, ind.unidad, ind.fecha)
```

### Serie reciente

Trae los últimos 31 puntos del código pedido.

```python
serie = cli.historial("uf")
for punto in serie.puntos[:3]:
    print(punto.fecha, punto.valor)
```

### Serie por año

Trae la serie completa del año. Acepta cualquier año entre 1 y 9999. Un año sin datos retorna serie vacía.

```python
anual = cli.historial_anual("ipc", 2024)
print(len(anual.puntos))
```

### Valor puntual

Trae el valor de una fecha. Recibe `date`, no texto. Sin dato retorna `None`.

```python
from datetime import date

punto = cli.puntual("dolar", date(2026, 9, 17))
print(punto.valor if punto else "sin dato")
```

### DataFrames

```python
df = cli.historial_df("uf")
print(df.head())

actual_df = cli.actual_df()
print(actual_df[["codigo", "valor"]])
```

Columnas de serie: `fecha`, `valor`. Columnas de foto: `codigo`, `nombre`, `unidad`, `fecha`, `valor`.

### Caché en memoria

Apagado por defecto. Se prende con `cache=True`. Guarda las 4 lecturas con TTL de 1 hora.

```python
from mindicador import Client

with Client(cache=True) as cli:
    cli.actual()
    cli.actual()  # sale del caché

cli.limpiar_cache()  # fuerza datos frescos
```

Para otro TTL en segundos: `Client(cache=True, cache_ttl=900)`.

## Códigos

`uf`, `ivp`, `dolar`, `euro`, `ipc`, `utm`, `imacec`, `tpm`, `libra_cobre`, `tasa_desempleo`, `bitcoin`.

El código es sensible a mayúsculas. Un código fuera de la lista falla local sin llamar a la API. `dolar_intercambio` no es consultable por ser un dato descontinuado de 2014.

## Errores

Todos heredan de `MindicadorError`. Mensajes en español.

| Error | Cuándo sale |
|---|---|
| `CodigoInvalido` | Código fuera de la lista de 11. |
| `FechaInvalida` | Año o fecha con forma o rango inválido. |
| `ErrorRed` | Falla de conexión o timeout, con 1 reintento. |
| `ErrorAPI` | La API respondió con un error no mapeado. |

```python
from mindicador import Client, CodigoInvalido

with Client() as cli:
    try:
        cli.historial("UF")
    except CodigoInvalido as e:
        print(e)
```

El cliente usa timeout de 10 segundos por defecto: `Client(timeout=10.0)`.

## Desarrollo

```bash
uv sync --group dev
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright src/mindicador
uv run pytest -q tests
```
