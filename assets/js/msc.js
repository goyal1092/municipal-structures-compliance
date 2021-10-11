// Instantiate MDC Drawer
if (document.querySelector(".mdc-text-field")) {
  document.querySelectorAll(".mdc-text-field").forEach(function (el) {
    new mdc.textField.MDCTextField(el);
  });
}

if (document.querySelector(".mdc-button")) {
  const buttonRipple = new mdc.ripple.MDCRipple(
    document.querySelector(".mdc-button")
  );
}

const opener = document.getElementById("mdc-drawer-opener");
const appBar = document.getElementById("app-bar");
if (opener) {
  const drawerEl = document.querySelector(".mdc-drawer");
  const drawer = new mdc.drawer.MDCDrawer.attachTo(drawerEl);
  opener.addEventListener("click", () => {
    if (drawer.open) {
      opener.innerText = "menu";
      drawer.open = false;
      appBar.classList.remove('is-zindex-7');
    } else {
      opener.innerText = "close";
      drawer.open = true;
      appBar.classList.add('is-zindex-7');
    }
  });
}
