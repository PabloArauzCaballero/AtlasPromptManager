---
name: Estándar de la casa
alwaysApply: true
description: Estándar de trabajo obligatorio de la empresa — reglas no negociables, plan por hitos y reporte de cierre. Aplica a todo trabajo en este repo.
---

# Estándar de la casa

El estándar completo está en **[AGENTS.md](../../AGENTS.md)** (raíz del repo). Ante cualquier duda,
manda `AGENTS.md`.

> **Por qué existe este archivo y no alcanza con `AGENTS.md`:** a diferencia de Codex, Cursor,
> Copilot, Gemini CLI, Aider, Windsurf y Cline, la documentación de Continue **no menciona
> `AGENTS.md`**: sus reglas de proyecto se cargan desde `.continue/rules/`. Sin este puntero,
> Continue abre el repo sin el estándar.

## Las cinco reglas duras

1. **Verificar es observar el artefacto corriendo.** Leer el diff o compilar no es verificar.
   No uses una palabra de finalización más fuerte que la evidencia que podés pegar.
2. **No inventes.** Buscá el equivalente existente antes de crear una entidad, endpoint o
   componente. No escribas una API de terceros que no verificaste en su documentación.
3. **Diff mínimo.** Nada de refactors, renombres ni reformateos no pedidos. Lo roto fuera de
   alcance se anota, no se arregla.
4. **Datos personales, financieros y biométricos: nunca** en logs, trazas, URLs, capturas, ni en el
   plan o el reporte.
   Nunca copies producción a un entorno de prueba.
5. **No toques los tests para cerrar.** Nada de `skip`, borrar aserciones ni subir timeouts sin
   haber demostrado la causa del fallo.

## Formato obligatorio

- **Ningún trabajo empieza sin `docs/trabajo/<fecha>-<slug>/PLAN.md`** con hitos → subtareas →
  microtareas, cada una con criterio de aceptación y Definition of Done (con su comando).
- **Ningún trabajo se cierra sin `REPORTE.md`** con COMPLETADO / A MEDIAS / PENDIENTE. `A MEDIAS`
  exige cuatro respuestas: qué anda, qué no anda, qué falta exactamente, dónde quedó.

Esqueletos copiables: [AGENTS.md](../../AGENTS.md), sección 2.

> Continue no tiene el candado automático que sí tiene Claude Code en este repo. El plan y el
> reporte siguen siendo obligatorios: si el PR no los trae, se rechaza.

Catálogo de skills: [skills-router](../../.claude/skills/skills-router/SKILL.md).
