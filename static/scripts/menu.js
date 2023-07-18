function myFunction() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "flex") {
        x.style.display = "none";
    } else {
        x.style.display = "flex";
        x.style.flexDirection = "column";
        x.style.marginTop = "80px";
        x.style.backgroundColor = "rgba(237, 226, 226, 0.8)";
    }
}

function showabout() {
    var div1 = document.getElementById('aboutid');
    var div2 = document.getElementById('scheduleid');
    var div3 = document.getElementById('mainid')
    div1.style.display = 'flex';
    div2.style.display = 'none';
    div3.style.display = 'none';
}

function showschedule() {
    var div1 = document.getElementById('aboutid');
    var div2 = document.getElementById('scheduleid');
    var div3 = document.getElementById('mainid')
    div1.style.display = 'none';
    div2.style.display = 'flex';
    div3.style.display = 'none';
    
}

function showhome() {
    var div1 = document.getElementById('aboutid');
    var div2 = document.getElementById('scheduleid');
    var div3 = document.getElementById('mainid')

    div1.style.display = 'none';
    div2.style.display = 'none';
    div3.style.display = 'flex';
}
