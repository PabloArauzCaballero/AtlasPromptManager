---
name: frontend-i18n-l10n
description: Internacionalización y localización del frontend — ningún texto suelto en el código, catálogo de mensajes por locale, plurales y selección por género con ICU, formato de fecha/número/moneda por locale, soporte RTL, y no concatenar strings traducibles. Usar al agregar cualquier texto visible, al preparar el producto para un segundo idioma o región, al formatear fechas/montos, o al revisar por qué una traducción quedó rota o antinatural.
---

# i18n / l10n — frontend

Internacionalizar es separar el texto y los formatos del código para que se traduzcan sin
tocar la lógica. Hacerlo desde el inicio cuesta poco; retrofitearlo cuesta muchísimo.

## 1. Marcar todo texto visible

- Ningún string visible al usuario va hardcodeado suelto en el componente.
- Cada texto vive en el catálogo de mensajes bajo una **clave estable y con espacio de nombres**
  (`solicitudes.detalle.titulo`), no bajo el texto en español: si cambia la redacción, no se
  pierden las traducciones.
- Dale contexto al traductor: el mismo texto puede traducirse distinto según dónde aparezca.

```tsx
const t = useTranslations('solicitudes.detalle');
<h1>{t('titulo')}</h1>
<img src={avatar} alt={t('avatarAlt')} />
```

El catálogo es un archivo por locale, versionado y entregado a traducción; **nunca se traduce
editando el código fuente**. Una clave sin traducir tiene que ser visible en el build (o en un
test), no caer al idioma base en silencio.

## 2. No concatenar — usar placeholders e ICU

Concatenar rompe idiomas con otro orden de palabras o género. Usá interpolación con
placeholders nombrados y expresiones ICU para plurales y selección.

```html
// ❌ concatenado: intraducible a idiomas con otro orden/género
<span>{count} resultados encontrados</span>

// ✅ ICU en el catálogo: el traductor controla cada forma
// "resultados": "{count, plural, =0 {Sin resultados} =1 {1 resultado} other {# resultados}}"
<span>{t('resultados', { count })}</span>
```

## 3. Formatear con la API de la plataforma, por locale

Fechas, números y moneda se formatean según el locale, no a mano: `Intl.NumberFormat`,
`Intl.DateTimeFormat` o el formateador de la librería de i18n. Fijá la zona horaria de forma
explícita en el servidor, o el mismo dato se renderiza distinto arriba y abajo.

```html
<td>{fmtMoneda.format(monto)}</td>      {/* Intl.NumberFormat('es-BO', {style:'currency', currency:'BOB'}) */}
<td>{fmtFecha.format(creadoEn)}</td>    {/* Intl.DateTimeFormat con timeZone explícito */}
```

- Fechas: guardá y transportá en UTC/ISO; formateá en la zona del usuario en la vista.
- Números: separador decimal y de miles cambian por locale; nunca los pongas literales.
- No asumas el formato del país del desarrollador.

## 4. RTL (derecha-a-izquierda)

- Usá propiedades lógicas: `margin-inline-start`, `padding-inline`, `inset-inline`, `text-align: start`
  en vez de `left`/`right`. Así el layout se espeja solo cuando `dir="rtl"`.
- Iconos direccionales (flechas de "siguiente/atrás") deben espejarse; los no direccionales, no.
- Probá con `dir="rtl"` en el `<html>`.

## 5. SSR

Bajo SSR el texto se resuelve en el servidor; asegurate de que el locale correcto se aplique
en el render del servidor y no cambie al hidratar. Cada locale
suele ser su propio build/despliegue en el enfoque de compilación.

## Anti-patrones

- Texto visible hardcodeado sin marcar.
- Concatenar fragmentos traducibles (`'Hola ' + name + ', tenés ' + n + ' citas'`).
- Formatear fecha/número/moneda con `slice`/`replace` a mano.
- `left`/`right` fijos que rompen RTL.
- Traducir editando el código en vez del catálogo extraído.

## Checklist

- [ ] Todo string visible marcado con `i18n`/`$localize`, con id y contexto.
- [ ] Plurales y género con ICU; cero concatenación de traducibles.
- [ ] Fechas en UTC, formateadas por locale en la vista; números y moneda por pipe/`Intl`.
- [ ] Propiedades lógicas para que el layout soporte RTL; iconos direccionales espejables.
- [ ] Catálogo extraído con `ng extract-i18n`; traducción sobre el catálogo, no el código.
- [ ] Locale correcto bajo SSR sin cambio al hidratar.
