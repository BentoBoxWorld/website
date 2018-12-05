var URL_MODULES = "https://ci.codemc.org/job/BentoBoxWorld/api/json"

//var addons = 

function buildForm(){
  fetch(URL_MODULES, {'mode': 'no-cors'})
  .then(res => res.json())
  .then((out) => {
    console.log('Checkout this JSON! ', out);
})
.catch(err => { throw err });
}

function createJar(){
  alert("test");
}