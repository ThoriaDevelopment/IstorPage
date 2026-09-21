/* /search.js - the library's search palette.
 *
 * The directory has a find field, and it can only find what is on the directory.
 * This is the same idea with the whole library behind it, openable from any page
 * and from the keyboard, reading /search-index.json - a file built from the pages
 * themselves by Source/tools/make-search-index.py.
 *
 * FOUR DECISIONS:
 *
 * * **The rule is the directory's rule.** Every word typed has to appear, all of
 *   them, in any order. No ranking and no fuzzing: a rule a reader can predict
 *   after two searches beats a rank they cannot see, and the ordering below is the
 *   library's own order rather than a score. The matched words are marked in the
 *   result, so the reader can see why each one is there.
 * * **The results are links, and focus moves to them.** The same one focus order
 *   the directory uses: the field, then each result, then the field again. No ARIA
 *   listbox is layered over a list of links; a reader's screen reader announces
 *   each page's title as they arrive, and Enter activates natively.
 * * **It ships as a link and becomes a dialog.** The trigger in the header is an
 *   `<a href="/library/">`, so a reader whose script does not run still gets the
 *   directory rather than a button that does nothing. This file only upgrades it.
 * * **Nothing from the index is ever written as markup.** Every string arrives in
 *   a text node, built by `write()`. A search index is page text; page text that
 *   can carry markup is page text that can carry an injection.
 *
 * AND ONE THING THAT IS NOT ABOUT ORDER BUT ABOUT WHAT COUNTS AS A MATCH, because
 * a substring rule alone is not the rule a reader is holding in their head: it
 * survives an inflection the page did not write ("model" is inside "models") and
 * fails the direction a reader is most likely to type, which is the one where the
 * page wrote the singular and they typed the plural. "hallucinations" appears in
 * no page and "hallucination" is the title of one. So a typed word is folded into
 * a short list of spellings OF THAT WORD - see FOLD below - and the same all-words
 * rule runs over the list. The count still counts pages, the mark still marks the
 * words that matched, and the list is capped, because a rule that is predictable
 * after two searches is the whole point of this file.
 */
