/* Daily Dose of Gita: offline app. Today / Search by situation / Read / Settings.
   Reading data: data.js. Mood guidance: mood.js (separate). No server, no AI. Notifications use Capacitor LocalNotifications. */
(function () {
  'use strict';
  var DATA = window.GITA;
  var SPEAKER = { K: ['श्रीकृष्ण', 'Krishna'], A: ['अर्जुन', 'Arjuna'], S: ['संजय', 'Sanjaya'], D: ['धृतराष्ट्र', 'Dhritarashtra'] };
  var VERSES = DATA.verses.map(function (x) {
    return { id: x.i, chapter: x.c, verse: x.v, sp: x.sp, sanskrit: x.sa, meaning_hi: x.hi, meaning_en: x.en, moods: DATA.moods[x.i] || [] };
  });
  // Only these verses (Krishna's comforting and guiding words) appear in mood search and as the shloka of the day.
  // Mood guidance lives in its own file (mood.js), separate from the reading data above.
  var MD = window.MOOD;
  var GUIDE = Object.keys(MD.cards).map(function (id) {
    var c = MD.cards[id], p = id.split('.');
    return { id: id, chapter: +p[0], verse: +p[1], sanskrit: c.sa, hh: c.hh, he: c.he, sh: c.sh, se: c.se, moods: MD.tags[id] || [] };
  }).sort(function (a, b) { return a.chapter - b.chapter || a.verse - b.verse; });
  function GL(c, k) { return state.lang === 'hi' ? c[k + 'h'] : c[k + 'e']; }

  /* ---------- labels ---------- */
  var MOODS = {
    sadness: ['उदासी', 'Sadness'], grief: ['शोक', 'Grief'], fear: ['डर', 'Fear'], anger: ['गुस्सा', 'Anger'],
    stress: ['तनाव', 'Stress'], anxiety: ['चिंता', 'Anxiety'], confusion: ['उलझन', 'Confusion'], doubt: ['संदेह', 'Doubt'],
    courage: ['हिम्मत', 'Courage'], motivation: ['प्रेरणा', 'Motivation'], focus: ['ध्यान', 'Focus'],
    restlessness: ['बेचैनी', 'Restlessness'], peace: ['शांति', 'Peace'], desire: ['इच्छा', 'Desire'], duty: ['कर्तव्य', 'Duty'],
    patience: ['धैर्य', 'Patience'], acceptance: ['स्वीकार', 'Acceptance'], wisdom: ['ज्ञान', 'Wisdom'],
    'self-control': ['संयम', 'Self-control'], contentment: ['संतोष', 'Contentment'], curiosity: ['जिज्ञासा', 'Curiosity'],
    'seeking-guidance': ['मार्गदर्शन', 'Guidance'], hope: ['आशा', 'Hope'], loneliness: ['अकेलापन', 'Loneliness'], guilt: ['पछतावा', 'Guilt']
  };
  var HOME_MOODS = ['anger', 'fear', 'sadness', 'anxiety', 'loneliness', 'guilt', 'confusion', 'restlessness', 'focus', 'motivation', 'peace', 'hope'];

  var CHAPTERS = [
    ['अर्जुनविषादयोग', 'Arjuna Vishada Yoga'], ['सांख्य योग', 'Sankhya Yoga'], ['कर्म योग', 'Karma Yoga'],
    ['ज्ञानकर्मसंन्यास योग', 'Jnana Karma Sanyasa Yoga'], ['कर्मसंन्यास योग', 'Karma Sanyasa Yoga'], ['ध्यान योग', 'Dhyana Yoga'],
    ['ज्ञानविज्ञान योग', 'Jnana Vijnana Yoga'], ['अक्षरब्रह्म योग', 'Akshara Brahma Yoga'], ['राजविद्याराजगुह्य योग', 'Raja Vidya Raja Guhya Yoga'],
    ['विभूति योग', 'Vibhuti Yoga'], ['विश्वरूपदर्शन योग', 'Vishvarupa Darshana Yoga'], ['भक्ति योग', 'Bhakti Yoga'],
    ['क्षेत्रक्षेत्रज्ञविभाग योग', 'Kshetra Kshetrajna Vibhaga Yoga'], ['गुणत्रयविभाग योग', 'Gunatraya Vibhaga Yoga'],
    ['पुरुषोत्तम योग', 'Purushottama Yoga'], ['दैवासुरसम्पद्विभाग योग', 'Daivasura Sampad Vibhaga Yoga'],
    ['श्रद्धात्रयविभाग योग', 'Shraddhatraya Vibhaga Yoga'], ['मोक्षसंन्यास योग', 'Moksha Sanyasa Yoga']
  ];
  var AVAILABLE = {}; VERSES.forEach(function (v) { AVAILABLE[v.chapter] = true; });
  function speakerName(v) { return L(SPEAKER[v.sp]); }

  var T = {
    hi: {
      tabs: ['आज', 'खोजें', 'पढ़ें', 'सेटिंग'],
      today: 'आज का श्लोक', meaning: 'अर्थ', share: 'शेयर करें', copied: 'कॉपी हो गया',
      feel: 'आज कैसा महसूस हो रहा है?', feelSub: 'अपना मूड चुनें, श्लोक मिलेगा।',
      searchTitle: 'अपनी स्थिति से श्लोक खोजें', placeholder: 'जैसे: गुस्सा, डर, चिंता, मन नहीं लगता',
      orPick: 'या मूड चुनें', none: 'कोई श्लोक नहीं मिला। दूसरे शब्द आज़माएँ, जैसे "चिंता" या "डर"।', more: 'और दिखाएँ',
      results: 'श्लोक मिले', readTitle: 'पूरी गीता', soon: 'जल्द आ रहा है', chapter: 'अध्याय', jump: 'श्लोक पर जाएँ', back: '← अध्यायों पर वापस',
      doNow: 'अभी क्या करें', verses: 'श्लोक', settings: 'सेटिंग', language: 'भाषा', notif: 'रोज़ का श्लोक नोटिफ़िकेशन', time: 'समय',
      notifOn: 'हर दिन इस समय नया श्लोक आएगा। भरोसे के लिए ऐप महीने में एक बार खोल लें।',
      notifDenied: 'नोटिफ़िकेशन की अनुमति नहीं मिली। फ़ोन की सेटिंग में अनुमति दें।',
      notifWeb: 'नोटिफ़िकेशन सिर्फ़ फ़ोन ऐप में काम करते हैं।',
      about: 'यह ऐप भगवद्गीता से मार्गदर्शन के लिए है। यह डॉक्टर, काउंसलर या किसी पेशेवर सलाह का विकल्प नहीं है।',
      helpTitle: 'पहले अपना ध्यान रखें',
      helpBody: 'आप जो महसूस कर रहे हैं वह मायने रखता है। अगर आप खुद को नुकसान पहुँचाने के बारे में सोच रहे हैं, तो कृपया अभी किसी से बात करें। भारत में Tele-MANAS पर 24x7 मुफ़्त सहायता मिलती है:',
      softBody: 'अगर यह भारीपन कई दिनों से है, तो किसी अपने से या काउंसलर से बात करना मदद कर सकता है। भारत में Tele-MANAS (24x7, मुफ़्त):',
      call: 'कॉल करें', draft: 'ड्राफ़्ट: ऐप सार्वजनिक करने से पहले श्लोक और अर्थ की जाँच ज़रूरी है।', readHint: 'पूरी गीता, 18 अध्याय।'
    },
    en: {
      tabs: ['Today', 'Search', 'Read', 'Settings'],
      today: 'Shloka of the day', meaning: 'Meaning', share: 'Share', copied: 'Copied',
      feel: 'How are you feeling today?', feelSub: 'Pick a mood to find a shloka.',
      searchTitle: 'Find a shloka for your situation', placeholder: 'e.g. anger, fear, worry, cannot focus',
      orPick: 'Or pick a mood', none: 'No shloka found. Try other words like "worry" or "fear".', more: 'Show more',
      results: 'shlokas found', readTitle: 'Read the Gita', soon: 'Coming soon', chapter: 'Chapter', jump: 'Jump to verse', back: '← Back to chapters',
      doNow: 'What to do now', verses: 'verses', settings: 'Settings', language: 'Language', notif: 'Daily shloka notification', time: 'Time',
      notifOn: 'A new shloka arrives at this time every day. For reliability, open the app once a month.',
      notifDenied: 'Notification permission was not granted. Please allow it in your phone settings.',
      notifWeb: 'Notifications only work in the phone app.',
      about: 'This app offers guidance from the Bhagavad Gita. It is not a substitute for a doctor, counsellor or professional advice.',
      helpTitle: 'Please look after yourself first',
      helpBody: 'What you feel matters. If you are thinking about harming yourself, please talk to someone right now. In India, Tele-MANAS offers free 24x7 support:',
      softBody: 'If this heaviness has lasted many days, talking to someone close or a counsellor can help. In India, Tele-MANAS (free, 24x7):',
      call: 'Call', draft: 'Draft: verify the shlokas and meanings before making the app public.'
    }
  };

  /* ---------- situation words -> moods (Hindi, Hinglish and English) ---------- */
  var SYN = [
    ['anger', ['gussa', 'gusse', 'krodh', 'anger', 'angry', 'chidh', 'irritat', 'गुस्सा', 'क्रोध', 'चिढ़']],
    ['fear', ['darr', 'dar lag', 'daro', 'bhay', 'fear', 'scared', 'afraid', 'nervous', 'डर', 'भय']],
    ['sadness', ['udaas', 'udas', 'dukh', 'sad', 'nirash', 'hopeless', 'उदास', 'दुख', 'दुःख', 'निराश']],
    ['grief', ['mrityu', 'maut', 'death', 'died', 'passed away', 'loss', 'khoya', 'shok', 'grief', 'miss', 'शोक', 'मृत्यु', 'मौत']],
    ['anxiety', ['chinta', 'tension', 'anxiety', 'anxious', 'worry', 'worried', 'ghabra', 'overthink', 'चिंता', 'घबराहट', 'टेंशन']],
    ['stress', ['stress', 'pressure', 'tanav', 'burnout', 'thak', 'tired', 'तनाव', 'दबाव', 'थक']],
    ['confusion', ['confus', 'ulajh', 'uljhan', 'kya karun', 'decision', 'faisla', 'उलझन', 'कन्फ्यूज', 'फैसला']],
    ['doubt', ['shak', 'sandeh', 'doubt', 'unsure', 'संदेह', 'शक']],
    ['courage', ['himmat', 'hausla', 'courage', 'brave', 'sahas', 'हिम्मत', 'हौसला', 'साहस']],
    ['motivation', ['motivat', 'prerna', 'inspire', 'aalas', 'lazy', 'procrastinat', 'give up', 'हार', 'प्रेरणा', 'आलस']],
    ['focus', ['focus', 'concentrat', 'dhyan', 'man nahi lag', 'mann nahi lag', 'padhai', 'study', 'distract', 'ध्यान', 'एकाग्र', 'पढ़ाई', 'मन नहीं लग']],
    ['restlessness', ['bechain', 'restless', 'bhatak', 'mann bhatak', 'बेचैन', 'भटक']],
    ['peace', ['shanti', 'shaanti', 'peace', 'calm', 'sukoon', 'सुकून', 'शांति']],
    ['desire', ['ichha', 'lobh', 'craving', 'temptation', 'lalach', 'lust', 'इच्छा', 'लालच', 'लोभ']],
    ['duty', ['kartavya', 'duty', 'zimmedari', 'jimmedari', 'responsib', 'कर्तव्य', 'ज़िम्मेदारी', 'जिम्मेदारी']],
    ['patience', ['dhairya', 'sabr', 'patience', 'wait', 'धैर्य', 'सब्र']],
    ['acceptance', ['accept', 'swikar', 'sweekar', 'let go', 'letting go', 'स्वीकार']],
    ['wisdom', ['gyan', 'gyaan', 'wisdom', 'knowledge', 'ज्ञान']],
    ['self-control', ['sanyam', 'control', 'addiction', 'habit', 'aadat', 'phone', 'mobile', 'संयम', 'आदत', 'लत']],
    ['contentment', ['santosh', 'content', 'khushi', 'happy', 'संतोष']],
    ['hope', ['umeed', 'ummeed', 'hope', 'asha', 'aasha', 'faith', 'bharosa', 'उम्मीद', 'आशा', 'भरोसा', 'निराशा']],
    ['loneliness', ['akela', 'akelapan', 'alone', 'lonely', 'koi nahi', 'अकेला', 'अकेलापन']],
    ['guilt', ['galti', 'guilt', 'guilty', 'pachtav', 'paap', 'regret', 'sorry', 'शर्म', 'गलती', 'पछतावा', 'पाप']]
  ];
  var OUTCOME = ['result', 'phal', 'outcome', 'success', 'failure', 'safal', 'asafal', 'naukri', 'job', 'career', 'exam', 'fail', 'नौकरी', 'परिणाम', 'फल', 'असफल', 'सफल'];
  var CRISIS = ['suicide', 'suicidal', 'khudkushi', 'khud kushi', 'kill myself', 'end my life', 'want to die', 'marna chahta', 'marna chahti', 'mar jaun', 'jeena nahi', 'self harm', 'self-harm', 'आत्महत्या', 'खुदकुशी', 'मरना चाहता', 'मरना चाहती', 'जीना नहीं', 'मर जाऊं', 'मर जाऊँ'];
  var SOFT = ['depress', 'hopeless', 'worthless', 'no reason to live', 'डिप्रेशन', 'अवसाद'];

  /* ---------- helpers ---------- */
  var $view = document.getElementById('view');
  var $tabs = document.getElementById('tabs');
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function store(k, v) { try { if (v === undefined) return localStorage.getItem('gita.' + k); localStorage.setItem('gita.' + k, v); } catch (e) { return null; } }
  var state = {
    lang: store('lang') === 'en' ? 'en' : 'hi',
    tab: 'today',
    mood: null,
    query: '',
    shown: 10,
    chapter: null,
    notif: store('notif') === '1',
    time: store('time') || '07:00'
  };
  function t() { return T[state.lang]; }
  function L(pair) { return state.lang === 'hi' ? pair[0] : pair[1]; }
  function moodLabel(k) { return MOODS[k] ? L(MOODS[k]) : k; }
  function meaning(v, clean) {
    var m = state.lang === 'hi' ? v.meaning_hi : v.meaning_en;
    return clean ? m.replace(/^(श्रीकृष्ण बोले:|Krishna said:)\s*/, '') : m;
  }
  function cap(name) { try { return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins[name]; } catch (e) { return null; } }
  var toastTimer;
  function toast(msg) {
    var el = document.querySelector('.toast');
    if (!el) { el = document.createElement('div'); el.className = 'toast'; document.body.appendChild(el); }
    el.textContent = msg; el.hidden = false; clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.hidden = true; }, 1800);
  }

  /* ---------- shloka of the day ---------- */
  var POOL = GUIDE;
  function dayNum(d) { var x = new Date(d.getFullYear(), d.getMonth(), d.getDate()); return Math.floor((x.getTime() - x.getTimezoneOffset() * 60000) / 86400000); }
  function dailyFor(d) { return POOL[dayNum(d) % POOL.length]; }
  function ref(id) { return (state.lang === 'hi' ? 'गीता ' : 'Gita ') + id; }

  /* ---------- search ---------- */
  function norm(s) { return String(s).toLowerCase(); }
  function hasAny(q, list) { return list.some(function (w) { return q.indexOf(w) >= 0; }); }
  function search(query, mood) {
    var q = norm(query).trim();
    if (!q && !mood) return { crisis: false, soft: false, list: [] };
    var crisis = hasAny(q, CRISIS), soft = !crisis && hasAny(q, SOFT);
    var matched = {};
    SYN.forEach(function (row) { if (hasAny(q, row[1])) matched[row[0]] = 3; });
    if (hasAny(q, OUTCOME)) { matched.stress = 2; matched.motivation = 2; matched.focus = 1; matched.anxiety = 2; }
    if (soft) { matched.sadness = 3; matched.peace = 2; }
    if (mood) matched[mood] = 5;
    var tokens = q.split(/[^a-z0-9ऀ-ॿ]+/).filter(function (w) { return w.length >= 3; });
    var scored = GUIDE.map(function (v) {
      var s = 0;
      v.moods.forEach(function (m) { if (matched[m]) s += matched[m]; });
      var hay = norm(v.he + ' ' + v.hh + ' ' + v.se + ' ' + v.sh);
      tokens.forEach(function (w) { if (hay.indexOf(w) >= 0) s += 0.7; });
      return { v: v, s: s };
    }).filter(function (x) { return x.s >= 1.5; });
    if (mood) scored = scored.filter(function (x) { return x.v.moods.indexOf(mood) >= 0; });
    // Top-ranked verses of the best-matching mood come first (hand-picked order in mood.js).
    var best = null, bs = 0;
    Object.keys(matched).forEach(function (m) { if (MD.moods[m] && matched[m] > bs) { bs = matched[m]; best = m; } });
    scored.forEach(function (x) { if (best) { var ix = MD.moods[best].v.indexOf(x.v.id); if (ix >= 0) x.s += 10 - ix * 0.5; } });
    scored.sort(function (a, b) { return b.s - a.s || a.v.verse - b.v.verse; });
    return { crisis: crisis, soft: soft, mood: best, list: scored.map(function (x) { return x.v; }) };
  }

  /* ---------- views ---------- */
  function verseCard(v, opts) {
    opts = opts || {};
    var clean = !opts.read;
    return '<article class="card' + (opts.hero ? ' hero' : '') + '" id="v-' + v.chapter + '-' + v.verse + '">' +
      '<div class="meta">' + (opts.hero ? '<span class="pill">' + esc(t().today) + '</span>' : '') +
      '<span>' + (state.lang === 'hi' ? 'गीता ' : 'Gita ') + v.id + '</span><span>' + esc(speakerName(v)) + '</span></div>' +
      '<p class="sk">' + esc(v.sanskrit) + '</p>' +
      '<div><div class="lab">' + esc(t().meaning) + '</div><p class="meaning">' + esc(meaning(v, clean)) + '</p></div>' +
      (v.moods.length ? '<div class="moods">' + v.moods.map(function (m) { return '<button class="tag" data-mood="' + esc(m) + '">' + esc(moodLabel(m)) + '</button>'; }).join('') + '</div>' : '') +
      '<div class="actions"><button class="btn" data-share="' + v.id + '">' + esc(t().share) + '</button></div></article>';
  }
  function guideCard(c, opts) {
    opts = opts || {};
    return '<article class="card' + (opts.hero ? ' hero' : '') + '">' +
      (opts.hero ? '<div class="meta"><span class="pill">' + esc(t().today) + '</span></div>' : '') +
      '<p class="headline">' + esc(GL(c, 'h')) + '</p>' +
      '<p class="sk">' + esc(c.sanskrit) + '</p>' +
      '<p class="meaning">' + esc(GL(c, 's')) + '</p>' +
      '<div class="meta"><span>' + esc(ref(c.id)) + ' · ' + esc(L(SPEAKER.K)) + '</span></div>' +
      '<div class="actions"><button class="btn" data-shareg="' + c.id + '">' + esc(t().share) + '</button></div></article>';
  }
  function moodBox(m) {
    var g = MD.moods[m]; if (!g) return '';
    return '<section class="card hero"><div class="lab">' + esc(moodLabel(m)) + '</div><p class="headline">' + esc(L(g.t)) + '</p>' +
      '<div class="lab">' + esc(t().doNow) + '</div><ol class="steps">' + g.a.map(function (x) { return '<li>' + esc(L(x)) + '</li>'; }).join('') + '</ol></section>';
  }
  function helpCard(soft) {
    return '<section class="card help" role="note"><h2>' + esc(t().helpTitle) + '</h2><p>' + esc(soft ? t().softBody : t().helpBody) +
      '</p><div class="actions"><a class="btn primary" href="tel:14416" style="text-decoration:none;display:inline-flex;align-items:center">' + esc(t().call) + ' 14416</a></div></section>';
  }
  function moodChips(selected) {
    return '<div class="chips" role="group">' + HOME_MOODS.map(function (m) {
      return '<button class="chip" data-mood="' + m + '" aria-pressed="' + (selected === m) + '">' + esc(moodLabel(m)) + '</button>';
    }).join('') + '</div>';
  }

  function viewToday() {
    var v = dailyFor(new Date());
    return '<header><div class="brand">Daily Dose of Gita</div><h1>' + esc(t().today) + '</h1></header>' + guideCard(v, { hero: true }) +
      '<section class="card"><h2>' + esc(t().feel) + '</h2><p class="sub">' + esc(t().feelSub) + '</p>' + moodChips(null) + '</section>' +
      '<p class="note">' + esc(t().about) + '</p>';
  }

  function viewSearch() {
    var r = search(state.query, state.mood);
    var html = '<header><h1>' + esc(t().searchTitle) + '</h1></header>' +
      '<input id="q" type="search" enterkeyhint="search" autocomplete="off" placeholder="' + esc(t().placeholder) + '" value="' + esc(state.query) + '">' +
      '<div><h2>' + esc(t().orPick) + '</h2><div style="height:8px"></div>' + moodChips(state.mood) + '</div><div id="results">';
    html += resultsHtml(r);
    return html + '</div><p class="note">' + esc(t().about) + '</p>';
  }
  function resultsHtml(r) {
    var out = '';
    if (r.crisis) return helpCard(false);
    if (r.soft) out += helpCard(true);
    if (!state.query.trim() && !state.mood) return out;
    if (!r.list.length) return out + '<p class="empty">' + esc(t().none) + '</p>';
    if (r.mood) out += moodBox(r.mood);
    out += '<p class="sub">' + r.list.length + ' ' + esc(t().results) + '</p>';
    out += r.list.slice(0, state.shown).map(function (v) { return guideCard(v); }).join('');
    if (r.list.length > state.shown) out += '<button class="btn" id="more">' + esc(t().more) + '</button>';
    return out;
  }

  function viewRead() {
    if (state.chapter) {
      var vs = VERSES.filter(function (v) { return v.chapter === state.chapter; });
      var name = L(CHAPTERS[state.chapter - 1]);
      return '<button class="btn back" id="back">' + esc(t().back) + '</button><header><div class="brand">' + esc(t().chapter) + ' ' + state.chapter + '</div><h1>' + esc(name) + '</h1><p class="sub">' + vs.length + ' ' + esc(t().verses) + '</p></header>' +
        '<div><h2>' + esc(t().jump) + '</h2><div style="height:8px"></div><div class="jump">' + vs.map(function (v) { return '<button data-jump="' + v.chapter + '-' + v.verse + '">' + v.verse + '</button>'; }).join('') + '</div></div>' +
        vs.map(function (v) { return verseCard(v, { read: true }); }).join('');
    }
    return '<header><h1>' + esc(t().readTitle) + '</h1></header><div class="chapters">' + CHAPTERS.map(function (c, i) {
      var n = i + 1, ok = !!AVAILABLE[n];
      return '<button class="chapter" ' + (ok ? 'data-chapter="' + n + '"' : 'disabled') + '><b>' + esc(t().chapter) + ' ' + n + '</b><span>' + esc(L(c)) + '</span>' + (ok ? '' : '<span class="note">' + esc(t().soon) + '</span>') + '</button>';
    }).join('') + '</div>';
  }

  function viewSettings() {
    var native = !!cap('LocalNotifications');
    return '<header><h1>' + esc(t().settings) + '</h1></header>' +
      '<section class="card"><div class="row"><label for="lang">' + esc(t().language) + '</label><select id="lang" style="width:auto"><option value="hi"' + (state.lang === 'hi' ? ' selected' : '') + '>हिन्दी</option><option value="en"' + (state.lang === 'en' ? ' selected' : '') + '>English</option></select></div></section>' +
      '<section class="card"><div class="row"><span id="nl">' + esc(t().notif) + '</span><button class="switch" id="notif" role="switch" aria-labelledby="nl" aria-checked="' + state.notif + '"></button></div>' +
      '<div class="row"><label for="time">' + esc(t().time) + '</label><input id="time" type="time" value="' + esc(state.time) + '" style="width:auto"></div>' +
      '<p class="note" id="notifNote">' + esc(native ? t().notifOn : t().notifWeb) + '</p></section>' +
      '<p class="note">' + esc(t().about) + '</p><p class="note">' + esc(t().draft) + '</p>';
  }

  /* ---------- render ---------- */
  var ICONS = ['☀', '🔍', '📖', '⚙'];
  var KEYS = ['today', 'search', 'read', 'settings'];
  function renderTabs() {
    $tabs.innerHTML = KEYS.map(function (k, i) {
      return '<button class="tab" data-tab="' + k + '"' + (state.tab === k ? ' aria-current="page"' : '') + '><span class="ic" aria-hidden="true">' + ICONS[i] + '</span><span>' + esc(t().tabs[i]) + '</span></button>';
    }).join('');
  }
  function render(keepScroll) {
    document.documentElement.lang = state.lang;
    var y = window.scrollY;
    $view.innerHTML = state.tab === 'today' ? viewToday() : state.tab === 'search' ? viewSearch() : state.tab === 'read' ? viewRead() : viewSettings();
    renderTabs();
    window.scrollTo(0, keepScroll ? y : 0);
  }
  function refreshResults() {
    var box = document.getElementById('results');
    if (box) box.innerHTML = resultsHtml(search(state.query, state.mood));
  }
  function go(tab) { state.tab = tab; render(); }

  /* ---------- sharing ---------- */
  function shareVerse(id, isGuide) {
    var v = isGuide ? GUIDE.filter(function (x) { return x.id === id; })[0] : VERSES.filter(function (x) { return x.id === id; })[0]; if (!v) return;
    var text = isGuide ? GL(v, 'h') + '\n\n' + v.sanskrit + '\n\n' + GL(v, 's') + '\n\n— '
      : v.sanskrit + '\n\n' + meaning(v, true) + '\n\n— ' + (state.lang === 'hi' ? 'भगवद्गीता ' : 'Bhagavad Gita ') + v.id + '\nDaily Dose of Gita';
    var sh = cap('Share');
    if (sh && sh.share) { sh.share({ text: text }).catch(function () {}); return; }
    if (navigator.share) { navigator.share({ text: text }).catch(function () {}); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast(t().copied); }, function () {});
  }

  /* ---------- notifications ---------- */
  function scheduleNotifications() {
    var LN = cap('LocalNotifications');
    if (!LN) return Promise.resolve('web');
    return LN.requestPermissions().then(function (p) {
      if (p.display !== 'granted') return 'denied';
      return LN.createChannel({ id: 'daily', name: 'Daily shloka', importance: 4 }).catch(function () {})
        .then(function () { return LN.getPending(); })
        .then(function (pend) { return pend.notifications.length ? LN.cancel({ notifications: pend.notifications }) : null; })
        .then(function () {
          var hm = state.time.split(':'), now = new Date(), list = [];
          for (var i = 0; i < 30; i++) {
            var at = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i, +hm[0], +hm[1], 0);
            if (at <= now) continue;
            var v = dailyFor(at);
            list.push({
              id: dayNum(at), channelId: 'daily',
              title: (state.lang === 'hi' ? 'आज का श्लोक · गीता ' : 'Shloka of the day · Gita ') + v.id,
              body: GL(v, 'h'),
              schedule: { at: at, allowWhileIdle: true }
            });
          }
          return list.length ? LN.schedule({ notifications: list }) : null;
        }).then(function () { return 'ok'; });
    }).catch(function () { return 'denied'; });
  }
  function cancelNotifications() {
    var LN = cap('LocalNotifications'); if (!LN) return;
    LN.getPending().then(function (p) { if (p.notifications.length) LN.cancel({ notifications: p.notifications }); }).catch(function () {});
  }

  /* ---------- events ---------- */
  document.addEventListener('click', function (e) {
    var el;
    if ((el = e.target.closest('[data-tab]'))) return go(el.dataset.tab);
    if ((el = e.target.closest('[data-share]'))) return shareVerse(el.dataset.share);
    if ((el = e.target.closest('[data-shareg]'))) return shareVerse(el.dataset.shareg, true);
    if ((el = e.target.closest('[data-chapter]'))) { state.chapter = +el.dataset.chapter; return render(); }
    if (e.target.closest('#back')) { state.chapter = null; return render(); }
    if ((el = e.target.closest('[data-jump]'))) { var tgt = document.getElementById('v-' + el.dataset.jump); if (tgt) tgt.scrollIntoView({ behavior: 'smooth', block: 'start' }); return; }
    if ((el = e.target.closest('[data-mood]'))) {
      var m = el.dataset.mood;
      state.mood = (state.tab === 'search' && state.mood === m) ? null : m;
      state.shown = 10; state.tab = 'search'; render(); return;
    }
    if (e.target.closest('#more')) { state.shown += 10; refreshResults(); return; }
    if (e.target.closest('#notif')) {
      state.notif = !state.notif; store('notif', state.notif ? '1' : '0');
      var sw = document.getElementById('notif'); sw.setAttribute('aria-checked', state.notif);
      var note = document.getElementById('notifNote');
      if (state.notif) {
        scheduleNotifications().then(function (r) {
          if (r === 'denied') { state.notif = false; store('notif', '0'); sw.setAttribute('aria-checked', 'false'); }
          note.textContent = r === 'denied' ? t().notifDenied : r === 'web' ? t().notifWeb : t().notifOn;
        });
      } else cancelNotifications();
    }
  });
  document.addEventListener('input', function (e) {
    if (e.target.id === 'q') { state.query = e.target.value; state.mood = null; state.shown = 10; refreshResults(); var chips = document.querySelectorAll('.chip'); chips.forEach(function (c) { c.setAttribute('aria-pressed', 'false'); }); }
  });
  document.addEventListener('change', function (e) {
    if (e.target.id === 'lang') { state.lang = e.target.value; store('lang', state.lang); render(true); if (state.notif) scheduleNotifications(); }
    if (e.target.id === 'time') { state.time = e.target.value || '07:00'; store('time', state.time); if (state.notif) scheduleNotifications(); }
  });

  render();
  if (state.notif) scheduleNotifications();
})();
