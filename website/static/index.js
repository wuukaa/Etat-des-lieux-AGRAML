function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }

const dropdown = document.getElementById("structure-type-logement");

dropdown.addEventListener("change", function() {
  document.getElementById("logement-selection").submit();
});