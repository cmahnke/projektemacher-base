import Mirador from 'mirador/dist/mirador.min.js';
//import Mirador from 'mirador/dist/es/src'
import unfetch from 'unfetch';
const fetch = unfetch;

window.addMirador = function (id, uri) {
    // Languages
    var lang = 'en';
    if (document.documentElement.lang !== undefined) {
        lang = document.documentElement.lang;
    }

    var mirador = Mirador.viewer({
        id: id,
        // See https://github.com/ProjectMirador/mirador/blob/master/src/config/settings.js
        language: lang,
        availableLanguages: {
          de: 'Deutsch',
          en: 'English',
        },
        windows: [{
            "loadedManifest": uri,
            thumbnailNavigationDisplayed: false
        }],
        window: {
            allowFullscreen: true,
            allowMaximize: false,
            allowClose: false,
            allowTopMenuButton: true, //false
      	    defaultSideBarPanel: 'info',
      	    sideBarOpenByDefault: false,
            defaultView: 'single',
            hideWindowTitle: true,
            panels: {
                info: true,
                attribution: false,
                canvas: false,
                annotations: false,
                search: false
            },
            views: [
                { key: 'single', behaviors: ['individuals'] },
                { key: 'book', behaviors: ['paged'] }
            ]
        },
        workspace: {
             draggingEnabled: false,
             allowNewWindows: false,
      	     showZoomControls: true,
             type: 'mosaic'
        },
        workspaceControlPanel: {
          enabled: false,
        }
    });
    return mirador;
}
