const fs = require('fs');

// Helper to clean HTML entities and tags
function cleanText(str) {
  if (!str) return '';
  return str
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

// Function to extract text from body_html converted to text lines
function parseBodySpecs(bodyHtml) {
  const specs = {
    producer: '',
    farm: '',
    location: '',
    variety: '',
    process: '',
    altitude: '',
    fermentationDot: '',
    sweetnessDot: '',
    acidityDot: '',
    roastDot: ''
  };

  if (!bodyHtml) return specs;

  // Replace br and closing tags with newline to make line-based parsing easy
  const formatted = bodyHtml
    .replace(/<br\s*[\/]?>/gi, '\n')
    .replace(/<\/(p|div|tr|li|h[1-6])>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ');

  const lines = formatted.split('\n').map(l => l.trim()).filter(l => l.length > 0);

  for (const line of lines) {
    const cleaned = cleanText(line);

    // Producer / Farmer
    if (/^(producer|farmer)\s*[:：]/i.test(cleaned)) {
      specs.producer = cleaned.replace(/^(producer|farmer)\s*[:：]\s*/i, '').trim();
    }
    // Farm / Washing Station / Station
    else if (/^(farm|washing station|station|estate)\s*[:：]/i.test(cleaned)) {
      specs.farm = cleaned.replace(/^(farm|washing station|station|estate)\s*[:：]\s*/i, '').trim();
    }
    // Location / Region / Origin
    else if (/^(location|region|origin)\s*[:：]/i.test(cleaned)) {
      specs.location = cleaned.replace(/^(location|region|origin)\s*[:：]\s*/i, '').trim();
    }
    // Variety / Varietal
    else if (/^(variety|varietal)\s*[:：]/i.test(cleaned)) {
      specs.variety = cleaned.replace(/^(variety|varietal)\s*[:：]\s*/i, '').trim();
    }
    // Process / Processing
    else if (/^(process|processing)\s*[:：]/i.test(cleaned)) {
      specs.process = cleaned.replace(/^(process|processing)\s*[:：]\s*/i, '').trim();
    }
    // Altitude / Elevation
    else if (/^(altitude|elevation)\s*[:：]/i.test(cleaned)) {
      specs.altitude = cleaned.replace(/^(altitude|elevation)\s*[:：]\s*/i, '').trim();
    }
  }

  // Dots extraction (Fermentation, Sweetness, Acidity, Roast)
  const dotRegex = /(Fermentation|Sweetness|Acidity|Roast)[\s\S]*?([▪▫]{3,5})/g;
  let dMatch;
  while ((dMatch = dotRegex.exec(bodyHtml)) !== null) {
    const key = dMatch[1].toLowerCase();
    const dots = dMatch[2];
    if (key === 'fermentation') specs.fermentationDot = dots;
    else if (key === 'sweetness') specs.sweetnessDot = dots;
    else if (key === 'acidity') specs.acidityDot = dots;
    else if (key === 'roast') specs.roastDot = dots;
  }

  return specs;
}

async function fetchDetails(productHandle) {
  const url = `https://archerscoffee.com/products/${productHandle}`;
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });
    if (!res.ok) return { error: `HTTP ${res.status}` };
    const html = await res.text();

    // Tasting notes from metafield
    let tastingNotes = '';
    const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
    if (metafieldMatch && metafieldMatch[1]) {
      tastingNotes = cleanText(metafieldMatch[1]);
    }

    // Fallback: meta description
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
    const metaDesc = descMatch ? cleanText(descMatch[1]) : '';
    if (!tastingNotes && metaDesc) {
      const notesInDesc = metaDesc.match(/tasting notes of\s*([^.]+)/i) || metaDesc.match(/notes of\s*([^.]+)/i);
      if (notesInDesc && notesInDesc[1]) {
        tastingNotes = notesInDesc[1].trim();
      }
    }

    // Roast profile from page options
    const roastProfileMatch = html.match(/data-select-label=["']Roast Profile["'][\s\S]*?<label[^>]*>([^<]+)<\/label>/i);
    let roastProfile = roastProfileMatch ? cleanText(roastProfileMatch[1]) : '';

    return {
      tastingNotes,
      metaDesc,
      roastProfile
    };
  } catch (e) {
    return { error: e.message };
  }
}

async function processCollection(collectionName) {
  const rawProducts = JSON.parse(fs.readFileSync(`c:/cowork/coffee/${collectionName}_full.json`, 'utf8'));
  console.log(`Processing ${collectionName}: ${rawProducts.length} items`);

  const results = [];

  // Batch process with concurrency limit 5
  for (let i = 0; i < rawProducts.length; i += 5) {
    const batch = rawProducts.slice(i, i + 5);
    const batchPromises = batch.map(async (p) => {
      const specs = parseBodySpecs(p.body_html);
      const pageDetails = await fetchDetails(p.handle);

      // Country detection
      let country = '';
      const countries = [
        'Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador',
        'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras',
        'Brazil', 'Indonesia', 'Rwanda', 'Burundi', 'Peru', 'Bolivia'
      ];
      for (const c of countries) {
        if (p.title.toLowerCase().includes(c.toLowerCase()) || (p.tags && p.tags.some(t => t.toLowerCase() === c.toLowerCase()))) {
          country = c;
          break;
        }
      }

      // Roast profile fallback
      let roast = pageDetails.roastProfile || '';
      if (!roast) {
        if (p.tags && p.tags.some(t => /filter/i.test(t))) roast = 'Filter';
        else if (specs.roastDot) roast = `Light-Medium (${specs.roastDot})`;
      }
      if (specs.roastDot && !roast.includes('(')) {
        roast = `${roast || 'Filter'} (${specs.roastDot})`;
      }

      // Variants / Price / Weight
      const variants = p.variants || [];
      // Group variants by weight
      // Usually options are 100g, 200g, 250g, 1kg
      const weightPrices = [];
      for (const v of variants) {
        // extract weight from variant title (e.g., '100 Grams', '200 Grams', '250g', '1 Kilogram')
        const wMatch = v.title.match(/(\d+)\s*(gram|g|kg|kilogram)/i);
        let weightGrams = 0;
        let weightLabel = '';
        if (wMatch) {
          const num = parseInt(wMatch[1], 10);
          const unit = wMatch[2].toLowerCase();
          if (unit.startsWith('k')) {
            weightGrams = num * 1000;
            weightLabel = `${num}kg`;
          } else {
            weightGrams = num;
            weightLabel = `${num}g`;
          }
        }
        const price = parseFloat(v.price);
        weightPrices.push({
          title: v.title,
          price: price,
          weightGrams,
          weightLabel,
          available: v.available
        });
      }

      // Pick representative retail weight (prefer 100g or 200g or 250g)
      const retailVariants = weightPrices.filter(v => v.weightGrams > 0 && v.weightGrams <= 250);
      let selectedVariant = retailVariants.find(v => v.available) || retailVariants[0] || weightPrices[0];
      
      let priceAED = selectedVariant ? selectedVariant.price : 0;
      let weightDisplay = selectedVariant && selectedVariant.weightLabel ? selectedVariant.weightLabel : 'N/A';
      let pricePer100g = 0;
      if (selectedVariant && selectedVariant.weightGrams > 0) {
        pricePer100g = (priceAED / selectedVariant.weightGrams) * 100;
      }

      // Check overall availability
      const isAvailable = variants.some(v => v.available);

      return {
        id: p.id,
        title: p.title,
        handle: p.handle,
        url: `https://archerscoffee.com/products/${p.handle}`,
        collection: collectionName,
        country: country || '기타',
        location: specs.location || '',
        farm: specs.farm || '',
        producer: specs.producer || '',
        variety: specs.variety || '',
        process: specs.process || '',
        altitude: specs.altitude || '',
        roast: roast || 'Filter (라이트/미디엄라이트)',
        tastingNotes: pageDetails.tastingNotes || '',
        weightDisplay,
        priceAED,
        pricePer100g: Math.round(pricePer100g * 100) / 100,
        available: isAvailable,
        weightOptions: Array.from(new Set(weightPrices.map(wp => `${wp.weightLabel || '기본'}: AED ${wp.price} (${wp.available ? '재고있음' : '품절'})`))),
        rawSpecs: specs,
        tags: p.tags
      };
    });

    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
    console.log(`Processed ${results.length}/${rawProducts.length} items...`);
  }

  fs.writeFileSync(`c:/cowork/coffee/${collectionName}_parsed.json`, JSON.stringify(results, null, 2));
  console.log(`Saved ${collectionName}_parsed.json successfully!`);
  return results;
}

async function main() {
  await processCollection('microlot-2026');
  await processCollection('microlot-reserve-2025');
  await processCollection('competition-series-2025');
  console.log('All collections successfully parsed and saved!');
}

main();
