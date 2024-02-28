window.addFSToggle = function (button, elem) {
    button.addEventListener('click', function() {
        var fsStyle = 'position: fixed; top: 0; left: 0; height: 100%; width: 100%; overflow: hidden;';
        var closeClass = 'close';
        if (!document.fullscreenElement) {

            elem.setAttribute('style', fsStyle);
            button.setAttribute('style', 'position: fixed;');
            button.classList.add(closeClass);
            document.querySelector('body').setAttribute('style', 'overflow: hidden;');
            document.documentElement.requestFullscreen();
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
                elem.setAttribute('style', '');
                button.setAttribute('style', '');
                button.classList.remove(closeClass);
                document.querySelector('body').setAttribute('style', '');
            }
        }
    });
};
