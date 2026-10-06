from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

for fname in ['theespressolab_verified.html', 'theespressolab_mobile.html']:
    print(f"\n==================== Auditing {fname} ====================")
    with open(fname, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Broken images check
    imgs = soup.find_all('img')
    broken_imgs = [img['src'] for img in imgs if 'via.placeholder' in img.get('src', '') or not img.get('src')]
    print(f"1. Total images: {len(imgs)}, Placeholder/Empty count: {len(broken_imgs)}")
    if broken_imgs:
        print(f"   Broken sample: {broken_imgs[:3]}")

    # Check top rec images specifically
    rec_imgs = [img['src'] for img in soup.select('.rec-pkg-img, .m-card-img')]
    print(f"   Recommendation & card package images sample: {rec_imgs[:3]}")

    # 2. Hyperlinks in coffee names
    if 'theespressolab_verified.html' in fname:
        rec_title_links = soup.select('.rec-title-link')
        table_coffee_links = soup.select('.coffee-link')
        print(f"2. Rec card title links: {len(rec_title_links)} / 6 expected")
        print(f"   Table coffee title links: {len(table_coffee_links)} / 54 expected")
        for r_link in rec_title_links[:2]:
            print(f"   Sample rec link: text='{r_link.text.strip()}' href='{r_link.get('href')}'")
    else:
        m_title_links = soup.select('.m-title-link')
        print(f"2. Mobile card title links: {len(m_title_links)} / 54 expected")

    # 3. CSS check for table header clipping
    if 'theespressolab_verified.html' in fname:
        has_separate = 'border-collapse: separate' in html_content
        has_padding_top = '.data-table tbody tr:first-child td' in html_content
        print(f"3. Table clipping fix: border-collapse: separate? {has_separate}, first-child padding-top? {has_padding_top}")

    # 4. Roast profile explanation
    roast_badges = soup.find_all(text=re.compile(r'Filter \(Light'))
    has_roast_banner = 'The Espresso Lab 공식 로스팅 포인트' in html_content or '푸어오버' in html_content
    print(f"4. Roast badges count: {len(roast_badges)}, Roast banner present? {has_roast_banner}")

    # 5. Review links
    review_links = [a['href'] for a in soup.find_all('a') if 'reddit.com' in a.get('href', '') or 'home-barista.com' in a.get('href', '')]
    print(f"5. Authentic review links count: {len(review_links)}")
    if review_links:
        print(f"   Sample review link: {review_links[0]}")

    # 6. Korea shop links: check for unwanted naver search links
    naver_links = [a['href'] for a in soup.find_all('a') if 'naver.com' in a.get('href', '')]
    legit_korea_links = [a['href'] for a in soup.find_all('a') if 'korea-link' in a.get('class', []) or 'm-link' in a.get('class', [])]
    no_import_badges = soup.find_all(text=re.compile(r'국내 공식 미수입'))
    print(f"6. Unwanted Naver search links: {len(naver_links)} (Expected 0)")
    print(f"   Legitimate Korea shop links: {len(legit_korea_links)}")
    print(f"   '국내 공식 미수입' explicit count: {len(no_import_badges)}")

print("\nAudit completed!")
