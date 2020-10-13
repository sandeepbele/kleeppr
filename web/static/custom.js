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



//document.querySelector("#copy").addEventListener("click", copy);