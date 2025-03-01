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

  var form = document.getElementById('edl_form');

  form.addEventListener('submit', () => {
    if(document.getElementById('visible').checked) {
        document.getElementById('cache').disabled = true;
    }
});

var button = document.getElementById("file1");

  button.addEventListener('change', (event) => {
    button.setAttribute("id", "");
    addElement();
    button = document.getElementById("file1");
  });

function addElement() {
  const newDiv = document.createElement("new");
  var x = document.createElement("INPUT");
  x.setAttribute("id", "file1");
  x.setAttribute("type", "file");
  x.setAttribute("class", "form-control");
  newDiv.appendChild(x);
  const currentDiv = document.getElementById("file-div");
  currentDiv.appendChild(newDiv);
};