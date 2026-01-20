const app = document.getElementById("app");

// global state
let orderType = "DINE_IN"; // set from Service screen later
let cart = {};            // { productId: qty }
let lastReceipt = null;

async function loadPage(page) {
  const res = await fetch(`pages/${page}.html`);
  app.innerHTML = await res.text();

  if (page === "menu") await renderMenu();
  if (page === "receipt") renderReceipt();
}

function go(page) {
  loadPage(page);
}

// -------- MENU --------
async function renderMenu() {
  const wrap = document.getElementById("products");
  wrap.innerHTML = "";

  const products = await pywebview.api.list_products();
  for (const p of products) {
    const col = document.createElement("div");
    col.className = "col-6 col-md-4";
    col.innerHTML = `
      <div class="card h-100">
        <div class="card-body text-center">
          <div class="fw-bold fs-5">${escapeHtml(p.name)}</div>
          <div class="text-muted my-2 fs-4">$${Number(p.price).toFixed(2)}</div>
          <button class="btn btn-success btn-lg w-100" onclick="addToCart(${p.id})">
            Add
          </button>
        </div>
      </div>
    `;
    wrap.appendChild(col);
  }

  renderCart();
}

function addToCart(productId) {
  cart[productId] = (cart[productId] || 0) + 1;
  renderCart();
}

function decItem(productId) {
  if (!cart[productId]) return;
  cart[productId] -= 1;
  if (cart[productId] <= 0) delete cart[productId];
  renderCart();
}

function incItem(productId) {
  cart[productId] = (cart[productId] || 0) + 1;
  renderCart();
}

function removeItem(productId) {
  delete cart[productId];
  renderCart();
}

function clearCart() {
  cart = {};
  renderCart();
}

async function renderCart() {
  const box = document.getElementById("cartItems");
  const totalEl = document.getElementById("cartTotal");
  const msg = document.getElementById("cartMsg");
  if (!box || !totalEl) return;

  msg.textContent = "";
  box.innerHTML = "";

  const ids = Object.keys(cart).map(x => Number(x));
  if (ids.length === 0) {
    box.innerHTML = `<div class="text-muted">Cart is empty</div>`;
    totalEl.textContent = "$0.00";
    return;
  }

  let total = 0;

  // load each product (simple & clear; we can optimize later)
  for (const id of ids) {
    const p = await pywebview.api.get_product(id);
    if (!p) continue;

    const qty = cart[id];
    const lineTotal = Number(p.price) * qty;
    total += lineTotal;

    const row = document.createElement("div");
    row.className = "d-flex justify-content-between align-items-center border rounded p-2";
    row.innerHTML = `
      <div class="me-2">
        <div class="fw-bold">${escapeHtml(p.name)}</div>
        <div class="text-muted small">$${Number(p.price).toFixed(2)} each</div>
      </div>

      <div class="d-flex align-items-center gap-1">
        <button class="btn btn-sm btn-outline-secondary" onclick="decItem(${id})">-</button>
        <div class="px-2 fw-bold">${qty}</div>
        <button class="btn btn-sm btn-outline-secondary" onclick="incItem(${id})">+</button>
        <button class="btn btn-sm btn-outline-danger ms-2" onclick="removeItem(${id})">x</button>
      </div>
    `;
    box.appendChild(row);
  }

  totalEl.textContent = `$${total.toFixed(2)}`;
}

async function checkout() {
  const msg = document.getElementById("cartMsg");
  msg.textContent = "";

  const items = Object.keys(cart).map(id => ({
    product_id: Number(id),
    qty: cart[id]
  }));

  const res = await pywebview.api.create_order({
    order_type: orderType,
    items
  });

  if (!res.ok) {
    msg.textContent = res.message || "Checkout failed.";
    return;
  }

  lastReceipt = res;
  cart = {}; // reset cart after saving order
  go("receipt");
}

// -------- RECEIPT --------
function renderReceipt() {
  const box = document.getElementById("receiptBox");
  if (!box) return;

  if (!lastReceipt) {
    box.innerHTML = `<div class="text-danger">No receipt data.</div>`;
    return;
  }

  const itemsHtml = lastReceipt.items.map(it => `
    <tr>
      <td>${escapeHtml(it.name)}</td>
      <td class="text-end">${it.qty}</td>
      <td class="text-end">$${Number(it.price).toFixed(2)}</td>
      <td class="text-end">$${Number(it.line_total).toFixed(2)}</td>
    </tr>
  `).join("");

  box.innerHTML = `
    <div class="mb-2"><span class="badge bg-secondary">${lastReceipt.order_type}</span></div>
    <div class="fw-bold">Order #${lastReceipt.order_id}</div>

    <table class="table table-sm mt-3">
      <thead>
        <tr>
          <th>Item</th>
          <th class="text-end">Qty</th>
          <th class="text-end">Price</th>
          <th class="text-end">Total</th>
        </tr>
      </thead>
      <tbody>${itemsHtml}</tbody>
    </table>

    <div class="d-flex justify-content-between fw-bold fs-5">
      <span>Total</span>
      <span>$${Number(lastReceipt.total).toFixed(2)}</span>
    </div>
  `;
}

function finishOrder() {
  lastReceipt = null;
  orderType = "DINE_IN";
  go("splash");
}

// -------- helpers --------
function escapeHtml(str) {
  return (str ?? "").replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("contextmenu", e => e.preventDefault());

window.addEventListener("pywebviewready", async () => {
  const res = await pywebview.api.ping();
  console.log(res.message);
  go("splash");
});


let lastPdfPath = null;

async function savePdf() {
  const msg = document.getElementById("pdfMsg");
  msg.textContent = "";

  if (!lastReceipt) {
    msg.textContent = "No receipt data.";
    return;
  }

  const res = await pywebview.api.save_receipt_pdf(lastReceipt);
  if (!res.ok) {
    msg.textContent = res.message || "Failed to save PDF.";
    return;
  }

  lastPdfPath = res.path;
  msg.textContent = "Saved: " + lastPdfPath;
}

async function openLastPdf() {
  const msg = document.getElementById("pdfMsg");
  msg.textContent = "";

  if (!lastPdfPath) {
    msg.textContent = "No PDF saved yet.";
    return;
  }

  const res = await pywebview.api.open_file(lastPdfPath);
  if (!res.ok) msg.textContent = res.message || "Cannot open file.";
}
