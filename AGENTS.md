# mindicador - reglas del repo

## Idioma y estilo

- Docs y mensajes en espanol. Voz directa, frases cortas, una idea por frase.
- Aplica unslop a todo texto humano: sin frases de chatbot, sin adornos, sin jerga abstracta.

## Alcance actual

- Fase de base. No hay diseno de API publica. No agregues firmas, tipos ni cliente hasta que se converse aqui.
- Docs nuevas van en `docs/`. Decisiones firmes van en `docs/decisiones.md`. Dudas van en `docs/preguntas-pendientes.md`.

## Trabajo con Python y uv

- Python minimo 3.12. Usa `uv` para deps y grupos.
- Nivel 0 para docs: revisa diff, enlaces y consistencia. No corras lint, typecheck, tests ni build.
- Nivel 2 para codigo futuro: acota `ruff`, `pyright` y `pytest` al paquete o test tocado.

## Versionamiento

- Puedes crear commits locales con solo tus cambios. No reescribas historial.
- No hagas push, no publiques ramas, no crees PR ni releases sin orden explicita.
- Commits y PR en espanol, claros y cortos. Sin mencionar Codex, agentes ni automatizacion.
