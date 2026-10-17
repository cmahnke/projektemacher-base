/*
 * PostCSS configuration for the theme's stylesheet pipeline
 * (layouts/partials/html/head/style.html).
 *
 * This file is picked up automatically by Hugo's css.PostCSS: Hugo
 * searches the assets filesystem at 'assets/_jsconfig/' (project first,
 * theme second) before falling back to a 'postcss.config.js' in the
 * site root. Sites using this theme therefore need no PostCSS setup of
 * their own.
 *
 * It removes duplicated CSS rules which appear when the separately
 * compiled SCSS resources and plain CSS resources are concatenated.
 *
 * The plugin ships with the theme's package.json and is installed into
 * the site's node_modules via 'scripts/init/package.json.sh'. If it
 * can't be loaded (no node_modules or incomplete install), the plugin
 * list stays empty and the CSS passes through unprocessed.
 */
const plugins = [];
try {
  // This file is loaded as CommonJS by PostCSS, require() is the only way to load the plugin
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  plugins.push(require('postcss-discard-duplicates'));
} catch {
  console.warn("[projektemacher-base] postcss-discard-duplicates not installed, skipping CSS deduplication (run 'npm install', see the theme's scripts/init/package.json.sh)");
}

module.exports = { plugins };
