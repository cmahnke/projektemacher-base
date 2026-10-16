function addCopyToClipboard(button: HTMLButtonElement, content: HTMLTextAreaElement): void {
  button.addEventListener('click', () => {
    const text: string = content.value;

    navigator.clipboard.writeText(text).then(() => {
      /*console.log(`Wrote '${text}' to clipboard`);*/
    }, () => {
      console.warn('Failed to write to clipboard!');
    });
  });
}

window.addCopyToClipboard = addCopyToClipboard;

//export { addCopyToClipboardButtons }
