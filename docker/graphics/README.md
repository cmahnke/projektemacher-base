Image for Graphics processing
=============================

# Purpose

This image bundles the system packages required for graphics processing,
so they don't have to be installed on the runner itself — pulling the
image is faster than installing the packages. It is built and pushed to
`ghcr.io` by the `Publish Docker images` workflow
(`.github/workflows/docker.yml`) as
`ghcr.io/cmahnke/projektemacher-base/graphics`.

# Contents

* Ubuntu base image
* ImageMagick (built from source with JXL, UltraHDR, WebP and OpenEXR
  support) and `ultrahdr_app` (libultrahdr)
* libvips (`libvips-tools`) with libjxl
* Inkscape and Ghostscript
* Saxon HE XSLT processor (via `scripts/github/setup-xslt.sh`)
* The theme's fonts, installed as system fonts (converted with the
  `font-action` image and `scripts/github/setup-system-fonts.sh`)

# TODO

*
