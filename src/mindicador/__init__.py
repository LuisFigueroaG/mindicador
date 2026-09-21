"""mindicador: SDK simple en Python para mindicador.cl."""

from __future__ import annotations

from .client import CODIGOS, Client
from .errors import CodigoInvalido, ErrorAPI, ErrorRed, FechaInvalida, MindicadorError
from .models import Foto, IndicadorActual, Punto, Serie

__all__ = [
    "CODIGOS",
    "Client",
    "CodigoInvalido",
    "ErrorAPI",
    "ErrorRed",
    "FechaInvalida",
    "Foto",
    "IndicadorActual",
    "MindicadorError",
    "Punto",
    "Serie",
]
