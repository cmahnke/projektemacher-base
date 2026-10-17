"use strict";(()=>{})();

;
"use strict";(()=>{function i(t,o){t.addEventListener("click",()=>{let e=o.value;navigator.clipboard.writeText(e).then(()=>{},()=>{console.warn("Failed to write to clipboard!")})})}window.addCopyToClipboard=i;})();
