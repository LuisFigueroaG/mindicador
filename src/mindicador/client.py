"""Cliente sync de lectura para mindicador.cl."""

from __future__ import annotations

from contextlib import suppress
from datetime import date
from time import monotonic
from typing import Any, Self

import httpx
import pandas as pd
import polars as pl

from .errors import CodigoInvalido, ErrorAPI, ErrorRed, FechaInvalida
from .models import Foto, Punto, Serie

BASE_URL = "https://mindicador.cl/api"

CODIGOS = [
    "uf",
    "ivp",
    "dolar",
    "euro",
    "ipc",
    "utm",
    "imacec",
    "tpm",
    "libra_cobre",
    "tasa_desempleo",
    "bitcoin",
]

_MENSAJE_CODIGO = "codigo invalido: {codigo}. Usa uno de: {lista}."
_MENSAJE_FECHA = "fecha invalida: {detalle}."
_MENSAJE_RED = "no se pudo conectar a mindicador.cl: {detalle}."
_MENSAJE_API = "mindicador.cl respondio con error: {detalle}."


class Client:
    """Cliente sync. Solo lectura."""

    def __init__(
        self,
        timeout: float = 10.0,
        base_url: str = BASE_URL,
        transporte: httpx.BaseTransport | None = None,
        cache: bool = False,
        cache_ttl: float = 3600.0,
    ) -> None:
        self._timeout = timeout
        self._base = base_url.rstrip("/")
        self._http = httpx.Client(timeout=timeout, transport=transporte)
        self._cache_on = cache
        self._cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, Any]] = {}

    def cerrar(self) -> None:
        self._http.close()

    def close(self) -> None:
        self.cerrar()

    def limpiar_cache(self) -> None:
        """Borra todo lo guardado en el cache de memoria."""
        self._cache.clear()

    def __del__(self) -> None:
        with suppress(Exception):
            self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.cerrar()

    def actual(self) -> Foto:
        dato = self._get("")
        return Foto.desde_api(dato, CODIGOS)

    def historial(self, codigo: str) -> Serie:
        self._valida_codigo(codigo)
        dato = self._get(f"/{codigo}", codigo)
        return Serie.desde_api(dato)

    def historial_anual(self, codigo: str, anio: int) -> Serie:
        self._valida_codigo(codigo)
        self._valida_anio(anio)
        dato = self._get(f"/{codigo}/{anio}", codigo)
        return Serie.desde_api(dato)

    def puntual(self, codigo: str, fecha: date) -> Punto | None:
        self._valida_codigo(codigo)
        self._valida_fecha(fecha)
        texto = fecha.strftime("%d-%m-%Y")
        dato = self._get(f"/{codigo}/{texto}", codigo)
        serie = Serie.desde_api(dato)
        if not serie.puntos:
            return None
        return serie.puntos[0]

    def historial_df(self, codigo: str) -> pd.DataFrame:
        serie = self.historial(codigo)
        df = pd.DataFrame(
            [{"fecha": p.fecha, "valor": p.valor} for p in serie.puntos],
            columns=["fecha", "valor"],
        )
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df

    def historial_pl(self, codigo: str) -> pl.DataFrame:
        serie = self.historial(codigo)
        df = pl.DataFrame(
            [{"fecha": p.fecha, "valor": p.valor} for p in serie.puntos],
            schema={"fecha": pl.Date, "valor": pl.Float64},
        )
        return df

    def actual_pl(self) -> pl.DataFrame:
        foto = self.actual()
        return pl.DataFrame(
            [
                {
                    "codigo": ind.codigo,
                    "nombre": ind.nombre,
                    "unidad": ind.unidad,
                    "fecha": ind.fecha,
                    "valor": ind.valor,
                }
                for ind in foto.indicadores.values()
            ],
            schema={
                "codigo": pl.String,
                "nombre": pl.String,
                "unidad": pl.String,
                "fecha": pl.Date,
                "valor": pl.Float64,
            },
        )

    def actual_df(self) -> pd.DataFrame:
        foto = self.actual()
        filas = [
            {
                "codigo": ind.codigo,
                "nombre": ind.nombre,
                "unidad": ind.unidad,
                "fecha": ind.fecha,
                "valor": ind.valor,
            }
            for ind in foto.indicadores.values()
        ]
        df = pd.DataFrame(filas, columns=["codigo", "nombre", "unidad", "fecha", "valor"])
        if not df.empty:
            df["fecha"] = pd.to_datetime(df["fecha"])
        return df

    def _valida_codigo(self, codigo: str) -> None:
        if codigo not in CODIGOS:
            raise CodigoInvalido(_MENSAJE_CODIGO.format(codigo=codigo, lista=", ".join(CODIGOS)))

    def _valida_anio(self, anio: int) -> None:
        if not isinstance(anio, int) or isinstance(anio, bool):
            raise FechaInvalida(_MENSAJE_FECHA.format(detalle=f"anio {anio!r} no es entero"))
        if anio < 1 or anio > 9999:
            raise FechaInvalida(_MENSAJE_FECHA.format(detalle=f"anio {anio} fuera de 1 a 9999"))

    def _valida_fecha(self, fecha: date) -> None:
        if not isinstance(fecha, date):
            raise FechaInvalida(_MENSAJE_FECHA.format(detalle=f"fecha {fecha!r} no es date"))

    def _get(self, ruta: str, codigo: str | None = None) -> dict:
        ahora = monotonic()
        if self._cache_on and ruta in self._cache:
            expira, guardado = self._cache[ruta]
            if ahora < expira:
                return guardado
        url = f"{self._base}{ruta}"
        try:
            respuesta = self._http.get(url)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
            try:
                respuesta = self._http.get(url)
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e2:
                raise ErrorRed(_MENSAJE_RED.format(detalle=str(e2))) from e2
        dato = self._revisa(respuesta, codigo)
        if self._cache_on:
            self._cache[ruta] = (ahora + self._cache_ttl, dato)
        return dato

    def _revisa(self, respuesta: httpx.Response, codigo: str | None = None) -> dict:
        try:
            dato = respuesta.json()
        except ValueError as e:
            raise ErrorAPI(_MENSAJE_API.format(detalle="respuesta no JSON")) from e
        if respuesta.status_code == 200:
            if isinstance(dato, dict):
                return dato
            raise ErrorAPI(_MENSAJE_API.format(detalle="respuesta con forma rara"))
        mensaje = ""
        if isinstance(dato, dict):
            mensaje = str(dato.get("message", ""))
        if "Fecha incorrecta" in mensaje:
            raise FechaInvalida(_MENSAJE_FECHA.format(detalle=mensaje))
        if "No se ha encontrado" in mensaje or "incorrecto" in mensaje.lower():
            raise CodigoInvalido(
                _MENSAJE_CODIGO.format(codigo=codigo or "?", lista=", ".join(CODIGOS))
            )
        raise ErrorAPI(_MENSAJE_API.format(detalle=mensaje or f"HTTP {respuesta.status_code}"))
