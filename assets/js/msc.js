// Instantiate MDC Drawer
if (document.getElementById("mdc-drawer-opener")) {
  const drawerEl = document.querySelector(".mdc-drawer");
  const drawer = new mdc.drawer.MDCDrawer.attachTo(drawerEl);
  document.getElementById("mdc-drawer-opener").addEventListener("click", () => {
    drawer.open = !drawer.open;
  });
}
