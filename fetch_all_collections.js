const fs = require('fs');

async function getAllProductsFromCollection(handle) {
  let page = 1;
  let allProducts = [];
  while (true) {
    const url = `https://archerscoffee.com/collections/${handle}/products.json?limit=250&page=${page}`;
    console.log(`Fetching ${url}...`);
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });
    if (!res.ok) {
      console.log(`Failed with status ${res.status}`);
      break;
    }
    const data = await res.json();
    if (!data.products || data.products.length === 0) {
      break;
    }
    allProducts.push(...data.products);
    console.log(`Page ${page}: got ${data.products.length} products (total: ${allProducts.length})`);
    if (data.products.length < 250) break;
    page++;
  }
  return allProducts;
}

async function run() {
  const collections = ['microlot-2026', 'microlot-reserve-2025', 'competition-series-2025'];
  const summary = {};

  for (const c of collections) {
    console.log(`\n=== Processing ${c} ===`);
    const products = await getAllProductsFromCollection(c);
    summary[c] = products;
    fs.writeFileSync(`c:/cowork/coffee/${c}_full.json`, JSON.stringify(products, null, 2));
    console.log(`Total products in ${c}: ${products.length}`);
  }

  console.log('\n--- SUMMARY ---');
  for (const [k, v] of Object.entries(summary)) {
    console.log(`${k}: ${v.length} products`);
  }
}

run();
