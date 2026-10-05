const fs = require('fs');

async function testPattern() {
  const handles = [
    'panama-abu-coffee-geisha-washed-lot-2690',
    'panama-hacienda-la-esmeralda-mario-arriba-4-nb',
    'panama-finca-los-cenizos-geisha-washed-gw208',
    'panama-finca-nuguo-geisha-washed-lot-841',
    'panama-kotowa-coffee-las-brujas-lot-6934',
    'panama-santamaria-estate-geisha-df-washed',
    'panama-spectrum',
    'panama-symbiosis',
    'ethiopia-alo-village-archers-lot-1-sfw'
  ];
  for (const h of handles) {
    const res = await fetch('https://archerscoffee.com/products/' + h, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const html = await res.text();
    const metaDesc = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
    console.log(h, '-->', metaDesc ? metaDesc[1] : 'none');
  }
}
testPattern();
