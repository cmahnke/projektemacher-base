import PDFObject from 'pdfobject';

interface PDFViewerParams {
  [key: string]: unknown;
  pdfOpenParams: {
    navpanes: number;
    toolbar: number;
    statusbar: number;
    scrollbar: number;
    view: string;
  };
  PDFJS_URL: string;
}

window.addPDFViewer = function (elemId: string, url: string, options?: PDFViewerParams): unknown {
  if (options === undefined) {
    options = {
      pdfOpenParams: {
        navpanes: 1,
        toolbar: 1,
        statusbar: 1,
        scrollbar: 1,
        view: 'FitH',
      },
      //forcePDFJS: true,
      PDFJS_URL: '/pdfjs/web/viewer.html',
    };
  }

  return PDFObject.embed(url, elemId, options);
};
