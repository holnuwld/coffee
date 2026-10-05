const fs = require('fs');

async function debugMissingNotes() {
  const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/competition-series-2025_parsed.json', 'utf8'));
  const missing = comp.filter(p => !p.tastingNotes);
  console.log(`Total missing notes in competition series: ${missing.length}`);

  // Inspect first 3 missing items
  for (let i = 0; i < Math.min(3, missing.length); i++) {
    const item = missing[i];
    console.log(`\n--- Inspecting: ${item.title} (${item.handle}) ---`);
    const url = item.url;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const html = await res.text();

    fs.writeFileSync(`c:/cowork/coffee/debug_item_${i}.html`, html);

    // Look for any text mentioning notes, flavor, taste, cup
    const lines = html.split('\n');
    const matchedLines = [];
    lines.forEach((l, idx) => {
      if (/taste|flavor|notes|cup|profile|aroma/i.test(l)) {
        if (l.trim().length > 0 && l.trim().length < 250) {
          matchedLines.push(`L${idx}: ${l.trim()}`);
        }
      }
    });
    console.log(`Found ${matchedLines.length} matched lines. Sample 10:`);
    console.log(matchedLines.slice(0, 10).join('\n'));

    // Check meta tags specifically
    const metaDesc = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i);
    const ogDesc = html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']*)["']/i);
    console.log('meta description:', metaDesc ? metaDesc[1] : 'none');
    console.log('og description:', ogDesc ? ogDesc[1] : 'none');
  }
}

debugMissingNotes();
