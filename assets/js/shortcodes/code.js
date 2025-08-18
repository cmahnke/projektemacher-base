function addCopyToClipboard(button, content) {
  button.addEventListener("click", (e)  => {
    const text = content.value;

    navigator.clipboard.writeText(text).then(() => {
      /*console.log(`Wrote '${text}' to clipboard`);*/
    }, () => {
      console.warn("Failed to write to clipboard!");
    });
  })

}

window.addCopyToClipboard = addCopyToClipboard

//export { addCopyToClipboardButtons }
