"""Errores del SDK en espanol."""

from __future__ import annotations


class MindicadorError(Exception):
    """Base de todos los errores del SDK."""


class CodigoInvalido(MindicadorError):
    """El codigo pedido no esta en la lista de 12."""


class FechaInvalida(MindicadorError):
    """Anio o fecha puntual con formato o rango invalido."""


class ErrorRed(MindicadorError):
    """Falla de conexion o timeout contra mindicador.cl."""


class ErrorAPI(MindicadorError):
    """La API respondio con un error no mapeado."""
