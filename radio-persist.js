/**
 * Persistent live radio across soft navigations (language + same-origin pages).
 * The <audio id="liveRadioPlayer"> element must sit outside #site-root.
 */
(function () {
  'use strict';

  var LIVE_RADIO_URL = 'https://radio.owonamedia.de/radio.mp3';
  var STORAGE_KEY = 'salomonRadioPlaying';

  var LABELS = {
    sw: {
      idle: 'Salomon Radio',
      live: 'Salomon Radio · Live',
      err: 'Stream haipatikani — jaribu tena baadaye'
    },
    de: {
      idle: 'Salomon Radio',
      live: 'Salomon Radio · Live',
      err: 'Stream nicht verfügbar – bitte später erneut versuchen'
    },
    en: {
      idle: 'Salomon Radio',
      live: 'Salomon Radio · Live',
      err: 'Stream unavailable — please try again later'
    },
    fr: {
      idle: 'Salomon Radio',
      live: 'Salomon Radio · Live',
      err: 'Flux indisponible — réessayez plus tard'
    }
  };

  var livePlayer = null;
  var isLivePlaying = false;
  var navigating = false;
  var menuKeyHandler = null;

  function currentLang() {
    var lang = (document.documentElement.lang || 'sw').toLowerCase().slice(0, 2);
    return LABELS[lang] ? lang : 'sw';
  }

  function labels() {
    return LABELS[currentLang()];
  }

  function ensurePlayer() {
    livePlayer = document.getElementById('liveRadioPlayer');
    if (!livePlayer) {
      livePlayer = document.createElement('audio');
      livePlayer.id = 'liveRadioPlayer';
      livePlayer.preload = 'none';
      livePlayer.setAttribute('playsinline', '');
      livePlayer.style.display = 'none';
      document.body.insertBefore(livePlayer, document.body.firstChild);
    }
    if (!livePlayer.dataset.bound) {
      livePlayer.addEventListener('error', function () {
        isLivePlaying = false;
        try {
          sessionStorage.setItem(STORAGE_KEY, '0');
        } catch (e) { /* ignore */ }
        syncRadioUI(true);
      });
      livePlayer.addEventListener('pause', function () {
        if (!livePlayer.src) return;
        // User or soft-nav pause — UI sync only if intentionally stopped via toggle
      });
      livePlayer.dataset.bound = '1';
    }
    return livePlayer;
  }

  function syncRadioUI(showError) {
    var L = labels();
    var button = document.getElementById('playIcon');
    var title = document.getElementById('trackName');
    var playing = isLivePlaying && livePlayer && !livePlayer.paused;

    if (button) {
      button.textContent = playing ? '❚❚' : '▶';
      button.setAttribute('aria-pressed', playing ? 'true' : 'false');
      var label = playing ? button.dataset.labelPause : button.dataset.labelPlay;
      if (label) button.setAttribute('aria-label', label);
    }
    if (title) {
      if (showError) title.textContent = L.err;
      else title.textContent = playing ? L.live : L.idle;
    }
  }

  function setPlaying(playing) {
    isLivePlaying = playing;
    try {
      sessionStorage.setItem(STORAGE_KEY, playing ? '1' : '0');
    } catch (e) { /* ignore */ }
    syncRadioUI(false);
  }

  function toggleArchiveRadio() {
    ensurePlayer();
    var button = document.querySelector('.play-btn');
    if (button) {
      button.style.transform = 'scale(0.9)';
      setTimeout(function () {
        button.style.transform = 'scale(1)';
      }, 150);
    }

    if (isLivePlaying && livePlayer && !livePlayer.paused) {
      livePlayer.pause();
      livePlayer.removeAttribute('src');
      livePlayer.load();
      setPlaying(false);
      return;
    }

    livePlayer.src = LIVE_RADIO_URL;
    livePlayer.play().then(function () {
      setPlaying(true);
    }).catch(function () {
      setPlaying(false);
      syncRadioUI(true);
    });
  }

  function toggleMenu(forceClose) {
    var hamburger = document.getElementById('navToggle');
    var sidebarEl = document.getElementById('sidebar');
    var overlayEl = document.getElementById('overlay');
    if (!hamburger || !sidebarEl || !overlayEl) return;

    var open = forceClose === true ? false : !sidebarEl.classList.contains('active');
    hamburger.classList.toggle('active', open);
    sidebarEl.classList.toggle('active', open);
    overlayEl.classList.toggle('active', open);
    document.body.style.overflow = open ? 'hidden' : '';
    hamburger.setAttribute('aria-expanded', open ? 'true' : 'false');
    var label = open ? hamburger.dataset.labelClose : hamburger.dataset.labelOpen;
    if (label) hamburger.setAttribute('aria-label', label);
  }

  function bindMenu() {
    var navToggle = document.getElementById('navToggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('overlay');
    if (!navToggle || !sidebar || !overlay) return;

    navToggle.onclick = function () {
      toggleMenu();
    };
    overlay.onclick = function () {
      toggleMenu(true);
    };
    sidebar.querySelectorAll('.sidebar-nav a[href^="#"]').forEach(function (link) {
      link.addEventListener('click', function () {
        toggleMenu(true);
      });
    });

    if (menuKeyHandler) {
      document.removeEventListener('keydown', menuKeyHandler);
    }
    menuKeyHandler = function (e) {
      if (e.key === 'Escape' && sidebar.classList.contains('active')) {
        toggleMenu(true);
      }
    };
    document.addEventListener('keydown', menuKeyHandler);
  }

  function localeUrl(lang) {
    var isLocal =
      location.hostname === 'localhost' ||
      location.hostname === '127.0.0.1';
    if (isLocal) {
      return lang === 'sw' ? 'index.html' : lang + '.html';
    }
    return lang === 'sw' ? '/' : '/' + lang;
  }

  function shouldSoftNav(anchor) {
    if (!anchor || anchor.target === '_blank' || anchor.hasAttribute('download')) {
      return false;
    }
    var href = anchor.getAttribute('href');
    if (!href || href.startsWith('mailto:') || href.startsWith('tel:')) return false;
    if (href.startsWith('#')) return false;

    var url;
    try {
      url = new URL(anchor.href, location.href);
    } catch (e) {
      return false;
    }
    if (url.origin !== location.origin) return false;
    // Same-page hash only
    if (url.pathname === location.pathname && url.hash) return false;
    return true;
  }

  function softNavigate(url, replace) {
    if (navigating) return Promise.resolve();
    navigating = true;
    toggleMenu(true);

    return fetch(url, { credentials: 'same-origin', headers: { Accept: 'text/html' } })
      .then(function (res) {
        if (!res.ok) throw new Error('nav ' + res.status);
        return res.text();
      })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var nextRoot = doc.querySelector('#site-root');
        var curRoot = document.querySelector('#site-root');
        if (!nextRoot || !curRoot) {
          location.href = url;
          return;
        }

        var nextStyle = doc.querySelector('#page-style');
        var curStyle = document.querySelector('#page-style');
        if (nextStyle && curStyle) {
          curStyle.textContent = nextStyle.textContent;
        }

        document.documentElement.lang = doc.documentElement.lang || document.documentElement.lang;
        document.title = doc.title || document.title;

        var nextDesc = doc.querySelector('meta[name="description"]');
        var curDesc = document.querySelector('meta[name="description"]');
        if (nextDesc && curDesc) {
          curDesc.setAttribute('content', nextDesc.getAttribute('content') || '');
        }

        var nextCanon = doc.querySelector('link[rel="canonical"]');
        var curCanon = document.querySelector('link[rel="canonical"]');
        if (nextCanon && curCanon) {
          curCanon.setAttribute('href', nextCanon.getAttribute('href') || '');
        }

        curRoot.replaceWith(document.importNode(nextRoot, true));
        // Keep the live <audio> node — it lives outside #site-root

        if (replace) {
          history.replaceState({ soft: true }, '', url);
        } else {
          history.pushState({ soft: true }, '', url);
        }

        bindMenu();
        ensurePlayer();
        syncRadioUI(false);
        window.scrollTo(0, 0);
      })
      .catch(function () {
        location.href = url;
      })
      .then(function () {
        navigating = false;
      });
  }

  function switchLanguage(lang) {
    softNavigate(localeUrl(lang), false);
  }

  function onDocumentClick(e) {
    var anchor = e.target.closest && e.target.closest('a[href]');
    if (!anchor || !shouldSoftNav(anchor)) return;
    // Language buttons are <button>, not links
    e.preventDefault();
    softNavigate(anchor.href, false);
  }

  function init() {
    ensurePlayer();
    bindMenu();
    syncRadioUI(false);

    // Resume after hard reload if browser allows (media engagement)
    try {
      if (sessionStorage.getItem(STORAGE_KEY) === '1' && livePlayer.paused) {
        livePlayer.src = LIVE_RADIO_URL;
        livePlayer.play().then(function () {
          setPlaying(true);
        }).catch(function () {
          /* autoplay blocked — user taps play again */
          setPlaying(false);
        });
      }
    } catch (e) { /* ignore */ }
  }

  window.toggleArchiveRadio = toggleArchiveRadio;
  window.toggleMenu = toggleMenu;
  window.switchLanguage = switchLanguage;

  document.addEventListener('click', onDocumentClick);
  window.addEventListener('popstate', function () {
    softNavigate(location.href, true);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
