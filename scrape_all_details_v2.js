const fs = require('fs');

function cleanHtml(html) {
  if (!html) return '';
  return html
    .replace(/<meta[^>]*>/gi, '')
    .replace(/<br\s*[\/]?>/gi, '\n')
    .replace(/<\/(p|div|tr|li|h[1-6])>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\r/g, '')
    .replace(/[ \t]+/g, ' ');
}

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

  // Dots
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

  const cleaned = cleanHtml(bodyHtml);
  const lines = cleaned.split('\n').map(l => l.trim()).filter(l => l.length > 0);

  for (const line of lines) {
    // Producer / Farmer
    if (/^(producer|farmer)\s*[:：]/i.test(line)) {
      specs.producer = line.replace(/^(producer|farmer)\s*[:：]\s*/i, '').trim();
    }
    // Farm / Washing Station / Station / Estate
    else if (/^(farm|washing station|station|estate)\s*[:：]/i.test(line)) {
      specs.farm = line.replace(/^(farm|washing station|station|estate)\s*[:：]\s*/i, '').trim();
    }
    // Location / Region / Origin
    else if (/^(location|region|origin)\s*[:：]/i.test(line)) {
      specs.location = line.replace(/^(location|region|origin)\s*[:：]\s*/i, '').trim();
    }
    // Variety / Varietal
    else if (/^(variety|varietal)\s*[:：]/i.test(line)) {
      specs.variety = line.replace(/^(variety|varietal)\s*[:：]\s*/i, '').trim();
    }
    // Process / Processing
    else if (/^(process|processing)\s*[:：]/i.test(line)) {
      specs.process = line.replace(/^(process|processing)\s*[:：]\s*/i, '').trim();
    }
    // Altitude / Elevation
    else if (/^(altitude|elevation)\s*[:：]/i.test(line)) {
      specs.altitude = line.replace(/^(altitude|elevation)\s*[:：]\s*/i, '').trim();
    }
  }

  return specs;
}

function extractTastingNotes(html, bodyHtml) {
  let notes = '';

  // 1. Metafield span
  const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
  if (metafieldMatch && metafieldMatch[1]) {
    notes = cleanHtml(metafieldMatch[1]).trim();
    if (notes) return notes;
  }

  // 2. Meta description or OG description
  const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i) ||
                    html.match(/<meta\s+property=["']og:description["']\s+content=["']([\s\S]*?)["']/i);
  if (descMatch && descMatch[1]) {
    const rawDesc = cleanHtml(descMatch[1]);
    // Try patterns like "with tasting notes of X", "notes of X", "tasting notes: X"
    const m1 = rawDesc.match(/(?:with tasting notes of|tasting notes of|notes of|tasting notes:)\s*([^.]+?)(?:\.\s*This coffee|\.\s*Coffee sourced|\.\s*Works best|\.$|$)/i);
    if (m1 && m1[1]) {
      notes = m1[1].trim();
      if (notes) return notes;
    }
  }

  // 3. Check body_html text for tasting notes
  if (bodyHtml) {
    const cleanedBody = cleanHtml(bodyHtml);
    const m2 = cleanedBody.match(/(?:tasting notes|flavor notes|taste profile|cup notes)\s*[:：]\s*([^\n\r]+)/i);
    if (m2 && m2[1]) {
      notes = m2[1].trim();
      if (notes) return notes;
    }
  }

  return notes;
}

async function fetchDetails(productHandle, bodyHtml) {
  const url = `https://archerscoffee.com/products/${productHandle}`;
  try {
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
      }
    });
    if (!res.ok) return { error: `HTTP ${res.status}` };
    const html = await res.text();

    const tastingNotes = extractTastingNotes(html, bodyHtml);

    // Roast profile from page options
    const roastProfileMatch = html.match(/data-select-label=["']Roast Profile["'][\s\S]*?<label[^>]*>([^<]+)<\/label>/i);
    let roastProfile = roastProfileMatch ? cleanHtml(roastProfileMatch[1]).trim() : '';

    // Description text for extra context
    const descMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
    const metaDesc = descMatch ? cleanHtml(descMatch[1]).trim() : '';

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

  for (let i = 0; i < rawProducts.length; i += 5) {
    const batch = rawProducts.slice(i, i + 5);
    const batchPromises = batch.map(async (p) => {
      const specs = parseBodySpecs(p.body_html);
      const pageDetails = await fetchDetails(p.handle, p.body_html);

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

      // If location has country
      if (!country && specs.location) {
        for (const c of countries) {
          if (specs.location.toLowerCase().includes(c.toLowerCase())) {
            country = c;
            break;
          }
        }
      }

      // Roast profile
      let roast = pageDetails.roastProfile || '';
      if (!roast) {
        if (p.tags && p.tags.some(t => /filter/i.test(t))) roast = 'Filter';
        else if (specs.roastDot) roast = `Light-Medium`;
      }
      if (specs.roastDot) {
        roast = `${roast || 'Filter'} (${specs.roastDot})`;
      } else {
        roast = roast || 'Filter (라이트/미디엄라이트)';
      }

      // Variants
      const variants = p.variants || [];
      const weightPrices = [];
      for (const v of variants) {
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

      // Pick representative retail weight
      // Prefer in-stock 100g, 200g, 250g
      const retailVariants = weightPrices.filter(v => v.weightGrams > 0 && v.weightGrams <= 250);
      let selectedVariant = retailVariants.find(v => v.available) || retailVariants[0] || weightPrices.find(v => v.available) || weightPrices[0];

      let priceAED = selectedVariant ? selectedVariant.price : 0;
      let weightDisplay = selectedVariant && selectedVariant.weightLabel ? selectedVariant.weightLabel : 'N/A';
      let pricePer100g = 0;
      if (selectedVariant && selectedVariant.weightGrams > 0) {
        pricePer100g = (priceAED / selectedVariant.weightGrams) * 100;
      }

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
        roast,
        tastingNotes: pageDetails.tastingNotes || '',
        metaDesc: pageDetails.metaDesc || '',
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

  fs.writeFileSync(`c:/cowork/coffee/${collectionName}_parsed_v2.json`, JSON.stringify(results, null, 2));
  console.log(`Saved ${collectionName}_parsed_v2.json successfully!`);
  return results;
}

async function main() {
  await processCollection('microlot-2026');
  await processCollection('microlot-reserve-2025');
  await processCollection('competition-series-2025');
  console.log('All collections V2 parsed successfully!');
}

main();
