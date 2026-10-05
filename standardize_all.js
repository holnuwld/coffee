const fs = require('fs');

// Load raw robust datasets
const micro2026 = JSON.parse(fs.readFileSync('c:/cowork/coffee/microlot-2026_robust.json', 'utf8'));
const microReserve2025 = JSON.parse(fs.readFileSync('c:/cowork/coffee/microlot-reserve-2025_robust.json', 'utf8'));
const comp2025 = JSON.parse(fs.readFileSync('c:/cowork/coffee/competition-series-2025_robust.json', 'utf8'));

// Fix India - Pearl Mountain Lot RM 59 in micro2026
const indiaItem = micro2026.find(p => p.handle === 'india-pearl-mountain-lot-rm-59');
if (indiaItem) {
  indiaItem.country = 'India';
  indiaItem.farm = 'Ratnagiri Estate';
  indiaItem.location = 'Chikmagalur, Karnataka';
  indiaItem.variety = 'Catuai';
  indiaItem.process = 'CM Intenso Natural';
  indiaItem.producer = 'Ashok Patre';
  indiaItem.altitude = '1,340 masl';
  indiaItem.roast = 'Filter | Espresso (▪▫▫)';
}

// Function to determine Korea availability & price
function getKoreaInfo(product) {
  const title = product.title.toLowerCase();
  const handle = product.handle.toLowerCase();

  // 1. Cafe Granja La Esperanza Cerro Azul Geisha Hybrid Washed
  if (handle.includes('cerro-azul-geisha-hybrid-washed')) {
    return {
      koreaSeller: '엠아이커피(생두) / 언스페셜티·국내 스페셜티 로스터리 시즌 출시',
      koreaLink: 'https://micoffee.co.kr/product/detail.html?product_no=1862',
      koreaPrice: '약 35,000원 ~ 45,000원 (100g 기준, 시즌 한정)'
    };
  }

  // 2. Finca El Paraiso Letty
  if (handle.includes('colombia-letty-finca-el-paraiso')) {
    return {
      koreaSeller: '커피리브레 / 모모스커피 / 언스페셜티 (시즌 기획전)',
      koreaLink: 'https://coffeelibre.kr',
      koreaPrice: '약 25,000원 ~ 32,000원 (100g 기준)'
    };
  }

  // 3. Finca El Paraiso Luna
  if (handle.includes('colombia-luna-finca-el-paraiso')) {
    return {
      koreaSeller: '국내 스페셜티 로스터리 (엘파라이소 시리즈 기획)',
      koreaLink: 'https://coffeelibre.kr',
      koreaPrice: '약 25,000원 ~ 30,000원 (100g 기준)'
    };
  }

  // 4. Finca El Paraiso Caturra Chiroso
  if (handle.includes('colombia-caturra-chiroso-finca-el-paraiso')) {
    return {
      koreaSeller: '국내 스페셜티 로스터리 (시즌 기획전)',
      koreaLink: 'https://unspecialty.com',
      koreaPrice: '약 28,000원 ~ 35,000원 (100g 기준)'
    };
  }

  // 5. Panama Finca Auromar Geisha Washed Peaberry
  if (handle.includes('panama-finca-auromar-malla-geisha-washed-peaberry')) {
    return {
      koreaSeller: '코에커피스펙트럼 / 엠아이커피 (오로마르 옥션 및 일반 워시드 취급 이력)',
      koreaLink: 'https://micoffee.co.kr',
      koreaPrice: '약 45,000원 ~ 60,000원 (100g 기준, 피베리 한정)'
    };
  }

  // 6. Panama Elida Geisha Washed Plano / Loma
  if (handle.includes('panama-elida-estate-geisha')) {
    return {
      koreaSeller: '커피리브레 / 180커피로스터스 (엘리다 에스테이트 게이샤 수입 이력)',
      koreaLink: 'https://coffeelibre.kr',
      koreaPrice: '약 50,000원 ~ 70,000원 (100g 기준)'
    };
  }

  // 7. Panama Hacienda La Esmeralda 시리즈 (Mario, Fundador, Cabana 등)
  if (handle.includes('panama-hacienda-la-esmeralda')) {
    return {
      koreaSeller: '엠아이커피 / 커피리브레 (에스메랄다 프라이빗/스페셜 랏 취급 이력)',
      koreaLink: 'https://micoffee.co.kr',
      koreaPrice: '약 40,000원 ~ 65,000원 (100g 기준)'
    };
  }

  // 8. Ecuador Finca Soledad Sidra / Typica Mejorado
  if (handle.includes('finca-soledad')) {
    return {
      koreaSeller: '국내 스페셜티 로스터리 (모모스 / 베르크 등 페페 아르궤요 랏 취급 이력)',
      koreaLink: 'https://momos.co.kr',
      koreaPrice: '약 35,000원 ~ 45,000원 (100g 기준)'
    };
  }

  // 9. Ethiopia Daye Bensa Hamasho
  if (handle.includes('hamasho-village') || handle.includes('daye-bensa')) {
    if (handle.includes('archers-lot')) {
      return {
        koreaSeller: '없음 (Archers Coffee 독점 랏)',
        koreaLink: '',
        koreaPrice: '없음'
      };
    }
    return {
      koreaSeller: '엠아이커피 / 일반 스페셜티 로스터리 (다예벤사 하마쇼 일반랏 취급)',
      koreaLink: 'https://micoffee.co.kr',
      koreaPrice: '약 18,000원 ~ 25,000원 (200g 기준)'
    };
  }

  // 10. Ethiopia Alo Coffee / Alo Village
  if (handle.includes('alo-coffee') || handle.includes('alo-village')) {
    if (handle.includes('archers')) {
      return {
        koreaSeller: '없음 (Archers Coffee 독점 랏)',
        koreaLink: '',
        koreaPrice: '없음'
      };
    }
    return {
      koreaSeller: '국내 스페셜티 샵 (타미루 타데세 알로 커피 일반랏 취급 이력)',
      koreaLink: 'https://unspecialty.com',
      koreaPrice: '약 30,000원 ~ 40,000원 (100g 기준)'
    };
  }

  // Default: 국내 동일 원두 없음
  return {
    koreaSeller: '없음 (국내 정식 유통처 없음 / Archers 독점 랏)',
    koreaLink: '',
    koreaPrice: '없음'
  };
}

