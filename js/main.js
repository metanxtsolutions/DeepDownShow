/* Deep Down Show বাংলা — site script */
(() => {
  'use strict';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  // EMBED=false (set by the published build) opens videos on YouTube instead of an in-page iframe.
  const EMBED = window.DDS_EMBED !== false && document.documentElement.dataset.embed !== 'off';
  const THUMBS = window.DDS_THUMBS || {};

  /* ---------------- data ---------------- */
  const EPISODES = [
    { id: 'upYFnCkCqxQ', ep: 25, cat: 'society',  dur: '1:41:06', date: '2026-09-05', views: 114,  guest: 'Karimul Haque · Padma Shri', feature: true,
      title: 'The real Bike Ambulance Dada: saving lives, the Padma Shri, and a biopic by Dev' },
    { id: '1q3-XnlWuQo', ep: 24, cat: 'society',  dur: '1:05:10', date: '2026-07-04', views: 3157, guest: 'Nandini Bhattacharjee',
      title: 'Men’s rights, marriage cases, and the precautions to take before marriage' },
    { id: 'ucUoXDrRDA0', ep: 23, cat: 'society',  dur: '1:23:25', date: '2026-02-13', views: 411,  guest: 'Gourav Banerjee',
      title: 'Safety, self-defence and martial arts for everyone' },
    { id: '7yLfZnfdTMI', ep: 22, cat: 'society',  dur: '1:10:05', date: '2025-11-22', views: 9312, guest: 'Dr. Prabir Basu',
      title: 'Sex, plainly: men’s real-life issues, unhealthy practices and their solutions' },
    { id: 'mK3A4GY-ICk', ep: 21, cat: 'business', dur: '2:11:42', date: '2025-07-26', views: 589,  guest: 'Aarijit Hajra',
      title: 'Think again: AI, business, the education system and life' },
    { id: 'u-z1QQj3Bg4', ep: 20, cat: 'arts',     dur: '1:26:14', date: '2025-01-18', views: 4089, guest: 'Satadeep Saha',
      title: 'Why Khadaan, Pushpa 2 and Marco became blockbusters: inside film distribution' },
    { id: 'XNLdEr0XCUI', ep: 19, cat: 'business', dur: '36:15',   date: '2024-12-27', views: 2948, guest: 'Debaditya Chaudhury',
      title: 'Building Chowman, Oudh 1590 and Chapter 2, with a rock band on the side' },
    { id: '6LQaILniQZE', ep: 18, cat: 'business', dur: '1:16:22', date: '2024-11-09', views: 801,  guest: 'Manab Paul',
      title: 'The opportunity in Bengal’s real estate business' },
    { id: 'ZdMiBhwYMnE', ep: 17, cat: 'business', dur: '1:11:08', date: '2024-06-29', views: 441,  guest: 'Pallab Ghosh',
      title: 'Gappu: Bengal’s original musical instrument manufacturer' },
    { id: 'UafYhxJs_oI', ep: 16, cat: 'science',  dur: '1:35:13', date: '2024-04-27', views: 428,  guest: 'Abhishek Mitra',
      title: 'Cyber attacks, cyber security, startups, love and relationships' },
    { id: 'So5XtutB0rg', ep: 15, cat: 'arts',     dur: '1:44:40', date: '2023-11-26', views: 381,  guest: 'The Wizard SD',
      title: 'The science behind magic and supernatural activities' },
    { id: 'Y0tZDrQiK_8', ep: 14, cat: 'arts',     dur: '1:18:23', date: '2023-10-13', views: 757,  guest: 'The makers of Kalkokkho',
      title: 'Kalkokkho (House of Time): can a low-budget film win awards?' },
    { id: '0sqCgdt6hFA', ep: 13, cat: 'culture',  dur: '1:31:51', date: '2023-09-22', views: 465,  guest: 'Dr. Janardan Ghosh',
      title: 'The controversial areas of the Ramayan' },
    { id: 'tjk4qyeQTHc', ep: 12, cat: 'business', dur: '51:37',   date: '2023-08-14', views: 238,  guest: 'Deep Das',
      title: 'Rags to riches: five profitable ventures in six years' },
    { id: 'RyCDGQM4KsI', ep: 11, cat: 'business', dur: '1:19:29', date: '2023-07-28', views: 605,  guest: 'A commercial photographer',
      title: 'Brand building, commercial photography and family culture' },
    { id: 'LbH8PHxQ6Xw', ep: 10, cat: 'culture',  dur: '1:12:37', date: '2023-06-24', views: 518,  guest: 'Akash · Ravanayan',
      title: 'Is Ravan actually a hero? Different theories of the Ramayan' },
    { id: 'DiO0yYtr9ks', ep: 9,  cat: 'science',  dur: '42:15',   date: '2023-06-09', views: 328,  guest: 'A 3D-printing engineer',
      title: 'Is organ printing really possible? 3D printing technology, explained' },
    { id: 'JBx0MaRqktU', ep: 8,  cat: 'business', dur: '56:36',   date: '2023-06-03', views: 341,  guest: 'Shyamacharan Nursery',
      title: 'Does corporate experience help you run a business? A century-old nursery answers' },
    { id: '48lg-J2KBkU', ep: 7,  cat: 'business', dur: '54:09',   date: '2023-05-26', views: 1118, guest: 'Subhashis Dutt',
      title: 'Why Bengalis don’t do business: India’s first umbrella manufacturer' },
    { id: 'tYZWrmmfzcU', ep: 6,  cat: 'business', dur: '1:06:14', date: '2023-04-30', views: 604,  guest: 'The founder of Adda Khana', parts: 2,
      title: 'How a backbencher built Durgapur’s best tea shop, and whether you should open one' },
    { id: '4PoAPRZfBqE', ep: 5,  cat: 'business', dur: '50:58',   date: '2023-04-18', views: 817,  guest: 'Avelo Roy · Kolkata Ventures',
      title: 'Startups, spirituality and a lot more' },
    { id: 'zFJdoy5IPWY', ep: 4,  cat: 'business', dur: '1:01:47', date: '2023-04-07', views: 332,  guest: 'Ayon Das · Izifiso', parts: 2,
      title: 'Building a backpackers’ camp on Mousuni Island, and whether startups need funding' },
    { id: 'E4som7uyDZ0', ep: 3,  cat: 'arts',     dur: '41:46',   date: '2023-02-21', views: 451,  guest: 'Rupsha Saha',
      title: 'How to become a poet, and the three best Bangla books' },
    { id: 'mzqnaha8kLc', ep: 2,  cat: 'culture',  dur: '56:28',   date: '2021-12-11', views: 548,  guest: 'Dr. Janardan Ghosh', parts: 2,
      title: 'How to find your passion, and whether to be spiritual or religious' },
    { id: 'Kx0rjhoGefM', ep: 1,  cat: 'arts',     dur: '54:48',   date: '2021-04-30', views: 978,  guest: 'Kheyali Paul Mukherjee · Nritricks',
      title: 'What is love? A dancer answers, in the first ever episode' },
  ];

  const SHORTS = [
    { id: 'F7wu1XiWPqo', views: '1.3K', title: 'Best time to have sex to fight infertility?' },
    { id: 'uv1lF5etGr8', views: '1.2K', title: '“আমার টা different!” Pre-cautions before marriage' },
    { id: '5RNLMJeFcLI', views: '1K',   title: 'Why was Viagra actually invented?' },
    { id: 'Q4MckiLfEQw', views: '794',  title: 'Stop being so afraid of the police and lawyers' },
    { id: 'QMqF_Me6vn8', views: '430',  title: 'When women won’t take the husband’s surname' },
    { id: '9ZuPujbJ6l0', views: '343',  title: 'Why is there no Men’s Commission?' },
  ];

  const CLIPS = [
    { id: '4cFJIUzgpaA', dur: '13:00', title: 'Masturbation: right or wrong? A urologist answers' },
    { id: 'U3nD2b1LAXg', dur: '7:45',  title: 'How parenting should be' },
    { id: 'pUH1jYwq5ZU', dur: '14:20', title: 'Did Shri Ram do injustice to Maa Sita?' },
  ];

  const GUESTS = [
    { name: 'Karimul Haque', role: 'Padma Shri. The Bike Ambulance Dada of Jalpaiguri', ep: 25, quote: 'মরলে জাতের বিচার হবে না, আত্মার বিচার হবে।' },
    { name: 'Dr. Prabir Basu', role: 'Urologist, andrologist and uro-oncologist, Kolkata', ep: 22, quote: '“Sex education should start from home.”', en: true },
    { name: 'Nandini Bhattacharjee', role: 'Men’s rights activist. President, All Bengal Men’s Forum', ep: 24, quote: 'পুরুষদের আগে নিজেদের মূল্য বুঝতে হবে।' },
    { name: 'Dr. Janardan Ghosh', role: 'Theatre practitioner and scholar of the Ramayan’s many retellings', ep: 13, quote: '“The villain of the story is often the good one.”', en: true },
    { name: 'Debaditya Chaudhury', role: 'Founder of Chowman, Oudh 1590 and Chapter 2. Lakkhichhara', ep: 19, quote: '“Restaurants by day, a rock band by night.”', en: true },
    { name: 'Aarijit Hajra', role: 'Entrepreneur. On AI, business and the Bengali mind', ep: 21, quote: '“Your parents cannot be your good mentor.”', en: true },
    { name: 'Satadeep Saha', role: 'Film distributor. On why some films break out', ep: 20, quote: '“Distribution decides the blockbuster.”', en: true },
    { name: 'Gourav Banerjee', role: 'Founder, Rezilienz Empowerment. Self-defence for all', ep: 23, quote: 'ছেলে বা মেয়ে — সবারই safety need আছে।' },
    { name: 'Subhashis Dutt', role: 'India’s first umbrella manufacturing company', ep: 7, quote: '“Bengalis can do business. They just stopped.”', en: true },
    { name: 'Avelo Roy', role: 'Kolkata Ventures. Startups and spirituality', ep: 5, quote: '“Build the founder before the company.”', en: true },
    { name: 'Kheyali Paul Mukherjee', role: 'Founder, Nritricks Dance. The very first guest', ep: 1, quote: '“What is love? Ask a dancer.”', en: true },
  ];

  const CAT_LABEL = { business: 'Business', society: 'Society & Health', culture: 'Culture', arts: 'Arts & Cinema', science: 'Science & Tech' };
  const thumb = id => THUMBS[id] || `thumbs/${id}.jpg`;
  const thumbFallback = id => `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
  const thumbVertical = id => THUMBS[id + '_v'] || `thumbs/${id}_v.jpg`;
  const onloadFix = (id, fb) => THUMBS[id] ? '' : ` onerror="this.onerror=null;this.src='${fb}'"`;
  const embed = id => `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1`;
  const watch = id => `https://www.youtube.com/watch?v=${id}`;
  const fmtDate = iso => new Date(iso).toLocaleDateString('en-GB', { month: 'short', year: 'numeric' });
  const fmtViews = n => n >= 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K' : String(n);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

  // Swap in bundled thumbnails for images marked data-thumb (hero poster).
  $$('img[data-thumb]').forEach(img => { const id = img.dataset.thumb; if (THUMBS[id]) img.src = THUMBS[id]; else img.onerror = () => { img.onerror = null; img.src = thumbFallback(id); }; });

  /* ---------------- episode grid ---------------- */
  const grid = $('#clipGrid');
  const countAll = $('#countAll');
  if (countAll) countAll.textContent = EPISODES.length;

  function epCard(c, i) {
    const feature = c.feature ? ' clip--feature' : '';
    const parts = c.parts ? ` · ${c.parts} parts` : '';
    return `
      <button class="clip${feature}" type="button" data-id="${c.id}" data-title="${esc(c.title)}" data-kicker="Episode ${c.ep} · ${esc(c.guest)}" style="animation-delay:${Math.min(i, 8) * 55}ms">
        <div class="clip__thumb">
          <img src="${thumb(c.id)}" alt="" loading="lazy"${onloadFix(c.id, thumbFallback(c.id))}>
          <span class="clip__dur">${c.dur}</span>
          <span class="clip__play" aria-hidden="true"><svg viewBox="0 0 24 24" width="18" height="18"><path d="M8 5.5v13l11-6.5-11-6.5Z" fill="currentColor"/></svg></span>
        </div>
        <div class="clip__body">
          <div class="clip__tags"><span class="ep">DDS ${c.ep}</span><span>${CAT_LABEL[c.cat]}</span></div>
          <h3 class="clip__title">${esc(c.title)}</h3>
          <div class="clip__meta"><span>Ft. ${esc(c.guest)}${parts}</span><time datetime="${c.date}">${fmtDate(c.date)} · ${fmtViews(c.views)} views</time></div>
        </div>
      </button>`;
  }

  function renderEpisodes(filter = 'all') {
    if (!grid) return;
    const list = EPISODES.filter(c => filter === 'all' || c.cat === filter);
    grid.innerHTML = list.map(epCard).join('') || '<p class="section__lede">No episodes in this theme yet.</p>';
    // Fill the last row: a feature card takes 4 cells. One orphan spans the row, two share it.
    const cards = $$('.clip', grid);
    const cells = cards.reduce((n, c) => n + (c.classList.contains('clip--feature') ? 4 : 1), 0);
    const last = cards[cards.length - 1];
    if (last && !last.classList.contains('clip--feature')) {
      if (cells % 3 === 1) last.classList.add('clip--full');
      if (cells % 3 === 2) last.classList.add('clip--wide');
    }
  }
  renderEpisodes();

  const filters = $('#filters');
  function setFilter(f, scroll = false) {
    $$('.chip', filters).forEach(ch => {
      const on = ch.dataset.filter === f;
      ch.classList.toggle('is-active', on);
      ch.setAttribute('aria-selected', on);
    });
    renderEpisodes(f);
    if (scroll) $('#episodes').scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
  }
  filters?.addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (chip) setFilter(chip.dataset.filter);
  });
  $$('[data-jump]').forEach(b => b.addEventListener('click', () => setFilter(b.dataset.jump, true)));

  /* ---------------- shorts rail ---------------- */
  const shortsRail = $('#shortsRail');
  if (shortsRail) {
    shortsRail.innerHTML = SHORTS.map(s => `
      <button class="short" type="button" data-id="${s.id}" data-title="${esc(s.title)}" data-kicker="Short · Deep Down Show" data-vertical="1">
        <img src="${thumbVertical(s.id)}" alt="" loading="lazy"${onloadFix(s.id + '_v', thumbFallback(s.id))}>
        <span class="short__ov" aria-hidden="true"></span>
        <span class="short__play" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16"><path d="M8 5.5v13l11-6.5-11-6.5Z" fill="currentColor"/></svg></span>
        <span class="short__body"><span class="short__title">${esc(s.title)}</span><span class="short__views">${s.views} views</span></span>
      </button>`).join('');
  }

  /* ---------------- clips stack ---------------- */
  const stack = $('#clipStack');
  if (stack) {
    stack.innerHTML = CLIPS.map((c, i) => `
      <a class="stackcard" href="${watch(c.id)}" target="_blank" rel="noopener" style="--i:${i}">
        <img src="${thumb(c.id)}" alt="" loading="lazy"${onloadFix(c.id, thumbFallback(c.id))}>
        <span class="stackcard__body"><span class="stackcard__dur">${c.dur}</span><span class="stackcard__title">${esc(c.title)}</span></span>
      </a>`).join('');
  }

  /* ---------------- guests ---------------- */
  const guestRail = $('#guestRail');
  if (guestRail) {
    guestRail.innerHTML = GUESTS.map((g, i) => {
      const initials = g.name.replace(/^Dr\.\s*/, '').split(/\s+/).map(w => w[0]).slice(0, 2).join('');
      return `
      <article class="guest">
        <div class="guest__top">
          <div class="guest__mono" style="--a:${i * 37}deg"><span>${initials}</span></div>
          <span class="guest__ep">Episode ${g.ep}</span>
        </div>
        <div>
          <h3 class="guest__name">${esc(g.name)}</h3>
          <p class="guest__role">${esc(g.role)}</p>
        </div>
        <p class="guest__quote${g.en ? ' en' : ''}">${esc(g.quote)}</p>
      </article>`;
    }).join('');
  }

  /* ---------------- rails nav ---------------- */
  $$('.rail__btn').forEach(b => b.addEventListener('click', () => {
    const rail = document.getElementById(b.dataset.rail);
    rail?.scrollBy({ left: Number(b.dataset.dir) * rail.clientWidth * .7, behavior: reduced ? 'auto' : 'smooth' });
  }));

  /* ---------------- video opening ---------------- */
  const modal = $('#modal');
  const modalVideo = $('#modalVideo');
  let lastFocus = null;

  function makeIframe(id, title) {
    const iframe = document.createElement('iframe');
    iframe.src = embed(id);
    iframe.title = title;
    iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    iframe.allowFullscreen = true;
    return iframe;
  }
  function openVideo(id, title, kicker, vertical) {
    if (!EMBED) { window.open(watch(id), '_blank', 'noopener'); return; }
    lastFocus = document.activeElement;
    $('#modalTitle').textContent = title;
    $('#modalKicker').textContent = kicker;
    $('#modalLink').href = watch(id);
    modalVideo.style.aspectRatio = vertical ? '9 / 16' : '16 / 9';
    modalVideo.style.maxHeight = vertical ? '78vh' : '';
    modalVideo.style.marginInline = vertical ? 'auto' : '';
    modalVideo.replaceChildren(makeIframe(id, title));
    modal.hidden = false;
    document.body.classList.add('modal-open');
    $('.modal__close').focus();
  }
  function closeModal() {
    modal.hidden = true;
    modalVideo.replaceChildren();
    document.body.classList.remove('modal-open');
    lastFocus?.focus?.();
  }
  document.addEventListener('click', e => {
    const card = e.target.closest('.clip, .short');
    if (card) openVideo(card.dataset.id, card.dataset.title, card.dataset.kicker, !!card.dataset.vertical);
    if (e.target.closest('[data-close]')) closeModal();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !modal.hidden) closeModal();
    if (e.key === 'Tab' && !modal.hidden) {
      const f = $$('button, a, iframe', modal).filter(el => !el.hidden);
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    }
  });

  const featured = $('#featuredPlayer');
  featured?.querySelector('.player__play')?.addEventListener('click', () => {
    if (!EMBED) { window.open(watch(featured.dataset.id), '_blank', 'noopener'); return; }
    featured.querySelector('.player__frame').replaceChildren(makeIframe(featured.dataset.id, featured.dataset.title));
  });

  /* ---------------- nav ---------------- */
  const nav = $('#nav');
  const progress = $('#progressBar');
  function onScroll() {
    const y = window.scrollY;
    nav.classList.toggle('is-scrolled', y > 24);
    const max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.width = (max > 0 ? (y / max) * 100 : 0) + '%';
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  const burger = $('#burger');
  const mobileMenu = $('#mobileMenu');
  burger?.addEventListener('click', () => {
    const open = burger.getAttribute('aria-expanded') !== 'true';
    burger.setAttribute('aria-expanded', open);
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    mobileMenu.classList.toggle('is-open', open);
  });
  mobileMenu?.addEventListener('click', e => {
    if (e.target.tagName === 'A') { burger.setAttribute('aria-expanded', 'false'); mobileMenu.classList.remove('is-open'); }
  });

  /* ---------------- theme ---------------- */
  const root = document.documentElement;
  const toggle = $('#themeToggle');
  const systemLight = matchMedia('(prefers-color-scheme: light)');
  const currentTheme = () => root.getAttribute('data-theme') || (systemLight.matches ? 'light' : 'dark');
  function syncToggle() {
    const next = currentTheme() === 'light' ? 'dark' : 'light';
    toggle?.setAttribute('aria-label', `Switch to ${next} theme`);
    $('meta[name="theme-color"]')?.setAttribute('content', currentTheme() === 'light' ? '#F5EEDC' : '#090E22');
  }
  toggle?.addEventListener('click', () => {
    const next = currentTheme() === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', next);
    try { localStorage.setItem('dds-theme', next); } catch (_) {}
    syncToggle();
  });
  systemLight.addEventListener?.('change', syncToggle);
  syncToggle();

  /* ---------------- reveal on scroll ---------------- */
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  $$('.reveal').forEach(el => io.observe(el));

  /* ---------------- count-up stats ---------------- */
  const statIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const el = en.target; statIO.unobserve(el);
      const target = Number(el.dataset.count), prefix = el.dataset.prefix || '', suffix = el.dataset.suffix || '';
      if (reduced || el.dataset.raw) { el.textContent = prefix + target + suffix; return; }
      const start = performance.now(), dur = 1400;
      const tick = now => {
        const p = Math.min(1, (now - start) / dur), e = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + Math.round(target * e) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: .6 });
  $$('.stat strong').forEach(el => statIO.observe(el));

  /* ---------------- ticker: duplicate for seamless loop ---------------- */
  const ticker = $('#ticker');
  if (ticker) ticker.innerHTML += ticker.innerHTML;

  /* ---------------- hero glow follows pointer ---------------- */
  const hero = $('#hero'), glow = $('#heroGlow');
  if (hero && glow && matchMedia('(pointer: fine)').matches && !reduced) {
    hero.addEventListener('pointermove', e => {
      const r = hero.getBoundingClientRect();
      glow.style.transform = `translate(${e.clientX - r.left - 320}px, ${e.clientY - r.top - 320}px)`;
      glow.style.opacity = '1';
    });
    hero.addEventListener('pointerleave', () => { glow.style.opacity = '0'; });
  }

  if (reduced) $$('animateTransform').forEach(a => a.remove());

  const y = $('#year'); if (y) y.textContent = new Date().getFullYear();
})();
