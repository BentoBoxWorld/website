function selectedGameMode(){
    document.getElementById("submit-button").removeAttribute('disabled');
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
