const fs = require('fs');

async function traceOne() {
  const p = { handle: 'panama-finca-auromar-malla-geisha-washed-peaberry' };
  const url = `https://archerscoffee.com/products/${p.handle}`;
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const html = await res.text();

  let notes = '';
  const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
  console.log('metafieldMatch:', metafieldMatch ? metafieldMatch[1] : 'null');
  if (metafieldMatch && metafieldMatch[1]) {
    notes = metafieldMatch[1].replace(/<[^>]+>/g, '').trim();
  }

  console.log('notes after metafield:', notes);
}
traceOne();
