/* ============================================================
   TX v8.11.6 - Annex C canonical JS
   KTX301 byte-level canonical
   body 閉じタグ直前の script ブロック内部に逐語コピー
   ※ コメント本文内に "</" + "body>" のリテラルを書かないこと。
   　 ホスト側の単一ファイル注入が正規表現でこのリテラルに
   　 誤マッチして注入位置がコメント内になりJSが壊れる事故あり
   　 (AP-41 / S77 で検知)
   ============================================================ */

(function(){
  'use strict';
  if (window.__txInteractive || window.__ktxInteractive) return;
  window.__txInteractive = true;
  window.__ktxInteractive = true;

  function escapeHTML(s){
    return String(s == null ? '' : s)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
  }
  function readCorrect(el){
    return (el && el.dataset && (el.dataset.correctValue || el.dataset.correct)) || '';
  }
  function readUserVal(btn){
    if (btn && btn.dataset && btn.dataset.value) return btn.dataset.value;
    var t = (btn && btn.textContent) ? btn.textContent.trim() : '';
    if (t.indexOf('○') === 0) return '○';
    if (t.indexOf('×') === 0) return '×';
    return '';
  }

  // ========================================================
  // A-2 解答エリア — v8.11.3: 3 Type 対応 (single / multi / ox-grid)
  //   single:  クリックで選択ハイライト → reveal で正誤判定
  //   multi:   複数クリックで選択 (max=正解数)、トグル可、FIFO で最古解除
  //   ox-grid: 各 ox-row で 1 つずつ選択、全行揃ったら reveal 有効化
  // ========================================================
  function getAnswerType(area){
    return (area && area.dataset && area.dataset.answerType) || 'single';
  }
  function updateRevealBtnState(area){
    if (!area) return;
    var type = getAnswerType(area);
    var rb = area.querySelector('.reveal-answer-btn');
    if (!rb) return;
    var ready = false;
    if (type === 'single') {
      ready = !!area.querySelector('.answer-slot.selected');
    } else if (type === 'multi') {
      var correct = readCorrect(area) || '';
      var maxSel = correct.split(',').length;
      var count = area.querySelectorAll('.answer-slot.selected').length;
      ready = (count === maxSel);
      // counter 更新
      var counter = area.querySelector('.selection-counter');
      if (counter) counter.textContent = '選択中: ' + count + ' / ' + maxSel + ' 個';
    } else if (type === 'ox-grid') {
      var rows = area.querySelectorAll('.ox-row');
      var allSel = rows.length > 0;
      rows.forEach(function(r){
        if (!r.querySelector('.ox-btn.selected')) allSel = false;
      });
      ready = allSel;
    }
    rb.disabled = !ready;
  }
  function handleAnswerSlot(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var type = getAnswerType(area);
    if (type === 'multi') {
      var correct = readCorrect(area) || '';
      var maxSel = correct.split(',').length;
      if (btn.classList.contains('selected')) {
        btn.classList.remove('selected');
      } else {
        var selected = area.querySelectorAll('.answer-slot.selected');
        if (selected.length >= maxSel) {
          selected[0].classList.remove('selected'); // FIFO
        }
        btn.classList.add('selected');
      }
    } else {
      // single
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.classList.remove('selected');
      });
      btn.classList.add('selected');
    }
    updateRevealBtnState(area);
  }
  function handleOxBtn(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var row = btn.closest('.ox-row');
    if (!row) return;
    row.querySelectorAll('.ox-btn').forEach(function(b){
      b.classList.remove('selected');
    });
    btn.classList.add('selected');
    updateRevealBtnState(area);
  }
  function handleRevealAnswerBtn(btn){
    var area = btn.closest('.answer-area');
    if (!area || area.classList.contains('answered')) return;
    var type = getAnswerType(area);
    var correct = readCorrect(area);
    if (!correct) return;
    var ok = false;
    if (type === 'single') {
      var selected = area.querySelector('.answer-slot.selected');
      if (!selected) return;
      var user = readUserVal(selected);
      ok = (user === correct);
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.disabled = true;
        var sv = readUserVal(s);
        if (sv === correct) s.classList.add('correct-mark');
        else if (s === selected) s.classList.add('incorrect-mark');
      });
    } else if (type === 'multi') {
      var correctArr = correct.split(',').map(function(s){return s.trim();});
      var correctSet = {};
      correctArr.forEach(function(v){ correctSet[v] = true; });
      var selectedSlots = area.querySelectorAll('.answer-slot.selected');
      var userArr = [];
      selectedSlots.forEach(function(s){ userArr.push(readUserVal(s)); });
      ok = (userArr.length === correctArr.length);
      if (ok) {
        for (var i = 0; i < userArr.length; i++){
          if (!correctSet[userArr[i]]) { ok = false; break; }
        }
      }
      var userSet = {};
      userArr.forEach(function(v){ userSet[v] = true; });
      area.querySelectorAll('.answer-slot').forEach(function(s){
        s.disabled = true;
        var sv = readUserVal(s);
        if (correctSet[sv]) s.classList.add('correct-mark');
        else if (userSet[sv]) s.classList.add('incorrect-mark');
      });
    } else if (type === 'ox-grid') {
      var rows = area.querySelectorAll('.ox-row');
      var userVal = '';
      var selectedBtns = [];
      rows.forEach(function(r){
        var sel = r.querySelector('.ox-btn.selected');
        userVal += (sel ? readUserVal(sel) : '?');
        selectedBtns.push(sel);
      });
      ok = (userVal === correct);
      rows.forEach(function(r, idx){
        var correctChar = correct.charAt(idx);
        var selBtn = selectedBtns[idx];
        r.querySelectorAll('.ox-btn').forEach(function(b){
          b.disabled = true;
          var bv = readUserVal(b);
          if (bv === correctChar) b.classList.add('correct-mark');
          else if (b === selBtn) b.classList.add('incorrect-mark');
        });
      });
    }
    btn.disabled = true;
    var fb = area.querySelector('#answer-feedback') || area.querySelector('.answer-feedback');
    if (fb){
      fb.hidden = false;
      if (ok) {
        fb.style.background = 'linear-gradient(180deg,#e8f5e9 0%,#f3faf4 60%,#ffffff 100%)';
        fb.style.borderLeft = '5px solid var(--recall-correct-light)';
        fb.style.boxShadow = '0 0 0 1px rgba(46,125,50,.18), 0 4px 14px rgba(46,125,50,.14)';
        fb.innerHTML = '<strong class="fb-verdict fb-correct">✓ 正解</strong>';
      } else {
        fb.style.background = 'linear-gradient(180deg,#ffeef0 0%,#fff4f6 60%,#ffffff 100%)';
        fb.style.borderLeft = '5px solid var(--recall-incorrect)';
        fb.style.boxShadow = '0 0 0 1px rgba(176,0,50,.18), 0 4px 14px rgba(176,0,50,.14)';
        fb.innerHTML = '<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>　正解は<span class="fb-answer">' + escapeHTML(correct) + '</span>';
      }
    }
    revealFinalAnswer();
    area.classList.add('answered');
  }

  // ========================================================
  // A-2 互換型（choice-row + check-btn）
  // ========================================================
  var selectedChoice = null;
  var legacyARevealed = false;
  function handleChoiceRow(row){
    if (legacyARevealed) return;
    document.querySelectorAll('.choice-row').forEach(function(r){ r.classList.remove('selected'); });
    row.classList.add('selected');
    selectedChoice = row.dataset.choice || null;
  }
  function handleCheckBtn(btn){
    if (legacyARevealed) return;
    var area = btn.closest('.answer-area');
    var ar = document.getElementById('answer-result') || (area && area.querySelector('.answer-result'));
    if (!selectedChoice){
      if (ar){
        ar.innerHTML = '<div style="color:var(--recall-incorrect);font-weight:600;padding:8px 0;">先に肢を1つ選んでください。</div>';
        ar.classList.add('show');
      }
      return;
    }
    legacyARevealed = true;
    var correct = (area && area.dataset.correctValue) || '';
    var exp = (area && area.dataset.explanation) || '';
    var ok = (selectedChoice === correct);
    document.querySelectorAll('.choice-row').forEach(function(r){
      var c = r.dataset.choice;
      if (c === correct) r.classList.add('correct');
      else if (c === selectedChoice) r.classList.add('incorrect');
    });
    if (ar){
      var verdictHTML = ok
        ? '<strong class="fb-verdict fb-correct">✓ 正解</strong>'
        : '<strong class="fb-verdict fb-incorrect">✗ 不正解</strong>';
      ar.innerHTML = '<div class="result-msg" style="padding:14px 18px;border-radius:8px;background:' +
        (ok ? 'linear-gradient(180deg,#e8f5e9,#f3faf4)' : 'linear-gradient(180deg,#ffeef0,#fff4f6)') +
        ';border-left:5px solid ' + (ok ? 'var(--recall-correct-light)' : 'var(--recall-incorrect)') +
        ';">' + verdictHTML + '　' + exp.replace(/^[○×\d]+。\s*/,'') + '</div>';
      ar.classList.add('show');
    }
    btn.disabled = true;
    revealFinalAnswer();
  }
  function revealFinalAnswer(){
    var fa = document.querySelector('.final-answer');
    if (!fa) return;
    fa.hidden = false;
    fa.removeAttribute('hidden');
    fa.classList.add('revealed');
  }

  // ========================================================
  // ARENA tracking
  // ========================================================
  var arenaQuizzes = document.querySelectorAll('.self-check-quiz[data-arena="1"]');
  var arenaTotal = arenaQuizzes.length;
  var arenaState = { answered: 0, correct: 0, incorrect: 0 };
  var arenaCurrent  = document.getElementById('arena-current');
  var arenaFill     = document.getElementById('arena-fill');
  var arenaCorrect  = document.getElementById('arena-correct');
  var arenaIncorrect= document.getElementById('arena-incorrect');
  var scoreCard     = document.getElementById('arena-scorecard');
  var scoreCorrect  = document.getElementById('scorecard-correct');
  var scoreGrade    = document.getElementById('scorecard-grade');
  var scoreMsg      = document.getElementById('scorecard-msg');

  function updateArenaCounter(){
    if (!arenaCurrent) return;
    arenaCurrent.textContent = arenaState.answered;
    if (arenaCorrect)   arenaCorrect.textContent   = arenaState.correct;
    if (arenaIncorrect) arenaIncorrect.textContent = arenaState.incorrect;
    if (arenaFill && arenaTotal) arenaFill.style.width = (arenaState.answered / arenaTotal * 100) + '%';
  }
  function showScoreCard(){
    if (!scoreCard || !arenaTotal) return;
    if (scoreCorrect) scoreCorrect.textContent = arenaState.correct;
    var pct = arenaState.correct / arenaTotal;
    var grade, msg;
    if (pct === 1)        { grade = 'S — PERFECT';     msg = '全問完答。論点群を完全に固められた状態。本試験でも即答できる水準。'; }
    else if (pct >= 11/12){ grade = 'A — EXCELLENT';   msg = 'ほぼ完答。誤答した問題の論点を解説リンクで再確認すれば合格水準を超える。'; }
    else if (pct >= 9/12) { grade = 'B — GOOD';        msg = '良好な仕上がり。誤答した論点について解説リンクから戻り、なぜ間違えたかを言語化してから再演習を。'; }
    else if (pct >= 7/12) { grade = 'C — DEVELOPING';  msg = 'まだ取りこぼしが多い。各記述の解説（PART B）と体系（PART C）に戻って論点をもう一度紐解いてから再挑戦を。'; }
    else                  { grade = 'D — REBUILD';     msg = '論点知識が定着していない。PART AからPART Cまで通読し、軸を掴み直そう。'; }
    if (scoreGrade) scoreGrade.textContent = grade;
    if (scoreMsg)   scoreMsg.textContent   = msg;
    scoreCard.hidden = false;
    scoreCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function resetArena(){
    arenaQuizzes.forEach(function(quiz){
      var buttons = quiz.querySelectorAll('.quiz-btn');
      var answer = quiz.querySelector('.quiz-answer');
      var result = quiz.querySelector('.quiz-result');
      buttons.forEach(function(b){
        b.disabled = false;
        b.classList.remove('correct-mark', 'incorrect-mark', 'quiz-correct-mark', 'quiz-incorrect-mark');
      });
      if (answer) {
        answer.hidden = true;
        answer.classList.remove('quiz-answer-correct', 'quiz-answer-incorrect');
      }
      if (result) {
        result.textContent = '';
        result.style.color = '';
        result.classList.remove('quiz-result-correct', 'quiz-result-incorrect');
      }
      quiz.dataset.done = '';
      quiz.classList.remove('answered');
    });
    arenaState.answered = 0;
    arenaState.correct  = 0;
    arenaState.incorrect = 0;
    updateArenaCounter();
    if (scoreCard) scoreCard.hidden = true;
  }

  // ========================================================
  // self-check-quiz
  // ========================================================
  function handleQuizBtn(btn){
    var quiz = btn.closest('.self-check-quiz');
    if (!quiz || quiz.classList.contains('answered') || quiz.dataset.done === '1') return;
    quiz.dataset.done = '1';
    quiz.classList.add('answered');

    var correct = readCorrect(quiz);
    var user = readUserVal(btn);
    var isArena = quiz.getAttribute('data-arena') === '1';

    var ok;
    if (correct) {
      ok = user ? (user === correct) : (btn.getAttribute('data-correct') === 'true');
    } else {
      ok = btn.getAttribute('data-correct') === 'true';
    }

    quiz.querySelectorAll('.quiz-btn').forEach(function(b){
      b.disabled = true;
      var bc = b.getAttribute('data-correct') === 'true';
      if (bc) b.classList.add('correct-mark');
      else    b.classList.add('incorrect-mark');
    });

    var answer = quiz.querySelector('.quiz-answer');
    var result = quiz.querySelector('.quiz-result');
    if (answer) answer.hidden = false;
    if (result) {
      if (ok) {
        result.textContent = '✓ 正解';
        result.classList.add('quiz-result-correct');
        if (answer) answer.classList.add('quiz-answer-correct');
      } else {
        result.textContent = '✗ 不正解';
        result.classList.add('quiz-result-incorrect');
        if (answer) answer.classList.add('quiz-answer-incorrect');
      }
    }

    if (isArena) {
      arenaState.answered += 1;
      if (ok) arenaState.correct += 1; else arenaState.incorrect += 1;
      updateArenaCounter();
      if (arenaState.answered === arenaTotal) setTimeout(showScoreCard, 600);
    }
  }

  // ========================================================
  // 単一クリック委譲
  // ========================================================
  document.addEventListener('click', function(e){
    var t = e.target;
    if (!t || !t.closest) return;
    var slot = t.closest('.answer-slot');       if (slot)     { handleAnswerSlot(slot); return; }
    var ox   = t.closest('.ox-btn');             if (ox)       { handleOxBtn(ox); return; }
    var rb   = t.closest('.reveal-answer-btn');  if (rb)       { handleRevealAnswerBtn(rb); return; }
    var row  = t.closest('.choice-row');      if (row)      { handleChoiceRow(row); return; }
    var ck   = t.closest('.check-btn');       if (ck)       { handleCheckBtn(ck); return; }
    var qb   = t.closest('.quiz-btn');        if (qb)       { handleQuizBtn(qb); return; }
    var rs   = t.closest('.arena-reset');     if (rs)       {
      if (confirm('ARENAをリセットしますか？すべての回答がクリアされます。')) resetArena();
      return;
    }
  }, false);

  // ========================================================
  // スムーズスクロール
  // ========================================================
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(e){
      var id = a.getAttribute('href');
      if (id.length <= 1) return;
      var tgt = document.querySelector(id);
      if (tgt){
        e.preventDefault();
        tgt.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  function init(){ updateArenaCounter(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
