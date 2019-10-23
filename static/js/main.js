function selectedGameMode(){
    elements = document.querySelectorAll("input");
    
    if (elements[0].checked || elements[1].checked || elements[2].checked || elements[3].checked){
        document.getElementById("submit-button").removeAttribute('disabled');
    }else{
        document.getElementById("submit-button").setAttribute('disabled', true);
    }

}

function playLoadingAnimation(){
    document.getElementById("submit-button").classList.add("is-loading");
    
    setInterval(function() {
        if (document.cookie.indexOf("downloaded=") >= 0) {
            document.cookie = 'downloaded=; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
            document.getElementById("submit-button").classList.remove("is-loading");
        }
      }, 100);
}

var textBox = document.getElementById("textbox");
var textBoxTitle = document.getElementById("textboxTitle");

function showDescription(labelEle){
    textBoxTitle.innerHTML = labelEle.getAttribute("data-title");
    textBox.innerHTML = labelEle.getAttribute("data-desc");
}
