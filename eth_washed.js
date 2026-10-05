const fs = require('fs');
const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_comp2025.json', 'utf8'));
const microRes = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_microReserve2025.json', 'utf8'));
const micro = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_micro2026.json', 'utf8'));
const all = [...micro, ...microRes, ...comp];
const ethWashed = all.filter(p => p.country === 'Ethiopia' && (/washed/i.test(p.process) || /washed/i.test(p.title)));
ethWashed.forEach(p => {
  console.log(`[${p.category}] ${p.title}`);
  console.log(`   Producer: ${p.producer} | Station: ${p.farm} | Variety: ${p.variety} | Process: ${p.process} | Alt: ${p.altitude}`);
  console.log(`   Notes: ${p.tastingNotes}`);
  console.log(`   Price: AED ${p.priceAED} (${p.weight}) | 100g당 AED ${p.pricePer100g} | Stock: ${p.available}`);
  console.log(`   URL: ${p.url}`);
  console.log('---');
});
