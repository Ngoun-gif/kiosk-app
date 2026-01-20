async function loadProducts() {
  const wrap = document.getElementById("products");
  wrap.innerHTML = "";

  const products = await pywebview.api.list_products();
  for (const p of products) {
    const col = document.createElement("div");
    col.className = "col-6 col-md-4";
    col.innerHTML = `
      <div class="card h-100">
        <div class="card-body text-center">
          <h5 class="card-title">${p.name}</h5>
          <p class="card-text fs-4">$${p.price.toFixed(2)}</p>
          <button class="btn btn-primary btn-lg w-100" onclick="addToCart(${p.id})">
            Add
          </button>
        </div>
      </div>
    `;
    wrap.appendChild(col);
  }
}

function addToCart(id){
  // next step
  alert("Added product ID " + id);
}

document.addEventListener("contextmenu", e => e.preventDefault());
window.addEventListener("pywebviewready", loadProducts);
