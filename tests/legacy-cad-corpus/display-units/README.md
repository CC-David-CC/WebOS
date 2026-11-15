# Document display units — host candidate

Core source4ceb313f2 introduces document-owned inch presentation while canonical
geometry, expressions and manufacturing remain millimeters/radians. The host
registers `inspect-display-units` and `set-display-units`, plus two ordinary
View-mode menu actions using the same manager methods. No new wrapper bar,
geometry solver or implicit Save is involved.

```js
const display = await call('inspect-display-units');
await call('set-display-units', {revision: display.revision, lengthUnit: 'inch'});
// Model/edit command numbers remain canonical millimeters. Save normally.
```

The read-only dirty serializer includes only the manager's validated optional
`presentation:{version:1,lengthUnit:'inch'}` metadata. Default millimeter
presentation is omitted. A saved inch preference and missing/invalid current
metadata cannot silently appear clean. Manufacturing metadata remains separate.
Host/account/window/document-operation guards remain in effect, and a known
synchronous metadata commit retains `committed:true` if the host is revoked.

Nine adapter/dirty/manufacturing controls pass; index syntax passes. These use
explicit manager doubles to check boundary behavior, not geometry or storage
claims. Actual menu interaction, annotation paint, unchanged native geometry,
authored journal, normal Save/server sync/fresh Open, two-window isolation and
New/reset still require the source-pinned signed runtime.

No new beta deployment or full Gate1/unit-system completion is claimed here.
