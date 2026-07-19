// Screenshot harness: node shot.mjs <url-or-file> <out.png> [width] [height] [--full]
// Uses installed Edge via playwright-core (no browser download).
import { chromium } from "playwright-core";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [, , target, out, w = "1440", h = "900", full] = process.argv;
if (!target || !out) {
  console.error("usage: node shot.mjs <url-or-file> <out.png> [width] [height] [--full]");
  process.exit(1);
}
const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(resolve(target)).href;

const browser = await chromium.launch({ channel: "msedge", headless: true });
const page = await browser.newPage({
  viewport: { width: Number(w), height: Number(h) },
  deviceScaleFactor: 1.5,
});
await page.goto(url, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
// force lazy images + let reveal animations settle
await page.evaluate(() => {
  document.querySelectorAll("img[loading='lazy']").forEach((img) => (img.loading = "eager"));
  document.querySelectorAll(".rv, .rv-rule, .rv-img").forEach((el) => el.classList.add("in"));
});
await page.evaluate(async () => {
  for (let y = 0; y < document.body.scrollHeight; y += 800) {
    window.scrollTo(0, y);
    await new Promise((r) => setTimeout(r, 40));
  }
  window.scrollTo(0, 0);
});
await page.waitForLoadState("networkidle");
await page.waitForTimeout(400);
await page.screenshot({ path: out, fullPage: full === "--full" });
// report layout health
const overflow = await page.evaluate(() => {
  const doc = document.documentElement;
  const bad = [];
  if (doc.scrollWidth > doc.clientWidth + 1) {
    document.querySelectorAll("body *").forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.right > doc.clientWidth + 1 && r.width > 0 && bad.length < 8) {
        bad.push(`${el.tagName.toLowerCase()}.${[...el.classList].join(".")} right=${Math.round(r.right)}`);
      }
    });
  }
  return { scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, bad };
});
console.log(JSON.stringify(overflow));
await browser.close();
