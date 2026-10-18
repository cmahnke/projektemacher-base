import * as echarts from 'echarts';

declare global {
  interface Window {
    initializeChart: typeof initializeChart;
  }
}

const defaultHeightVH = 20;

interface ChartSeries {
  data: string[];
  type: string;
  label: string;
  showSymbol: boolean;
  silent: boolean;
  connectNulls: boolean;
  [key: string]: unknown;
}

interface ChartOptions {
  type?: string;
  duration?: number;
  scale?: boolean;
  font?: string;
  series?: Record<string, ChartSeries>;
  [key: string]: unknown;
}

function between(x: string | number, min: number, max: number): boolean {
  const value = Number(x);
  return value >= min && value <= max;
}

function parseTable(markdownTable: string): Record<string, string[]> | null {
  if (!markdownTable) {
    return null;
  }

  const lines = markdownTable.trim().split('\n');
  if (lines.length < 2) {
    return null; // Not a valid table
  }

  const headerRow = lines[0].trim();
  const separatorRow = lines[1].trim();

  if (!headerRow.startsWith('|') || !separatorRow.startsWith('|')) {
    return null; // Not a valid table
  }

  const headers = headerRow
    .split('|')
    .map((header) => header.trim())
    .filter((header) => header !== '');

  const dataRows = lines.slice(2);
  const columns: Record<string, string[]> = {};

  headers.forEach(header => {
      columns[header] = [];
  });

  for (const row of dataRows) {
    const values = row
      .split('|')
      .map((value) => value.trim())
      .filter((value) => value !== '');

    if (values.length !== headers.length) {
      continue; // Skip rows with incorrect number of columns
    }

    for (let i = 0; i < headers.length; i++) {
      columns[headers[i]].push(values[i]);
    }
  }

  return columns;
}

export function initializeChart(options: ChartOptions = {}): void {
  document.querySelectorAll<HTMLElement>('pre.chart-data').forEach(data => {
    let md = data.innerHTML;
    const lines = md.trim().split('\n');
    let tableOptions: Partial<ChartOptions> | undefined
    if (lines[0].startsWith("#")) {
      tableOptions = JSON.parse(lines[0].substring(lines[0].indexOf('#') + 1).trim()) as Partial<ChartOptions>
      md = lines.slice(1).join("\n")
    }
    const json = parseTable(md)
    options = {...options, ...tableOptions}
    setupChart(data, json, options)
  });
}

function setupChart(element: HTMLElement, data: Record<string, string[]> | null, options: ChartOptions): void {
  if (data === null) {
    return;
  }
  let animationDuration = 2000;
  const xAxisName = Object.keys(data)[0]
  const xAxisData = data[xAxisName];
  const series: ChartSeries[] = [];
  let min: number | undefined, max: number | undefined;
  let seriesType = 'line'
  if (typeof options.type === "string") {
    seriesType = options.type
  }
  Object.keys(data).slice(1).forEach(key => {
    const values = data[key];
    const numericValues = values.filter(element => element !== '-').map(Number);
    const seriesMin = Math.min(...numericValues)
    const seriesMax = Math.max(...numericValues)
    let s: ChartSeries = {data: values, type: seriesType, label: key, showSymbol: false, silent: true, connectNulls: true}
    if (options.series !== undefined && key in options.series) {
      s = {...s, ...options.series[key]}
    }
    series.push(s)
    if (min === undefined || seriesMin < min) {
      min = seriesMin
    }
    if (max === undefined || seriesMax > max) {
      max = seriesMax
    }
  });

  if (typeof options.duration === "number") {
    animationDuration = options.duration
  }

  if (options.scale === true) {
    const factor = Math.pow(10, max!.toString().length - 2)
    min = Math.floor(min! / factor) * factor
    max = Math.ceil(max! / factor) * factor
  } else {
    min = undefined
    max = undefined
  }

  const type = 'category'
  if (between(xAxisData[0], 1800, 2100) && between(xAxisData[xAxisData.length - 1], 1800, 2100)) {
    //type = 'time'
  }

  const chartOptions: Record<string, unknown> = {
    xAxis: {
      type: type,
      label: xAxisName,
      data: xAxisData
    },
    grid: {
      left: 60,
      right: 10,
      top: 20,
      bottom: '10%'
    },
    yAxis: {
      type: 'value',
      min: min,
      max: max
    },
    series: series,
    animationDuration: animationDuration
  };

  if (typeof options.font === "string") {
    chartOptions["textStyle"] = {
      fontFamily: options.font
    }
  }

  const container = element.parentElement?.querySelector<HTMLElement>('.chart-container');
  if (container === undefined || container === null) {
    return;
  }
  const [width, height] = getSize(container);
  const chart = echarts.init(container, null, { renderer: "svg", width: width, height: height});
  chart.setOption(chartOptions as unknown as echarts.EChartsOption);
  const registry = window.projektemacher ?? (window.projektemacher = {});
  (registry.charts ??= {})[String(container)] = chart
}

function getSize(container: HTMLElement): [number, number] {
  let width = container.offsetWidth;
  if (width === 0) {
    width = (container.parentElement?.parentElement as HTMLElement).offsetWidth;
  }
  let height = container.offsetHeight;
  if (height === 0) {
    height = Math.round(window.innerHeight / 100) * defaultHeightVH;
  }
  return [width, height]
}

window.initializeChart = initializeChart;
