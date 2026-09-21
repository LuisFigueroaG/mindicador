# Referencia observada de la API

Fecha: 2026-09-20. Fuente: https://mindicador.cl/api. Version: 1.7.0.
Metodo: pruebas directas con GET. Sin llave. Sin login.

## Base

- Base: `https://mindicador.cl/api`.
- Respuesta: JSON con `Content-Type: application/json; charset=utf-8`.
- Version reportada en cada respuesta: `1.7.0`.
- Autor reportado: `mindicador.cl`.
- Sin autenticacion. Sin cuota documentada. Sin SLA.

## Endpoints

- `GET /api`: foto actual. Trae los 12 indicadores con ultimo valor.
- `GET /api/{codigo}`: serie reciente. Trae 31 puntos.
- `GET /api/{codigo}/{anio}`: serie del anio. Largo variable segun indicador.
- `GET /api/{codigo}/{dd-mm-yyyy}`: valor puntual. Serie con 1 punto o vacia.

Notas de ruta:

- Acepta slash final. `GET /uf/` equivale a `GET /uf`.
- Codigo sensible a mayusculas. `GET /UF` falla como indicador no encontrado.
- Fecha puntual exige `dd-mm-yyyy`. `yyyy-mm-dd` responde 500 con Fecha incorrecta.
- Fecha imposible como `31-02-2024` responde 500 con Fecha incorrecta.
- Texto no fecha como `notafecha` responde 500 con Fecha incorrecta.

## Codigos

El SDK consulta 11. `dolar_intercambio` existe en la API pero se excluye por ser dato descontinuado de 2014.

Foto del 2026-09-20T23:00:00.000Z. Valores de ese momento.

| codigo | nombre | unidad | fecha | valor |
|---|---|---|---|---|
| uf | Unidad de fomento (UF) | Pesos | 2026-09-20T03:00:00.000Z | 40975.41 |
| ivp | Indice de valor promedio (IVP) | Pesos | 2026-09-20T03:00:00.000Z | 42510.85 |
| dolar | Dolar observado | Pesos | 2026-09-17T03:00:00.000Z | 954.85 |
| dolar_intercambio | Dolar acuerdo | Pesos | 2014-11-13T03:00:00.000Z | 758.87 |
| euro | Euro | Pesos | 2026-09-17T03:00:00.000Z | 1100.95 |
| ipc | Indice de Precios al Consumidor (IPC) | Porcentaje | 2025-12-01T03:00:00.000Z | -0.2 |
| utm | Unidad Tributaria Mensual (UTM) | Pesos | 2026-09-01T04:00:00.000Z | 71721 |
| imacec | Imacec | Porcentaje | 2026-07-01T04:00:00.000Z | -1.5 |
| tpm | Tasa Politica Monetaria (TPM) | Porcentaje | 2026-09-17T03:00:00.000Z | 4.5 |
| libra_cobre | Libra de Cobre | Dolar | 2026-09-17T03:00:00.000Z | 6.36 |
| tasa_desempleo | Tasa de desempleo | Porcentaje | 2026-07-01T04:00:00.000Z | 9.53 |
| bitcoin | Bitcoin | Dolar | 2026-09-18T03:00:00.000Z | 80872.23 |

## Forma GET /api

Campos: `version`, `autor`, `fecha`, mas una llave por codigo.

Cada indicador trae: `codigo`, `nombre`, `unidad_medida`, `fecha`, `valor`.

Muestra real recortada:

```json
{
  "version": "1.7.0",
  "autor": "mindicador.cl",
  "fecha": "2026-09-20T23:00:00.000Z",
  "uf": {
    "codigo": "uf",
    "nombre": "Unidad de fomento (UF)",
    "unidad_medida": "Pesos",
    "fecha": "2026-09-20T03:00:00.000Z",
    "valor": 40975.41
  },
  "dolar": {
    "codigo": "dolar",
    "nombre": "Dolar observado",
    "unidad_medida": "Pesos",
    "fecha": "2026-09-17T03:00:00.000Z",
    "valor": 954.85
  }
}
```

Largo total visto: 1710 bytes.

## Forma GET /api/{codigo}

Campos: `version`, `autor`, `codigo`, `nombre`, `unidad_medida`, `serie`.

Cada punto: `fecha` ISO con hora, `valor` numerico.

Orden: descendente. El primero es el mas reciente.

Largo: 31 puntos en los 12 codigos el 2026-09-20.

Muestra `GET /api/uf` recortada a 2 puntos:

