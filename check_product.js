const fs = require('fs');

async function checkProductPage() {
  const url = 'https://archerscoffee.com/products/colombia-aroma-nativo-pink-bouron-efm-lot-1289';
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const html = await res.text();
  fs.writeFileSync('c:/cowork/coffee/sample_product.html', html);
  console.log('Saved sample_product.html, length:', html.length);

  // Look for sections in HTML
  const lines = html.split('\n');
  lines.forEach((l, idx) => {
    if (/tasting|flavor|notes|profile|roast|altitude|producer/i.test(l)) {
      if (l.trim().length > 0 && l.trim().length < 300) {
        console.log(`L${idx}: ${l.trim()}`);
      }
    }
  });
}

checkProductPage();