(function () {
  'use strict';

  var opener = document.querySelector('[data-search-open]');
  if (!opener) return;

  var INDEX = '/search-index.json';
  var SHOWN = 8;            /* rows before the count takes over */

  var records = null;       /* null until the first open */
  var asked = false;        /* a fetch is in flight */
  var broke = false;        /* the fetch failed */
  var kept = '';            /* what was typed last, so reopening continues */

  var dialog = null, field = null, said = null, list = null, foot = null;
  var total = 0;

  /* The page's own find field, if it has one - the directory does. `/` belongs to
     it there: the directory's copy invites the reader to press `/` to search the
     list in front of them, and a palette that hijacked that key would open a
     second search over the first. The palette keeps Cmd/Ctrl+K and its own link. */
  var pageFind = document.querySelector('.index-find');

  /* ── the palette's own markup, built once ─────────────────────────────── */

  function build() {
    if (dialog) return;
    dialog = document.createElement('dialog');
    dialog.className = 'palette';
    dialog.setAttribute('aria-labelledby', 'palette-label');

    var panel = document.createElement('div');
    panel.className = 'palette-panel';

    var label = document.createElement('label');
    label.className = 'palette-label';
    label.id = 'palette-label';
    label.setAttribute('for', 'palette-field');
    label.textContent = 'Search the library';

    field = document.createElement('input');
    field.className = 'palette-field';
    field.id = 'palette-field';
    field.type = 'search';
    field.autocomplete = 'off';
    field.spellcheck = false;
    field.placeholder = 'what is a context window';

    said = document.createElement('p');
    said.className = 'palette-said';
    said.setAttribute('role', 'status');

    list = document.createElement('ul');
    list.className = 'palette-results';

    foot = document.createElement('p');
    foot.className = 'palette-foot';

    panel.appendChild(label);
    panel.appendChild(field);
    panel.appendChild(said);
    panel.appendChild(list);
    panel.appendChild(foot);
    dialog.appendChild(panel);
    document.body.appendChild(dialog);

    field.addEventListener('input', render);
    field.addEventListener('keydown', fromField);
    list.addEventListener('keydown', fromResult);
    /* A click that reaches the dialog itself landed outside the panel: the panel
       is the only child, and the dialog's own background is transparent. */
    dialog.addEventListener('click', function (event) {
      if (event.target === dialog) close();
    });
    dialog.addEventListener('close', function () {
      kept = field.value;
      opener.setAttribute('aria-expanded', 'false');
    });
  }

  /* ── loading ──────────────────────────────────────────────────────────── */

  function load() {
    if (records || asked) return;
    asked = true;
    fetch(INDEX, { credentials: 'same-origin' })
      .then(function (response) {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then(function (data) {
        records = data.map(function (record) {
          record.hay = [record.title, record.summary]
            .concat(record.lines).join(' ').toLowerCase();
          return record;
        });
        total = records.length;
        /* `foot` is null until the palette is built, and this runs in a promise: a
           response that arrived before the dialog existed would take the whole
           success path down with it and be reported to the reader as a failed
           load. The audit's own self-test found that by making the fetch early. */
        if (foot) {
          foot.textContent = 'Every title, summary and section heading in ' + total +
            ' pages. Enter opens the first result.';
        }
        render();
      })
      .catch(function () {
        broke = true;
        render();
      });
  }

  /* ── matching: the directory's rule, over more text ───────────────────── */

  function wordsOf(query) {
    return query.toLowerCase().split(/\s+/).filter(Boolean);
  }

  /* What a reader typed, and the other spellings of it that count as the same
     word. Every row is a declared ending: `strip` removes one a reader added,
     `swap` changes the spelling this library does not use into the one it does,
     `add` supplies one a reader left off. Nothing here is fuzzy - no edit
     distance, no dictionary, no ranking - so each variant is still a string the
     reader could have typed and every one of them is visible when it matches.

     Each family was measured against the built index before it was written, and
     the numbers are why the table is this small:

       strip  s/ies/es   "hallucinations" 0 pages -> 3, "tokens" 3 -> 9,
                         "parameters" 4 -> 9. A stripped query is a prefix of
                         itself, so this is exactly the direction a substring
                         rule cannot do.
       swap   ise/ize    "quantisation" 1 -> 6, "tokeniser" 0 -> 1. The library
                         writes one spelling; an English reader may type either.
       add    y/ies      "boundary" 0 -> 1, "property" 2 -> 3, "entry" 2 -> 3.

     What is deliberately NOT here: verb endings in the `add` direction. The
     library writes "adjusted" and a reader types "adjust", and substring already
     handles that; generating the inflections instead produced "bak" -> "baked"
     and "ceil" -> "ceiling", which match words nobody typed. The cap below is
     the other half of the bound: four spellings of one word, never more.

     The guarantee, and `spansIn` below is where it is kept: every spelling in a
     list is a spelling of THAT word. The fold never adds a fragment of a longer
     one, so a word this library has never used still finds nothing.

     And its limit, measured rather than hoped: this folds ONE word. A term the
     library writes in another shape across a hyphen is still a miss - "fine-tuned"
     finds nothing while "fine-tuning" is the title of the page it means, because
     the stripped stem is not a whole word there. That is a phrase question, and a
     phrase table is a different feature with a different cost. */
  var FOLD = [
    ['strip', 'ies', 'y'],
    ['strip', 'ses', 's'], ['strip', 'xes', 'x'], ['strip', 'zes', 'z'],
    ['strip', 'ches', 'ch'], ['strip', 'shes', 'sh'],
    ['strip', 'es', ''], ['strip', 'ing', ''], ['strip', 'ed', ''],
    ['strip', 's', ''],
    ['swap', 'isation', 'ization'], ['swap', 'iser', 'izer'],
    ['swap', 'ising', 'izing'], ['swap', 'ise', 'ize'],
    ['add', 'y', 'ies'],
  ];

  var FOLDED = {};          /* one query word folded once, since every row asks */
  var FOLD_CAP = 4;         /* spellings of one word, and the bound is the point */

  function alts(word) {
    if (FOLDED[word]) return FOLDED[word];
    var out = [word];
    function keep(candidate) {
      if (candidate.length < 3 || out.indexOf(candidate) !== -1) return;
      if (out.length < FOLD_CAP) out.push(candidate);
    }
    FOLD.forEach(function (row) {
      var kind = row[0], has = row[1], gets = row[2];
      if (kind === 'strip') {
        /* A bare `s` needs a word to leave behind: "is" and "bus" are not plurals of
           anything, and "class" is not the singular of "clas". An earlier version of
           this guard also refused a word ending in `us`, on the theory that "status"
           would fold to "statu" - it does, harmlessly, and the guard was costing the
           plurals of the library's own acronyms: "gpus" found nothing while "gpu" is
           a word of eight pages. Measurement, not caution, decided the row. */
        if (!word.endsWith(has)) return;
        if (has === 's' && (word.endsWith('ss') || word.length < 4)) return;
        keep(word.slice(0, word.length - has.length) + gets);
      } else if (kind === 'swap') {
        if (word.endsWith(has)) keep(word.slice(0, word.length - has.length) + gets);
        else if (word.endsWith(gets)) keep(word.slice(0, word.length - gets.length) + has);
      } else if (kind === 'add') {
        /* "boundary" -> "boundaries" only for a consonant + y: "day" is not
           "daies", and "key" is not "keies". The row replaces its ending like the
           others, which the audit caught the first time it ran: appending gave
           "boundaryies", a word no page has ever written. */
        if (!word.endsWith(has) || word.length < 4) return;
        if (word.length >= 2 && 'aeiou'.indexOf(word.charAt(word.length - 2)) !== -1) return;
        keep(word.slice(0, word.length - has.length) + gets);
      }
    });
    FOLDED[word] = out;
    return out;
  }

  function altsOf(words) {
    return words.map(alts);
  }

  /* A mark should cover a WORD, not the fragment of one that happened to match: a
     reader who typed "hallucinations" and gets the page whose text says
     "hallucinations" should see that word marked, not its first eleven letters.
     A span always comes from a spelling found in this very string, so the offsets
     are the text's own and this only has to grow them out to the letters around
     them. */
  var WORDISH = /[A-Za-z0-9'-]/;

  function widen(text, from, to) {
    while (from > 0 && WORDISH.test(text.charAt(from - 1))) from--;
    while (to < text.length && WORDISH.test(text.charAt(to))) to++;
    return [from, to];
  }

  /* Where a spelling occurs in a piece of text, and whether it has to be the whole
     word there.

     The surface word keeps the substring rule, because that is the directory's rule
     and it is how a reader types half a word: "quantiz" finds "quantization". A
     FOLDED spelling does not, and that distinction is the entire safety of the
     table above. Without it the stripped stem matches fragments of unrelated words
     - "cars" folds to "car", and "car" is inside "carried" - so the fold would
     answer a query with pages that never said the word. With it, the fold only ever
     offers another spelling of the SAME word, and a reader who typed "cars" still
     gets the honest answer: nothing here. */
  function spansIn(text, word, whole) {
    var from = 0, at, out = [];
    while ((at = text.indexOf(word, from)) !== -1) {
      var before = at > 0 ? text.charAt(at - 1) : '';
      var after = at + word.length < text.length ? text.charAt(at + word.length) : '';
      if (!whole || (!WORDISH.test(before) && !WORDISH.test(after))) {
        out.push([at, at + word.length]);
      }
      from = at + 1;
    }
    return out;
  }

  /* Which of a word's spellings this TEXT carries, surface form first: a line that
     says "tokens" is marked on "tokens" rather than on every "token" in it. */
  function carriedBy(text, list) {
    for (var i = 0; i < list.length; i++) {
      if (spansIn(text, list[i], i > 0).length) return list[i];
    }
    return null;
  }

  function hitsFor(words) {
    var lists = altsOf(words);
    var hits = records.filter(function (record) {
      return lists.every(function (list) {
        return carriedBy(record.hay, list) !== null;
      });
    });
    /* Pages whose TITLE carries every word go first, and that is the whole of the
       ordering rule: a reader who typed the name of a page gets that page, and
       everything else is in the library's own order. It is a sort rather than a
       score because a score is a thing the reader cannot check - and the title is
       marked, so the reader can see the reason for the order in the result. */
    var named = [], rest = [];
    hits.forEach(function (record) {
      var title = record.title.toLowerCase();
      (lists.every(function (list) { return carriedBy(title, list) !== null; })
        ? named : rest).push(record);
    });
    return named.concat(rest);
  }

  /* The line to quote back: whichever of the page's own lines carries the most of
     what was typed, with the title first among equals. A reader who searched two
     words and sees one mark on a heading can tell at a glance which part missed. */
  function quoteFor(record, lists) {

    var pool = [record.title, record.summary].concat(record.lines);
    var best = pool[0], bestHits = -1;
    pool.forEach(function (line) {
      var lower = line.toLowerCase(), hits = 0;
      lists.forEach(function (list) {
        if (carriedBy(lower, list) !== null) hits++;
      });
      if (hits > bestHits) {
        best = line;
        bestHits = hits;
      }
    });
    return best;
  }

  /* ── drawing ──────────────────────────────────────────────────────────── */

  /* Text nodes and <mark> elements, built by hand. See the header: never
     innerHTML, because these strings are the pages' own words. */
  function write(into, text, lists) {
    var lower = text.toLowerCase();
    var spans = [];
    lists.forEach(function (list) {
      /* The list arrives as spellings of one typed word. Whichever spelling this
         line actually carries is the one marked, so a surface form wins over a
         fold of it and nothing the reader did not type is ever marked for its
         own sake. */
      var found = carriedBy(lower, list);
      if (found === null) return;
      spansIn(lower, found, found !== list[0]).forEach(function (span) {
        spans.push(widen(text, span[0], span[1]));
      });
    });
    spans.sort(function (a, b) { return a[0] - b[0]; });

    var merged = [];
    spans.forEach(function (span) {
      var last = merged[merged.length - 1];
      if (last && span[0] <= last[1]) last[1] = Math.max(last[1], span[1]);
      else merged.push(span.slice());
    });

    var at = 0;
    merged.forEach(function (span) {
      if (span[0] > at) {
        into.appendChild(document.createTextNode(text.slice(at, span[0])));
      }
      var mark = document.createElement('mark');
      mark.textContent = text.slice(span[0], span[1]);
      into.appendChild(mark);
      at = span[1];
    });
    if (at < text.length) {
      into.appendChild(document.createTextNode(text.slice(at)));
    }
  }

  function row(record, lists) {
    var li = document.createElement('li');
    li.className = 'palette-hit';
    var link = document.createElement('a');
    link.className = 'palette-link';
    link.href = record.url;

    var where = document.createElement('span');
    where.className = 'palette-where';
    where.textContent = record.group;

    var title = document.createElement('span');
    title.className = 'palette-title';
    write(title, record.title, lists);

    link.appendChild(where);
    link.appendChild(title);

    /* When the line that best answers the query IS the title, the title has
       already shown it with its marks on, and repeating it underneath reads as a
       rendering fault. The row is one line shorter and says the same thing. */
    var quote = quoteFor(record, lists);
    if (quote !== record.title) {
      var line = document.createElement('span');
      line.className = 'palette-line';
      write(line, quote, lists);
      link.appendChild(line);
    }

    li.appendChild(link);
    return li;
  }

  function groupRow(name, anchor) {
    var li = document.createElement('li');
    li.className = 'palette-hit is-group';
    var link = document.createElement('a');
    link.className = 'palette-link';
    link.href = '/library/#' + anchor;
    var title = document.createElement('span');
    title.className = 'palette-title';
    title.textContent = name;
    link.appendChild(title);
    li.appendChild(link);
    return li;
  }

  function render() {
    if (!list || !said) return;
    while (list.firstChild) list.removeChild(list.firstChild);

    if (broke) {
      said.textContent = 'The index did not load. Browse the directory instead.';
      return;
    }
    if (!records) {
      said.textContent = 'Loading the index ...';
      return;
    }

    var query = field.value.trim();
    var words = wordsOf(query);

    if (!words.length) {
      /* An empty field is not an empty palette: the seven groups are how the
         library is organised, and they are a better answer than a blank list. */
      var seen = [];
      records.forEach(function (record) {
        if (seen.indexOf(record.group) === -1) seen.push(record.group);
      });
      seen.forEach(function (name) {
        list.appendChild(groupRow(name, slugOf(name)));
      });
      said.textContent = total + ' pages, seven groups. Type a word.';
      return;
    }

    var hits = hitsFor(words);
    var lists = altsOf(words);
    hits.slice(0, SHOWN).forEach(function (record) {
      list.appendChild(row(record, lists));
    });

    said.textContent = hits.length
      ? (hits.length > SHOWN ? 'The first ' + SHOWN + ' of ' : '') + hits.length +
        ' page' + (hits.length === 1 ? '' : 's') + ' match "' + query + '".'
      : 'Nothing matches "' + query + '". Try a shorter word.';
  }

  function slugOf(name) {
    return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
  }

  /* ── one focus order: the field, then each result, then the field ─────── */

  function rows() {
    return [].slice.call(list.querySelectorAll('.palette-link'));
  }

  function walk(step) {
    var links = rows();
    if (!links.length) return false;
    var at = links.indexOf(document.activeElement);
    /* ArrowDown in the field enters the list; ArrowUp in the field leaves focus
       where it is rather than jumping to the last result off a page-long list. */
    if (at === -1 && document.activeElement === field) {
      if (step > 0) links[0].focus();
      return true;
    }
    if (at === -1) return false;
    var next = at + step;
    if (next < 0 || next >= links.length) field.focus();
    else links[next].focus();
    return true;
  }

  function fromField(event) {
    if (event.key === 'ArrowDown') {
      if (walk(1)) event.preventDefault();
      return;
    }
    if (event.key === 'Enter' && !event.isComposing) {
      var links = rows();
      if (links.length) {
        event.preventDefault();
        links[0].click();
      }
    }
  }

  function fromResult(event) {
    if (event.key === 'ArrowDown' && walk(1)) event.preventDefault();
    else if (event.key === 'ArrowUp' && walk(-1)) event.preventDefault();
  }

  /* ── opening and closing ──────────────────────────────────────────────── */

  function open() {
    build();
    if (dialog.open) return;
    opener.setAttribute('aria-expanded', 'true');
    dialog.showModal();
    if (kept) field.value = kept;
    field.focus();
    field.select();
    render();
    load();
  }

  function close() {
    if (dialog && dialog.open) dialog.close();
  }

  /* The link becomes a button HERE rather than in the markup, because that is the
     truth of the arrangement: with no script it is a link to the directory, and
     with this one it is a control that opens a dialog. */
  opener.setAttribute('role', 'button');
  opener.setAttribute('aria-haspopup', 'dialog');
  opener.setAttribute('aria-expanded', 'false');
  opener.setAttribute('aria-keyshortcuts', 'Control+K Meta+K');
  opener.addEventListener('click', function (event) {
    event.preventDefault();
    open();
  });

  document.addEventListener('keydown', function (event) {
    var target = event.target;
    var typing = target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' ||
                            target.isContentEditable);
    var plain = !event.metaKey && !event.ctrlKey && !event.altKey;

    if ((event.metaKey || event.ctrlKey) && (event.key === 'k' || event.key === 'K')) {
      event.preventDefault();
      open();
      return;
    }
    if (event.key === '/' && plain && !typing && !pageFind &&
        !(dialog && dialog.open)) {
      event.preventDefault();
      open();
    }
  });
})();
