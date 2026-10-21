---
title: csv-chart
displayinlist: false
metaPage: true
---

# csv-chart

Renders a stacked bar chart from a CSV file (a page resource), grouped by month. Expects the columns `Date` and `Blog` and counts the entries per month and category (used for statistics like "posts per blog per month"). Months without data are filled with zeros so the time axis is continuous.

## Parameters

| Parameter | Type | Required | Default | Purpose |
| --- | --- | --- | --- | --- |
| `csv` | string | yes | — | Path of the CSV page resource |
| `opts` | string | no | — | JSON object with [ECharts options](https://echarts.apache.org/en/option.html) overrides |

## Example

```text
{{</* csv-chart csv="stats.csv" opts='{"yAxis":{"label":"Posts"}}' */>}}
```

## Assets

Via the shortcode helper: TS `ts/shortcodes/chart.ts` (shared with [`chart`](../chart/)) and SCSS `scss/shortcodes/csv-chart.scss`.

## Dependencies

| Package | Required mount |
|---|---|
| `echarts` | – |
