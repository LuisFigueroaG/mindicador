"""Tests offline del cliente con mocks."""

from __future__ import annotations

from datetime import date

import httpx
import pytest

from mindicador import (
    Client,
    CodigoInvalido,
    ErrorAPI,
    ErrorRed,
    FechaInvalida,
)

FOTO = {
    "version": "1.7.0",
    "autor": "mindicador.cl",
    "fecha": "2026-09-20T23:00:00.000Z",
    "uf": {
        "codigo": "uf",
        "nombre": "Unidad de fomento (UF)",
        "unidad_medida": "Pesos",
        "fecha": "2026-09-20T03:00:00.000Z",
        "valor": 40975.41,
    },
    "dolar": {
        "codigo": "dolar",
        "nombre": "D\u00f3lar observado",
        "unidad_medida": "Pesos",
        "fecha": "2026-09-17T03:00:00.000Z",
        "valor": 954.85,
    },
}

SERIE = {
    "version": "1.7.0",
    "autor": "mindicador.cl",
    "codigo": "uf",
    "nombre": "Unidad de fomento (UF)",
    "unidad_medida": "Pesos",
    "serie": [
        {"fecha": "2026-09-20T03:00:00.000Z", "valor": 40975.41},
        {"fecha": "2026-09-19T03:00:00.000Z", "valor": 40967.24},
    ],
}

VACIA = {
    "version": "1.7.0",
    "autor": "mindicador.cl",
    "codigo": "uf",
    "nombre": "Unidad de fomento (UF)",
    "unidad_medida": "Pesos",
    "serie": [],
}


def cliente_con(respuestas: dict[str, object]) -> Client:
    def maneja(pedido: httpx.Request) -> httpx.Response:
        ruta = pedido.url.path
        if ruta in respuestas:
            valor = respuestas[ruta]
            if isinstance(valor, Exception):
                raise valor
            return httpx.Response(200, json=valor)
        return httpx.Response(500, json={"message": "ruta no mockeada"})

    transporte = httpx.MockTransport(maneja)
    return Client(transporte=transporte)


def test_actual_mapea_foto() -> None:
    cli = cliente_con({"/api": FOTO})
    foto = cli.actual()
    assert foto.indicadores["uf"].valor == 40975.41
    assert foto.indicadores["uf"].fecha == date(2026, 9, 20)


def test_historial_mapea_serie() -> None:
    cli = cliente_con({"/api/uf": SERIE})
    serie = cli.historial("uf")
    assert serie.codigo == "uf"
    assert len(serie.puntos) == 2
    assert serie.puntos[0].valor == 40975.41


def test_historial_anual_permite_futuro_vacio() -> None:
    cli = cliente_con({"/api/uf/9999": VACIA})
    serie = cli.historial_anual("uf", 9999)
    assert serie.puntos == []


def test_puntual_retorna_punto() -> None:
    cli = cliente_con({"/api/uf/20-09-2026": SERIE})
    punto = cli.puntual("uf", date(2026, 9, 20))
    assert punto is not None
    assert punto.valor == 40975.41


def test_puntual_sin_dato_retorna_none() -> None:
    cli = cliente_con({"/api/uf/01-01-1900": VACIA})
    assert cli.puntual("uf", date(1900, 1, 1)) is None


def test_codigo_con_mayuscula_falla_local() -> None:
    cli = cliente_con({})
    with pytest.raises(CodigoInvalido):
        cli.historial("UF")


def test_anio_no_entero_falla() -> None:
    cli = cliente_con({})
    with pytest.raises(FechaInvalida):
        cli.historial_anual("uf", "2024")  # type: ignore[arg-type]


def test_mapea_fecha_incorrecta() -> None:
    def maneja(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "Fecha incorrecta"})

    cli = Client(transporte=httpx.MockTransport(maneja))
    with pytest.raises(FechaInvalida):
        cli.historial("uf")


def test_mapea_codigo_servidor() -> None:
    def maneja(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "No se ha encontrado el indicador"})

    cli = Client(transporte=httpx.MockTransport(maneja))
    with pytest.raises(CodigoInvalido):
        cli.historial("uf")


def test_error_api_generico() -> None:
    def maneja(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "algo raro"})

    cli = Client(transporte=httpx.MockTransport(maneja))
    with pytest.raises(ErrorAPI):
        cli.historial("uf")


