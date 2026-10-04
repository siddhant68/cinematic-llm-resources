// Pinterest harvester. Run with the built-in browser's javascript tool on a Pinterest SEARCH page:
//   https://www.pinterest.com/search/pins/?q=<url-encoded query>&filter_genai=true      (filter_genai=true = "Less AI")
// It scrolls `screens` times, collects every pin with its thumbnail path and alt text, and returns lines:
//   <pinId> <pinimg path> <alt text>
// Paste the lines (without the first "N pins" header) into <work>/pinterest/<group>/list.txt, then run contact_sheet.py.
// Proven on reels 009/010 and Violet (40-50 pins per search after 3-4 screens).
(async (screens = 4) => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const out = [], seen = new Set();
  const collect = () => document.querySelectorAll('a[href*="/pin/"]').forEach(a => {
    const m = a.href.match(/\/pin\/(\d+)/);
    const img = a.querySelector('img[src*="i.pinimg.com"]');
    if (!m || !img || seen.has(m[1])) return;
    const path = img.src.split(/i\.pinimg\.com\/[^/]+\//)[1];
    if (!path) return;
    seen.add(m[1]);
    out.push(m[1] + ' ' + path + ' ' + (img.alt || '').replace(/\s+/g, ' ').slice(0, 120));
  });
  collect();
  for (let i = 0; i < screens; i++) { window.scrollBy(0, innerHeight * 0.9); await sleep(1400); collect(); }
  return out.length + ' pins\n' + out.join('\n');
})()
