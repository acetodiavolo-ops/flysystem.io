// WebKit (Safari engine) screenshot: node shot-webkit.mjs <url-or-file> <out.png> [width] [height] [--full]
import { webkit } from "playwright";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";

const [, , target, out, w = "390", h = "844", full] = process.argv;
const url = /^https?:|^file:/.test(target) ? target : pathToFileURL(resolve(target)).href;

const browser = await webkit.launch();
const page = await browser.newPage({
  viewport: { width: Number(w), height: Number(h) },
  deviceScaleFactor: 2,
});
await page.goto(url, { waitUntil: "networkidle" });
await page.evaluate(() => document.fonts.ready);
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
await page.waitForTimeout(500);
await page.screenshot({ path: out, fullPage: full === "--full" });
const doc = await page.evaluate(() => ({
  scrollWidth: document.documentElement.scrollWidth,
  clientWidth: document.documentElement.clientWidth,
}));
console.log(JSON.stringify(doc));
await browser.close();
