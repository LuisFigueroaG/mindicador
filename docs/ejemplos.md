# Ejemplos con salidas reales

Datos del 2026-09-21. Fuente: mindicador.cl.

## Foto actual

```python
foto = cli.actual()
print(foto.fecha)
print(foto.indicadores["uf"])
```

```text
2026-09-21T02:00:00+00:00
codigo='uf' nombre='Unidad de fomento (UF)' unidad='Pesos' fecha=datetime.date(2026, 9, 20) valor=40975.41
```

## Serie reciente

```python
serie = cli.historial("uf")
print(serie.codigo, serie.nombre, len(serie.puntos))
print(serie.puntos[0])
```

```text
uf Unidad de fomento (UF) 31
fecha=datetime.date(2026, 9, 20) valor=40975.41
```

## Serie por año

```python
anual = cli.historial_anual("ipc", 2024)
print(len(anual.puntos), anual.puntos[0])
```

```text
12 fecha=datetime.date(2024, 12, 1) valor=-0.2
```

## Valor puntual

```python
from datetime import date

print(cli.puntual("dolar", date(2026, 9, 17)))
print(cli.puntual("uf", date(1900, 1, 1)))
```

```text
fecha=datetime.date(2026, 9, 17) valor=954.85
None
```

## DataFrames

```python
print(cli.historial_df("uf").head(3).to_string(index=False))
print(cli.actual_df()[["codigo", "valor"]].to_string(index=False))
```

```text
     fecha    valor
2026-09-20 40975.41
2026-09-19 40967.24
2026-09-18 40959.07

        codigo    valor
            uf 40975.41
           ivp 42510.85
         dolar   954.85
          euro  1100.95
           ipc    -0.20
           utm 71721.00
        imacec    -1.50
           tpm     4.50
   libra_cobre     6.36
tasa_desempleo     9.53
       bitcoin 80872.23
```

## Cache

```python
with Client(cache=True) as cli:
    cli.actual()  # llama a la API
    cli.actual()  # sale del caché
    cli.limpiar_cache()
    cli.actual()  # llama de nuevo
```
