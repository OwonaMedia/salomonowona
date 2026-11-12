/* Salomon Owona Shop – cart + test-mode checkout. No secrets. */
(function () {
  const KEY = "so-shop-cart-v1";
  const SHOP_LIVE = window.SO_SHOP && window.SO_SHOP.shopLive === true;
  const API_BASE = (window.SO_SHOP && window.SO_SHOP.apiBase) || "https://owona.de";
  const SHOP_ID = (window.SO_SHOP && window.SO_SHOP.shopId) || "salomonowona";
  const XAF = (window.SO_SHOP && window.SO_SHOP.xafRate) || 655;

  function products() {
    return (window.SO_SHOP && window.SO_SHOP.products) || [];
  }
  function byId(id) {
    return products().find((p) => p.id === id);
  }
  function load() {
    try {
      const raw = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(raw) ? raw : [];
    } catch {
      return [];
    }
  }
  function save(cart) {
    localStorage.setItem(KEY, JSON.stringify(cart));
    badge();
  }
  function badge() {
    const n = load().reduce((s, i) => s + (i.qty || 0), 0);
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(n);
    });
  }
  function add(id, qty) {
    const p = byId(id);
    if (!p || p.fulfillment !== "own") return false;
    const cart = load();
    const row = cart.find((i) => i.id === id);
    const q = Math.max(1, Math.min(9, Number(qty) || 1));
    if (row) row.qty = Math.min(9, row.qty + q);
    else cart.push({ id, qty: q });
    save(cart);
    return true;
  }
  function setQty(id, qty) {
    const q = Math.max(0, Math.min(9, Number(qty) || 0));
    let cart = load();
    if (q === 0) cart = cart.filter((i) => i.id !== id);
    else {
      const row = cart.find((i) => i.id === id);
      if (row) row.qty = q;
    }
    save(cart);
  }
  function clear() {
    save([]);
  }
  function euro(cents) {
    return (cents / 100).toLocaleString("de-DE", { style: "currency", currency: "EUR" });
  }
  function xaf(cents) {
    return Math.max(1, Math.round((cents / 100) * XAF)).toLocaleString("de-DE") + " XAF";
  }
  function totalCents(cart) {
    return cart.reduce((s, i) => {
      const p = byId(i.id);
      return s + (p && p.priceCents ? p.priceCents * i.qty : 0);
    }, 0);
  }

  function renderCart() {
    const root = document.getElementById("cart-root");
    if (!root) return;
    const cart = load();
    if (!cart.length) {
      root.innerHTML = '<p class="shop-muted">Dein Warenkorb ist leer. <a href="/shop/" style="color:var(--accent)">Zum Shop →</a></p>';
      return;
    }
    let rows = "";
    for (const item of cart) {
      const p = byId(item.id);
      if (!p) continue;
      rows += `<tr>
        <td><a href="/shop/${p.slug}">${escapeHtml(p.title)}</a></td>
        <td class="shop-price">${euro(p.priceCents)}</td>
        <td><input type="number" min="0" max="9" value="${item.qty}" data-qty="${p.id}" aria-label="Menge"></td>
        <td class="shop-price">${euro(p.priceCents * item.qty)}</td>
        <td><button type="button" class="shop-text-btn" data-remove="${p.id}">Entfernen</button></td>
      </tr>`;
    }
    const t = totalCents(cart);
    root.innerHTML = `
      <table class="shop-cart">
        <thead><tr><th>Titel</th><th>Preis</th><th>Menge</th><th>Summe</th><th></th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <p><strong>Gesamt: <span class="shop-price">${euro(t)}</span></strong>
        <span class="shop-muted"> · ca. ${xaf(t)} bei Zahlung mit Mobile Money</span></p>
      <div class="shop-actions">
        <a class="contact-btn" href="/shop/kasse">Zur Kasse</a>
        <button type="button" class="shop-text-btn" data-clear>Warenkorb leeren</button>
      </div>`;
    root.querySelectorAll("[data-qty]").forEach((el) => {
      el.addEventListener("change", () => {
        setQty(el.getAttribute("data-qty"), el.value);
        renderCart();
      });
    });
    root.querySelectorAll("[data-remove]").forEach((el) => {
      el.addEventListener("click", () => {
        setQty(el.getAttribute("data-remove"), 0);
        renderCart();
      });
    });
    const clr = root.querySelector("[data-clear]");
    if (clr) clr.addEventListener("click", () => { clear(); renderCart(); });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function bindAddButtons() {
    document.querySelectorAll("[data-add]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-add");
        if (add(id, 1)) {
          btn.textContent = "Im Warenkorb";
          const go = document.getElementById("after-add");
          if (go) go.hidden = false;
        }
      });
    });
  }

  async function onCheckout(ev) {
    ev.preventDefault();
    const form = ev.target;
    const err = form.querySelector("[data-error]");
    const out = form.querySelector("[data-result]");
    if (err) err.textContent = "";
    const cart = load();
    if (!cart.length) {
      if (err) err.textContent = "Der Warenkorb ist leer.";
      return;
    }
    const fd = new FormData(form);
    const email = String(fd.get("email") || "").trim();
    if (!email || !email.includes("@")) {
      if (err) err.textContent = "Bitte eine gültige E-Mail-Adresse angeben.";
      return;
    }
    if (!fd.get("agb") || !fd.get("privacy") || !fd.get("widerruf")) {
      if (err) err.textContent = "Bitte AGB, Datenschutz und den Hinweis zum Widerrufsrecht bestätigen.";
      return;
    }
    const method = String(fd.get("pay") || "stripe");
    if (method === "momo") {
      const phone = String(fd.get("phone") || "").trim();
      if (phone.length < 8) {
        if (err) err.textContent = "Für Mobile Money bitte eine Telefonnummer angeben.";
        return;
      }
    }

    // Feature flag: never charge until Firmin's Go AND backend flag is on.
    if (!SHOP_LIVE) {
      const order = {
        test: true,
        shop: SHOP_ID,
        email,
        method,
        items: cart,
        totalCents: totalCents(cart),
        at: new Date().toISOString(),
      };
      sessionStorage.setItem("so-shop-last-test-order", JSON.stringify(order));
      clear();
      window.location.href = "/shop/danke?test=1";
      return;
    }

    // Live path (unused until flags are on). Prices come from the server, never from this form.
    const items = cart.map((i) => {
      const p = byId(i.id);
      return { id: i.id, quantity: i.qty, ebook_lang: (p && p.language) || "de" };
    });
    const payload = {
      shop: SHOP_ID,
      items,
      customer: {
        email,
        firstName: fd.get("firstName"),
        lastName: fd.get("lastName"),
        phone: fd.get("phone"),
        lang: "de",
      },
      lang: "de",
    };
    try {
      const url =
        method === "momo"
          ? `${API_BASE}/api/create-momo-checkout`
          : `${API_BASE}/api/create-checkout-session`;
      const body =
        method === "momo"
          ? {
              ...payload,
              provider: "notchpay",
              channel: fd.get("channel") || "cm.mobile",
              phone: fd.get("phone"),
            }
          : payload;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Checkout fehlgeschlagen");
      if (data.url) {
        window.location.href = data.url;
        return;
      }
      throw new Error("Keine Zahlungs-URL erhalten.");
    } catch (e) {
      if (err) err.textContent = e.message || "Checkout fehlgeschlagen.";
      if (out) out.textContent = "";
    }
  }

  function renderCheckoutSummary() {
    const el = document.getElementById("checkout-summary");
    if (!el) return;
    const cart = load();
    if (!cart.length) {
      el.innerHTML = '<p class="shop-muted">Kein Artikel im Warenkorb. <a href="/shop/" style="color:var(--accent)">Zum Shop →</a></p>';
      const form = document.getElementById("checkout-form");
      if (form) form.hidden = true;
      return;
    }
    const t = totalCents(cart);
    const lines = cart
      .map((i) => {
        const p = byId(i.id);
        if (!p) return "";
        return `<li>${escapeHtml(p.title)} × ${i.qty} — <span class="shop-price">${euro(p.priceCents * i.qty)}</span></li>`;
      })
      .join("");
    el.innerHTML = `<ul class="shop-summary">${lines}</ul>
      <p><strong>Gesamt: <span class="shop-price">${euro(t)}</span></strong>
      <span class="shop-muted"> · ca. ${xaf(t)} bei Mobile Money (Kurs ${XAF} XAF/EUR, wie im Shop von Owona Media)</span></p>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    badge();
    bindAddButtons();
    renderCart();
    renderCheckoutSummary();
    const form = document.getElementById("checkout-form");
    if (form) form.addEventListener("submit", onCheckout);
    const momo = document.getElementById("pay-momo");
    const extra = document.getElementById("momo-extra");
    function syncMomo() {
      if (extra) extra.hidden = !(momo && momo.checked);
    }
    document.querySelectorAll('input[name="pay"]').forEach((r) => r.addEventListener("change", syncMomo));
    syncMomo();
  });

  window.SOShop = { add, load, clear, euro, xaf, SHOP_LIVE };
})();
