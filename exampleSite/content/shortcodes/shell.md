---
title: shell
params:
  displayinlist: false
  metaPage: true
---

# shell

Renders a syntax highlighted code block (Hugo's `transform.Highlight`/Chroma) as a macOS style shell window with traffic light buttons: the red and green buttons collapse (or expand) the window, the yellow button copies the raw code to the clipboard.

> This page documents the shortcode; see [demo/shell](demo/shell/) for a live example.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `lang` | string | no | — | Chroma highlighting language, disables syntax guessing |
| `title` | string | no | `Terminal` | Window title in the title bar |
| `class` | string | no | — | Custom class name |
| `lineNumbers` | bool | no | `true` | Show inline, anchored line numbers |
| `collapsed` | bool | no | `false` | Render the window initially collapsed |
| `lineNumbersIDPrefix` | string | no | — | Chroma `lineAnchors` ID prefix |

The inner content is the code itself. Copying always copies this raw content, independent of the displayed highlighting or line numbers.

## Example

```text
{{</* shell lang="bash" title="Terminal" */>}}
hugo server --source exampleSite
{{</* /shell */>}}
```

## Live demo

{{< shell lang="bash" title="Live example" >}}
hugo server --source exampleSite
{{< /shell >}}

## Assets

Via the shortcode helper: JS `ts/shortcodes/code.ts` (`addCopyToClipboard`), SCSS `scss/shortcodes/shell.scss`.

## References

- [transform.Highlight](https://gohugo.io/functions/transform/highlight/)
- [Code block render hooks](https://gohugo.io/render-hooks/code-blocks/)
