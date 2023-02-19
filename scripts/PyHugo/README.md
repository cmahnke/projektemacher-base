PyHugolib
---------

# Features

## Usage

Import PyHugolib

```
from PyHugolib import *
```


## Loading of a Site config

The `Config` class can be sued to load a Hugo configuration

```
PyHugolib().setDebug(True)
cfg = Config().load("../../../../config.toml")
print(cfg["baseURL"])
```

# Building

```
./build.sh
```

# Known issues

* `setup.py` not working
* Theme configuration is not loaded
* Building a site structure doesn't work yet
