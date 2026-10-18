#!/usr/bin/env node

import puppeteer from 'puppeteer';
import fs from 'fs';
import toml from 'toml';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import axe from 'axe-core';

const waitMs = 30000;

const argv = yargs(hideBin(process.argv))
  .option('u', {
    alias: 'url',
    description: 'URL to check (defaults to the baseURL from the Hugo config, http://localhost:1313/ as fallback)',
    type: 'string'
  })
  .option('f', {
    alias: 'urls-file',
    description: 'JSON file with a "urls" array (e.g. test-urls.json), checked in addition to --url; relative paths resolve against the baseURL',
    type: 'string'
  })
  .option('o', {
    alias: 'output',
    description: 'Additionally write the markdown report to this file',
    type: 'string'
  })
  .option('c', {
    alias: 'config',
    description: 'Hugo configuration file (TOML) to read the baseURL from',
    type: 'string'
  })
  .option('w', {
    alias: 'wait',
    description: 'Milliseconds to wait for the page to settle after load',
    type: 'number',
    default: 3000
  })
  .option('i', {
    alias: 'include-meta-viewport',
    description: 'Do not exclude the meta-viewport rule (documented false positive for the disableScale feature)',
    type: 'boolean',
    default: false
  })
  .help()
  .alias('help', 'h')
  .parse();

function resolveBaseURL() {
  const candidates = argv.config ? [argv.config] : ['config.toml', 'hugo.toml'];
  for (const cf of candidates) {
    if (fs.existsSync(cf)) {
      const parsed = toml.parse(fs.readFileSync(cf, 'utf8'));
      if (parsed.baseURL) {
        return parsed.baseURL;
      }
    }
  }
  return 'http://localhost:1313/';
}

let baseURL = resolveBaseURL();
if (!baseURL.endsWith('/')) {
  baseURL += '/';
}

const pages = [];
if (argv.url) {
  pages.push(argv.url);
}
if (argv.urlsFile) {
  if (!fs.existsSync(argv.urlsFile)) {
    console.error('URL file %s doesn\'t exist, exiting!', argv.urlsFile);
    process.exit(1);
  }
  const list = JSON.parse(fs.readFileSync(argv.urlsFile, 'utf8'));
  const urls = Array.isArray(list) ? list : list.urls;
  if (!Array.isArray(urls)) {
    console.error('URL file %s contains no "urls" array, exiting!', argv.urlsFile);
    process.exit(1);
  }
  for (const u of urls) {
    const s = String(u);
    pages.push(/^https?:\/\//i.test(s) ? s : baseURL + s.replace(/^\/+/, ''));
  }
}
if (!pages.length) {
  pages.push(baseURL);
}

const disabledRules = argv.includeMetaViewport ? [] : ['meta-viewport'];
const results = [];

console.error('Base URL is %s', baseURL);
console.error('Checking %d page(s), excluded rules: %s', pages.length, disabledRules.join(', ') || 'none');

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-extensions']
});
const page = await browser.newPage();
page.setDefaultTimeout(waitMs);

for (const pageUrl of pages) {
  console.error('-> Checking %s', pageUrl);
  const entry = { url: pageUrl, error: null, violations: [] };
  try {
    await page.goto(pageUrl, { waitUntil: 'networkidle0', timeout: waitMs });
    await new Promise(r => setTimeout(r, argv.wait));
    await page.addScriptTag({ content: axe.source });
    entry.violations = await page.evaluate((disabled) => {
      const options = {};
      if (disabled.length) {
        options.rules = {};
        for (const id of disabled) {
          options.rules[id] = { enabled: false };
        }
      }
      return window.axe.run(options).then((r) => r.violations.map((v) => ({
        id: v.id,
        impact: v.impact,
        help: v.help,
        helpUrl: v.helpUrl,
        nodes: v.nodes.map((n) => n.target.join(' '))
      })));
    }, disabledRules);
  } catch (e) {
    entry.error = e.message;
  }
  results.push(entry);
}

await browser.close();

const impactOrder = { critical: 0, serious: 1, moderate: 2, minor: 3 };

function cell(s) {
  return String(s).replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
}

function pagePath(u) {
  try {
    return new URL(u).pathname;
  } catch {
    return u;
  }
}

function nodeCell(nodes) {
  if (!nodes.length) {
    return '—';
  }
  const shown = nodes.slice(0, 4).map((s) => '`' + cell(s) + '`');
  if (nodes.length > 4) {
    shown.push(`… (+${nodes.length - 4} more)`);
  }
  return shown.join('<br>');
}

function buildReport() {
  const lines = [];
  lines.push('# Accessibility report (axe-core)');
  lines.push('');
  lines.push('- **Generated**: ' + new Date().toISOString());
  lines.push('- **axe-core version**: ' + axe.version);
  lines.push('- **Base URL**: ' + baseURL);
  lines.push('- **Excluded rules**: ' + (disabledRules.join(', ') || 'none'));
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push('| Page | Rules | Nodes | Critical | Serious | Moderate | Minor |');
  lines.push('|---|---|---|---|---|---|---|');
  for (const r of results) {
    if (r.error) {
      lines.push('| [' + cell(pagePath(r.url)) + '](' + r.url + ') | load error | | | | | |');
      continue;
    }
    const counts = { critical: 0, serious: 0, moderate: 0, minor: 0 };
    let nodeCount = 0;
    for (const v of r.violations) {
      nodeCount += v.nodes.length;
      if (v.impact in counts) {
        counts[v.impact] += v.nodes.length;
      }
    }
    const status = r.violations.length ? String(r.violations.length) : '0';
    lines.push('| [' + cell(pagePath(r.url)) + '](' + r.url + ') | ' + status + ' | ' + nodeCount + ' | ' +
      counts.critical + ' | ' + counts.serious + ' | ' + counts.moderate + ' | ' + counts.minor + ' |');
  }
  lines.push('');
  for (const r of results) {
    lines.push('## ' + r.url);
    lines.push('');
    if (r.error) {
      lines.push('**Page failed to load**: ' + cell(r.error));
      lines.push('');
      continue;
    }
    if (!r.violations.length) {
      lines.push('No violations found.');
      lines.push('');
      continue;
    }
    const sorted = [...r.violations].sort((a, b) =>
      ((impactOrder[a.impact] ?? 4) - (impactOrder[b.impact] ?? 4)) || a.id.localeCompare(b.id));
    lines.push('| Rule | Impact | Nodes | Help |');
    lines.push('|---|---|---|---|');
    for (const v of sorted) {
      const help = '[' + cell(v.help) + '](' + v.helpUrl + ')';
      lines.push('| `' + cell(v.id) + '` | ' + cell(v.impact || 'n/a') + ' | ' + nodeCell(v.nodes) + ' | ' + help + ' |');
    }
    lines.push('');
  }
  return lines.join('\n') + '\n';
}

const report = buildReport();
process.stdout.write(report);
if (argv.output) {
  fs.writeFileSync(argv.output, report);
  console.error('Report written to %s', argv.output);
}

if (results.some((r) => r.error)) {
  console.error('One or more pages failed to load, exiting with code 2');
  process.exit(2);
}
