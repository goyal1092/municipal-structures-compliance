// Instantiate MDC Drawer
const opener = document.getElementById("mdc-drawer-opener");
if (opener) {
  const drawerEl = document.querySelector(".mdc-drawer");
  const drawer = new mdc.drawer.MDCDrawer.attachTo(drawerEl);
  opener.addEventListener("click", () => {
    if (drawer.open) {
      opener.innerText = "menu";
      drawer.open = false;
    } else {
      opener.innerText = "close";
      drawer.open = true;
    }
  });
}
