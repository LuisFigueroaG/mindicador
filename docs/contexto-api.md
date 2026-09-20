# Contexto de la API observada

Fecha de observacion: 2026-09-20. Fuente: https://mindicador.cl/api. Version reportada: 1.7.0.

La API es publica, sin llave ni login. Entrega JSON. Se actualiza varias veces al dia segun el indicador.

Formas observadas:

- `GET /api` entrega foto actual con los 12 indicadores y su ultimo valor.
- `GET /api/{codigo}` entrega la serie reciente del codigo pedido.
- `GET /api/{codigo}/{anio}` entrega la serie del anio pedido.
- `GET /api/{codigo}/{dd-mm-yyyy}` entrega el valor de esa fecha.

Codigos vistos: uf, ivp, dolar, dolar_intercambio, euro, ipc, utm, imacec, tpm, libra_cobre, tasa_desempleo, bitcoin.

Notas para el diseno futuro:

- El formato de fecha puntual exige `dd-mm-yyyy`. Con `yyyy-mm-dd` el server responde 500 con mensaje Fecha incorrecta.
- Las frecuencias varian. UF y dolar son diarias. IPC, UTM e imacec son mensuales. Cada serie trae fecha ISO y valor numerico.
- `dolar_intercambio` lleva fijo desde 2014-11-13. Hay que decidir como tratarlo en docs.
- Errores vistos: 500 con Fecha incorrecta y 404 para rutas malas. El SDK futuro debe normalizar estos casos.
- La fuente es independiente y sin SLA. Si cambia o cae, el SDK debe fallar con mensaje claro.
