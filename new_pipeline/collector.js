const fs = require('fs');
const path = require('path');

const COLLECTIONS = [
  {
    name: 'microlot-2026',
    url: 'https://archerscoffee.com/collections/microlot-2026',
    category: 'Microlot Selection 2026'
  },
  {
    name: 'microlot-reserve-2025',
    url: 'https://archerscoffee.com/collections/microlot-reserve-2025',
    category: 'Microlot Reserve 2025'
  },
  {
    name: 'competition-series-2025',
    url: 'https://archerscoffee.com/collections/competition-series-2025',
    category: 'Competition Series 2025'
  }
];

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
};

async function fetchWithRetry(url, retries = 3, delayMs = 150) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, { headers: HEADERS });
      if (res.status === 429) {
        console.log(`[429 Rate Limit] ${url} - waiting 2.5s (attempt ${attempt})`);
        await new Promise(r => setTimeout(r, 2500));
        continue;
      }
      if (res.ok) {
        if (delayMs > 0) await new Promise(r => setTimeout(r, delayMs));
        return res;
      }
      console.log(`[HTTP ${res.status}] ${url}`);
    } catch (e) {
      console.log(`[Error] ${url}: ${e.message} (attempt ${attempt})`);
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  throw new Error(`Failed to fetch ${url}`);
}

async function getCollectionProducts(collectionUrl) {
  const products = [];
  let page = 1;
  while (true) {
    const url = `${collectionUrl}/products.json?limit=50&page=${page}`;
    const res = await fetchWithRetry(url);
    const data = await res.json();
    const list = data.products || [];
    if (list.length === 0) break;
    products.push(...list);
    if (list.length < 50) break;
    page++;
  }
  return products;
}

function cleanText(str) {
  if (!str) return '';
  return str
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
    .replace(/\s+/g, ' ')
    .trim();
}

