const fs = require('fs');

function parseProductDetails(product, collectionName) {
  const title = product.title || '';
  const handle = product.handle || '';
  const url = `https://archerscoffee.com/products/${handle}`;
  const bodyHtml = product.body_html || '';

  // Extract from bodyHtml
  // Typical patterns:
  // Producer: Luis Marcelino
  // Farm: Veci Project
  // Location: Pitalito, Huila
  // Variety: Pink Bourbon
  // Process: Honey Double Fermentation
  // Altitude: 1,700 - 1,750 masl

  function extractField(patterns) {
    for (const p of patterns) {
      const match = bodyHtml.match(p);
      if (match && match[1]) {
        // Strip html tags and extra whitespace
        return match[1].replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim();
      }
    }
    return '';
  }

  const producer = extractField([
    /Producer\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Producer\s*:\s*([^<\n\r]+)/i,
    /<strong>Farmer<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Farmer\s*:\s*([^<\n\r]+)/i
  ]);

  const farm = extractField([
    /Farm\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Farm\s*:\s*([^<\n\r]+)/i,
    /Washing Station\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Station\s*<\/strong>\s*:\s*([^<\n\r]+)/i
  ]);

  const location = extractField([
    /Location\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Location\s*:\s*([^<\n\r]+)/i,
    /Region\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Region\s*:\s*([^<\n\r]+)/i,
    /Origin\s*<\/strong>\s*:\s*([^<\n\r]+)/i
  ]);

  const variety = extractField([
    /Variety\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Variety\s*:\s*([^<\n\r]+)/i,
    /Varietal\s*<\/strong>\s*:\s*([^<\n\r]+)/i
  ]);

  const process = extractField([
    /Process\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Process\s*:\s*([^<\n\r]+)/i,
    /Processing\s*<\/strong>\s*:\s*([^<\n\r]+)/i
  ]);

  const altitude = extractField([
    /Altitude\s*<\/strong>\s*:\s*([^<\n\r]+)/i,
    /Altitude\s*:\s*([^<\n\r]+)/i,
    /Elevation\s*<\/strong>\s*:\s*([^<\n\r]+)/i
  ]);

  // Country from title or tags or location
  let country = '';
  const firstWord = title.split(/[-–—:]/)[0].trim();
  const knownCountries = ['Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador', 'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras', 'Brazil', 'Indonesia'];
  for (const kc of knownCountries) {
    if (firstWord.toLowerCase().includes(kc.toLowerCase()) || title.toLowerCase().includes(kc.toLowerCase())) {
      country = kc;
      break;
    }
  }

  // Variants info
  const variants = product.variants || [];
  // Find weight options and pricing
  // Usually variants have options like 100g, 200g, 250g, 1kg
  return {
    id: product.id,
    title,
    handle,
    url,
    collection: collectionName,
    country,
    location,
    farm,
    producer,
    variety,
    process,
    altitude,
    tags: product.tags,
    variantCount: variants.length,
    variants: variants.map(v => ({
      title: v.title,
      price: v.price,
      sku: v.sku,
      available: v.available
    }))
  };
}

const cols = ['microlot-2026', 'microlot-reserve-2025', 'competition-series-2025'];
cols.forEach(c => {
  const raw = JSON.parse(fs.readFileSync(`c:/cowork/coffee/${c}_full.json`, 'utf8'));
  const parsed = raw.map(p => parseProductDetails(p, c));
  console.log(`\n=== Sample 3 from ${c} ===`);
  parsed.slice(0, 3).forEach(p => {
    console.log(JSON.stringify({
      title: p.title,
      country: p.country,
      location: p.location,
      farm: p.farm,
      producer: p.producer,
      variety: p.variety,
      process: p.process,
      altitude: p.altitude,
      samplePrice: p.variants[0] ? `${p.variants[0].title}: AED ${p.variants[0].price} (${p.variants[0].available ? 'In Stock' : 'Sold Out'})` : 'No variant'
    }, null, 2));
  });
});
