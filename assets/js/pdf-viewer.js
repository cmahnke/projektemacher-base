import PDFObject from 'pdfobject';

window.addPDFViewer = function (elemId, url, options) {
    if (options === undefined) {
        options = {
            pdfOpenParams: {
                navpanes: 1,
                toolbar: 1,
                statusbar: 1,
                scrollbar: 1,
                view: "FitH"
            },
            //forcePDFJS: true,
            PDFJS_URL: "/js/pdfjs/web/viewer.html"
        }
    }

    return  PDFObject.embed(url, elemId, options);
}
