---
name: frontend-security
description: Gate de seguridad del cliente web — XSS al renderizar HTML dinámico (el sanitizador del framework y los riesgos de saltearlo), Content-Security-Policy y Trusted Types, no guardar tokens en `localStorage`, CSRF según el modelo de auth, datos sensibles fuera del HTML de SSR y del estado transferido, y control de dependencias del front. Usar al renderizar HTML dinámico, al integrar contenido de terceros, al decidir dónde vive el token de sesión, o al revisar cualquier vista que muestre datos de clientes.
allowed-tools: Read Grep Glob Bash
effort: high
---

# Seguridad del cliente — gate

El navegador es territorio hostil: el usuario puede leer todo lo que llega al cliente y un
atacante puede inyectar script. El front no reemplaza los controles del backend
(`security-guardrails`, `authz-access-control`) — los complementa evitando XSS, fuga de datos
y robo de sesión.

## 1. XSS y el escapado del framework

- En React/JSX, `{expresión}` **escapa** por defecto: es seguro.
- El riesgo aparece con `dangerouslySetInnerHTML`, con APIs de DOM crudas (`innerHTML`,
  `document.write`) y con `href`/`src` armados desde entrada del usuario (`javascript:`).
- El framework **no** sanea lo que entra por `dangerouslySetInnerHTML`: ahí no hay red de
  seguridad. Si de verdad hace falta renderizar HTML ajeno, pasa antes por un sanitizador
  mantenido (DOMPurify o equivalente), y cada uso necesita justificación y una fuente confiable.

```tsx
// ❌ HTML de origen no controlado = XSS
<div dangerouslySetInnerHTML={{ __html: respuestaDelUsuario }} />
el.innerHTML = contenidoDeTercero;

// ✅ renderizar como texto, o sanear explícitamente antes
<div>{contenido}</div>
<div dangerouslySetInnerHTML={{ __html: sanitize(contenido) }} />
```

Nunca construyas HTML ni URLs concatenando entrada del usuario. Validá el esquema de una URL
antes de ponerla en un `href` (`https:` sí, `javascript:` no).

## 2. CSP y Trusted Types

- Serví una **Content-Security-Policy** que restrinja `script-src` (sin `unsafe-inline`) para
  que un XSS inyectado no ejecute. Con SSR y scripts inline del framework, la vía sostenible es
  **nonce por respuesta** desde el middleware, no `unsafe-inline`.
- **Trusted Types** (`require-trusted-types-for 'script'`) convierte cada asignación cruda al DOM
  en un error en vez de en una fuga silenciosa; cualquier librería que escriba HTML necesita su
  política declarada, lo que vuelve auditable cada excepción.
- Definí la CSP y los security headers del lado del servidor/proxy (ver `server-hardening`).

## 3. Dónde vive el token de sesión

- **No** guardes tokens de sesión en `localStorage`/`sessionStorage`: cualquier XSS los lee.
- Preferí cookie `HttpOnly` + `Secure` + `SameSite` para la sesión; el JS no la ve. El modelo
  de auth completo está en `authn-identity`.
- Si el diseño exige un token accesible por JS, mantenelo solo en memoria (un store del cliente),
  nunca persistido, y asumí que un XSS lo compromete.

## 4. CSRF

- Con auth por cookie, protegé contra CSRF: token anti-CSRF o `SameSite=Strict/Lax` según el
  flujo. Si el cliente manda un token anti-CSRF por header, que lo haga la capa de datos, una vez
  y para todas las mutaciones, no cada llamada a mano.
- Con auth por header `Authorization: Bearer` (no cookie), el CSRF clásico no aplica, pero
  vuelve el problema de dónde guardar el token (punto 3).

## 5. Datos sensibles en el cliente y en SSR

- No incrustes en el HTML servido, ni en el transfer state de SSR, datos que el usuario no
  debería ver o que son datos sensibles innecesaria. El transfer cache de HTTP debe excluir respuestas con
  headers de auth y datos sensibles (ver `data-privacy-sensitive`).
- La UI **no** es barrera de autorización: ocultar un botón no protege el endpoint. Todo se
  valida en el backend (`authz-access-control`).
- No pongas secretos (API keys de servicios de pago, etc.) en el bundle del cliente: es público.

## 6. Dependencias del front

- El código de terceros corre con los permisos de tu página. Fijá versiones (lockfile),
  revisá lo que agregás, y corré auditoría de dependencias en CI (ver `github-security-features`,
  `dependency-management`).
- Cuidado con scripts de terceros embebidos (analytics, widgets): pueden leer el DOM y la
  entrada del usuario. Restringilos por CSP y evaluá su necesidad en páginas con datos sensibles.

## Evidencia / DoD

Para declarar segura la superficie del cliente que tocaste, pegá:
- `grep` de `dangerouslySetInnerHTML`/`innerHTML`/`localStorage` en el diff, con justificación de cada aparición.
- La CSP efectiva servida (header real, no la intención).
- Confirmación de dónde vive el token (cookie HttpOnly o memoria) y de que no se persiste en storage.
- Para vistas SSR con datos: qué se incluye en el transfer state y por qué no hay datos sensibles de más.

## Checklist

- [ ] Sin HTML crudo no justificado; `dangerouslySetInnerHTML` solo con contenido saneado o confiable.
- [ ] CSP con `script-src` sin `unsafe-inline`; Trusted Types activo si aplica.
- [ ] Token de sesión en cookie `HttpOnly`/`Secure`/`SameSite`, no en `localStorage`.
- [ ] CSRF cubierto según el modelo de auth.
- [ ] Sin datos sensibles ni secretos innecesarios en HTML SSR, transfer state o bundle.
- [ ] Dependencias del front fijadas y auditadas; scripts de terceros restringidos.
