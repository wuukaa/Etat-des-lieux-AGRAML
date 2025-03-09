const generateUUID = () =>
    ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
      (
        c ^
        (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
      ).toString(16)
    );
    
      function ajouterInput()
      {
        var uuid = generateUUID();
        var divElement = document.getElementById('imagesInputs'); 
        var newdiv = document.createElement('div');
        var buttondiv = document.createElement('div');
        var inputImage = document.createElement("input");
        var suppBooutton = document.createElement("button");
        var sautLigne = document.createElement("br");
        buttondiv.setAttribute("class", "input-group mb-3")
        newdiv.setAttribute('id',uuid);
        newdiv.setAttribute('class', 'col');
        inputImage.setAttribute("name", "-1.image." + uuid);
        inputImage.setAttribute("type", "file");
        inputImage.setAttribute("class", "form-control");
        suppBooutton.setAttribute("href", "#");
        suppBooutton.setAttribute("class", "btn-outline-danger btn btn-outline-secondary");
        suppBooutton.setAttribute("onclick", "RemoveHtmlElement('" + uuid + "')");
        suppBooutton.textContent = "X";
        buttondiv.appendChild(inputImage);
        buttondiv.appendChild(suppBooutton);
        buttondiv.appendChild(sautLigne);
        newdiv.appendChild(buttondiv);
        divElement.appendChild(newdiv);
          
      }
      function RemoveHtmlElement(divNum)
      { 
          var divId = document.getElementById("imagesInputs"); 
          var childId = document.getElementById(divNum); 
          divId.removeChild(childId); 
      }