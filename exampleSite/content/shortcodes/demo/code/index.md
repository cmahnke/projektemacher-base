---
title: Code
displayinlist: false
metaPage: true
---

# Example

{{< code lang="js" title="Example with title" >}}
navigator.clipboard.writeText(...)
{{< /code >}}

{{< code lang="js" title="Example without line numbers" lineNumbers=false >}}
navigator.clipboard.writeText(...)
{{< /code >}}

# Options

* `lang` - string: One of those [supported languages](https://gohugo.io/content-management/syntax-highlighting/#languages)
* `class` - string: Custom class name
* `title` - string: Custom title
* `lineNumbers` - boolean: If line numbers should be shown, default: `true`
* `lineNumbersIDPrefix` - string: Refix for the lin number id's

# References

* [transform.Highlight](https://gohugo.io/functions/transform/highlight/)
* [Code block render hooks](https://gohugo.io/render-hooks/code-blocks/)
