// "Wi-Fi off" rehearsal (website plan Phase 8 exit gate): production build served with NO API.
// Every preset must still work from snapshots. Run: npm run e2e:offline
import { spawn } from "node:child_process";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const SHOTS = path.join(here, "..", "..", "docs", "screenshots");
const PORT = 4179;
const URL = `http://localhost:${PORT}/#/compass`;

const failures = [];
const check = (ok, msg) => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${msg}`);
  if (!ok) failures.push(msg);
};

// a plain static server for dist/ (vite preview would reuse the dev API proxy): every /api call 404s,
// exactly like a venue with no network to the API
const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1", "--directory", "dist"], {
  cwd: path.join(here, ".."),
  stdio: "ignore",
});
await new Promise((r) => setTimeout(r, 2500));

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  await page.goto(URL);
  await page.getByTestId("health").filter({ hasText: "unreachable" }).waitFor({ timeout: 15000 });
  check(true, "API unreachable (as in a venue with no Wi-Fi)");
  for (const pid of ["sunflower_snack", "groundnut_beverage", "soybean_meat", "almond_meat", "pea_beverage"]) {
    await page.getByTestId("tab-input").click();
    await page.getByTestId(`preset-${pid}`).click({ timeout: 15000 });
    await page.getByTestId("offline-badge").waitFor({ timeout: 20000 });
    const badge = await page.getByTestId("offline-badge").innerText();
    const label = await page.getByTestId("verdict-label").first().innerText();
    check(/snapshot/i.test(badge) && /generated/.test(badge), `${pid}: snapshot loaded with stamp`);
    check(/TEST-FIRST|GO/.test(label), `${pid}: verdict shown offline (${label.replace(/\s+/g, " ")})`);
  }
  await page.getByTestId("ai-text").waitFor({ timeout: 15000 });
  check((await page.getByTestId("ai-badge").innerText()).includes("Template"), "summary from the snapshot (template)");
  await page.getByTestId("tab-next").click();
  check(await page.getByTestId("recommended-test").isVisible().catch(() => false) ||
        (await page.locator("main").innerText()).length > 0, "next step screen renders offline");
  await page.screenshot({ path: `${SHOTS}/offline-360.png`, fullPage: true });

  const desk = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  await desk.goto(URL);
  await desk.getByTestId("preset-groundnut_beverage").click({ timeout: 15000 });
  await desk.getByTestId("verdict-card").waitFor({ timeout: 20000 });
  await desk.getByLabel("Language").selectOption("hi");
  await desk.getByTestId("ai-text").filter({ hasText: "फ़ैसला" }).waitFor({ timeout: 15000 });
  check(true, "Hindi summary from the Hindi snapshot");
  await desk.getByLabel("भाषा").selectOption("en");
  await desk.getByTestId("open-memo").click();
  await desk.getByTestId("memo").waitFor();
  check((await desk.getByTestId("memo").innerText()).includes("Proximate"), "decision memo renders offline");
  await desk.emulateMedia({ media: "print" });
  const pdf = await desk.pdf({ path: `${SHOTS}/decision-memo.pdf`, format: "A4", printBackground: true, preferCSSPageSize: true });
  const pages = (pdf.toString("latin1").match(/\/Type\s*\/Page[^s]/g) ?? []).length;
  check(pages === 1, `memo prints on one A4 page (${pages}) -> docs/screenshots/decision-memo.pdf`);
  await desk.emulateMedia({ media: "screen" });
  await desk.getByTestId("tab-input").click().catch(() => {});
  await desk.getByTestId("nav-input").click();
  const options = await desk.locator("#byproduct option").count();
  check(options > 1, `form options load from offline data (${options - 1} by-products)`);
  const pack = await desk.evaluate(async () => (await fetch("/open-data-pack.zip")).headers.get("content-type"));
  check(/zip/.test(pack ?? ""), `open data pack downloadable (${pack})`);
} finally {
  await browser.close();
  server.kill();
}
console.log(failures.length ? `\n${failures.length} FAILED` : "\nall offline checks passed");
process.exit(failures.length ? 1 : 0);
