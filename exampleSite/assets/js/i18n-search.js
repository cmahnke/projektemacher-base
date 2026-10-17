/*
 * Client side filter for the i18n strings tables rendered by the
 * 'i18n-strings' shortcode. See content/i18n/index.md.
 */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input.i18n-search').forEach((input) => {
    const table = document.getElementById(input.dataset.i18nTable);
    if (!table) {
      return;
    }
    const rows = table.querySelectorAll('tbody tr');
    const lang = input.dataset.i18nTable.replace('i18n-table-', '');
    const counter = document.querySelector(`[data-i18n-count="${lang}"]`);
    const update = () => {
      const query = input.value.trim().toLowerCase();
      let visible = 0;
      rows.forEach((row) => {
        const match = !query || row.textContent.toLowerCase().includes(query);
        row.hidden = !match;
        if (match) {
          visible++;
        }
      });
      if (counter) {
        counter.textContent = `${visible} / ${rows.length}`;
      }
    };
    input.addEventListener('input', update);
  });
});
