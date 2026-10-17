/*
 * Client side column filter for the single i18n strings table rendered by
 * the 'i18n-strings' shortcode. Each language's search input (in the table
 * header) filters rows by the key and that language's column; active
 * filters are combined. The counter shows how many rows match the column's
 * own filter. See content/i18n/index.md.
 */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('table.i18n-table').forEach((table) => {
    const rows = [...table.querySelectorAll('tbody tr')];
    const filters = [...table.querySelectorAll('input.i18n-search')].map((input) => ({
      input,
      column: input.closest('th').cellIndex,
      counter: document.querySelector(`[data-i18n-count="${input.dataset.i18nLang}"]`),
    }));

    const matches = (row, filter, query) =>
      row.cells[filter.column].textContent.toLowerCase().includes(query) ||
      row.cells[0].textContent.toLowerCase().includes(query);

    const update = () => {
      const queries = filters.map((f) => f.input.value.trim().toLowerCase());
      rows.forEach((row) => {
        row.hidden = !filters.every((f, i) => !queries[i] || matches(row, f, queries[i]));
      });
      filters.forEach((f, i) => {
        if (!f.counter) {
          return;
        }
        const visible = queries[i] ? rows.filter((row) => matches(row, f, queries[i])).length : rows.length;
        f.counter.textContent = `${visible} / ${rows.length}`;
      });
    };

    filters.forEach((f) => f.input.addEventListener('input', update));
  });
});
