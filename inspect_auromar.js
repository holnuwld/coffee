const fs = require('fs');

async function inspectAuromar() {
  const url = 'https://archerscoffee.com/products/panama-finca-auromar-malla-geisha-washed-peaberry';
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const html = await res.text();
  fs.writeFileSync('c:/cowork/coffee/auromar.html', html);

  // Check lines
  const lines = html.split('\n');
  console.log(`Auromar lines count: ${lines.length}`);
  lines.forEach((l, idx) => {
    if (/tasting|flavor|notes|peaberry|jasmine|bergamot|peach|citrus|floral|apricot/i.test(l)) {
      if (l.trim().length > 0 && l.trim().length < 250) {
        console.log(`L${idx}: ${l.trim()}`);
      }
    }
  });

  const metaDesc = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i);
  console.log('\nmetaDesc:', metaDesc ? metaDesc[1] : 'none');
}

inspectAuromar();
