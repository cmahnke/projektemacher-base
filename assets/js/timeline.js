import { Timeline } from 'vis-timeline/standalone';

window.addTimeline = function (id, data, options) {
    // See https://visjs.github.io/vis-timeline/docs/timeline/
    var div = document.getElementById(id);
    var timeline = new Timeline(div, data, options);
    return timeline;
}
