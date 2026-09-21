# docs/trabajo/

Un directorio por trabajo, con el nombre `<AAAA-MM-DD>-<slug>`:

```
docs/trabajo/<AAAA-MM-DD>-<slug>/PLAN.md       ← antes de la primera línea de código
docs/trabajo/<AAAA-MM-DD>-<slug>/REPORTE.md    ← al cerrar, siempre, también si quedó a medias
docs/trabajo/<AAAA-MM-DD>-<slug>/evidencia/    ← salidas, capturas, traces
```

Los esqueletos copiables de `PLAN.md` y `REPORTE.md` están en [`AGENTS.md`](../../AGENTS.md) §2.

En un repo de producto, esta misma carpeta vive **en ese repo**, no acá: el plan y la evidencia
viajan con el código que explican. `plan_gate.py` busca el `PLAN.md` en el checkout donde estás
trabajando.

Lo que sí vive acá es el trabajo sobre **el estándar en sí**: agregar o corregir una skill, cambiar
una regla, tocar un candado.
