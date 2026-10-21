---
title: chart
displayinlist: false
metaPage: true
---

# chart

Renders a [ECharts](https://echarts.apache.org/) line/bar chart from a Markdown table given in the shortcode body. The data is kept in a `<pre class="chart-data">` element, so it stays available as a text fallback (also useful for search and screen readers).

The optional first line of the body can start with `#` followed by a JSON object with [ECharts options](https://echarts.apache.org/en/option.html) overrides (e.g. `{"type": "bar"}`).

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `class` | string | no | — | Extra class on the `<figure>` |
| `caption` | string | no | — | Caption below the chart |

## Example

````text
{{</* chart caption="Posts per year" class="wide" >}}
# {"type": "bar", "scale": true}
| Year | Posts |
|------|-------|
| 2023 | 12    |
| 2024 | 30    |
{{< /chart */>}}
````

## Assets

Via the shortcode helper: TS `ts/shortcodes/chart.ts` and SCSS `scss/shortcodes/chart.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `echarts` | – |
