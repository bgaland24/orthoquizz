/* ================================================================
   POKEMON-SLIDER.JS — Défilement automatique du slider Pokémon
   ================================================================ */

(function () {
    var imgs    = document.querySelectorAll('#pokemonSlider img');
    var current = 0;
    setInterval(function () {
        imgs[current].classList.remove('active');
        current = (current + 1) % imgs.length;
        imgs[current].classList.add('active');
    }, 3000);
})();