def test_reintenta_una_vez_y_luego_falla() -> None:
    llamadas = {"n": 0}

    def maneja(pedido: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        raise httpx.ConnectError("corte")

    cli = Client(transporte=httpx.MockTransport(maneja))
    with pytest.raises(ErrorRed):
        cli.historial("uf")
    assert llamadas["n"] == 2


def test_historial_df_columnas() -> None:
    cli = cliente_con({"/api/uf": SERIE})
    df = cli.historial_df("uf")
    assert list(df.columns) == ["fecha", "valor"]
    assert len(df) == 2


def test_actual_df_columnas() -> None:
    cli = cliente_con({"/api": FOTO})
    df = cli.actual_df()
    assert list(df.columns) == ["codigo", "nombre", "unidad", "fecha", "valor"]
    assert len(df) == 2


def test_anio_fuera_de_rango_falla() -> None:
    cli = cliente_con({})
    with pytest.raises(FechaInvalida):
        cli.historial_anual("uf", 0)


def test_anio_bool_falla() -> None:
    cli = cliente_con({})
    with pytest.raises(FechaInvalida):
        cli.historial_anual("uf", True)  # type: ignore[arg-type]


def test_respuesta_no_json_da_error_api() -> None:
    def maneja(pedido: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"no json")

    cli = Client(transporte=httpx.MockTransport(maneja))
    with pytest.raises(ErrorAPI):
        cli.historial("uf")


def test_serie_malformada_da_error_api() -> None:
    mala = {
        "version": "1.7.0",
        "autor": "mindicador.cl",
        "codigo": "uf",
        "nombre": "Unidad de fomento (UF)",
        "unidad_medida": "Pesos",
        "serie": [{"fecha": "mala-fecha", "valor": 1.0}],
    }
    cli = cliente_con({"/api/uf": mala})
    with pytest.raises(ErrorAPI):
        cli.historial("uf")


def test_punto_sin_valor_da_error_api() -> None:
    mala = {
        "version": "1.7.0",
        "autor": "mindicador.cl",
        "codigo": "uf",
        "nombre": "Unidad de fomento (UF)",
        "unidad_medida": "Pesos",
        "serie": [{"fecha": "2026-09-20T03:00:00.000Z"}],
    }
    cli = cliente_con({"/api/uf": mala})
    with pytest.raises(ErrorAPI):
        cli.historial("uf")


def test_foto_incompleta_omite_llaves() -> None:
    parcial = {
        "version": "1.7.0",
        "autor": "mindicador.cl",
        "fecha": "2026-09-20T23:00:00.000Z",
        "uf": {
            "codigo": "uf",
            "nombre": "Unidad de fomento (UF)",
            "unidad_medida": "Pesos",
            "fecha": "2026-09-20T03:00:00.000Z",
            "valor": 40975.41,
        },
    }
    cli = cliente_con({"/api": parcial})
    foto = cli.actual()
    assert list(foto.indicadores) == ["uf"]


def test_dolar_acuerdo_no_consultable() -> None:
    cli = cliente_con({})
    with pytest.raises(CodigoInvalido):
        cli.historial("dolar_intercambio")


def test_sin_cache_llama_dos_veces() -> None:
    llamadas = {"n": 0}

    def maneja(pedido: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(200, json=SERIE)

    cli = Client(transporte=httpx.MockTransport(maneja))
    cli.historial("uf")
    cli.historial("uf")
    assert llamadas["n"] == 2


def test_con_cache_llama_una_vez() -> None:
    llamadas = {"n": 0}

    def maneja(pedido: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(200, json=SERIE)

    cli = Client(transporte=httpx.MockTransport(maneja), cache=True)
    cli.historial("uf")
    cli.historial("uf")
    assert llamadas["n"] == 1


def test_limpiar_cache_fuerza_llamada() -> None:
    llamadas = {"n": 0}

    def maneja(pedido: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(200, json=SERIE)

    cli = Client(transporte=httpx.MockTransport(maneja), cache=True)
    cli.historial("uf")
    cli.limpiar_cache()
    cli.historial("uf")
    assert llamadas["n"] == 2


def test_cache_ttl_corto_expira() -> None:
    import time

    llamadas = {"n": 0}

    def maneja(pedido: httpx.Request) -> httpx.Response:
        llamadas["n"] += 1
        return httpx.Response(200, json=SERIE)

    cli = Client(transporte=httpx.MockTransport(maneja), cache=True, cache_ttl=0.05)
    cli.historial("uf")
    time.sleep(0.08)
    cli.historial("uf")
    assert llamadas["n"] == 2


def test_historial_pl_columnas() -> None:
    cli = cliente_con({"/api/uf": SERIE})
    df = cli.historial_pl("uf")
    assert df.columns == ["fecha", "valor"]
    assert len(df) == 2


def test_actual_pl_columnas() -> None:
    cli = cliente_con({"/api": FOTO})
    df = cli.actual_pl()
    assert df.columns == ["codigo", "nombre", "unidad", "fecha", "valor"]
    assert len(df) == 2
