`projektemacher-base` Theme
===========================

# Introduction

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

# Development dependencies

## Dart SASS on Mac OS

Download the binary from https://github.com/sass/dart-sass-embedded/releases and install it to `/usr/local/bin/`.

To use Dart SASS on the command line also install it from brew

```
brew install sass/sass/sass
```
