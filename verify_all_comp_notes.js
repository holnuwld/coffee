const fs = require('fs');

function extractTastingNotesFromMeta(text) {
  if (!text) return '';
  // replace html entities
  const cleaned = text
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  const regex = /(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^.\n\r]+)/i;
  const match = cleaned.match(regex);
  if (match && match[1]) {
    let notes = match[1].trim();
    // cut off if any trailing sentence start
    notes = notes.split(/(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)/i)[0].trim();
    notes = notes.replace(/\.+$/, '').trim();
    return notes;
  }
  return '';
}

async function verifyAllCompetitionNotes() {
  const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/competition-series-2025_full.json', 'utf8'));
  console.log(`Checking all ${comp.length} items in competition series...`);

  let countWithNotes = 0;
  const missing = [];

  for (let i = 0; i < comp.length; i += 5) {
    const batch = comp.slice(i, i + 5);
    await Promise.all(batch.map(async p => {
      const url = `https://archerscoffee.com/products/${p.handle}`;
      const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
      const html = await res.text();

      // 1. Metafield span
      let notes = '';
      const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
      if (metafieldMatch && metafieldMatch[1]) {
        notes = metafieldMatch[1].replace(/<[^>]+>/g, '').trim();
      }

      // 2. Meta description
      if (!notes) {
        const metaDescMatch = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
        if (metaDescMatch && metaDescMatch[1]) {
          notes = extractTastingNotesFromMeta(metaDescMatch[1]);
        }
      }

      // 3. Twitter description
      if (!notes) {
        const twDescMatch = html.match(/<meta\s+name=["']twitter:description["']\s+content=["']([\s\S]*?)["']/i);
        if (twDescMatch && twDescMatch[1]) {
          notes = extractTastingNotesFromMeta(twDescMatch[1]);
        }
      }

      if (notes) {
        countWithNotes++;
      } else {
        missing.push({ title: p.title, handle: p.handle });
      }
    }));
  }

  console.log(`Total found notes: ${countWithNotes} / ${comp.length}`);
  if (missing.length > 0) {
    console.log(`Still missing ${missing.length} items:`, missing);
  }
}

verifyAllCompetitionNotes();
