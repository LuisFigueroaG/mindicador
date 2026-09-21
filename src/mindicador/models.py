"""Modelos Pydantic del SDK."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from .errors import ErrorAPI

_MENSAJE_FORMA = "mindicador.cl respondio con dato con forma rara: {detalle}."


def _solo_fecha(valor: str) -> date:
    try:
        return date.fromisoformat(valor[:10])
    except (ValueError, TypeError) as e:
        raise ErrorAPI(_MENSAJE_FORMA.format(detalle=f"fecha {valor!r}")) from e


def _a_datetime(valor: str) -> datetime:
    try:
        return datetime.fromisoformat(valor)
    except (ValueError, TypeError) as e:
        raise ErrorAPI(_MENSAJE_FORMA.format(detalle=f"fecha {valor!r}")) from e


class Punto(BaseModel):
    fecha: date
    valor: float

    @classmethod
    def desde_api(cls, dato: dict[str, Any]) -> Punto:
        try:
            return cls(fecha=_solo_fecha(str(dato["fecha"])), valor=float(dato["valor"]))
        except ErrorAPI:
            raise
        except (KeyError, TypeError, ValueError, ValidationError) as e:
            raise ErrorAPI(_MENSAJE_FORMA.format(detalle="punto sin fecha o valor")) from e


class IndicadorActual(BaseModel):
    codigo: str
    nombre: str
    unidad: str
    fecha: date
    valor: float

    @classmethod
    def desde_api(cls, dato: dict[str, Any]) -> IndicadorActual:
        try:
            return cls(
                codigo=str(dato["codigo"]),
                nombre=str(dato["nombre"]),
                unidad=str(dato["unidad_medida"]),
                fecha=_solo_fecha(str(dato["fecha"])),
                valor=float(dato["valor"]),
            )
        except ErrorAPI:
            raise
        except (KeyError, TypeError, ValueError, ValidationError) as e:
            raise ErrorAPI(_MENSAJE_FORMA.format(detalle="indicador incompleto")) from e


class Serie(BaseModel):
    codigo: str
    nombre: str
    unidad: str
    puntos: list[Punto] = Field(default_factory=list)

    @classmethod
    def desde_api(cls, dato: dict[str, Any]) -> Serie:
        try:
            serie = dato.get("serie", [])
            return cls(
                codigo=str(dato["codigo"]),
                nombre=str(dato["nombre"]),
                unidad=str(dato["unidad_medida"]),
                puntos=[Punto.desde_api(p) for p in serie],
            )
        except ErrorAPI:
            raise
        except (KeyError, TypeError, ValueError, ValidationError, AttributeError) as e:
            raise ErrorAPI(_MENSAJE_FORMA.format(detalle="serie incompleta")) from e


class Foto(BaseModel):
    fecha: datetime
    indicadores: dict[str, IndicadorActual] = Field(default_factory=dict)

    @classmethod
    def desde_api(cls, dato: dict[str, Any], codigos: list[str]) -> Foto:
        try:
            indicadores: dict[str, IndicadorActual] = {}
            for codigo in codigos:
                if codigo in dato:
                    indicadores[codigo] = IndicadorActual.desde_api(dato[codigo])
            return cls(fecha=_a_datetime(str(dato["fecha"])), indicadores=indicadores)
        except ErrorAPI:
            raise
        except (KeyError, TypeError, ValueError, ValidationError, AttributeError) as e:
            raise ErrorAPI(_MENSAJE_FORMA.format(detalle="foto incompleta")) from e
