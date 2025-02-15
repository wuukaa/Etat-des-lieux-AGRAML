const dropdown = document.getElementById("structure-type-logement");

dropdown.addEventListener("change", function() {
  document.getElementById("logement-selection").submit();
});