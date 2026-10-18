// See https://observablehq.com/@d3/stacked-to-grouped-bars
//import { bb, bar } from 'billboard.js';
import * as echarts from 'echarts';

const defaultHeightVH = 50;
const addEmptyMonths = true

/*
const colors = [
    '#c23531',
    '#2f4554',
    '#61a0a8',
    '#d48265',
    '#91c7ae',
    '#749f83',
    '#ca8622',
    '#bda29a',
    '#6e7074',
    '#546570',
    '#c4ccd3'
  ];
  */

//const colors = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9', '#ffffff', '#000000'];

const colors = [
  "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5", "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"];

function formatIndex(dateStr) {
  const date = new Date(dateStr);
  const month = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
  return month;
}

async function loadCSVFromURL(url) {
  try {
    const response = await fetch(url);
    const text = await response.text();
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
      const row = lines[i].split(',');
      const obj = {};
      headers.forEach((header, j) => {
        obj[header] = row[j];
      });
      if (row[1] !== undefined) {
        data.push(obj);
      } else {
        //console.warn('Blog is empty: ', row);
      }
    }

    let groupedData = {};
    data.forEach(row => {

      const month = formatIndex(row['Date'])
      if (!groupedData[month]) {
        groupedData[month] = {};
      }
      const category = row['Blog'];
      groupedData[month][category] = (groupedData[month][category] || 0) + 1;
    });

    //console.log(groupedData);
    return groupedData;
  } catch (error) {
    console.error('Error loading CSV from URL:', error);
    return [];
  }
}

function chart(csvFile, element, options) {
  if (element.startsWith('#')) {
    element = element.substring(1);
  }
  loadCSVFromURL(csvFile).then(data => {
    const container = document.getElementById(element)
    let width = container.offsetWidth;
    if (width === 0) {
      width = container.parentElement.parentElement.offsetWidth;
    }
    let height = container.offsetHeight;
    if (height === 0) {
      height = Math.round(window.innerHeight / 100) * defaultHeightVH;
    }

    let xAxisData = [];
    if (addEmptyMonths) {
      const filledData = {};
      const first = new Date(Object.keys(data)[0]);
      const last = new Date(Object.keys(data).slice(-1));
      const firstYear = first.getFullYear();
      const lastYear = last.getFullYear();
      const yearRange = Array.from({ length: lastYear - firstYear + 1 }, (_, i) => firstYear + i);
      yearRange.forEach((i) => {
        const y = i;
        [...Array(12).keys()].forEach((m) => {
          if ((y == first.getFullYear() && m < first.getMonth()) || (y == last.getFullYear() && m > last.getMonth())) {
            return
          }
          let missingMonth = `${y}-${(m + 1).toString().padStart(2, '0')}`
          xAxisData.push(formatIndex(missingMonth))
        });
      });
      //console.log(first, last, yearRange, xAxisData);
    } else {
      xAxisData = Object.keys(data);
    }


    const seriesData = [];
    let colorIndex = 0;
    const blogs = new Set(Object.keys(data).map((key) => { return Object.keys(data[key])[0] }));
    //WTF: `for in` won't work with Sets and only itereates over array index, JS is stupid as shit
    for (const blog of [...blogs]) {
      seriesData.push({
        name: blog,
        type: 'bar',
        stack: 'total',
        data: xAxisData.map(month => {
          if (month in data) {
            return data[month][blog] || 0
          }
          return 0;
        }),
        itemStyle: {
          color: colors[colorIndex % colors.length]
        },
        emphasis: {
          focus: 'series'
        }
      });
      colorIndex++;
    }

    let chartOptions = {
      color: colors,
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
        label: "Date",
        //scale: true,
        axisLabel: {
          formatter: value => {
            return new Date(value).toLocaleString('default', { year: "numeric", month: "short"});
          },
          align: 'center'
        }
      },
      yAxis: {
        type: 'value',
        /*
        min: 'dataMin',
        max: 'dataMax',
        type: 'log',
        logBase: 2,
        */
        width: 54,
        label: "Posts",
        scale: true,
        axisLabel: {
          formatter: '{value} Posts',
          align: 'center'
        }
      },
      series: seriesData,
      dataZoom: []
    };

    if (options !== undefined && options != null) {
      chartOptions = {...chartOptions, ...options};
    }

    let chart = echarts.init(container, null, { renderer: "svg", width: width, height: height});
    chart.setOption(chartOptions);
  });
}

window.chart = chart;
