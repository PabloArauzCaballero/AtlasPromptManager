# Instrucciones del repo para GitHub Copilot

El estándar completo está en **[`AGENTS.md`](../AGENTS.md)** (raíz del repo). Leelo antes de
trabajar. Acá va solo lo mínimo imprescindible; ante cualquier duda manda `AGENTS.md`.

## Las cinco reglas duras

1. **Verificar es observar el artefacto corriendo.** Leer el diff o compilar no es verificar.
   No uses una palabra de finalización más fuerte que la evidencia que podés pegar.
2. **No inventes.** Antes de crear una entidad, endpoint o componente, buscá el equivalente
   existente. No escribas una API de terceros que no verificaste en su documentación.
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

Los esqueletos copiables de ambos archivos están en [`AGENTS.md`](../AGENTS.md), sección 2.

> Copilot no tiene el candado automático que sí tiene Claude Code en este repo. El plan y el
> reporte siguen siendo obligatorios: si el PR no los trae, se rechaza.

El catálogo de skills se navega desde
[`.claude/skills/skills-router/SKILL.md`](../.claude/skills/skills-router/SKILL.md).
