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
    if (/^(producer|farmer)\s*[:：]/i.test(line)) {
      specs.producer = line.replace(/^(producer|farmer)\s*[:：]\s*/i, '').trim();
    } else if (/^(farm|washing station|station|estate)\s*[:：]/i.test(line)) {
      specs.farm = line.replace(/^(farm|washing station|station|estate)\s*[:：]\s*/i, '').trim();
    } else if (/^(location|region|origin)\s*[:：]/i.test(line)) {
      specs.location = line.replace(/^(location|region|origin)\s*[:：]\s*/i, '').trim();
    } else if (/^(variety|varietal)\s*[:：]/i.test(line)) {
      specs.variety = line.replace(/^(variety|varietal)\s*[:：]\s*/i, '').trim();
    } else if (/^(process|processing)\s*[:：]/i.test(line)) {
      specs.process = line.replace(/^(process|processing)\s*[:：]\s*/i, '').trim();
    } else if (/^(altitude|elevation)\s*[:：]/i.test(line)) {
      specs.altitude = line.replace(/^(altitude|elevation)\s*[:：]\s*/i, '').trim();
    }
  }

  return specs;
}

function parseTastingNotesFromMeta(text) {
  if (!text) return '';
  const cleaned = text
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  const regex = /(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^\n\r.]+)/i;
  const match = cleaned.match(regex);
  if (match && match[1]) {
    let notes = match[1].trim();
    notes = notes.split(/(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)/i)[0].trim();
    notes = notes.replace(/\.+$/, '').trim();
    return notes;
  }
  return '';
}

function extractTastingNotesFromHtml(html, bodyHtml) {
  if (!html) return '';

  // 1. Metafield span
  const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
  if (metafieldMatch && metafieldMatch[1]) {
    const notes = metafieldMatch[1].replace(/<[^>]+>/g, '').trim();
    if (notes) return notes;
  }

  // 2. Meta description or OG description
  const metaDescMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
                        html.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i) ||
                        html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']*)["']/i);
  if (metaDescMatch && metaDescMatch[1]) {
    const notes = parseTastingNotesFromMeta(metaDescMatch[1]);
    if (notes) return notes;
  }

  // 3. Twitter description
  const twMatch = html.match(/<meta[^>]*name=["']twitter:description["'][^>]*content=["']([^"']*)["']/i);
  if (twMatch && twMatch[1]) {
    const notes = parseTastingNotesFromMeta(twMatch[1]);
    if (notes) return notes;
  }

  // 4. Body html check
  if (bodyHtml) {
    const cleanedBody = cleanHtml(bodyHtml);
    const m = cleanedBody.match(/(?:tasting notes|flavor notes|taste profile|cup notes)\s*[:：]\s*([^\n\r]+)/i);
    if (m && m[1]) {
      return m[1].trim();
    }
  }

  return '';
}

async function fetchWithRetry(url, retries = 3, delayMs = 300) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
      });
      if (res.status === 429 || res.status === 430) {
        console.log(`Rate limited on ${url}, waiting 1500ms... (attempt ${attempt})`);
        await new Promise(r => setTimeout(r, 1500));
        continue;
      }
      if (!res.ok) {
        console.log(`HTTP ${res.status} on ${url} (attempt ${attempt})`);
        await new Promise(r => setTimeout(r, 500));
        continue;
      }
      const text = await res.text();
      return text;
    } catch (e) {
      console.log(`Error on ${url}: ${e.message} (attempt ${attempt})`);
      await new Promise(r => setTimeout(r, 500));
    }
  }
  return null;
}

async function processAllCollectionsRobust() {
  const collections = ['microlot-2026', 'microlot-reserve-2025', 'competition-series-2025'];

  for (const cName of collections) {
    const rawProducts = JSON.parse(fs.readFileSync(`c:/cowork/coffee/${cName}_full.json`, 'utf8'));
    console.log(`\n========================================`);
    console.log(`Processing ${cName} (${rawProducts.length} items) robustly...`);
    console.log(`========================================`);

    const processedList = [];

    for (let i = 0; i < rawProducts.length; i++) {
      const p = rawProducts[i];
      const url = `https://archerscoffee.com/products/${p.handle}`;
      const html = await fetchWithRetry(url);

      const specs = parseBodySpecs(p.body_html);
      let tastingNotes = '';
      let roastProfile = '';

      if (html) {
        tastingNotes = extractTastingNotesFromHtml(html, p.body_html);
        const roastMatch = html.match(/data-select-label=["']Roast Profile["'][\s\S]*?<label[^>]*>([^<]+)<\/label>/i);
        roastProfile = roastMatch ? cleanHtml(roastMatch[1]).trim() : '';
      }

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
      if (!country && specs.location) {
        for (const c of countries) {
          if (specs.location.toLowerCase().includes(c.toLowerCase())) {
            country = c;
            break;
          }
        }
      }

      // Roast formatting
      let roast = roastProfile;
      if (!roast) {
        if (p.tags && p.tags.some(t => /filter/i.test(t))) roast = 'Filter';
        else if (specs.roastDot) roast = 'Filter | Espresso';
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

      const retailVariants = weightPrices.filter(v => v.weightGrams > 0 && v.weightGrams <= 250);
      let selectedVariant = retailVariants.find(v => v.available) || retailVariants[0] || weightPrices.find(v => v.available) || weightPrices[0];

      let priceAED = selectedVariant ? selectedVariant.price : 0;
      let weightDisplay = selectedVariant && selectedVariant.weightLabel ? selectedVariant.weightLabel : 'N/A';
      let pricePer100g = 0;
      if (selectedVariant && selectedVariant.weightGrams > 0) {
        pricePer100g = (priceAED / selectedVariant.weightGrams) * 100;
      }

      const isAvailable = variants.some(v => v.available);

      const record = {
        id: p.id,
        title: p.title,
        handle: p.handle,
        url,
        collection: cName,
        country: country || '기타',
        location: specs.location || '',
        farm: specs.farm || '',
        producer: specs.producer || '',
        variety: specs.variety || '',
        process: specs.process || '',
        altitude: specs.altitude || '',
        roast,
        tastingNotes: tastingNotes || 'N/A',
        weightDisplay,
        priceAED,
        pricePer100g: Math.round(pricePer100g * 100) / 100,
        available: isAvailable,
        weightOptions: Array.from(new Set(weightPrices.map(wp => `${wp.weightLabel || '기본'}: AED ${wp.price} (${wp.available ? '재고있음' : '품절'})`))),
        rawSpecs: specs
      };

      processedList.push(record);
      process.stdout.write(`[${i + 1}/${rawProducts.length}] ${p.title.substring(0, 30)}... Notes: ${tastingNotes ? 'OK' : 'MISSING'}\n`);

      // Gentle pause of 80ms to avoid burst rate-limit
      await new Promise(r => setTimeout(r, 80));
    }

    fs.writeFileSync(`c:/cowork/coffee/${cName}_robust.json`, JSON.stringify(processedList, null, 2));
    console.log(`Saved ${cName}_robust.json successfully!`);
  }
}

processAllCollectionsRobust();
