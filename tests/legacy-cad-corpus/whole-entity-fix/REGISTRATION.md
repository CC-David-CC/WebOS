# Whole-entity Fix host source splice

SOURCE ONLY / UNEXECUTED. Root serially adds to apps/system/jsketcher/index.mjs:

```js
import {registerFixedEntityCommands} from './fixed-entity-commands.mjs';
// Alongside the other rectangle.target() shared closed-sketch adapters:
if(host.commands)host.onDispose(registerFixedEntityCommands(host,()=>rectangle.target()));
```

Existing inspect-closed-sketch exposes fixedEntities.targets / fixedEntities.rows.
Public apply/remove commands admit only exact bounded own identity/revision data,
capture method/account/window/document authority, and reuse settleScopedCommand.
No new file coordinator, UI, schema relaxation or fixed geometry caller fields.

Core whole driver/oracle lives under test/closed-whole-entity-fix-workflow. Root
builds/executes only after composing the complete packet. No runtime claim here.
