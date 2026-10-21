---
title: Menu
params:
  displayinlist: false
  metaPage: true
---

# Adding HTML or draft menu entries

```toml
[[languages.en.menu.main]]
    name = '<input type="text" placeholder="Search" class="search-input"><button type="submit" class="search-button">Search</button>'
    weight = 7
    url = "search"

    [[languages.en.menu.main.params]]
        html = true
        draft = true
```
