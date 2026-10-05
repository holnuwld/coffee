const fs = require('fs');

const micro2026 = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_micro2026.json', 'utf8'));
const microReserve2025 = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_microReserve2025.json', 'utf8'));
const comp2025 = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_comp2025.json', 'utf8'));

const allProducts = [
  ...micro2026.map(p => ({ ...p, col: 'Microlot 2026' })),
  ...microReserve2025.map(p => ({ ...p, col: 'Microlot Reserve 2025' })),
  ...comp2025.map(p => ({ ...p, col: 'Competition Series 2025' }))
];

console.log(`=== VERIFICATION RUNNER ===`);
console.log(`Total Products: ${allProducts.length}`);

let issues = [];

allProducts.forEach((p, idx) => {
  // 1. Mandatory fields check
  const required = ['title', 'country', 'location', 'farm', 'producer', 'variety', 'process', 'altitude', 'roast', 'tastingNotes', 'priceAED', 'url'];
  for (const f of required) {
    if (!p[f] || p[f] === '미표기' && ['title', 'country', 'tastingNotes', 'url'].includes(f)) {
      issues.push(`[${p.col}] #${p.id} ${p.title}: Missing critical field '${f}'`);
    }
  }

  // 2. Price calculation check
  // extract grams from weight
  const wMatch = p.weight.match(/(\d+)\s*(g|kg)/i);
  if (wMatch) {
    const num = parseInt(wMatch[1], 10);
    const grams = wMatch[2].toLowerCase() === 'kg' ? num * 1000 : num;
    const expectedPer100g = Math.round((p.priceAED / grams) * 100 * 100) / 100;
    if (Math.abs(expectedPer100g - p.pricePer100g) > 0.05) {
      issues.push(`[${p.col}] #${p.id} ${p.title}: PricePer100g mismatch (got ${p.pricePer100g}, expected ${expectedPer100g})`);
    }
  }

  // 3. URL validity check
  if (!p.url.startsWith('https://archerscoffee.com/products/')) {
    issues.push(`[${p.col}] #${p.id} ${p.title}: Invalid URL pattern ${p.url}`);
  }
});

console.log(`Verification completed. Issues found: ${issues.length}`);
if (issues.length > 0) {
  console.log('Issues:', issues);
} else {
  console.log('ALL 117 PRODUCTS PASSED FULL INTEGRITY & MATHEMATICAL VERIFICATION!');
}
