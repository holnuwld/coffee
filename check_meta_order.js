const fs = require('fs');
const html = fs.readFileSync('c:/cowork/coffee/auromar.html', 'utf8');
const m1 = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i);
const m2 = html.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i);
console.log('m1 (name first):', m1 ? m1[1] : 'none');
console.log('m2 (content first):', m2 ? m2[1] : 'none');
