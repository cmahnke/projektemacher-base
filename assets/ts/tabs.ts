function paneId(tab: HTMLAnchorElement): string {
  return tab.getAttribute("aria-controls") ?? tab.hash.replace(/^#/, "");
}

function switchTo(tab: HTMLAnchorElement): void {
  const tablist = tab.closest('[role="tablist"]');
  if (tablist === null) {
    return;
  }
  const tabs = Array.from(tablist.querySelectorAll<HTMLAnchorElement>('a[role="tab"]'));
  tabs.forEach((other) => {
    const selected = other === tab;
    other.classList.toggle("active", selected);
    other.setAttribute("aria-selected", String(selected));
  });
  const activeId = paneId(tab);
  tabs.map((other) => paneId(other)).forEach((id) => {
    const pane = document.getElementById(id);
    if (pane === null) {
      return;
    }
    const selected = id === activeId;
    pane.classList.toggle("active", selected);
    pane.classList.toggle("show", selected);
  });
}

window.showTab = function (id: string): void {
  const tab = document.getElementById(id);
  if (tab instanceof HTMLAnchorElement && tab.getAttribute("role") === "tab") {
    switchTo(tab);
  }
};

function init(): void {
  document.querySelectorAll<HTMLAnchorElement>('[role="tablist"] a[role="tab"]').forEach((tab) => {
    tab.addEventListener("click", (event) => {
      event.preventDefault();
      switchTo(tab);
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
