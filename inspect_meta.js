const fs = require('fs');

async function checkSample() {
  const handles = [
    'colombia-las-margaritas-geisha-hybrid-washed',
    'colombia-letty-finca-el-paraiso',
    'colombia-luna-finca-el-paraiso',
    'costa-rica-hacienda-copey-don-ks-geisha-lot-131',
    'costa-rica-hacienda-copey-itadaki-geisha-honey-lot-182',
    'panama-elida-estate-geisha-plano-2801'
  ];

  for (const h of handles) {
    const url = `https://archerscoffee.com/products/${h}`;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    const html = await res.text();
    const metaDesc = html.match(/<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
    console.log(`\n=== Handle: ${h} ===`);
    console.log('meta desc:', metaDesc ? metaDesc[1] : 'none');
  }
}

checkSample();
