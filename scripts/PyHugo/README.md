PyHugo
---------

**This is outdated and applies only to the deleted Go based prototype**

# Features

## Usage

Import PyHugo

```
from PyHugo import *
```


## Loading of a Site config

The `Config` class can be used to load a Hugo configuration

```
PyHugo().setDebug(True)
cfg = Config().load("../../../../config.toml")
print(cfg["baseURL"])
```

## Loading of a Site structure

The `Site` class can be used to load a Hugo site structure

```
PyHugo().setDebug(True)
structure = Site().structure("../../../../config.toml")
print(structure)
```

# Building

```
./build.sh
```

# Known issues

* Building with `setup.py` throws errors on Linux (see building of `Dockerfile`)
* Theme configuration is not loaded
* Loading configuration from directory (`_config`) certainly doesn't work
* Building a site structure doesn't work yet
* getEnv() doesn't work

# Using Docker

```
BUILDKIT_PROGRESS=plain docker buildx build .
```
