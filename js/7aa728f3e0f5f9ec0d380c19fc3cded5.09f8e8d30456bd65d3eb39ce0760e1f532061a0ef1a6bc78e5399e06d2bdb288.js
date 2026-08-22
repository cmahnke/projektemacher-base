(()=>{})();

;
(()=>{function d(o,t){o.addEventListener("click",e=>{let a=t.value;navigator.clipboard.writeText(a).then(()=>{},()=>{console.warn("Failed to write to clipboard!")})})}window.addCopyToClipboard=d;})();
