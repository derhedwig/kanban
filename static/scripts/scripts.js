function autogrow(el) {
    el.style.setProperty('height', 'auto');
    var newHeight = el.offsetHeight + el.scrollHeight - el.clientHeight;
    if (newHeight == 0) return
    el.style.height = newHeight + "px";
}

// listen for input events everywhere
document.addEventListener("input", function (event) {
    if (event.target.tagName == "TEXTAREA") {
        autogrow(event.target)
    }
})

// run autogrow on page load
function initAutogrow() {
    document.querySelectorAll("textarea").forEach(function (el) {
        autogrow(el);
    })
}
document.addEventListener("DOMContentLoaded", initAutogrow)
document.addEventListener("htmx:afterOnLoad", initAutogrow)