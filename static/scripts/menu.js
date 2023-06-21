function myFunction() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "flex") {
        x.style.display = "none";
    } else {
        x.style.display = "flex";
        x.style.flexDirection = "column";
        x.style.marginTop = "80px";
        x.style.backgroundColor = "yellow";
    }
}
function toggleAbout() {
    var aboutDiv = document.getElementById("about");
    if (aboutDiv.style.display === "none") {
        aboutDiv.style.display = "block";
    } else {
        aboutDiv.style.display = "none";
    }
}