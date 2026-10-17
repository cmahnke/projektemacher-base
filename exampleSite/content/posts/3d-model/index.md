---
title: 3D model manifest
description: "Demo of a IIIF Presentation 4 manifest including a 3D model"
date: 2024-01-15
outputs: [html, iiif-manifest]
iiif:
  presentationVersion: 4
  behavior: individuals
resources:
  - src: model/example.glb
    params:
      label: Example model
  - src: model/bare.glb
    params:
      label: Model without poster
  - src: model/example.jpg
    name: preview
---

# 3D model manifests

GLB resources are emitted as Presentation API 4 `Scene` containers with painting annotations of the type `Model`. The `bare.glb` resource has no sibling poster image — its Scene simply has no thumbnail, the build doesn't fail. See [Page metadata](/iiif/page-metadata/#3d-models/) for the full rules.
