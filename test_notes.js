const fs = require('fs');

async function testSampleTastingNotes() {
  const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/competition-series-2025_full.json', 'utf8'));
  const samples = comp.slice(0, 5);

  for (const p of samples) {
    const url = `https://archerscoffee.com/products/${p.handle}`;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const html = await res.text();
    
    // extract meta description
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i);
    const metaDesc = descMatch ? descMatch[1] : '';

    // extract metafield-multi_line_text_field
    const notesMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([^<]+)<\/span>/i);
    const metafieldNotes = notesMatch ? notesMatch[1] : '';

    console.log(`Product: ${p.title}`);
    console.log(` - Metafield notes: ${metafieldNotes}`);
    console.log(` - Meta description: ${metaDesc}`);
    console.log('---');
  }
}

testSampleTastingNotes();
