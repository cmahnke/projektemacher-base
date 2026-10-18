import * as echarts from 'echarts';

declare global {
  interface Window {
    initializeChart: typeof initializeChart;
    chart: typeof chartFromCSV;
  }
}

const defaultHeightVH = 20;
const csvHeightVH = 50;
const addEmptyMonths = true;

// https://observablehq.com/@d3/stacked-to-grouped-bars
const palette = [
  '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5'];

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
    if (data.dataset.chartProcessed !== undefined) {
      return;
    }
    data.dataset.chartProcessed = 'true';
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

function formatIndex(dateStr: string): string {
  const date = new Date(dateStr);
  const month = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
  return month;
}

type CSVGroupedData = Record<string, Record<string, number>>;

async function loadCSVFromURL(url: string): Promise<CSVGroupedData> {
  try {
    const response = await fetch(url);
    const text = await response.text();
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    const data: Record<string, string>[] = [];

    for (let i = 1; i < lines.length; i++) {
      const row = lines[i].split(',');
      const obj: Record<string, string> = {};
      headers.forEach((header, j) => {
        obj[header] = row[j];
      });
      if (row[1] !== undefined) {
        data.push(obj);
      }
    }

    const groupedData: CSVGroupedData = {};
    data.forEach(row => {
      const month = formatIndex(row['Date']);
      if (!groupedData[month]) {
        groupedData[month] = {};
      }
      const category = row['Blog'];
      groupedData[month][category] = (groupedData[month][category] || 0) + 1;
    });

    return groupedData;
  } catch (error) {
    console.error('Error loading CSV from URL:', error);
    return {};
  }
}

export function chartFromCSV(csvFile: string, element: string, options: ChartOptions = {}): void {
  loadCSVFromURL(csvFile).then(data => {
    const id = element.startsWith('#') ? element.substring(1) : element;
    const container = document.getElementById(id);
    if (container === null) {
      return;
    }
    const [width, height] = getSize(container, csvHeightVH);

    let xAxisData: string[] = [];
    if (addEmptyMonths) {
      const keys = Object.keys(data);
      if (keys.length > 0) {
        const first = new Date(keys[0]);
        const last = new Date(keys[keys.length - 1]);
        const firstYear = first.getFullYear();
        const lastYear = last.getFullYear();
        const yearRange = Array.from({ length: lastYear - firstYear + 1 }, (_, i) => firstYear + i);
        yearRange.forEach((y) => {
          [...Array(12).keys()].forEach((m) => {
            if ((y === first.getFullYear() && m < first.getMonth()) || (y === last.getFullYear() && m > last.getMonth())) {
              return
            }
            const missingMonth = `${y}-${(m + 1).toString().padStart(2, '0')}`
            xAxisData.push(formatIndex(missingMonth))
          });
        });
      }
    } else {
      xAxisData = Object.keys(data);
    }

    const seriesData: Record<string, unknown>[] = [];
    let colorIndex = 0;
    const categories = new Set(Object.keys(data).flatMap((key) => Object.keys(data[key])));
    for (const category of categories) {
      seriesData.push({
        name: category,
        type: 'bar',
        stack: 'total',
        data: xAxisData.map(month => {
          if (month in data) {
            return data[month][category] || 0
          }
          return 0;
        }),
        itemStyle: {
          color: palette[colorIndex % palette.length]
        },
        emphasis: {
          focus: 'series'
        }
      });
      colorIndex++;
    }

    let chartOptions: Record<string, unknown> = {
      color: palette,
      legend: {
        right: '15%',
        left: '15%',
        top: 5,
        data: seriesData.map(series => series.name)
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: <b>{c}</b>'
      },
      grid: {
        left: 56,
        right: 0,
        top: 20,
        bottom: '10%'
      },
      xAxis: {
        type: 'category',
        data: xAxisData,
        label: 'Date',
        axisLabel: {
          formatter: (value: string) => new Date(value).toLocaleString('default', { year: 'numeric', month: 'short' }),
          align: 'center'
        }
      },
      yAxis: {
        type: 'value',
        width: 54,
        label: 'Posts',
        scale: true,
        axisLabel: {
          formatter: '{value} Posts',
          align: 'center'
        }
      },
      series: seriesData,
      dataZoom: []
    };

    chartOptions = {...chartOptions, ...options};

    const chart = echarts.init(container, null, { renderer: 'svg', width: width, height: height });
    chart.setOption(chartOptions as unknown as echarts.EChartsOption);
    const registry = chartRegistry();
    (registry.charts ??= {})[String(container)] = chart
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
  const registry = chartRegistry();
  (registry.charts ??= {})[String(container)] = chart
}

function chartRegistry(): Record<string, Record<string, unknown>> {
  const w = window as unknown as { projektemacher?: Record<string, Record<string, unknown>> };
  w.projektemacher ??= {};
  return w.projektemacher;
}

function getSize(container: HTMLElement, defaultVH: number = defaultHeightVH): [number, number] {
  let width = container.offsetWidth;
  if (width === 0) {
    width = (container.parentElement?.parentElement as HTMLElement).offsetWidth;
  }
  let height = container.offsetHeight;
  if (height === 0) {
    height = Math.round(window.innerHeight / 100) * defaultVH;
  }
  return [width, height]
}

document.addEventListener('DOMContentLoaded', () => initializeChart());

window.initializeChart = initializeChart;
window.chart = chartFromCSV;
