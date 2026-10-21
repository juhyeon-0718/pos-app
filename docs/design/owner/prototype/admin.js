/* U-01 프로토타입 공용 스크립트. 더미 데이터만 사용한다(D-28). 모든 문자열은 textContent로만 넣는다(D-24). */
(function () {
  const SVG_NS = 'http://www.w3.org/2000/svg';
  const ICONS = {
    check: 'M5 12l5 5L20 7',
    x: 'M6 6l12 12M18 6L6 18',
    plus: 'M12 5v14M5 12h14',
    ban: 'M12 3a9 9 0 100 18 9 9 0 000-18zM5.6 5.6l12.8 12.8',
    warn: 'M12 3L2 21h20L12 3zM12 10v5M12 18v.01',
    info: 'M12 3a9 9 0 100 18 9 9 0 000-18zM12 11v6M12 7v.01',
    spinner: 'M12 3a9 9 0 019 9'
  };

  function icon(name) {
    const s = document.createElementNS(SVG_NS, 'svg');
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('class', 'icon' + (name === 'spinner' ? ' spin' : ''));
    s.setAttribute('aria-hidden', 'true');
    const p = document.createElementNS(SVG_NS, 'path');
    p.setAttribute('d', ICONS[name]);
    s.appendChild(p);
    return s;
  }

  function h(tag, attrs, ...kids) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === 'class') e.className = v;
      else if (k === 'text') e.textContent = v;
      else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
      else if (v === true) e.setAttribute(k, '');
      else e.setAttribute(k, v);
    }
    for (const c of kids.flat()) {
      if (c == null || c === false) continue;
      e.append(c.nodeType ? c : document.createTextNode(String(c)));
    }
    return e;
  }

  const won = (n) => Number(n).toLocaleString('ko-KR') + '원';
  const num = (n) => Number(n).toLocaleString('ko-KR', { maximumFractionDigits: 3 });

  /* 공용 상단 바 */
  function appBar(current) {
    const link = (href, label, key) => h('a', { href, 'aria-current': current === key ? 'page' : null, text: label });
    return h('header', { class: 'app-bar' },
      h('div', { class: 'app-bar-inner' },
        h('img', { class: 'app-logo', src: '../../brand/logo-compact-black.png', alt: '75MHz LIVE PUB' }),
        h('span', { class: 'app-title', text: '사장 관리' }),
        h('nav', { class: 'nav', 'aria-label': '관리 메뉴' },
          link('menus.html', '메뉴 관리', 'menus'),
          link('ingredients.html', '식재료 관리', 'ingredients'))));
  }

  /* 프로토타입 전용: 상태 전환 바 */
  function stateBar(groups, current, onPick) {
    const bar = h('div', { class: 'proto-bar', role: 'region', 'aria-label': '프로토타입 상태 보기' });
    const inner = h('div', { class: 'proto-bar-inner' });
    groups.forEach((g) => {
      const wrap = h('div', { class: 'proto-group' }, h('span', { class: 'proto-label', text: g.label }));
      g.items.forEach((it) => {
        wrap.append(h('button', {
          type: 'button',
          'aria-pressed': String(current === it.key),
          onclick: () => onPick(it.key),
          text: it.label
        }));
      });
      inner.append(wrap);
    });
    bar.append(inner);
    return bar;
  }

  /* 모달: 포커스 가두기, Esc 닫기(처리 중에는 막음), 닫힌 뒤 원래 버튼으로 포커스 복귀 */
  let lastFocus = null;
  let escHandler = null;
  function closeModal(keepFocus) {
    const ov = document.getElementById('overlay');
    if (ov) ov.remove();
    if (escHandler) { document.removeEventListener('keydown', escHandler); escHandler = null; }
    if (!keepFocus && lastFocus && document.contains(lastFocus)) lastFocus.focus();
  }
  function openModal(opts) {
    // opts: { title, body: [nodes], footer: [nodes], alert: bool, busy: bool, onClose }
    const reopen = !!document.getElementById('overlay');
    if (!reopen) lastFocus = document.activeElement;
    closeModal(true);
    const dlg = h('div', {
      class: 'modal', role: opts.alert ? 'alertdialog' : 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'modal-title'
    },
      h('h2', { id: 'modal-title', class: 'modal-title', text: opts.title }),
      h('div', { class: 'modal-body' }, opts.body),
      h('div', { class: 'modal-footer' }, opts.footer));
    const ov = h('div', { id: 'overlay', class: 'overlay' }, dlg);
    document.body.append(ov);
    const focusables = () => Array.from(dlg.querySelectorAll('button, input, select, textarea, a[href]')).filter((e) => !e.disabled);
    escHandler = (ev) => {
      if (ev.key === 'Escape' && !opts.busy && opts.onClose) { ev.preventDefault(); opts.onClose(); }
      if (ev.key === 'Tab') {
        const f = focusables();
        if (!f.length) { ev.preventDefault(); return; }
        const first = f[0], last = f[f.length - 1];
        if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
        else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', escHandler);
    const target = dlg.querySelector('[data-autofocus]') || focusables()[0] || dlg;
    if (target === dlg) dlg.setAttribute('tabindex', '-1');
    target.focus();
  }

  /* 토스트: 성공 안내 전용. 오류는 배너로 화면에 남긴다. */
  function toast(message) {
    let area = document.getElementById('toast-area');
    if (!area) {
      area = h('div', { id: 'toast-area', class: 'toast-area', role: 'status', 'aria-live': 'polite' });
      document.body.append(area);
    }
    const t = h('div', { class: 'toast' }, icon('check'), h('span', { text: message }));
    area.append(t);
    setTimeout(() => t.remove(), 4000);
  }

  function banner(kind, title, text, action) {
    const ic = kind === 'info' ? 'info' : 'warn';
    return h('div', { class: 'banner banner-' + kind, role: kind === 'error' ? 'alert' : 'status' },
      icon(ic),
      h('div', { class: 'banner-body' },
        title ? h('div', { class: 'banner-title', text: title }) : null,
        text ? h('div', { text }) : null),
      action || null);
  }

  function btn(label, kind, onclick, extra) {
    return h('button', Object.assign({ type: 'button', class: 'btn btn-' + kind, onclick }, extra || {}), label);
  }

  function activeBadge(isActive, onText, offText) {
    return isActive
      ? h('span', { class: 'badge badge-active' }, icon('check'), onText)
      : h('span', { class: 'badge badge-inactive' }, icon('ban'), offText);
  }

  function skeletonCells(n) {
    const cells = [];
    for (let i = 0; i < n; i++) cells.push(h('td', null, h('span', { class: 'skeleton', style: 'width:' + (50 + ((i * 17) % 40)) + '%' })));
    return cells;
  }

  function stateFromHash(def) {
    const q = new URLSearchParams(location.search).get('state');
    return q || def;
  }

  window.Admin = { icon, h, won, num, appBar, stateBar, openModal, closeModal, toast, banner, btn, activeBadge, skeletonCells, stateFromHash };
})();
