const fs = require('fs');

async function testCollections() {
  const collections = [
    { name: 'microlot-2026', url: 'https://archerscoffee.com/collections/microlot-2026' },
    { name: 'microlot-reserve-2025', url: 'https://archerscoffee.com/collections/microlot-reserve-2025' },
    { name: 'competition-series-2025', url: 'https://archerscoffee.com/collections/competition-series-2025' }
  ];

  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
  };

  for (const col of collections) {
    console.log(`\n================ Testing ${col.name} ================`);
    
    // Try products.json first
    try {
      const jsonRes = await fetch(`${col.url}/products.json?limit=50`, { headers });
      if (jsonRes.ok) {
        const data = await jsonRes.json();
        console.log(`[JSON SUCCESS] Found ${data.products ? data.products.length : 0} products`);
        if (data.products && data.products.length > 0) {
          data.products.forEach(p => {
            console.log(` - [${p.id}] ${p.title} (/products/${p.handle}) - variants: ${p.variants.length}`);
          });
          fs.writeFileSync(`c:/cowork/coffee/${col.name}.json`, JSON.stringify(data, null, 2));
          continue;
        }
      } else {
        console.log(`[JSON Status] ${jsonRes.status} ${jsonRes.statusText}`);
      }
    } catch (e) {
      console.log(`[JSON Error] ${e.message}`);
    }

    // Try HTML fetch
    try {
      const htmlRes = await fetch(col.url, { headers });
      const html = await htmlRes.text();
      console.log(`[HTML SUCCESS] Received ${html.length} bytes`);
      fs.writeFileSync(`c:/cowork/coffee/${col.name}.html`, html);
      
      // regex to find product handles
      const regex = /\/products\/([a-zA-Z0-9_-]+)/g;
      const matches = new Set();
      let m;
      while ((m = regex.exec(html)) !== null) {
        matches.add(m[1]);
      }
      console.log(`Found ${matches.size} product handles in HTML:`, Array.from(matches));
    } catch (e) {
      console.log(`[HTML Error] ${e.message}`);
    }
  }
}

testCollections();
