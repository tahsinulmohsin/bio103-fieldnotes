import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
const BASE = process.env.BASE_URL ?? "http://localhost:3103";
// Screenshots every stage at desktop and phone sizes in both themes, and records overflow,
// text under 12px, small touch targets and axe (WCAG 2.2 AA) results in <out>/results.json.
const OUT = process.argv[2] ?? "out";
fs.mkdirSync(OUT, { recursive: true });
const R = { screens: {}, axe: {} };
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
async function ctx({ width, height, theme, mobile = false, semester = "fall2026", unlock = [], progressExtra = null }) {
  const context = await browser.newContext({ viewport: { width, height }, colorScheme: theme, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: 1 });
  await context.addInitScript(({ theme, semester }) => { try { localStorage.setItem("bio103-theme", theme); localStorage.setItem("bio103-selected-semester", semester); } catch {} }, { theme, semester });
  const page = await context.newPage();
  await page.goto(BASE + "/#/");
  if (unlock.length) {
    await page.evaluate(async ({ unlock, semester, extra }) => {
      const key = semester === "fall2026" ? "bio103-progress-fall2026" : "bio103-fieldnotes-v1";
      const p = { version: 1, modules: {}, lastModule: unlock[0] };
      for (const id of unlock) {
        const m = await fetch(`/course-data/${semester}/${id}`).then(r => r.json());
        p.modules[id] = { read: m.slides.slice(0, Math.floor(m.slides.length * 0.6)).map(s => s.id), known: m.flashcards.slice(0, 3).map(c => c.id), again: m.flashcards.slice(3, 5).map(c => c.id), missed: m.quiz.slice(0, 2).map(q => q.id), shortMissed: [], bestScore: 70, attempts: 1, lastSlide: 10 };
      }
      localStorage.setItem(key, JSON.stringify(p));
    }, { unlock, semester, extra: progressExtra });
  }
  return { context, page };
}
async function open(page, hash) { await page.goto(BASE + "/" + hash); await page.waitForTimeout(700); }
async function measure(page, name, mobile) {
  R.screens[name] = await page.evaluate((mobile) => {
    const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
    let tiny = []; const fams = new Set();
    for (const e of document.querySelectorAll("body *")) { if (!vis(e)) continue; if (![...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())) continue; const s = getComputedStyle(e); fams.add(s.fontFamily.split(",")[0]); if (parseFloat(s.fontSize) < 12) tiny.push(parseFloat(s.fontSize) + "px " + e.textContent.trim().slice(0, 24)); }
    const small = []; for (const e of document.querySelectorAll("button, a, input, textarea, [role=button]")) { if (!vis(e)) continue; const r = e.getBoundingClientRect(); const lim = mobile ? 44 : 24; if (r.width < lim || r.height < lim) small.push(Math.round(r.width) + "x" + Math.round(r.height) + " " + (e.getAttribute("aria-label") || e.textContent).trim().slice(0, 24)); }
    return { overflowX: document.documentElement.scrollWidth > innerWidth, tiny: tiny.length, tinySamples: tiny.slice(0, 6), small: small.length, smallSamples: small.slice(0, 8), fonts: [...fams] };
  }, mobile);
}
async function axe(page, name) { const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]).analyze(); R.axe[name] = r.violations.map(v => ({ id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes.slice(0, 3).map(x => (x.any[0]?.message || "").slice(0, 140) + " @ " + x.target.join(" ")) })); }
const shot = (page, name, full = false) => page.screenshot({ path: `${OUT}/${name}.png`, fullPage: full });
const D = { width: 1440, height: 900 }, M = { width: 390, height: 844, mobile: true };
try {
  for (const theme of ["light", "dark"]) {
    let { context, page } = await ctx({ ...D, theme, unlock: ["cells"] });
    await open(page, "#/"); await shot(page, `home-desktop-${theme}`); await shot(page, `home-desktop-${theme}-full`, true); await measure(page, `home-desktop-${theme}`); await axe(page, `home-${theme}`);
    await open(page, "#/lecture/cells/11"); await page.waitForSelector(".slide-title"); await page.waitForTimeout(400); await shot(page, `read-desktop-${theme}`); await measure(page, `read-desktop-${theme}`); await axe(page, `read-${theme}`);
    await open(page, "#/lecture/cells/practise"); await page.waitForSelector(".option"); await page.locator(".option").nth(0).click(); await page.getByRole("button", { name: "Check" }).click(); await page.waitForTimeout(400); await shot(page, `practise-desktop-${theme}`); await axe(page, `practise-${theme}`);
    await context.close();
  }
  let { context, page } = await ctx({ ...D, theme: "light", unlock: ["cells"] });
  await open(page, "#/lecture/cells/recall"); await page.waitForSelector(".card"); await shot(page, "recall-front-desktop-light"); await page.keyboard.press("Space"); await page.waitForTimeout(200); await shot(page, "recall-back-desktop-light"); await measure(page, "recall-desktop-light"); await axe(page, "recall-light");
  await open(page, "#/lecture/circulation/practise"); await page.waitForSelector(".modes"); await page.getByRole("button", { name: /Short answer/ }).click(); await page.waitForTimeout(200);
  for (let i = 0; i < 20; i++) { const t = await page.locator("#sa-prompt").textContent(); if (/Artery and Vein/.test(t)) break; await page.getByRole("button", { name: /Show the slide/ }).click(); await page.getByRole("button", { name: "Had it" }).click(); }
  await page.getByRole("button", { name: /Show the slide/ }).click(); await page.waitForTimeout(200); await shot(page, "short-answer-desktop-light", true); await axe(page, "short-light");
  await open(page, "#/progress"); await shot(page, "progress-desktop-light"); await axe(page, "progress-light");
  await open(page, "#/sources"); await shot(page, "sources-desktop-light"); await axe(page, "sources-light");
  await page.evaluate(() => localStorage.setItem("bio103-selected-semester", "fall2025")); await open(page, "#/lecture/circulation/4"); await page.reload(); await page.waitForSelector(".slide-title"); await page.waitForTimeout(300); await shot(page, "read-fall2025-desktop-light"); await axe(page, "read-fall2025-light");
  await context.close();
  ({ context, page } = await ctx({ ...M, theme: "light", unlock: ["cells"] }));
  await open(page, "#/"); await shot(page, "home-mobile-light"); await shot(page, "home-mobile-light-full", true); await measure(page, "home-mobile-light", true); await axe(page, "home-mobile-light");
  await open(page, "#/lecture/cells/11"); await page.waitForSelector(".slide-title"); await page.waitForTimeout(300); await shot(page, "read-mobile-light"); await shot(page, "read-mobile-light-full", true); await measure(page, "read-mobile-light", true);
  await page.getByRole("button", { name: "Menu" }).click(); await page.waitForTimeout(150); await shot(page, "menu-mobile-light");
  await context.close();
  ({ context, page } = await ctx({ ...M, theme: "dark", unlock: ["cells"] }));
  await open(page, "#/lecture/cells/practise"); await page.waitForSelector(".option"); await page.locator(".option").nth(1).click(); await page.getByRole("button", { name: "Check" }).click(); await page.waitForTimeout(400); await shot(page, "practise-mobile-dark"); await measure(page, "practise-mobile-dark", true); await axe(page, "practise-mobile-dark");
  await open(page, "#/lecture/cells/recall"); await page.waitForSelector(".card"); await shot(page, "recall-mobile-dark"); await measure(page, "recall-mobile-dark", true);
  await context.close();
} catch (e) { console.error("capture failed:", e.message.split("\n")[0]); }
fs.writeFileSync(`${OUT}/results.json`, JSON.stringify(R, null, 2));
await browser.close();
console.log("screens", Object.keys(R.screens).length, "axe", Object.keys(R.axe).length);
