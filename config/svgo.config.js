module.exports = {
  multipass: true,
  plugins: [
    "preset-default",
    // v4 disabled both in preset-default; keep the v3 default behaviour
    "removeViewBox",
    "removeTitle",
    "removeEditorsNSData",
    {name: "removeAttrs",
      params: { "attrs": "(font-weight|font-size|font-family)" }
    }
  ]
}
