---
title: Shell
params:
  displayinlist: false
  metaPage: true
---

# Example

{{< shell lang="bash" title="Example with title" >}}
hugo server --source exampleSite
{{< /shell >}}

{{< shell lang="bash" title="Example without line numbers" lineNumbers=false >}}
hugo server --source exampleSite
{{< /shell >}}

{{< shell lang="console" title="Example initially collapsed" collapsed=true >}}
brew install hugo
{{< /shell >}}

# Options

* `lang` - string: One of those [supported languages](https://gohugo.io/content-management/syntax-highlighting/#languages)
* `class` - string: Custom class name
* `title` - string: Custom title, default: `Terminal`
* `lineNumbers` - boolean: If line numbers should be shown, default: `true`
* `collapsed` - boolean: If the window should be initially collapsed, default: `false`
* `lineNumbersIDPrefix` - string: Prefix for the line number ID's

# References

* [transform.Highlight](https://gohugo.io/functions/transform/highlight/)
* [Code block render hooks](https://gohugo.io/render-hooks/code-blocks/)
