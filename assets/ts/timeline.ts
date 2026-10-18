import { Timeline } from "vis-timeline/standalone";

window.addTimeline = function (id: string, data: object, options?: object): Timeline {
  // See https://visjs.github.io/vis-timeline/docs/timeline/
  const div = document.getElementById(id);
  const timeline = new Timeline(
    div as HTMLElement,
    data as ConstructorParameters<typeof Timeline>[1],
    options as ConstructorParameters<typeof Timeline>[2],
  );
  return timeline;
};
