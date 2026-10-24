// End-to-end check of journey J1 (website plan §6) with the pre-installed Playwright.
// Needs the API on :8000 and the web dev server on :5173. Run: npm run e2e
import { createRequire } from "node:module";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const here = path.dirname(fileURLToPath(import.meta.url));
const AXE = path.join(here, "..", "node_modules", "axe-core", "axe.min.js");
const SHOTS = process.env.SHOTS ?? path.join(here, "..", "..", "docs", "screenshots");
const URL = process.env.WEB_URL ?? "http://localhost:5173/#/compass";
mkdirSync(SHOTS, { recursive: true });

const failures = [];
const check = (ok, msg) => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${msg}`);
  if (!ok) failures.push(msg);
};

async function axe(page, label) {
  await page.addScriptTag({ path: AXE });
  const res = await page.evaluate(async () =>
    (await axe.run(document, { runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] })).violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      n: v.nodes.length,
      target: v.nodes[0]?.target?.join(" "),
    })),
  );
  const bad = res.filter((v) => v.impact === "serious" || v.impact === "critical");
  check(bad.length === 0, `axe ${label}: ${bad.length} serious/critical ${bad.length ? JSON.stringify(bad) : ""}`);
}

async function untaggedNumbers(page) {
  return page.$$eval("[data-testid=num]", (els) =>
    els.filter((el) => !el.parentElement?.querySelector("[title]")).length,
  );
}

const browser = await chromium.launch();
let current = null; // page under test, for a failure screenshot
try {
  // ---------- mobile 360 px: J1 up to the cost screen
  const ctx = await browser.newContext({ viewport: { width: 360, height: 800 } });
  const page = await ctx.newPage();
  await page.goto(URL);
  await page.getByTestId("health").filter({ hasText: "ok" }).waitFor({ timeout: 15000 });
  await axe(page, "input (360)");
  await page.screenshot({ path: `${SHOTS}/360-input.png`, fullPage: true });
  await page.getByTestId("preset-groundnut_beverage").click();
  await page.getByTestId("verdict-card").waitFor({ timeout: 20000 });
  const label = await page.getByTestId("verdict-label").first().innerText();
  check(label.includes("TEST-FIRST"), `preset 1 verdict is TEST-FIRST (got "${label}")`);
  check((await page.getByTestId("gate-G1").innerText()).includes("53%"), "G1 shows prior P(fail) 53%");
  await axe(page, "verdict (360)");
  await page.screenshot({ path: `${SHOTS}/360-verdict.png`, fullPage: true });

  for (const tab of ["chains", "cost", "next"]) {
    await page.getByTestId(`tab-${tab}`).click();
    await page.waitForTimeout(300);
    if (tab === "next") {
      const rec = await page.getByTestId("recommended-test").innerText();
      check(/₹[\d,]+/.test(rec), `next: recommended test with a ₹ value (${rec.split("\n")[1]})`);
      check(await page.getByTestId("readiness").isVisible(), "next: readiness grade and checklist shown");
      check(await page.getByTestId("plan").isVisible(), "next: validation plan shown");
    }
    const wide = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    check(!wide, `no horizontal page scroll at 360 px (${tab})`);
    await axe(page, `${tab} (360)`);
    await page.screenshot({ path: `${SHOTS}/360-${tab}.png`, fullPage: true });
  }
  check((await untaggedNumbers(page)) === 0, "every number has a tag chip (next screen)");

  await page.getByTestId("tab-cost").click();
  const landed = () => page.getByTestId("pea-landed").evaluate((el) => el.textContent);
  const before = await landed();
  const thumb = page.getByTestId("slider-base").getByRole("slider");
  await thumb.focus();
  for (let i = 0; i < 8; i++) await page.keyboard.press("ArrowRight");
  await page.waitForFunction(
    (b) => document.querySelector("[data-testid=pea-landed]")?.textContent !== b,
    before,
    { timeout: 15000 },
  );
  const after = await landed();
  check(before !== after, `pea slider changes the result (${before} -> ${after})`);
  check((await untaggedNumbers(page)) === 0, "every number has a tag chip (cost screen)");
  await ctx.close();

  // ---------- desktop 1280 px: keyboard-only J1 + diagnosis and chain detail
  const dctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const d = await dctx.newPage();
  current = d;
  await d.goto(URL);
  await d.getByTestId("health").filter({ hasText: "ok" }).waitFor({ timeout: 15000 });
  let reached = false;
  for (let i = 0; i < 40 && !reached; i++) {
    await d.keyboard.press("Tab");
    reached = await d.evaluate(() => document.activeElement?.getAttribute("data-testid") === "preset-groundnut_beverage");
  }
  check(reached, "keyboard: preset button reachable with Tab");
  await d.keyboard.press("Enter");
  await d.getByTestId("verdict-card").waitFor({ timeout: 20000 });
  check(true, "keyboard: Enter runs the preset");
  await d.screenshot({ path: `${SHOTS}/1280-verdict.png`, fullPage: true });
  for (const s of ["diagnosis", "chains", "cost"]) {
    await d.getByTestId(`nav-${s}`).focus();
    await d.keyboard.press("Enter");
    await d.waitForTimeout(300);
    if (s === "chains") {
      await d.locator("[data-testid^=chain-]").first().click();
      await d.getByTestId("chain-detail").waitFor();
      check(true, "chain row opens the before/after panel");
    }
    if (s === "diagnosis") {
      check((await d.getByTestId("diag-trypsin_inhibitor").innerText()).includes("limiting"), "diagnosis marks trypsin inhibitor limiting");
    }
    await axe(d, `${s} (1280)`);
    await d.screenshot({ path: `${SHOTS}/1280-${s}.png`, fullPage: true });
  }
  // J1 continued: AI summary + enter a lab result (GT8) with before/after
  await d.getByTestId("nav-verdict").click();
  const badge = await d.getByTestId("ai-badge").innerText({ timeout: 20000 });
  check(/summary/i.test(badge), `verdict: AI summary card with badge ("${badge}")`);
  await d.getByTestId("nav-next").click();
  await d.getByTestId("lab-input").selectOption("cmp.phytic_acid");
  await d.getByTestId("lab-value").fill("1.8");
  await d.getByTestId("lab-submit").click();
  await d.getByTestId("before-after").waitFor({ timeout: 30000 });
  check(true, "next: lab result shows before/after");
  await axe(d, "next with lab result (1280)");
  await d.screenshot({ path: `${SHOTS}/1280-next-lab.png`, fullPage: true });
  await d.getByTestId("lab-keep").click();
  await d.getByTestId("recommended-test").waitFor();
  check(true, "next: keeping the lab result re-runs the analysis");

  // J3: describe in words -> filled form with highlights -> user confirms
  await d.getByTestId("nav-input").click();
  await d.getByTestId("describe").fill("Groundnut cake from Rajkot, about 48% protein, for a protein drink, no solvents");
  await d.getByTestId("fill-form").click();
  await d.getByTestId("parse-message").filter({ hasText: "highlighted" }).waitFor({ timeout: 20000 });
  const bp = await d.locator("#byproduct").inputValue();
  const prot = await d.locator("#protein").inputValue();
  const ring = await d.locator("#protein").getAttribute("class");
  check(bp === "groundnut_cake" && prot === "48" && ring.includes("ring-2"), `J3: form filled and highlighted (${bp}, ${prot}%)`);
  check(!(await d.getByTestId("verdict-card").count()), "J3: nothing is analysed until the user confirms");
  await d.getByTestId("submit").click();
  await d.getByTestId("verdict-card").waitFor({ timeout: 20000 });
  check(true, "J3: Analyse runs the filled request");

  // J3 by voice: Chromium exposes webkitSpeechRecognition, so the mic is offered (Firefox hides it: unit test)
  await d.getByTestId("nav-input").click();
  check(await d.getByTestId("mic").isVisible(), "voice: mic offered where the browser supports speech recognition");

  // J6: Hindi user
  await d.getByLabel("Language").selectOption("hi");
  await d.waitForFunction(() => document.documentElement.lang === "hi");
  check(await d.evaluate(() => !!document.getElementById("font-devanagari")), "hindi: Devanagari font loaded on demand");
  await d.getByTestId("nav-verdict").click();
  const nav = await d.getByTestId("nav-verdict").innerText();
  check(nav.includes("फ़ैसला"), `hindi: navigation in Hindi (${nav})`);
  const vl = await d.getByTestId("verdict-label").first().innerText();
  check(vl.includes("TEST-FIRST"), "hindi: verdict label kept in English (safety wording, not reviewed)");
  check(await d.getByTestId("safety-note").isVisible(), "hindi: safety-wording note shown");
  await d.getByTestId("ai-text").filter({ hasText: "फ़ैसला" }).waitFor({ timeout: 20000 });
  const hb = await d.getByTestId("ai-badge").innerText();
  check(hb.includes("मशीन"), `hindi: summary in Hindi with machine-written badge (${hb})`);
  await d.getByTestId("show-english").click();
  await d.getByTestId("ai-text").filter({ hasText: "Verdict:" }).waitFor({ timeout: 20000 });
  check(true, "hindi: 'show English' toggle shows the English summary");
  await axe(d, "verdict in Hindi (1280)");
  await d.screenshot({ path: `${SHOTS}/1280-verdict-hi.png`, fullPage: true });
  await d.getByTestId("nav-cost").click();
  const landedHi = await d.getByTestId("pea-landed").innerText();
  check(/₹[\d,]+/.test(landedHi), `hindi: ₹ formatting unchanged (${landedHi.split("\n")[0]})`);
  await d.getByLabel("भाषा").selectOption("en");

  const overflow = await d.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  check(!overflow, "no horizontal page scroll at 1280 px");
  await dctx.close();
} catch (e) {
  if (current) await current.screenshot({ path: `${SHOTS}/failure.png`, fullPage: true }).catch(() => {});
  throw e;
} finally {
  await browser.close();
}
console.log(failures.length ? `\n${failures.length} FAILED` : "\nall e2e checks passed");
process.exit(failures.length ? 1 : 0);
