const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("bernardReader", {
  desktop: true,
});
