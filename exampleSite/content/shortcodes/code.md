---
title: code
displayinlist: false
metaPage: true
---

# code

Renders a syntax highlighted code block (Hugo's `transform.Highlight`/Chroma) inside a container with a title bar, a copy-to-clipboard button and a collapse checkbox.

> This page documents the shortcode; see [demo/code](demo/code/) for a live example.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `lang` | string | no | — | Chroma highlighting language, disables syntax guessing |
| `title` | string | no | — | Header title of the container |
| `class` | string | no | — | Custom class name |
| `lineNumbers` | bool | no | `true` | Show inline, anchored line numbers |
| `lineNumbersIDPrefix` | string | no | — | Chroma `lineAnchors` ID prefix |

The inner content is the code itself.

## Example

```text
{{</* code lang="js" title="Copy to clipboard" */>}}
navigator.clipboard.writeText(text)
{{</* /code */>}}
```

## Live demo

{{< code lang="js" title="Live example" >}}
const answer = 42
console.log(`The answer is ${answer}`)
{{< /code >}}

## Assets

Via the shortcode helper: JS `ts/shortcodes/code.ts` (`addCopyToClipboard`), SCSS `scss/shortcodes/code.scss`.

## References

- [transform.Highlight](https://gohugo.io/functions/transform/highlight/)
- [Code block render hooks](https://gohugo.io/render-hooks/code-blocks/)
