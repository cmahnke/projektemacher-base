---
name: hugo-upgrade
description: Upgrade a Hugo site or theme to a newer Hugo version. Use when upgrading Hugo, fixing deprecation warnings after a Hugo version bump, migrating away from deprecated Hugo configuration keys, page/site methods or template functions, or checking which Hugo version introduced a breaking change.
---

# Hugo upgrade

Guide for upgrading Hugo between versions, based on the per-version
deprecation and fix notes from bep/myhugofixer.

## Sources

- Reference notes: [fixes.md](fixes.md) in this skill directory — a
  verbatim copy of bep/myhugofixer's per-version fixes (Hugo v0.55.0 –
  v0.169.0, fetched 2026-11-02). The skill lives in this repository
  (projektemacher-base).
- Newer versions: <https://github.com/bep/myhugofixer> is the upstream
  source. For a target version newer than v0.169.0, fetch the missing
  per-version notes from its
  [fixes/ directory](https://github.com/bep/myhugofixer/tree/main/fixes)
  and apply them in addition to [fixes.md](fixes.md).

## Workflow

1. Determine the current and the target Hugo version (`hugo version`).
   When upgrading a theme, also check the pinned minimum version in
   `theme.toml` (`min_version`) and `hugo.toml`
   (`[module.hugoVersion]`).
2. Collect the required changes: read [fixes.md](fixes.md) and list
   every item from the sections covering versions strictly above the
   current version up to and including the target version. For a
   target beyond v0.169.0, fetch the upstream notes first (see
   Sources).
3. Apply the fixes version by version. Most items are mechanical
   replacements (method → method, config key → config key); the
   "Notes" sections contain behavioural changes that need review
   instead of a fixed replacement.
4. Verify: build the site and resolve remaining deprecation warnings
   (`hugo --logLevel info` prints them with their template/function
   location). Grep for known patterns as needed — the "Mandatory
   post-upgrade checks" section in [Upgrade.md](../../Upgrade.md) of
   this repository has worked grep recipes for the common items.
5. When done, raise the pinned minimum Hugo version in `theme.toml` /
   `hugo.toml` if the applied fixes assume the new version.