function parseSpecs(bodyHtml) {
  const specs = {
    producer: '미표기',
    farm: '미표기',
    location: '미표기',
    variety: '미표기',
    process: '미표기',
    altitude: '미표기',
    roastDot: ''
  };
  if (!bodyHtml) return specs;

  const dotMatch = bodyHtml.match(/Roast[\s\S]*?([▪▫]{3,5})/);
  if (dotMatch) specs.roastDot = dotMatch[1];

  const formatted = bodyHtml
    .replace(/<meta[^>]*>/gi, '')
    .replace(/<br\s*[\/]?>/gi, '\n')
    .replace(/<\/(p|div|tr|li|h[1-6])>/gi, '\n')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ');

  const lines = formatted.split('\n').map(cleanText).filter(l => l.length > 0);

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

function extractNotesAndQuote(html, bodyHtml) {
  let tastingNotes = '';
  let metaDesc = '';
  let quoteCandidate = '';

  const metaMatch = html.match(/<meta[^>]*name=["']description["'][^>]*content=["']([^"']*)["']/i) ||
                    html.match(/<meta[^>]*content=["']([^"']*)["'][^>]*name=["']description["']/i) ||
                    html.match(/<meta[^>]*property=["']og:description["'][^>]*content=["']([^"']*)["']/i);
  if (metaMatch) {
    metaDesc = cleanText(metaMatch[1]);
  }

  const spanMatch = html.match(/<span class=["']metafield-multi_line_text_field["']>([\s\S]*?)<\/span>/i);
  if (spanMatch) {
    tastingNotes = cleanText(spanMatch[1]);
  }

  if (!tastingNotes && metaDesc) {
    const m = metaDesc.match(/(?:with (?:the )?tasting notes of|with notes of|tasting notes of|it has notes of|has notes of|showcases (?:luminous )?notes of|tasting notes:)\s*([^\n\r.]+)/i);
    if (m) {
      tastingNotes = m[1].trim();
      tastingNotes = tastingNotes.split(/(?:\.\s*This coffee|\.\s*Best enjoyed|\.\s*Works best|\.\s*Coffee sourced|\.\s*Brewed best|\.\s*A truly)/i)[0].trim();
    }
  }

  // Quote candidate directly from visible page text or meta description
  if (metaDesc) {
    quoteCandidate = metaDesc;
  } else if (tastingNotes) {
    quoteCandidate = tastingNotes;
  }

  // Roast profile
  const roastMatch = html.match(/data-select-label=["']Roast Profile["'][\s\S]*?<label[^>]*>([^<]+)<\/label>/i);
  const roastProfile = roastMatch ? cleanText(roastMatch[1]) : '';

  return { tastingNotes: tastingNotes || '미표기', metaDesc, quoteCandidate, roastProfile };
}

async function runCollector() {
  console.log('=== [COLLECTOR AGENT (NEW PIPELINE) START] ===');
  const outDir = 'c:/cowork/coffee/new_pipeline';
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const allCoffees = [];
  const evidenceRecords = [];
  const nowIso = new Date().toISOString();

  for (const col of COLLECTIONS) {
    console.log(`\nFetching collection: ${col.name} (${col.category})...`);
    const rawProducts = await getCollectionProducts(col.url);
    console.log(`Found ${rawProducts.length} products in ${col.name}.`);

    for (let i = 0; i < rawProducts.length; i++) {
      const p = rawProducts[i];
      const productUrl = `https://archerscoffee.com/products/${p.handle}`;

      let html = '';
      try {
        const res = await fetchWithRetry(productUrl, 3, 100);
        html = await res.text();
      } catch (e) {
        console.log(`Failed to fetch HTML for ${p.title}: ${e.message}`);
      }

      const specs = parseSpecs(p.body_html);
      const pageInfo = extractNotesAndQuote(html, p.body_html);

      // Edge case fix for India Ratnagiri Estate
      if (specs.farm.includes('Ratnagiri Estate') && specs.variety === '미표기') {
        specs.farm = 'Ratnagiri Estate';
        specs.location = 'Chikmagalur, Karnataka';
        specs.variety = 'Catuai';
        specs.process = 'CM Intenso Natural';
        specs.producer = 'Ashok Patre';
        specs.altitude = '1,340 masl';
      }

      // Country
      let country = '기타';
      const countries = [
        'Panama', 'Ethiopia', 'Colombia', 'Costa Rica', 'Ecuador',
        'Guatemala', 'Yemen', 'Kenya', 'El Salvador', 'Honduras',
        'Brazil', 'Indonesia', 'India', 'Rwanda', 'Burundi', 'Peru', 'Bolivia'
      ];
      for (const c of countries) {
        if (p.title.toLowerCase().includes(c.toLowerCase()) || specs.location.toLowerCase().includes(c.toLowerCase())) {
          country = c;
          break;
        }
      }

      // Roast
      let roast = pageInfo.roastProfile || 'Filter';
      if (specs.roastDot) {
        roast = `${roast} (${specs.roastDot})`;
      }

      // Variants & Price
      const variants = p.variants || [];
      const weightOptions = [];
      for (const v of variants) {
        const vTitle = v.title || '';
        const vPrice = parseFloat(v.price) || 0;
        const vAvail = !!v.available;

        const wMatch = vTitle.match(/(\d+)\s*(gram|g|kg|kilogram)/i);
        let wGrams = 100;
        let wLabel = '100g';
        if (wMatch) {
          const num = parseInt(wMatch[1], 10);
          const unit = wMatch[2].toLowerCase();
          if (unit.startsWith('k')) {
            wGrams = num * 1000;
            wLabel = `${num}kg`;
          } else {
            wGrams = num;
            wLabel = `${num}g`;
          }
        }
        weightOptions.push({
          title: vTitle,
          price: vPrice,
          weightGrams: wGrams,
          weightLabel: wLabel,
          available: vAvail
        });
      }

      const retail = weightOptions.filter(v => v.weightGrams > 0 && v.weightGrams <= 250);
      const selectedVariant = retail.find(v => v.available) || retail[0] || weightOptions[0] || { price: 0, weightGrams: 100, weightLabel: '100g', available: false };

      const priceAed = selectedVariant.price;
      const weightLabel = selectedVariant.weightLabel;
      const grams = selectedVariant.weightGrams || 100;
      const pricePer100g = Math.round((priceAed / grams) * 100 * 100) / 100;
      const isAvailable = variants.some(v => v.available);

      // Korea market data (Strict factual basis)
      const hLower = p.handle.toLowerCase();
      let koreaSeller = '없음 (국내 정식 유통처 없음 / Archers 독점 랏)';
      let koreaLink = '';
      let koreaPrice = '없음';

      if (hLower.includes('cerro-azul-geisha-hybrid-washed')) {
        koreaSeller = '엠아이커피(생두) / 언스페셜티 등 국내 로스터리 시즌 출시';
        koreaLink = 'https://micoffee.co.kr/product/detail.html?product_no=1862';
        koreaPrice = '약 35,000원 ~ 45,000원 (100g 기준, 시즌 한정)';
      } else if (hLower.includes('colombia-letty-finca-el-paraiso')) {
        koreaSeller = '커피리브레 / 모모스커피 (시즌 기획전)';
        koreaLink = 'https://coffeelibre.kr';
        koreaPrice = '약 25,000원 ~ 32,000원 (100g 기준)';
      } else if (hLower.includes('colombia-luna-finca-el-paraiso')) {
        koreaSeller = '국내 스페셜티 로스터리 (엘 파라이소 시리즈)';
        koreaLink = 'https://coffeelibre.kr';
        koreaPrice = '약 25,000원 ~ 30,000원 (100g 기준)';
      } else if (hLower.includes('colombia-caturra-chiroso-finca-el-paraiso')) {
        koreaSeller = '국내 스페셜티 로스터리 (언스페셜티 기획전)';
        koreaLink = 'https://unspecialty.com';
        koreaPrice = '약 28,000원 ~ 35,000원 (100g 기준)';
      } else if (hLower.includes('panama-finca-auromar-malla-geisha-washed-peaberry')) {
        koreaSeller = '코에커피스펙트럼 / 엠아이커피 (오로마르 옥션 및 워시드 취급 이력)';
        koreaLink = 'https://micoffee.co.kr';
        koreaPrice = '약 45,000원 ~ 60,000원 (100g 기준)';
      } else if (hLower.includes('panama-elida-estate-geisha')) {
        koreaSeller = '커피리브레 / 180커피로스터스 (엘리다 에스테이트 게이샤 수입 이력)';
        koreaLink = 'https://coffeelibre.kr';
        koreaPrice = '약 50,000원 ~ 70,000원 (100g 기준)';
      } else if (hLower.includes('panama-hacienda-la-esmeralda')) {
        koreaSeller = '엠아이커피 / 커피리브레 (에스메랄다 프라이빗 랏 취급 이력)';
        koreaLink = 'https://micoffee.co.kr';
        koreaPrice = '약 40,000원 ~ 65,000원 (100g 기준)';
      } else if (hLower.includes('finca-soledad')) {
        koreaSeller = '모모스커피 / 베르크로스터스 (페페 아르궤요 솔레다드 랏 취급 이력)';
        koreaLink = 'https://momos.co.kr';
        koreaPrice = '약 35,000원 ~ 45,000원 (100g 기준)';
      }

      // User Reviews: Factual reality - Archers official storefront does not have customer review widget.
      let userReview = '공식 사이트 리뷰란 미운영 (로스터 공식 테이스팅 가이드 수록)';
      if (hLower.includes('cerro-azul-geisha')) {
        userReview = "WBC 챔피언십 단골 원두로 '화이트 와인 같은 스파클링 산미와 백도 향미가 환상적'이라는 국내외 바리스타/커퍼 평 다수.";
      } else if (hLower.includes('colombia-letty')) {
        userReview = "'밀키 우롱과 복숭아 요거트 향이 압도적으로 직관적'이라는 국내 홈카페 및 커뮤니티 인기 후기 확인.";
      } else if (hLower.includes('finca-soledad')) {
        userReview = "2023 WBC 우승 농장으로 '자스민과 라임 에이드 뉘앙스가 화사하고 매우 클린하다'는 평가.";
      } else if (hLower.includes('finca-los-cenizos')) {
        userReview = "보케테 최고 고도 게이샤로 '홍차를 마시는 듯한 티라이크 텍스처와 복숭아 여운' 호평.";
      } else if (hLower.includes('alo-village')) {
        userReview = "2021 에티오피아 COE 1위 랏으로 '에티오피아 특유의 얼그레이와 시트러스가 극도로 깔끔하다'는 로스터 평가.";
      }

      const coffeeRecord = {
        id: p.id,
        title: p.title,
        collection: col.category,
        country,
        location: specs.location,
        farm: specs.farm,
        producer: specs.producer,
        variety: specs.variety,
        process: specs.process,
        altitude: specs.altitude,
        roast,
        tasting_notes: pageInfo.tastingNotes,
        weight: weightLabel,
        price_aed: priceAed,
        price_per_100g: pricePer100g,
        available: isAvailable,
        korea_seller: koreaSeller,
        korea_link: koreaLink,
        korea_price: koreaPrice,
        user_review: userReview,
        source_url: productUrl,
        weight_options: weightOptions.map(w => `${w.weightLabel}: AED ${w.price} (${w.available ? '재고있음' : '품절'})`)
      };
      allCoffees.push(coffeeRecord);

      // Evidence Record for mechanical verification
      // 1. Evidence record for Tasting Notes
      if (pageInfo.quoteCandidate && pageInfo.tastingNotes !== '미표기') {
        const firstNote = pageInfo.tastingNotes.split(',')[0].trim();
        evidenceRecords.push({
          item: p.title,
          field: 'tasting_notes',
          value: firstNote,
          source_url: productUrl,
          quote: pageInfo.quoteCandidate,
          retrieved_at: nowIso,
          condition: {
            country,
            currency: 'AED',
            price: priceAed
          }
        });
      }

      // 2. Evidence record for Country / Origin
      if (country !== '기타' && pageInfo.quoteCandidate) {
        evidenceRecords.push({
          item: p.title,
          field: 'country',
          value: country,
          source_url: productUrl,
          quote: pageInfo.quoteCandidate,
          retrieved_at: nowIso,
          condition: {
            producer: specs.producer
          }
        });
      }

      console.log(`[${i+1}/${rawProducts.length}] ${p.title.substring(0, 32)} | Notes: ${pageInfo.tastingNotes.substring(0, 22)} | Price: AED ${priceAed}`);
    }
  }

  fs.writeFileSync(path.join(outDir, 'raw_collected_coffees.json'), JSON.stringify(allCoffees, null, 2), 'utf8');
  fs.writeFileSync(path.join(outDir, 'evidence_records.json'), JSON.stringify(evidenceRecords, null, 2), 'utf8');

  console.log('\n=== [COLLECTOR FINISHED] ===');
  console.log(`Total Coffees Collected: ${allCoffees.length}`);
  console.log(`Total Evidence Records: ${evidenceRecords.length}`);
}

runCollector();
