/* ============ Draft Command — app layer ============ */
(function () {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const POS_ALL = ['QB', 'RB', 'WR', 'TE', 'K', 'DST'];

  // ---------------- setup state ----------------
  const setup = {
    teams: 10, mySlot: 5, playoffTeams: 6, scoring: 'ppr',
    slots: { QB: 1, RB: 2, WR: 2, TE: 1, FLEX: 1, K: 1, DST: 1, BENCH: 7 },
  };
  const SCORING_LABEL = { ppr: 'PPR', half: 'Half PPR', std: 'Standard' };
  let eng = null;
  let simGen = 0;             // cancellation token for async sims
  let curOdds = null;         // current-roster sim result
  let candOdds = {};          // playerId -> odds result
  let pendingPlayer = null;
  let activePane = 'draft';
  let posFilter = 'ALL';
  let showDrafted = false;
  let listQuery = '';

  // ---------------- crash-proof persistence ----------------
  const store = (() => {
    try { const t = window.localStorage; t.setItem('__t', '1'); t.removeItem('__t'); return t; } catch (e) { return null; }
  })();
  function encodeState() {
    const ex = JSON.parse(eng.exportState());
    const idx = new Map(PLAYERS.map((p, i) => [p.id, i]));
    const picks = ex.picks.map(pk => idx.get(pk.playerId) + '.' + pk.team).join(',');
    const c = ex.cfg;
    const slots = [c.slots.QB, c.slots.RB, c.slots.WR, c.slots.TE, c.slots.FLEX, c.slots.K, c.slots.DST, c.slots.BENCH].join('-');
    return ['1', c.scoring, c.teams, c.mySlot, c.playoffTeams, slots, picks].join('|');
  }
  function decodeState(s) {
    try {
      const parts = s.split('|');
      if (parts[0] !== '1') return null;
      const sl = parts[5].split('-').map(Number);
      const cfg = {
        scoring: parts[1], teams: +parts[2], mySlot: +parts[3], playoffTeams: +parts[4],
        slots: { QB: sl[0], RB: sl[1], WR: sl[2], TE: sl[3], FLEX: sl[4], K: sl[5], DST: sl[6], BENCH: sl[7] },
      };
      const picks = parts[6] ? parts[6].split(',').map(t => {
        const [i, tm] = t.split('.');
        return PLAYERS[+i] ? { playerId: PLAYERS[+i].id, team: +tm } : null;
      }).filter(Boolean) : [];
      return { cfg, picks };
    } catch (e) { return null; }
  }
  function persist() {
    if (!eng) return;
    const s = encodeState();
    try { history.replaceState(null, '', '#d=' + encodeURIComponent(s)); } catch (e) {}
    try { if (store) store.setItem('dc2026', s); } catch (e) {}
  }
  function clearPersist() {
    try { history.replaceState(null, '', location.pathname); } catch (e) {}
    try { if (store) store.removeItem('dc2026'); } catch (e) {}
  }
  function tryRestore() {
    let s = null;
    const m = location.hash.match(/d=([^&]+)/);
    if (m) s = decodeURIComponent(m[1]);
    if (!s && store) { try { s = store.getItem('dc2026'); } catch (e) {} }
    if (!s) return false;
    const d = decodeState(s);
    if (!d || !d.picks) return false;
    Object.assign(setup, {
      teams: d.cfg.teams, mySlot: d.cfg.mySlot, scoring: d.cfg.scoring || 'ppr',
      playoffTeams: d.cfg.playoffTeams || 6, slots: d.cfg.slots,
    });
    startDraft(d.picks);
    if (d.picks.length) toast('Draft restored — ' + d.picks.length + ' pick' + (d.picks.length === 1 ? '' : 's'));
    return true;
  }

  // ---------------- helpers ----------------
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
  function pct(x) { return Math.round(x * 100) + '%'; }
  function toast(msg) {
    const t = $('toast'); t.textContent = msg; t.classList.add('show');
    clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('show'), 2200);
  }
  function ord(n) { const s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
  function shortName(name) {
    const parts = name.split(' ');
    if (parts.length < 2 || name.includes('DST')) return name;
    return parts[0][0] + '. ' + parts.slice(1).join(' ');
  }
  function teamLabel(t) { return t === setup.mySlot ? 'You' : 'Team ' + t; }

  // ---------------- setup UI ----------------
  function buildSetup() {
    const scSeg = $('scoringSeg'); scSeg.innerHTML = '';
    ['ppr', 'half', 'std'].forEach(sc => {
      const b = document.createElement('button');
      b.textContent = SCORING_LABEL[sc]; b.className = sc === setup.scoring ? 'on' : '';
      b.onclick = () => { setup.scoring = sc; buildSetup(); };
      scSeg.appendChild(b);
    });
    const tSeg = $('teamsSeg'); tSeg.innerHTML = '';
    [8, 10, 12, 14].forEach(n => {
      const b = document.createElement('button');
      b.textContent = n; b.className = n === setup.teams ? 'on' : '';
      b.onclick = () => { setup.teams = n; if (setup.mySlot > n) setup.mySlot = n; buildSetup(); };
      tSeg.appendChild(b);
    });
    const sg = $('slotGrid'); sg.innerHTML = '';
    for (let i = 1; i <= setup.teams; i++) {
      const b = document.createElement('button');
      b.textContent = i; b.className = i === setup.mySlot ? 'on' : '';
      b.onclick = () => { setup.mySlot = i; buildSetup(); };
      sg.appendChild(b);
    }
    const st = $('slotSteppers'); st.innerHTML = '';
    const maxes = { QB: 2, RB: 4, WR: 4, TE: 2, FLEX: 3, K: 1, DST: 1, BENCH: 10 };
    Object.keys(setup.slots).forEach(k => {
      const row = document.createElement('div'); row.className = 'step';
      row.innerHTML = '<span class="lbl">' + k + '</span>';
      const ctr = document.createElement('div'); ctr.className = 'ctr';
      const minus = document.createElement('button'); minus.textContent = '−';
      const val = document.createElement('span'); val.className = 'val num'; val.textContent = setup.slots[k];
      const plus = document.createElement('button'); plus.textContent = '+';
      minus.onclick = () => { setup.slots[k] = Math.max(k === 'BENCH' ? 3 : 0, setup.slots[k] - 1); buildSetup(); };
      plus.onclick = () => { setup.slots[k] = Math.min(maxes[k], setup.slots[k] + 1); buildSetup(); };
      ctr.append(minus, val, plus); row.appendChild(ctr); st.appendChild(row);
    });
    const pSeg = $('playoffSeg'); pSeg.innerHTML = '';
    [4, 6, 8].forEach(n => {
      const b = document.createElement('button');
      b.textContent = n; b.className = n === setup.playoffTeams ? 'on' : '';
      b.onclick = () => { setup.playoffTeams = n; buildSetup(); };
      pSeg.appendChild(b);
    });
    const rounds = Object.values(setup.slots).reduce((a, b) => a + b, 0);
    $('setupNote').textContent = SCORING_LABEL[setup.scoring] + ' scoring · snake draft · ' + rounds +
      ' rounds · ' + (setup.teams * rounds) + ' total picks · you pick ' + ord(setup.mySlot) + ' overall.';
  }

  function startDraft(importedPicks) {
    const rounds = Object.values(setup.slots).reduce((a, b) => a + b, 0);
    eng = Engine.create(PLAYERS, {
      teams: setup.teams, mySlot: setup.mySlot, rounds, scoring: setup.scoring,
      slots: Object.assign({}, setup.slots), playoffTeams: setup.playoffTeams,
    });
    if (importedPicks) importedPicks.forEach(pk => { eng.state.picks.push(pk); eng.state.taken.add(pk.playerId); });
    curOdds = null; candOdds = {};
    $('setupView').classList.add('hidden');
    $('mainView').classList.remove('hidden');
    $('nav').classList.remove('hidden');
    renderAll(); persist(); scheduleSims();
  }

  // ---------------- global render ----------------
  function renderAll() {
    renderStatus(); renderDraftPane(); renderBoard(); renderTeam(); renderPlayers();
  }

  function renderStatus() {
    const c = eng.currentPick();
    const total = eng.totalPicks;
    $('progressFill').style.width = Math.min(100, ((c - 1) / total) * 100) + '%';
    if (eng.draftOver()) {
      $('statusLine1').textContent = 'Draft complete';
      $('statusLine2').textContent = total + ' picks made · see My team for final outlook';
      $('myTurnBanner').classList.add('hidden');
      return;
    }
    const clock = eng.onClock();
    const r = eng.pickRound(c);
    const mine = clock === setup.mySlot;
    $('statusLine1').textContent = 'Round ' + r + ' · Pick ' + c + ' — ' + (mine ? 'YOUR PICK' : teamLabel(clock) + ' on the clock');
    const nxt = eng.nextPickOf(setup.mySlot, c - (mine ? 1 : 0));
    let s2 = '';
    if (mine) {
      s2 = 'Pick now, or log another team’s pick with search';
    } else if (nxt) {
      s2 = 'Your turn in ' + (nxt - c) + ' pick' + (nxt - c === 1 ? '' : 's') + ' (#' + nxt + ')';
    } else { s2 = 'You have no picks left'; }
    if (curOdds) s2 += ' · playoff odds ' + pct(curOdds.playoffPct);
    $('statusLine2').textContent = s2;
    $('myTurnBanner').classList.toggle('hidden', !mine);
    if (mine) $('bannerTxt').textContent = 'You’re on the clock — recommendations below';
  }

  // ---------------- search ----------------
  function searchPlayers(q, includeDrafted) {
    q = q.trim().toLowerCase();
    if (!q) return [];
    const toks = q.split(/\s+/);
    const scored = [];
    for (const p of eng.players) {
      const name = p.name.toLowerCase();
      const drafted = eng.state.taken.has(p.id);
      if (drafted && !includeDrafted) continue;
      let ok = true, bonus = 0;
      for (const t of toks) {
        const i = name.indexOf(t);
        if (i < 0) { ok = false; break; }
        if (i === 0 || name[i - 1] === ' ' || name[i - 1] === '’' || name[i - 1] === "'") bonus += 2;
      }
      if (ok) scored.push({ p, key: bonus - p.adp / 400, drafted });
    }
    return scored.sort((a, b) => b.key - a.key).slice(0, 8);
  }

  function playerRow(p, opts) {
    opts = opts || {};
    const drafted = eng.state.taken.has(p.id);
    const draftedBy = drafted ? eng.state.picks.find(pk => pk.playerId === p.id) : null;
    const b = document.createElement('button');
    b.className = 'prow pos-' + p.pos + (drafted ? ' gone' : '');
    const right = opts.right || ('<div class="pname num">' + (p.adpF < 250 ? 'ADP ' + Math.round(p.adpF) : '—') + '</div>' +
      '<div class="pmeta num">' + Math.round(p.val) + ' pts · ' + p.pos + p.posRank + '</div>');
    b.innerHTML =
      '<span class="posdot"></span>' +
      '<div><div class="pname">' + esc(p.name) + '</div>' +
      '<div class="pmeta">' + p.pos + ' · ' + p.team + ' · bye ' + p.bye +
      (drafted && draftedBy ? ' · <b>' + teamLabel(draftedBy.team) + '</b>' : '') +
      (p.est ? ' · est.' : '') + '</div></div>' +
      '<div class="right">' + right + '</div>';
    if (!drafted && !eng.draftOver()) b.onclick = () => openConfirm(p);
    return b;
  }

  function renderSearchResults() {
    const box = $('searchResults');
    box.innerHTML = '';
    const q = $('searchInput').value;
    if (!q.trim()) return;
    const res = searchPlayers(q, true);
    if (!res.length) { box.innerHTML = '<div class="mut" style="padding:8px 4px">No matches.</div>'; return; }
    res.forEach(r => box.appendChild(playerRow(r.p)));
  }

  // ---------------- confirm ----------------
  function openConfirm(p) {
    pendingPlayer = p;
    $('confirmWho').textContent = p.name + ' (' + p.pos + ')';
    const sel = $('confirmTeam'); sel.innerHTML = '';
    for (let t = 1; t <= setup.teams; t++) {
      const o = document.createElement('option');
      o.value = t; o.textContent = '→ ' + teamLabel(t);
      sel.appendChild(o);
    }
    sel.value = eng.onClock() || setup.mySlot;
    $('confirmBar').classList.remove('hidden');
  }
  function closeConfirm() { pendingPlayer = null; $('confirmBar').classList.add('hidden'); }

  function commitPick(playerId, team) {
    const res = eng.makePick(playerId, team);
    if (!res.ok) { toast(res.err); return; }
    const p = eng.byId.get(playerId);
    toast('Pick ' + res.pick + ': ' + shortName(p.name) + ' → ' + teamLabel(res.team));
    $('searchInput').value = ''; $('searchResults').innerHTML = '';
    closeConfirm(); renderAll(); persist(); scheduleSims();
  }

  // ---------------- recommendations ----------------
  function reasonChip(r) {
    const cls = { gone: 'var(--serious)', cliff: 'var(--warn)', bye: 'var(--serious)', injury: 'var(--serious)', durable: 'var(--good)', news: 'var(--warn)' }[r.t];
    const icon = { gone: '⏳', cliff: '⛰', value: '＋', market: '≈', fit: '▸', wait: '⏸', bye: '!', run: '↯', tier: '⛰' }[r.t] || '';
    return '<span class="chip">' + (icon ? icon + ' ' : '') +
      (cls ? '<span style="color:' + cls + '">' + esc(r.txt) + '</span>' : esc(r.txt)) + '</span>';
  }

  function renderDraftPane() {
    const box = $('recSection');
    box.innerHTML = '';
    if (eng.draftOver()) {
      box.innerHTML = '<div class="sectionTitle">Draft complete</div>' +
        '<div class="card" style="padding:14px">Nice work — head to <b>My team</b> for your final lineup and playoff odds, or export the board from the menu.</div>';
      return;
    }
    const mine = eng.onClock() === setup.mySlot;
    const rec = eng.recommendations(mine ? 6 : 4);
    const title = document.createElement('div');
    title.className = 'sectionTitle';
    title.textContent = mine ? 'Best available — pick one' : 'On deck for you';
    box.appendChild(title);

    if (rec.run) {
      const runNote = document.createElement('div');
      runNote.innerHTML = '<span class="chip" style="margin-bottom:8px">↯ ' + rec.run + ' run in progress</span>';
      box.appendChild(runNote);
    }

    if (mine) {
      const dp = buildDecisionPanel(rec);
      if (dp) box.appendChild(dp);
    }
    rec.candidates.slice(0, mine ? 5 : 3).forEach((c, i) => {
      const card = document.createElement('div');
      card.className = 'card recCard pos-' + c.p.pos;
      card.dataset.pid = c.p.id;
      const odds = candOdds[c.p.id];
      const survTxt = rec.nextPick ? Math.round(c.surv * 100) + '% still here at your next pick' : '';
      card.innerHTML =
        '<div class="recTop">' +
          '<div class="rankBadge num">' + (i + 1) + '</div>' +
          '<span class="posdot"></span>' +
          '<div><div class="recName">' + esc(c.p.name) + '</div>' +
          '<div class="recMeta">' + c.p.pos + c.p.posRank + ' · ' + c.p.team + ' · bye ' + c.p.bye +
              ' · ADP ' + (c.p.adpF < 250 ? Math.round(c.p.adpF) : '—') +
              (c.p.ecr != null ? ' · analysts #' + c.p.ecr : '') +
              (c.p.wtLine != null ? ' · O/U ' + c.p.wtLine : '') + '</div></div>' +
          (mine ? '<button class="draftBtn" data-draft="' + c.p.id + '">Draft</button>' : '') +
        '</div>' +
        '<div class="statRow"><span>Value <b class="num">+' + Math.round(c.m) + '</b></span>' +
          '<span>Urgency <b class="num">+' + Math.round(c.urgency) + '</b></span>' +
          (survTxt && !mine ? '<span>' + survTxt + '</span>' : '') + '</div>' +
        (mine ? '<div class="oddsMini"><div class="oddsTrack"><div class="oddsFill" style="width:' +
            (odds ? Math.round(odds.playoffPct * 100) : 0) + '%"></div></div>' +
            '<div class="oddsVal num">' + (odds ? pct(odds.playoffPct) + ' playoff' : 'simulating…') + '</div></div>' : '') +
        (c.reasons.length ? '<div class="reasons">' + c.reasons.slice(0, 4).map(reasonChip).join('') + '</div>' : '');
      box.appendChild(card);
    });
    if (mine) {
      box.querySelectorAll('[data-draft]').forEach(b => {
        b.onclick = (ev) => { ev.stopPropagation(); commitPick(b.dataset.draft, setup.mySlot); };
      });
      markBestCard();
    }
    // recent picks
    const rp = $('recentPicks');
    const picks = eng.state.picks;
    if (!picks.length) { rp.textContent = 'No picks yet — log every pick as it happens (yours and theirs).'; }
    else {
      rp.innerHTML = picks.slice(-4).reverse().map((pk, idx) => {
        const p = eng.byId.get(pk.playerId);
        const n = picks.length - idx;
        return '<div>#' + n + ' · <b>' + esc(shortName(p.name)) + '</b> <span class="mut">(' + p.pos + ')</span> → ' + teamLabel(pk.team) + '</div>';
      }).join('');
    }
  }

  // ---- "The Decision" panel: argue the pick in prose, from the engine's own math ----
  function buildDecisionPanel(rec) {
    const cands = rec.candidates.filter(c => c.score > -400).slice(0, 6);
    if (cands.length < 2) return null;
    const top = cands[0];
    const nm = p => '<b>' + esc(shortName(p.name)) + '</b>';
    const div = document.createElement('div');
    div.className = 'card decision';
    let html = '<h4>The decision</h4>';

    // per-position best candidate + what waiting costs (engine's urgency math)
    const byPos = {};
    cands.forEach(c => { if (!byPos[c.p.pos] && c.p.pos !== 'K' && c.p.pos !== 'DST') byPos[c.p.pos] = c; });
    const posLines = [];
    Object.entries(byPos).forEach(([pos, c]) => {
      const nb = rec.nextBest[pos];
      if (rec.nextPick && nb && nb.likely && nb.likely.id !== c.p.id) {
        posLines.push({ pos, c, cost: Math.max(0, Math.round(c.urgency)), likely: nb.likely });
      }
    });

    // ---- paragraph 1: the verdict, argued through the next-pick asymmetry ----
    let p1 = 'The board says ' + nm(top.p) + '. ';
    const tl = posLines.find(l => l.pos === top.p.pos);
    const others = posLines.filter(l => l.pos !== top.p.pos).sort((a, b) => a.cost - b.cost);
    if (tl && others.length) {
      const lo = others[0];
      p1 += 'The next-pick asymmetry is most of this decision: pass on the ' + tl.pos +
        's now, and the likely best ' + tl.pos + ' when the draft snakes back to you at #' + rec.nextPick +
        ' is ' + esc(shortName(tl.likely.name)) + ' — waiting costs about <b>' + tl.cost + ' points</b>. ' +
        'Pass on the ' + lo.pos + 's instead and you only give up ~<b>' + lo.cost + '</b>, because ' +
        esc(shortName(lo.likely.name)) + ' is probably still there. ';
      if (tl.cost - lo.cost >= 8) {
        p1 += 'The board lets ' + lo.pos + ' wait; it does not forgive waiting on ' + tl.pos + '. ';
      }
    } else if (tl && rec.nextPick) {
      p1 += 'If you wait, the likely best ' + tl.pos + ' at #' + rec.nextPick + ' is ' +
        esc(shortName(tl.likely.name)) + ' — waiting costs about <b>' + tl.cost + ' points</b>. ';
    }
    const tierMates = eng.available().filter(q => q.pos === top.p.pos && q.tier === top.p.tier).length;
    if (tierMates <= 2 && top.p.tier < 8) {
      p1 += (tierMates === 1 ? 'He is also the last player left in his tier' :
        'He is also one of the last two left in his tier') + ' — after this group, the position steps down. ';
    }
    html += '<div class="dline">' + p1 + '</div>';

    // ---- paragraph 2: risk, alternatives, byes ----
    let p2 = '';
    const risky = cands.slice(0, 4).filter(c => c.p.dur >= 1.15);
    const clean = cands.slice(0, 4).filter(c => c.p.dur <= 0.91);
    if (risky.length && clean.length) {
      p2 += 'On risk: ' + risky.map(c => nm(c.p)).join(' and ') +
        (risky.length > 1 ? ' carry' : ' carries') + ' a real injury history — the simulations already discount ' +
        (risky.length > 1 ? 'their' : 'his') + ' playoff odds for it — while ' +
        clean.map(c => esc(shortName(c.p.name))).join(', ') +
        (clean.length > 1 ? ' come' : ' comes') + ' off back-to-back near-full seasons. ';
    }
    Object.values(byPos).forEach(t => {
      const alt = cands.find(c => c !== t && c.p.pos === t.p.pos &&
        Math.abs(c.p.val - t.p.val) <= 8 && c.p.dur <= t.p.dur - 0.2);
      if (alt) {
        p2 += 'If you want a ' + t.p.pos + ' regardless, the cleaner route is ' + nm(alt.p) +
          ' — within a few points of ' + esc(shortName(t.p.name)) + ' in value, with the better health record. ';
      }
    });
    const lu = eng.lineup(eng.rosterOf(setup.mySlot));
    cands.slice(0, 3).forEach(c => {
      const clash = lu.starters.filter(x => x.p.bye === c.p.bye && x.p.pos !== 'K' && x.p.pos !== 'DST').length;
      if (clash >= 2) {
        p2 += 'Heads up: drafting ' + nm(c.p) + ' would stack ' + (clash + 1) +
          ' starters on the week-' + c.p.bye + ' bye — his score already pays that penalty, but it is why he sits where he sits. ';
      }
    });
    if (p2) html += '<div class="dline">' + p2 + '</div>';

    // ---- paragraph 3: simulations (fills in as they finish) ----
    html += '<div class="dline" id="simVerdict">Deep simulations are running — each candidate is being drafted into hundreds of completed rosters and seasons…</div>';
    div.innerHTML = html;
    div.dataset.topPid = top.p.id;
    return div;
  }

  function updateSimVerdict() {
    const el = $('simVerdict');
    if (!el || !eng) return;
    const entries = Object.entries(candOdds)
      .map(([id, o]) => ({ p: eng.byId.get(id), o }))
      .filter(x => x.p)
      .sort((a, b) => b.o.playoffPct - a.o.playoffPct);
    if (entries.length < 2) return;
    const base = Math.round((eng.cfg.playoffTeams / eng.cfg.teams) * 100);
    const pct = x => Math.round(x.o.playoffPct * 100);
    let s = 'Across the simulated rest-of-drafts and seasons, taking ' +
      '<b>' + esc(shortName(entries[0].p.name)) + '</b> makes the playoffs <b>' + pct(entries[0]) + '%</b> of the time, vs ' +
      entries.slice(1).map(x => esc(shortName(x.p.name)) + ' at ' + pct(x) + '%').join(', ') +
      ' — against a ' + base + '% do-nothing baseline. ';
    const panel = document.querySelector('.decision');
    const topPid = panel && panel.dataset.topPid;
    if (topPid && entries[0].p.id === topPid) {
      s += 'The simulations agree with the board.';
    } else if (topPid) {
      const gap = pct(entries[0]) - (entries.find(x => x.p.id === topPid) ? pct(entries.find(x => x.p.id === topPid)) : 0);
      s += gap >= 3
        ? 'Note: the simulations lean <b>' + esc(shortName(entries[0].p.name)) + '</b> over the board score — the values are close, and the risk-and-roster picture decides it.'
        : 'The simulations call it a coin flip with the board pick — either is defensible.';
    }
    el.innerHTML = s;
  }

  function markBestCard() {
    updateSimVerdict();
    const cards = document.querySelectorAll('.recCard');
    let bestId = null, bestV = -1;
    cards.forEach(c => {
      const o = candOdds[c.dataset.pid];
      if (o && o.playoffPct > bestV) { bestV = o.playoffPct; bestId = c.dataset.pid; }
    });
    cards.forEach(c => {
      c.classList.toggle('best', c.dataset.pid === bestId && bestId !== null);
      const v = c.querySelector('.oddsVal');
      if (!v) return;
      v.textContent = v.textContent.replace('★ ', '');
      if (c.dataset.pid === bestId) v.textContent = '★ ' + v.textContent;
    });
  }

  // ---------------- board ----------------
  function renderBoard() {
    const sc = $('boardScroller');
    const T = setup.teams, R = eng.cfg.rounds;
    let html = '<table class="board"><thead><tr><th class="rnd"></th>';
    for (let t = 1; t <= T; t++) html += '<th class="' + (t === setup.mySlot ? 'me' : '') + '">' + (t === setup.mySlot ? 'YOU' : 'T' + t) + '</th>';
    html += '</tr></thead><tbody>';
    const cur = eng.currentPick();
    for (let r = 1; r <= R; r++) {
      html += '<tr><td class="rnd">' + r + '</td>';
      for (let t = 1; t <= T; t++) {
        const overall = (r - 1) * T + ((r % 2 === 1) ? t : T - t + 1);
        const pk = eng.state.picks[overall - 1];
        const isCur = overall === cur && !eng.draftOver();
        const me = t === setup.mySlot;
        let inner = '<span class="cSub num">' + overall + '</span>';
        let borderColor = 'transparent';
        if (pk) {
          const p = eng.byId.get(pk.playerId);
          borderColor = 'var(--pos-' + p.pos + ')';
          inner = '<span class="cName">' + esc(shortName(p.name)) + '</span><span class="cSub">' + p.pos + ' · ' + p.team + '</span>';
        }
        html += '<td class="' + (isCur ? 'cur ' : '') + (me ? 'mecell' : '') + '">' +
          '<div class="cellIn" style="border-left-color:' + borderColor + '">' + inner + '</div></td>';
      }
      html += '</tr>';
    }
    html += '</tbody></table>';
    sc.innerHTML = html;
  }

  // ---------------- team ----------------
  function renderTeam() {
    const roster = eng.rosterOf(setup.mySlot);
    const lu = eng.lineup(roster);
    // tiles
    if (curOdds) {
      $('oddsHero').textContent = pct(curOdds.playoffPct);
      $('oddsMeter').style.width = Math.round(curOdds.playoffPct * 100) + '%';
      $('winsTile').textContent = curOdds.expWins.toFixed(1);
      $('ptsTile').textContent = Math.round(curOdds.expPts / 14);
    } else {
      $('oddsHero').textContent = '—'; $('winsTile').textContent = '—'; $('ptsTile').textContent = '—';
      $('oddsMeter').style.width = '0%';
    }
    const base = Math.round((setup.playoffTeams / setup.teams) * 100);
    $('simNote').textContent = curOdds
      ? 'League baseline ' + base + '% (' + setup.playoffTeams + ' of ' + setup.teams + ' make it). Sims complete the draft realistically, then play a 14-week season many times.'
      : 'Simulations run automatically after each pick. League baseline ' + base + '%.';

    // lineup slots
    const order = [];
    ['QB', 'RB', 'WR', 'TE'].forEach(pos => { for (let i = 0; i < eng.cfg.slots[pos]; i++) order.push(pos + (eng.cfg.slots[pos] > 1 ? (i + 1) : '')); });
    for (let i = 0; i < (eng.cfg.slots.FLEX || 0); i++) order.push('FLEX');
    ['K', 'DST'].forEach(pos => { for (let i = 0; i < eng.cfg.slots[pos]; i++) order.push(pos); });
    const bySlot = {};
    lu.starters.forEach(s => {
      const key = s.slot;
      (bySlot[key] = bySlot[key] || []).push(s.p);
    });
    const lc = $('lineupCard'); lc.innerHTML = '';
    const consumed = {};
    order.forEach(tag => {
      const key = tag.replace(/\d+$/, '');
      consumed[key] = consumed[key] || 0;
      const p = (bySlot[key] || [])[consumed[key]++];
      const row = document.createElement('div');
      row.className = 'slotRow' + (p ? ' pos-' + p.pos : '');
      row.innerHTML = '<span class="slotTag">' + tag + '</span>' +
        (p ? '<span class="posdot"></span><span class="slotName">' + esc(p.name) + '</span>' +
             '<span class="slotMeta num">' + Math.round(p.val) + ' pts · bye ' + p.bye + '</span>'
           : '<span class="slotName empty">—</span>');
      lc.appendChild(row);
    });
    const bc = $('benchCard'); bc.innerHTML = '';
    if (!lu.bench.length) bc.innerHTML = '<div class="slotRow"><span class="slotName empty">No bench players yet</span></div>';
    lu.bench.forEach(p => {
      const row = document.createElement('div');
      row.className = 'slotRow pos-' + p.pos;
      row.innerHTML = '<span class="slotTag">BN</span><span class="posdot"></span>' +
        '<span class="slotName">' + esc(p.name) + '</span>' +
        '<span class="slotMeta num">' + p.pos + ' · ' + Math.round(p.val) + ' pts</span>';
      bc.appendChild(row);
    });

    // positional strength vs league average (drafted starters so far)
    const strengths = [];
    ['QB', 'RB', 'WR', 'TE'].forEach(pos => {
      const mine = startersProjAt(setup.mySlot, pos);
      let sum = 0, n = 0;
      for (let t = 1; t <= setup.teams; t++) { if (t !== setup.mySlot) { sum += startersProjAt(t, pos); n++; } }
      strengths.push({ pos, mine, avg: n ? sum / n : 0 });
    });
    const maxV = Math.max(1, ...strengths.map(s => Math.max(s.mine, s.avg)));
    const scd = $('strengthCard');
    scd.innerHTML = strengths.map(s => {
      const d = Math.round(s.mine - s.avg);
      const dTxt = (d >= 0 ? '+' : '') + d;
      return '<div class="strengthRow"><span class="sl">' + s.pos + '</span>' +
        '<div class="bar"><div class="fill" style="width:' + Math.round((s.mine / maxV) * 100) + '%"></div>' +
        '<div class="avgTick" style="left:' + Math.round((s.avg / maxV) * 100) + '%"></div></div>' +
        '<span class="dv num" style="color:' + (d >= 0 ? 'var(--good)' : 'var(--serious)') + '">' + dTxt + '</span></div>';
    }).join('') + '<div class="simNote" style="margin-top:4px">Bar = your starters’ projected points · tick = league average so far · Δ vs average</div>';

    // byes
    const chips = $('byeChips'); chips.innerHTML = '';
    const weeks = {};
    lu.starters.forEach(s => { if (s.p.bye) (weeks[s.p.bye] = weeks[s.p.bye] || []).push(s.p); });
    const wkKeys = Object.keys(weeks).sort((a, b) => a - b);
    if (!wkKeys.length) chips.innerHTML = '<span class="chip">No starters yet</span>';
    wkKeys.forEach(w => {
      const n = weeks[w].length;
      const col = n >= 3 ? 'var(--serious)' : (n === 2 ? 'var(--warn)' : 'var(--muted)');
      const chip = document.createElement('span'); chip.className = 'chip';
      chip.innerHTML = '<span style="color:' + col + '">Wk ' + w + ' · ' + n + ' starter' + (n > 1 ? 's' : '') + (n >= 3 ? ' ⚠' : '') + '</span>';
      chip.title = weeks[w].map(p => p.name).join(', ');
      chips.appendChild(chip);
    });
  }

  function startersProjAt(teamSlot, pos) {
    const lu = eng.lineup(eng.rosterOf(teamSlot));
    let v = 0;
    lu.starters.forEach(s => { if (s.p.pos === pos || (s.slot === 'FLEX' && s.p.pos === pos)) v += s.p.val; });
    return v;
  }

  // ---------------- players pane ----------------
  function renderPlayers() {
    const pf = $('posFilters');
    if (!pf.dataset.built) {
      pf.dataset.built = '1';
      ['ALL'].concat(POS_ALL).concat(['DRAFTED']).forEach(pos => {
        const b = document.createElement('button');
        b.textContent = pos === 'DRAFTED' ? 'Show drafted' : pos;
        b.dataset.f = pos;
        b.onclick = () => {
          if (pos === 'DRAFTED') { showDrafted = !showDrafted; }
          else posFilter = pos;
          syncFilterButtons(); renderPlayers();
        };
        pf.appendChild(b);
      });
      syncFilterButtons();
      $('searchInput2').addEventListener('input', () => { listQuery = $('searchInput2').value; renderPlayers(); });
    }
    const box = $('playerList');
    box.innerHTML = '';
    let list = eng.players.slice();
    if (posFilter !== 'ALL') list = list.filter(p => p.pos === posFilter);
    if (!showDrafted) list = list.filter(p => !eng.state.taken.has(p.id));
    const q = listQuery.trim().toLowerCase();
    if (q) list = list.filter(p => p.name.toLowerCase().includes(q));
    if (posFilter === 'ALL') {
      list.sort((a, b) => a.adp - b.adp);
      const frag = document.createDocumentFragment();
      list.slice(0, 120).forEach(p => frag.appendChild(playerListRow(p)));
      box.appendChild(frag);
      if (list.length > 120) {
        const more = document.createElement('div'); more.className = 'mut'; more.style.cssText = 'padding:10px;text-align:center;font-size:12px';
        more.textContent = '+' + (list.length - 120) + ' more — narrow with search or a position filter';
        box.appendChild(more);
      }
    } else {
      list.sort((a, b) => b.proj - a.proj);
      let tier = 0;
      const frag = document.createDocumentFragment();
      list.forEach(p => {
        if (p.tier !== tier) {
          tier = p.tier;
          const h = document.createElement('div'); h.className = 'tierHead'; h.textContent = 'Tier ' + tier;
          frag.appendChild(h);
        }
        frag.appendChild(playerListRow(p));
      });
      box.appendChild(frag);
    }
  }
  function syncFilterButtons() {
    document.querySelectorAll('#posFilters button').forEach(b => {
      if (b.dataset.f === 'DRAFTED') b.classList.toggle('on', showDrafted);
      else b.classList.toggle('on', b.dataset.f === posFilter);
    });
  }
  function playerListRow(p) {
    const mRank = p.ecrPosRank != null ? p.ecrPosRank : p.adpPosRank;
    const valGap = mRank - p.projPosRank;
    const val = valGap >= 5 && p.projPosRank <= 45 && p.adpF < 250 ? ' <span class="chip" style="color:var(--good)">value</span>' : '';
    const right = '<div class="pname num">' + Math.round(p.val) + '</div>' +
      '<div class="pmeta num">ADP ' + (p.adpF < 250 ? Math.round(p.adpF) : '—') +
      (p.ecr != null ? ' · ECR ' + p.ecr : '') + ' · VOR ' + Math.round(p.vorp) + '</div>';
    const row = playerRow(p, { right });
    if (val) row.querySelector('.pname').insertAdjacentHTML('beforeend', val);
    return row;
  }

  // ---------------- sims ----------------
  function scheduleSims() {
    simGen++;
    const gen = simGen;
    candOdds = {};
    clearTimeout(scheduleSims._t);
    scheduleSims._t = setTimeout(() => runSims(gen, false), 250);
  }

  function runSims(gen, deep) {
    if (!eng || gen !== simGen) return;
    const D = deep ? 32 : 14, S = deep ? 10 : 8;
    // 1. current roster odds
    setTimeout(() => {
      if (gen !== simGen) return;
      curOdds = eng.playoffOddsFor(null, D, S, 11)['__current__'];
      renderStatus();
      if (activePane === 'team') renderTeam();
      // 2. candidate odds if my turn
      if (!eng.draftOver() && eng.onClock() === setup.mySlot) {
        const rec = eng.recommendations(6);
        const ids = rec.candidates.slice(0, 5).filter(c => c.score > -400).map(c => c.p.id);
        let i = 0;
        const step = () => {
          if (gen !== simGen || i >= ids.length) {
            if (gen === simGen) { markBestCard(); maybeEscalate(gen, ids); }
            return;
          }
          const id = ids[i++];
          const r = eng.playoffOddsFor([id], D, S, 17)[id];
          candOdds[id] = r;
          const card = document.querySelector('.recCard[data-pid="' + id + '"]');
          if (card) {
            const fill = card.querySelector('.oddsFill'), v = card.querySelector('.oddsVal');
            if (fill) fill.style.width = Math.round(r.playoffPct * 100) + '%';
            if (v) v.textContent = pct(r.playoffPct) + ' playoff';
          }
          markBestCard();
          setTimeout(step, 30);
        };
        step();
      }
    }, 10);
  }

  // close call or board/sim disagreement -> automatically deepen sims on the top two
  function maybeEscalate(gen, ids) {
    if (maybeEscalate._done === gen) return;
    const entries = ids.map(id => ({ id, o: candOdds[id] })).filter(x => x.o)
      .sort((a, b) => b.o.playoffPct - a.o.playoffPct);
    if (entries.length < 2) return;
    const panel = document.querySelector('.decision');
    const boardBest = panel && panel.dataset.topPid;
    const close = (entries[0].o.playoffPct - entries[1].o.playoffPct) < 0.05;
    const disagree = !!boardBest && entries[0].id !== boardBest;
    if (!close && !disagree) return;
    maybeEscalate._done = gen;
    const two = [entries[0].id, entries[1].id];
    if (disagree && !two.includes(boardBest)) two[1] = boardBest;
    const v = $('simVerdict');
    if (v) v.innerHTML += ' <span class="mut">Close call — deepening the simulations on the top two…</span>';
    setTimeout(() => {
      if (gen !== simGen) return;
      const deep = eng.playoffOddsFor(two, 32, 10, 23);
      two.forEach(id => {
        candOdds[id] = deep[id];
        const card = document.querySelector('.recCard[data-pid="' + id + '"]');
        if (card) {
          const fill = card.querySelector('.oddsFill'), vv = card.querySelector('.oddsVal');
          if (fill) fill.style.width = Math.round(deep[id].playoffPct * 100) + '%';
          if (vv) vv.textContent = pct(deep[id].playoffPct) + ' playoff';
        }
      });
      markBestCard();
      const v2 = $('simVerdict');
      if (v2) v2.innerHTML += ' <span class="mut">(verdict re-checked at 3× simulation depth)</span>';
    }, 60);
  }

  // ---------------- CSV export ----------------
  function buildCsv() {
    const esc2 = s => '"' + String(s == null ? '' : s).replace(/"/g, '""') + '"';
    const rows = [['status', 'pick', 'round', 'team', 'player', 'pos', 'nfl_team', 'bye',
      'value', 'proj_raw', 'adp_league', 'analyst_rank', 'kalshi_leader_prob', 'team_ou', 'durability_mult', 'news'].join(',')];
    eng.state.picks.forEach((pk, i) => {
      const p = eng.byId.get(pk.playerId);
      rows.push([
        pk.team === eng.cfg.mySlot ? 'MINE' : 'drafted', i + 1, eng.pickRound(i + 1), teamLabel(pk.team),
        esc2(p.name), p.pos, p.team, p.bye, Math.round(p.val), Math.round(p.fmtProj),
        p.adpF < 250 ? p.adpF : '', p.ecr != null ? p.ecr : '', p.klProb != null ? p.klProb : '',
        p.wtLine != null ? p.wtLine : '', p.dur, esc2(p.news || ''),
      ].join(','));
    });
    eng.available().sort((a, b) => b.vorp - a.vorp).slice(0, 120).forEach(p => {
      rows.push(['available', '', '', '', esc2(p.name), p.pos, p.team, p.bye,
        Math.round(p.val), Math.round(p.fmtProj), p.adpF < 250 ? p.adpF : '',
        p.ecr != null ? p.ecr : '', p.klProb != null ? p.klProb : '',
        p.wtLine != null ? p.wtLine : '', p.dur, esc2(p.news || '')].join(','));
    });
    return rows.join('\n');
  }
  function downloadCsv() {
    const csv = buildCsv();
    try {
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'draft-command-board.csv';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 5000);
      toast('CSV downloaded'); closeSheet();
    } catch (e) {
      openSheet('<h3>Board CSV</h3><div class="note">Download blocked here — copy instead:</div>' +
        '<textarea id="ioArea" readonly></textarea><button class="sheetBtn" id="ioCopy">Copy to clipboard</button>');
      $('ioArea').value = csv;
      $('ioCopy').onclick = () => { $('ioArea').select(); document.execCommand('copy'); toast('Copied'); closeSheet(); };
    }
  }

  // ---------------- menu sheet ----------------
  function openSheet(html) {
    $('sheet').innerHTML = html;
    $('sheet').classList.remove('hidden');
    $('sheetBack').classList.remove('hidden');
  }
  function closeSheet() { $('sheet').classList.add('hidden'); $('sheetBack').classList.add('hidden'); }

  function menuSheet() {
    openSheet(
      '<h3>Menu</h3>' +
      '<button class="sheetBtn" id="mCsv">Download board as CSV</button>' +
      '<button class="sheetBtn" id="mExport">Export draft state (backup)</button>' +
      '<button class="sheetBtn" id="mImport">Import draft state</button>' +
      '<button class="sheetBtn" id="mDeep">Run deep simulation</button>' +
      '<button class="sheetBtn danger" id="mRestart">Restart draft (same league)</button>' +
      '<button class="sheetBtn danger" id="mSetup">New league setup</button>' +
      '<div class="note" style="margin-top:12px">Autosaves after every pick (URL + browser storage where available) — reopening this file or refreshing restores the draft. Export is still the belt-and-suspenders backup. ' +
      SCORING_LABEL[setup.scoring] + ' scoring. Values = projections blended with the analyst consensus board ' +
      '(weights fitted on a 2025 backtest); playoff % from Monte-Carlo draft + season sims with empirical bust rates and team correlation.</div>'
    );
    $('mCsv').onclick = () => { downloadCsv(); };
    $('mExport').onclick = () => {
      openSheet('<h3>Export</h3><textarea id="ioArea" readonly></textarea>' +
        '<button class="sheetBtn" id="ioCopy">Copy to clipboard</button>');
      $('ioArea').value = eng.exportState();
      $('ioCopy').onclick = () => {
        $('ioArea').select(); document.execCommand('copy');
        try { navigator.clipboard && navigator.clipboard.writeText($('ioArea').value); } catch (e) {}
        toast('Copied'); closeSheet();
      };
    };
    $('mImport').onclick = () => {
      openSheet('<h3>Import</h3><textarea id="ioArea" placeholder="Paste exported state…"></textarea>' +
        '<button class="sheetBtn" id="ioGo">Load</button>');
      $('ioGo').onclick = () => {
        try {
          const d = JSON.parse($('ioArea').value);
          if (!d.cfg || !Array.isArray(d.picks)) throw new Error('bad format');
          Object.assign(setup, {
            teams: d.cfg.teams, mySlot: d.cfg.mySlot, scoring: d.cfg.scoring || 'ppr',
            playoffTeams: d.cfg.playoffTeams || 6, slots: d.cfg.slots,
          });
          const valid = d.picks.every(pk => PLAYERS.some(p => p.id === pk.playerId));
          if (!valid) throw new Error('unknown player in picks');
          startDraft(d.picks);
          toast('Draft restored — ' + d.picks.length + ' picks');
          closeSheet();
        } catch (e) { toast('Could not import: ' + e.message); }
      };
    };
    $('mDeep').onclick = () => { closeSheet(); deepSim(); };
    $('mRestart').onclick = () => {
      if (!confirm('Clear all picks and restart this draft?')) return;
      startDraft(); closeSheet(); toast('Draft restarted');
    };
    $('mSetup').onclick = () => {
      if (!confirm('Leave this draft and return to setup?')) return;
      clearPersist(); closeSheet();
      $('mainView').classList.add('hidden'); $('nav').classList.add('hidden');
      $('setupView').classList.remove('hidden');
      $('confirmBar').classList.add('hidden');
    };
  }

  function deepSim() {
    toast('Running deep simulation…');
    simGen++;
    const gen = simGen;
    setTimeout(() => runSims(gen, true), 50);
  }

  // ---------------- nav & events ----------------
  function switchPane(name) {
    activePane = name;
    document.querySelectorAll('#nav button').forEach(b => b.classList.toggle('on', b.dataset.pane === name));
    ['draft', 'board', 'team', 'players'].forEach(p => $('pane-' + p).classList.toggle('hidden', p !== name));
    if (name === 'board') renderBoard();
    if (name === 'team') renderTeam();
    if (name === 'players') renderPlayers();
    window.scrollTo(0, 0);
  }

  function wire() {
    buildSetup();
    $('startBtn').onclick = () => startDraft();
    $('searchInput').addEventListener('input', renderSearchResults);
    $('undoBtn').onclick = () => {
      const last = eng && eng.undo();
      if (last) {
        const p = eng.byId.get(last.playerId);
        toast('Undid: ' + shortName(p.name) + ' (' + teamLabel(last.team) + ')');
        renderAll(); persist(); scheduleSims();
      } else toast('Nothing to undo');
    };
    $('menuBtn').onclick = menuSheet;
    $('sheetBack').onclick = closeSheet;
    $('confirmNo').onclick = closeConfirm;
    $('confirmYes').onclick = () => {
      if (!pendingPlayer) return;
      commitPick(pendingPlayer.id, parseInt($('confirmTeam').value, 10));
    };
    $('deepSimBtn').onclick = deepSim;
    document.querySelectorAll('#nav button').forEach(b => b.onclick = () => switchPane(b.dataset.pane));
  }

  function boot() { wire(); tryRestore(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();

  // test/debug hook (harmless in normal use)
  window.__dc = { eng: () => eng, commit: commitPick, setup, csv: () => buildCsv() };
})();
