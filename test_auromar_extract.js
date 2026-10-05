const fs = require('fs');

function extractTastingNotesFromMeta(text) {
  if (!text) return '';
  const cleaned = text
    .replace(/&amp;/g, '&')
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");

  const regex = /(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^.\n\r]+)/i;
  const match = cleaned.match(regex);
  if (match && match[1]) {
    let notes = match[1].trim();
    notes = notes.split(/(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)/i)[0].trim();
    notes = notes.replace(/\.+$/, '').trim();
    return notes;
  }
  return '';
}

const html = fs.readFileSync('c:/cowork/coffee/auromar.html', 'utf8');

// 1. Metafield span
let notes = '';
const metafieldMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
if (metafieldMatch && metafieldMatch[1]) {
  notes = metafieldMatch[1].replace(/<[^>]+>/g, '').trim();
  console.log('from metafield:', notes);
}

// 2. Meta description
const metaDescMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
                      html.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i);
console.log('metaDescMatch:', metaDescMatch ? metaDescMatch[1] : 'none');
if (metaDescMatch) {
  notes = extractTastingNotesFromMeta(metaDescMatch[1]);
  console.log('extracted notes from desc:', notes);
}