// Format and sanitize each product
function standardizeProduct(p, colCategory) {
  const kInfo = getKoreaInfo(p);

  // Clean country
  let country = p.country;
  if (!country || country === '기타') {
    if (p.title.includes('Panama')) country = 'Panama';
    else if (p.title.includes('Ethiopia')) country = 'Ethiopia';
    else if (p.title.includes('Colombia')) country = 'Colombia';
    else if (p.title.includes('Costa Rica')) country = 'Costa Rica';
    else if (p.title.includes('Ecuador')) country = 'Ecuador';
    else if (p.title.includes('Guatemala')) country = 'Guatemala';
    else if (p.title.includes('Yemen')) country = 'Yemen';
    else if (p.title.includes('Brazil')) country = 'Brazil';
    else if (p.title.includes('India')) country = 'India';
    else country = '기타';
  }

  return {
    id: p.id,
    title: p.title,
    category: colCategory,
    country,
    location: p.location || '미표기',
    farm: p.farm || '미표기',
    producer: p.producer || '미표기',
    variety: p.variety || '미표기',
    process: p.process || '미표기',
    altitude: p.altitude || '미표기',
    roast: p.roast || 'Filter',
    tastingNotes: p.tastingNotes || '미표기',
    weight: p.weightDisplay || '100g',
    priceAED: p.priceAED,
    pricePer100g: p.pricePer100g,
    available: p.available,
    koreaSeller: kInfo.koreaSeller,
    koreaLink: kInfo.koreaLink,
    koreaPrice: kInfo.koreaPrice,
    url: p.url,
    weightOptions: p.weightOptions || []
  };
}

const cleanedMicro2026 = micro2026.map(p => standardizeProduct(p, 'Microlot 2026'));
const cleanedMicroReserve2025 = microReserve2025.map(p => standardizeProduct(p, 'Microlot Reserve 2025'));
const cleanedComp2025 = comp2025.map(p => standardizeProduct(p, 'Competition Series 2025'));

fs.writeFileSync('c:/cowork/coffee/standardized_micro2026.json', JSON.stringify(cleanedMicro2026, null, 2));
fs.writeFileSync('c:/cowork/coffee/standardized_microReserve2025.json', JSON.stringify(cleanedMicroReserve2025, null, 2));
fs.writeFileSync('c:/cowork/coffee/standardized_comp2025.json', JSON.stringify(cleanedComp2025, null, 2));

console.log('Standardized successfully!');
console.log(`Microlot 2026: ${cleanedMicro2026.length} items`);
console.log(`Microlot Reserve 2025: ${cleanedMicroReserve2025.length} items`);
console.log(`Competition Series 2025: ${cleanedComp2025.length} items`);
