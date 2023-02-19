PyHugolib
---------

# Features

## Usage

Import PyHugolib

```
from PyHugolib import *
```


## Loading of a Site config

The `Config` class can be used to load a Hugo configuration

```
PyHugolib().setDebug(True)
cfg = Config().load("../../../../config.toml")
print(cfg["baseURL"])
```

## Loading of a Site structure

The `Site` class can be used to load a Hugo site structure

```
PyHugolib().setDebug(True)
structure = Site().structure("../../../../config.toml")
print(structure)
```

# Building

```
./build.sh
```

# Known issues

* `setup.py` not working
* Theme configuration is not loaded
* Building a site structure doesn't work yet
