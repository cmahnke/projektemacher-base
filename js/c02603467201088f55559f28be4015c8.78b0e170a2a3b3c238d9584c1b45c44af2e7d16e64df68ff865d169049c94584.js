"use strict";(()=>{})();

;
"use strict";(()=>{document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("input.i18n-search").forEach(e=>{let t=document.getElementById(e.dataset.i18nTable);if(!t)return;let n=t.querySelectorAll("tbody tr"),l=e.dataset.i18nTable.replace("i18n-table-",""),o=document.querySelector(`[data-i18n-count="${l}"]`),s=()=>{let a=e.value.trim().toLowerCase(),c=0;n.forEach(r=>{let d=!a||r.textContent.toLowerCase().includes(a);r.hidden=!d,d&&c++}),o&&(o.textContent=`${c} / ${n.length}`)};e.addEventListener("input",s)})});})();
