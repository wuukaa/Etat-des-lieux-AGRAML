function updatePar() {
    document.getElementById("filtre-form").submit();
  }

  function reinitialiserFiltre()
  {
    document.cookie = 'batiment=-; etage=-; type=-; prenom=; nom='
    batiment.value = '-';
    etage.value = '-';
    type.value = '-';
    prenom.value = '';
    nom.value = '';
    updatePar()
  }