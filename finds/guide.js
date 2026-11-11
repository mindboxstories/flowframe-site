// Shop-by-person filter for Digittouch Finds gift guides
(function () {
  var chips = document.querySelectorAll('.g-chip');
  var cards = document.querySelectorAll('.g-card');
  var status = document.querySelector('.g-status');
  if (!chips.length) return;
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var on = chip.getAttribute('aria-pressed') === 'true';
      chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); });
      var who = on ? '' : chip.dataset.who;
      if (who) chip.setAttribute('aria-pressed', 'true');
      var n = 0;
      cards.forEach(function (card) {
        var match = !who || (' ' + card.dataset.who + ' ').indexOf(' ' + who + ' ') > -1;
        card.classList.toggle('dim', !match);
        if (match) n++;
      });
      if (status) {
        status.textContent = who
          ? n + ' gift' + (n === 1 ? '' : 's') + ' ' + chip.textContent.toLowerCase() + ' are highlighted below. Tap again to show all.'
          : '';
      }
      if (who) {
        var first = document.querySelector('.g-card:not(.dim)');
        if (first) first.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
      }
    });
  });
})();
