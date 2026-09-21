/* The temperature page's slider: the library's one control a reader can drag.
 *
 * WHY THIS FILE HAS NO MATHS IN IT. The bar under the slider has to agree with the plate
 * above it at every position, and the plate is drawn from `Source/tools/odds.py`. So the
 * widths for every position on the slider are computed THERE, at build time, and baked
 * into the bar's `data-stops` attribute; this script looks a row up and writes it out. The
 * alternative - softmax written a second time, in JavaScript - is a second implementation
 * of the one thing on this page a reader can check by hand, and the two would agree until
 * the day they did not. `verify-links.py` recomputes the whole table from `odds.py` and
 * compares it to what shipped, so the page's numbers are checked even though this file
 * never computes them.
 *
 * WHAT IT DOES: unhides the control, moves four segment widths and three numbers.
 *
 * WHAT IT DOES NOT DO: run without being asked. The control is authored `hidden`, so a
 * reader whose script never arrives gets the plate and its caption - which is the whole
 * argument - and never meets a slider that would not move. It is also the reason this file
 * writes the initial state itself rather than trusting the markup: if a reader drags to a
 * position and then reloads, the markup's own bar and the read-out are what they see, and
 * both come from the same table.
 *
 * FOCUS IS LEFT ALONE. The slider ships as an ordinary `<input type="range">` with a label
 * and an `aria-valuetext` this file keeps in step with the picture, so every key a browser
 * gives a range input works here without anything below: arrows step it, Home and End jump
 * to the ends, and a screen reader announces the reading rather than a bare number.
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-temperature-dial]');
  if (!root) return;

  var input = root.querySelector('input[type="range"]');
  var bar = root.querySelector('svg');
  var segments = bar ? bar.querySelectorAll('[data-seg]') : [];
  var setting = root.querySelector('[data-readout="setting"]');
  var top = root.querySelector('[data-readout="top"]');
  var last = root.querySelector('[data-readout="last"]');
  if (!input || !bar || !segments.length || !setting) return;

  var stops = [];
  try {
    stops = JSON.parse(bar.getAttribute('data-stops')) || [];
  } catch (err) {
    stops = [];
  }
  var gap = parseFloat(bar.getAttribute('data-gap'));
  if (!stops.length || isNaN(gap)) return;

  // Matched by value rather than by index: a browser that rounds a step differently still
  // lands on the row whose setting it is showing, and a position with no row draws nothing
  // rather than a bar made of guesses.
  function rowFor(value) {
    for (var i = 0; i < stops.length; i++) {
      if (Math.abs(stops[i].t - value) < 0.001) return stops[i];
    }
    return null;
  }

  function percent(n) {
    return (Math.round(n * 10) / 10).toFixed(1) + '%';
  }

  function draw() {
    var row = rowFor(parseFloat(input.value));
    if (!row) return;
    var x = 0;
    for (var i = 0; i < segments.length; i++) {
      var w = i < row.w.length ? row.w[i] : 0;
      segments[i].setAttribute('x', x);
      segments[i].setAttribute('width', w);
      x += w + gap;
    }
    var reading = String(row.t);
    setting.textContent = reading;
    if (top) top.textContent = percent(row.top);
    if (last) last.textContent = percent(row.last);
    // The picture is one number to a screen reader, and a bare "1.5" would say nothing
    // about what moved, so the slider's own value text carries the reading.
    input.setAttribute('aria-valuetext',
      'setting ' + reading + ', likeliest word takes ' + percent(row.top));
  }

  root.removeAttribute('hidden');
  input.addEventListener('input', draw);
  draw();
})();
