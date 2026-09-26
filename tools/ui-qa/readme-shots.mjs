import { chromium } from "playwright";
import fs from "node:fs";
// Regenerates the screenshots used in the repository README (docs/screenshots/).
const BASE = process.env.BASE_URL ?? "http://localhost:3103";
const OUT = process.argv[2] ?? "../../docs/screenshots";
fs.mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });

async function page({ width, height, theme = "light", mobile = false }) {
  const context = await browser.newContext({ viewport: { width, height }, colorScheme: theme, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: 2 });
  await context.addInitScript((t) => { try { localStorage.setItem("bio103-theme", t); localStorage.setItem("bio103-selected-semester", "fall2026"); } catch {} }, theme);
  return { context, page: await context.newPage() };
}
const go = async (p, hash, selector) => { await p.goto(`${BASE}/${hash}`); await p.waitForSelector(selector); await p.waitForTimeout(2300); };

let s = await page({ width: 1440, height: 900 });
await go(s.page, "#/lecture/cells/11", ".slide-title");
await s.page.screenshot({ path: `${OUT}/read-desktop.png` });
await go(s.page, "#/lecture/cells/practise", ".option");
await s.page.locator(".option").nth(0).click();
await s.page.getByRole("button", { name: "Check" }).click();
await s.page.waitForTimeout(400);
await s.page.screenshot({ path: `${OUT}/practise-desktop.png` });
await go(s.page, "#/", ".nextup");
await s.page.screenshot({ path: `${OUT}/contents-desktop.png` });
await s.context.close();

s = await page({ width: 1440, height: 900, theme: "dark" });
await go(s.page, "#/lecture/circulation/13", ".slide-title");
await s.page.screenshot({ path: `${OUT}/read-desktop-dark.png` });
await s.context.close();

s = await page({ width: 390, height: 844, mobile: true });
await go(s.page, "#/lecture/cells/11", ".slide-title");
await s.page.screenshot({ path: `${OUT}/read-phone.png` });
await go(s.page, "#/lecture/cells/recall", ".card");
await s.page.keyboard.press("Space");
await s.page.waitForTimeout(500);
await s.page.screenshot({ path: `${OUT}/recall-phone.png` });
await s.context.close();

await browser.close();
console.log("screenshots written to", OUT);
