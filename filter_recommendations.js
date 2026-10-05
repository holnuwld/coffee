const fs = require('fs');
const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_comp2025.json', 'utf8'));
const microRes = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_microReserve2025.json', 'utf8'));
const micro = JSON.parse(fs.readFileSync('c:/cowork/coffee/standardized_micro2026.json', 'utf8'));

const all = [...micro, ...microRes, ...comp];

const userMatches = all.filter(p => {
  const isPanamaOrEth = p.country === 'Panama' || p.country === 'Ethiopia';
  const isWashed = /washed/i.test(p.process) || /washed/i.test(p.title);
  return isPanamaOrEth && isWashed;
});

console.log('=== Panama / Ethiopia Washed (Total: ' + userMatches.length + ') ===');
userMatches.forEach(p => {
  console.log(`[${p.category}] ${p.title}`);
  console.log(`   Variety: ${p.variety} | Process: ${p.process} | Alt: ${p.altitude}`);
  console.log(`   Notes: ${p.tastingNotes}`);
  console.log(`   Price: AED ${p.priceAED} (${p.weight}) | 100g당 AED ${p.pricePer100g} | InStock: ${p.available}`);
  console.log(`   URL: ${p.url}`);
  console.log('----------------------------------------------------');
});
