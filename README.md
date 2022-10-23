`projektemacher-base` Theme
===========================

# Introduction

# Installation

```
git submodule add https://github.com/cmahnke/projektemacher-base.git themes/projektemacher-base
```

# Site configuration

## IIIF manifests

To generate IIIF JSON manifests you need to add the `JSON` output format to the site `config.toml`.

```
[outputs]
    page = ["HTML", "JSON"]
```

# Scripts

To enable the merging of node dependencies including the `script` section you may want to add the following snippet to your setup

```
#NPM dependencies
echo "Calling theme scripts"
for SCRIPT in $PWD/themes/projektemacher-base/scripts/init/*.sh ; do
    echo "Running $SCRIPT"
    bash "$SCRIPT"
done
```
