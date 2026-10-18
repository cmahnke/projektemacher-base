#!/usr/bin/env node

import puppeteer from 'puppeteer';
import lighthouse from 'lighthouse';
import fs from 'fs';
import toml from 'toml';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

const categoryIds = ['performance', 'accessibility', 'best-practices', 'seo'];
const categoryTitles = {
  'performance': 'Performance',
  'accessibility': 'Accessibility',
  'best-practices': 'Best Practices',
  'seo': 'SEO'
};

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
  .option('k', {
    alias: 'categories',
    description: 'Comma separated list of categories to run (' + categoryIds.join(', ') + ')',
    type: 'string'
  })
  .help()
  .alias('help', 'h')
  .parse();

let categories = categoryIds;
if (argv.categories) {
  categories = argv.categories.split(',').map((s) => s.trim()).filter(Boolean);
  const invalid = categories.filter((c) => !categoryIds.includes(c));
  if (invalid.length) {
    console.error('Unknown category: %s (allowed: %s)', invalid.join(', '), categoryIds.join(', '));
    process.exit(1);
  }
  if (!categories.length) {
    console.error('No valid categories given, exiting!');
    process.exit(1);
  }
}

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

console.error('Base URL is %s', baseURL);
console.error('Checking %d page(s), categories: %s', pages.length, categories.join(', '));

const browser = await puppeteer.launch({
  headless: true,
  args: ['--no-sandbox', '--disable-extensions']
});
const port = new URL(browser.wsEndpoint()).port;
const results = [];

for (const pageUrl of pages) {
  console.error('-> Running Lighthouse for %s', pageUrl);
  const entry = { url: pageUrl, error: null, lhr: null };
  try {
    const result = await lighthouse(pageUrl, {
      port,
      output: 'json',
      onlyCategories: categories.length === categoryIds.length ? undefined : categories,
      logLevel: 'error'
    });
    if (!result || !result.lhr) {
      entry.error = 'Lighthouse returned no result';
    } else {
      entry.lhr = result.lhr;
    }
  } catch (e) {
    entry.error = e.message;
  }
  results.push(entry);
}

await browser.close();

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

function scorePct(score) {
  if (score === null || score === undefined) {
    return '—';
  }
  return String(Math.round(score * 100));
}

function failedAudits(lhr, catId) {
  const cat = lhr.categories[catId];
  if (!cat) {
    return [];
  }
  const failures = [];
  for (const ref of cat.auditRefs) {
    const audit = lhr.audits[ref.id];
    if (!audit || audit.score === null || audit.score === undefined) {
      continue;
    }
    if (audit.score < 1 && ref.weight > 0) {
      failures.push({
        id: ref.id,
        title: audit.title,
        category: cat.title || categoryTitles[catId],
        score: audit.score,
        weight: ref.weight,
        displayValue: audit.displayValue || ''
      });
    }
  }
  failures.sort((a, b) => a.score - b.score);
  return failures;
}

function buildReport() {
  const lines = [];
  lines.push('# Lighthouse report');
  lines.push('');
  lines.push('- **Generated**: ' + new Date().toISOString());
  lines.push('- **Lighthouse version**: ' + (results.find((r) => r.lhr)?.lhr.lighthouseVersion || 'n/a'));
  lines.push('- **Base URL**: ' + baseURL);
  lines.push('- **Categories**: ' + categories.map((c) => categoryTitles[c]).join(', '));
  lines.push('');
  lines.push('## Scores');
  lines.push('');
  lines.push('| Page | ' + categories.map((c) => categoryTitles[c]).join(' | ') + ' |');
  lines.push('|---' + '|---'.repeat(categories.length) + '|');
  for (const r of results) {
    if (r.error || !r.lhr) {
      lines.push('| [' + cell(pagePath(r.url)) + '](' + r.url + ') | ' + categories.map(() => 'load error').join(' | ') + ' |');
      continue;
    }
    const scores = categories.map((c) => {
      const cat = r.lhr.categories[c];
      return cat ? scorePct(cat.score) : '—';
    });
    lines.push('| [' + cell(pagePath(r.url)) + '](' + r.url + ') | ' + scores.join(' | ') + ' |');
  }
  lines.push('');
  for (const r of results) {
    lines.push('## ' + r.url);
    lines.push('');
    if (r.error || !r.lhr) {
      lines.push('**Page failed to check**: ' + cell(r.error || 'no result'));
      lines.push('');
      continue;
    }
    const lhr = r.lhr;
    const perfRefs = lhr.categories.performance
      ? lhr.categories.performance.auditRefs.filter((ref) => ref.group === 'metrics')
      : [];
    if (perfRefs.length) {
      lines.push('### Metrics');
      lines.push('');
      lines.push('| Metric | Value |');
      lines.push('|---|---|');
      for (const ref of perfRefs) {
        const audit = lhr.audits[ref.id];
        lines.push('| ' + cell(audit?.title || ref.id) + ' | ' + cell(audit?.displayValue || '—') + ' |');
      }
      lines.push('');
    }
    lines.push('### Failed audits');
    lines.push('');
    const failures = categories.flatMap((c) => failedAudits(lhr, c));
    if (!failures.length) {
      lines.push('No scored audits failed.');
      lines.push('');
      continue;
    }
    lines.push('| Audit | Category | Score | Weight | Details |');
    lines.push('|---|---|---|---|---|');
    for (const f of failures) {
      lines.push('| `' + cell(f.id) + '`<br>' + cell(f.title) + ' | ' + cell(f.category) + ' | ' +
        scorePct(f.score) + '% | ' + f.weight + ' | ' + cell(f.displayValue || '—') + ' |');
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
  console.error('One or more pages failed to check, exiting with code 2');
  process.exit(2);
}
