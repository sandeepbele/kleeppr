const copyToClipboard = str => {
  const el = document.createElement('textarea');
  el.value = str;
  el.setAttribute('readonly', '');
  el.style.position = 'absolute';
  el.style.left = '-9999px';
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  document.body.removeChild(el);
};


function showAlert(alertText,showAfterNode) {
    hideAlert();
    const node = '<div id="myAlert" class="alert alert-warning fade in show" role="alert">' +
    '<strong>'+ alertText+'</strong>'+
    '<button type="button" class="close" aria-label="Close" onClick="hideAlert()">'+
    '<span aria-hidden="true">&times;</span>' +
    '</button></div>';
    $("#"+showAfterNode).append(node);
}

function hideAlert() {
    $("#myAlert").remove()
}

function validateForm(){
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }

function formValidatorEventListener(){
  'use strict';
  window.addEventListener('load', validateForm,false);
  }



//document.querySelector("#copy").addEventListener("click", copy);