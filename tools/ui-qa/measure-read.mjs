import { chromium } from "playwright";
// Checks that the Read spread (slide + start of its explanation) fits above the bottom bar.
const BASE = process.env.BASE_URL ?? "http://localhost:3103";
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
const sizes = [[1440, 900, false], [1366, 768, false], [1280, 720, false], [390, 844, true], [360, 740, true]];
for (const [w, h, mobile] of sizes) {
  for (const [sem, hash] of [["fall2026", "#/lecture/cells/11"], ["fall2026", "#/lecture/circulation/13"], ["fall2025", "#/lecture/circulation/4"]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile });
    const page = await ctx.newPage();
    await page.goto(BASE + "/");
    await page.evaluate((s) => localStorage.setItem("bio103-selected-semester", s), sem);
    await page.goto(BASE + "/" + hash); await page.reload();
    await page.waitForSelector(".slide-title"); await page.waitForTimeout(600);
    const r = await page.evaluate(() => {
      const b = (sel) => { const e = document.querySelector(sel); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.bottom), Math.round(r.width), Math.round(r.height)]; };
      const firstText = document.querySelector(".textpane p, .textpane li");
      return { spread: b(".spread"), img: b(".figure-page img"), cap: b(".figure-page figcaption"), fig: b(".figure-page"), bar: b(".bar"), title: b(".slide-title"), text: firstText ? Math.round(firstText.getBoundingClientRect().top) : null, strip: b(".strip"), overflow: document.documentElement.scrollWidth > innerWidth };
    });
    const ok = mobile ? (r.text + 20 <= r.bar[0]) : (r.fig[1] <= r.bar[0]);
    console.log(`${w}x${h} ${sem} ${hash}`, JSON.stringify(r), ok ? "OK" : "OVER");
    await ctx.close();
  }
}
await browser.close();