```json
{
  "version": "1.7.0",
  "autor": "mindicador.cl",
  "codigo": "uf",
  "nombre": "Unidad de fomento (UF)",
  "unidad_medida": "Pesos",
  "serie": [
    {"fecha": "2026-09-20T03:00:00.000Z", "valor": 40975.41},
    {"fecha": "2026-09-19T03:00:00.000Z", "valor": 40967.24}
  ]
}
```

Bordes de serie reciente vistos:

- uf: 2026-09-20 a 2026-08-21.
- dolar: 2026-09-17 a 2026-08-06.
- dolar_intercambio: 2014-11-13 a 2014-10-01. Serie congelada.
- ipc: 2025-12-01 a 2023-06-01. Dato mensual.
- utm: 2026-09-01 a 2024-03-01. Dato mensual.
- imacec: 2026-07-01 a 2024-01-01. Dato mensual.
- tasa_desempleo: 2026-07-01 a 2024-01-01. Dato mensual.
- bitcoin: 2026-09-18 a 2026-05-21.

## Forma GET /api/{codigo}/{anio}

Misma forma que serie reciente. Serie completa del anio.

Largos vistos:

- `/uf/2024`: 366 puntos. Serie diaria.
- `/dolar_intercambio/2014`: 218 puntos.
- `/dolar_intercambio/2024`: 0 puntos. Responde 200 con serie vacia.
- `/bitcoin/2024`: 91 puntos.
- `/tpm/2024`: 248 puntos.

Muestra `GET /ipc/2024` recortada:

```json
{
  "version": "1.7.0",
  "autor": "mindicador.cl",
  "codigo": "ipc",
  "nombre": "Indice de Precios al Consumidor (IPC)",
  "unidad_medida": "Porcentaje",
  "serie": [
    {"fecha": "2024-12-01T03:00:00.000Z", "valor": -0.2},
    {"fecha": "2024-11-01T03:00:00.000Z", "valor": 0.2}
  ]
}
```

Anio futuro como `/uf/9999` responde 200 con `serie: []`.

## Forma GET /api/{codigo}/{fecha}

Misma forma. Serie con 1 punto si hay dato. Vacia si no hay.

Casos vistos:

- `/uf/20-09-2026`: 200 con 1 punto. Valor 40975.41.
- `/dolar/17-09-2026`: 200 con 1 punto. Valor 954.85.
- `/ipc/01-12-2025`: 200 con 1 punto. Valor -0.2.
- `/uf/01-01-1900`: 200 con `serie: []`.

Muestra:

```json
{
  "version": "1.7.0",
  "autor": "mindicador.cl",
  "codigo": "uf",
  "nombre": "Unidad de fomento (UF)",
  "unidad_medida": "Pesos",
  "serie": [
    {"fecha": "2026-09-20T03:00:00.000Z", "valor": 40975.41}
  ]
}
```

## Errores

Todos los errores vistos usan HTTP 500 con JSON. No se vio 404 en estas pruebas.

Formato:

```json
{"error": "500 Internal Server Error", "message": "...", "description": null}
```

Mensajes vistos:

- `GET /uf/2026-09-20` -> 500, `Fecha incorrecta`.
- `GET /uf/31-02-2024` -> 500, `Fecha incorrecta`.
- `GET /uf/notafecha` -> 500, `Fecha incorrecta`.
- `GET /UF` -> 500, `No se ha encontrado el indicador economico`.
- `GET /invalido` -> 500, `No se ha encontrado el indicador economico`.
- `GET /ruta-mala-xyz` -> 500, `Indicador economico incorrecto`.

Hay dos textos distintos para codigo malo. El SDK debe tratarlos como mismo caso.

## Frecuencias y rarezas

- UF e IVP: diario. Dolar, euro, tpm, cobre: diario habil segun muestra.
- IPC, UTM, imacec, desempleo: mensual. Fecha siempre dia 01.
- `dolar_intercambio` esta fijo desde 2014-11-13. Serie reciente repite octubre y noviembre 2014.
- IPC trae valores negativos y cero. No asumir solo positivos.
- UTM trae enteros. UF trae 2 decimales. Cobre trae 2 decimales.
- Fechas con `T03:00:00.000Z` o `T04:00:00.000Z` segun horario. No asumir hora fija.
- `fecha` de `/api` es hora de consulta. `fecha` por indicador es fecha del dato.

## Notas para desarrollo

- Validar codigo contra lista fija de 12 antes de llamar.
- Validar fecha puntual en `dd-mm-yyyy` en cliente. No mandar otro formato.
- Normalizar los 3 mensajes de error a 2 casos: fecha invalida e indicador invalido.
- Tratar serie vacia como dato valido sin registro. No como error.
- Definir timeout, reintento y cache porque la fuente no da SLA.
- Citar fuente en docs y salidas. Datos de mindicador.cl.
