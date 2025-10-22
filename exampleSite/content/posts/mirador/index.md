---
title: Mirador
displayinlist: false
metaPage: true
---

# Requirements

## `package.json`

Make sure to check out a dev version that can be used with the patch for page gaps.

```
{
  "dependencies": {
    "mirador": "ProjectMirador/mirador#5cb692ed31480c1e130f4a8715726688cb35796d"
  },
  "devDependencies": {
      "patch-package": "^8.0.0"
  },
  "scripts": {
    "prepatch": "cp -rf $INIT_CWD/themes/projektemacher-base/patches $INIT_CWD",
    "patch": "yarn run patch-package",
    "postinstall": "yarn run prepatch && yarn run patch && yarn run postinstall-mirador && ls -al node_modules/mirador/dist",
    "postinstall-mirador": "cd node_modules/mirador && yarn add -D @babel/plugin-proposal-private-property-in-object && yarn install && yarn run build"

  }
}
```
