/*
 * Client side column filter for the single i18n strings table rendered by
 * the 'i18n-strings' shortcode. Each language's search input (in the table
 * header) filters rows by the key and that language's column; active
 * filters are combined. The counter shows how many rows match the column's
 * own filter. See content/i18n/index.md.
 */
interface I18nFilter {
  input: HTMLInputElement;
  column: number;
  counter: Element | null;
}

document.addEventListener("DOMContentLoaded", () => {
  const tables = document.querySelectorAll<HTMLTableElement>("table.i18n-table");
  tables.forEach((table) => {
    const rows = Array.from(table.querySelectorAll<HTMLTableRowElement>("tbody tr"));
    const filters: I18nFilter[] = Array.from(
      table.querySelectorAll<HTMLInputElement>("input.i18n-search")
    ).map((input) => {
      const th = input.closest<HTMLTableCellElement>("th");
      return {
        input,
        column: th === null ? 0 : th.cellIndex,
        counter: document.querySelector(`[data-i18n-count="${input.dataset.i18nLang}"]`),
      };
    });

    const matches = (row: HTMLTableRowElement, filter: I18nFilter, query: string): boolean => {
      const cell = (row.cells[filter.column]?.textContent ?? "").toLowerCase();
      const key = (row.cells[0]?.textContent ?? "").toLowerCase();
      return cell.includes(query) || key.includes(query);
    };

    const update = (): void => {
      const queries = filters.map((f) => f.input.value.trim().toLowerCase());
      rows.forEach((row) => {
        row.hidden = !filters.every((f, i) => queries[i] === "" || matches(row, f, queries[i]));
      });
      filters.forEach((f, i) => {
        if (f.counter === null) {
          return;
        }
        const visible = queries[i] !== ""
          ? rows.filter((row) => matches(row, f, queries[i])).length
          : rows.length;
        f.counter.textContent = `${visible} / ${rows.length}`;
      });
    };

    filters.forEach((f) => {
      f.input.addEventListener("input", update);
    });
  });
});
