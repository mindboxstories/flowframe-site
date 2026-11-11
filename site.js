// flowframe.shop shared behaviour: Black Friday countdown, gift-guide bar state, article contents highlight
(function () {
  var ann = document.querySelector('.ann[data-countdown]');
  if (ann) {
    var days = Math.ceil((new Date(ann.dataset.countdown + 'T00:00:00') - new Date()) / 86400000);
    var b = ann.querySelector('.ann-days'), s = ann.querySelector('span');
    if (days > 1) b.textContent = days + ' days';
    else if (days === 1) b.textContent = '1 day';
    else if (s) s.innerHTML = '<b>Black Friday deals are live.</b> <i class="x"> Our gift guides are re-checked every week.</i>';
  }
  var badge = document.querySelector('.mz-badge[data-countdown]');
  if (badge) {
    var d = Math.ceil((new Date(badge.dataset.countdown + 'T00:00:00') - new Date()) / 86400000);
    if (d <= 0) { badge.querySelector('b').textContent = 'Now'; badge.querySelector('span').textContent = 'Black Friday deals are live'; }
    else badge.querySelector('b').textContent = d;
  }
  if (!('IntersectionObserver' in window)) return;
  function spy(links, targets) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id); });
      });
    }, { rootMargin: '-35% 0px -60% 0px' });
    targets.forEach(function (t) { if (t) io.observe(t); });
  }
  var bar = document.querySelectorAll('.g-bar a');
  if (bar.length) spy(bar, Array.prototype.map.call(bar, function (a) { return document.querySelector(a.getAttribute('href')); }));
  var toc = document.querySelectorAll('.toc ol a');
  if (toc.length) spy(toc, Array.prototype.map.call(toc, function (a) { return document.querySelector(a.getAttribute('href')); }));
})();
