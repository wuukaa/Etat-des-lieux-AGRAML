function updatePar() {
  document.getElementById("form_theme").submit();
}

var signaturePad = new SignaturePad(document.getElementById('signature-pad'), {
  backgroundColor: 'rgba(255, 255, 255, 0)',
  penColor: 'rgb(0, 0, 0)'
});
var saveButton = document.getElementById('save');
var cancelButton = document.getElementById('clear');
var image = document.getElementById("image");

signaturePad.fromDataURL(image.getAttribute("value"), { ratio: 1, width: 400, height: 200, xOffset: 0, yOffset: 0 });

signaturePad.addEventListener('endStroke', function (event) {
  var data = signaturePad.toDataURL('image/png');
  image.setAttribute("value", data);
});

cancelButton.addEventListener('click', function (event) {
  signaturePad.clear();
});