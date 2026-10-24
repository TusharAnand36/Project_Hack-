import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

import App from "./App";
import { CompassMark } from "./components/Brand";
import "./site.css";

const PAGES = ["home", "about", "mission", "how-it-works", "compass"] as const;
type Page = (typeof PAGES)[number];

function readPage(): Page {
  const page = window.location.hash.replace(/^#\/?/, "").split("?")[0] || "home";
  return PAGES.includes(page as Page) ? (page as Page) : "home";
}

function Arrow({ diagonal = false }: { diagonal?: boolean }) {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d={diagonal ? "M6 18 18 6M6 6h12v12" : "M4 12h15m-6-6 6 6-6 6"}
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function LineIcon({ kind }: { kind: "seed" | "science" | "path" }) {
  return (
    <svg
      width="36"
      height="36"
      viewBox="0 0 40 40"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.4"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {kind === "seed" ? (
        <>
          <path d="M20 34V18m0 9C7 27 7 17 7 12c8 0 13 5 13 15Zm0-6C20 9 28 6 34 6c0 8-3 15-14 15Z" />
          <path d="m20 21 8-8M13 18l7 9" />
        </>
      ) : kind === "science" ? (
        <>
          <path d="M15 5h10m-8 0v13L8 32c-1 2 0 3 2 3h20c2 0 3-1 2-3l-9-14V5M13 25h14" />
          <circle cx="21" cy="29" r="1" />
          <circle cx="18" cy="22" r="1" />
        </>
      ) : (
        <>
          <circle cx="9" cy="9" r="4" />
          <circle cx="31" cy="31" r="4" />
          <path d="M13 9h12a6 6 0 0 1 0 12H15a5 5 0 0 0 0 10h12m-7-15 5 5-5 5" />
        </>
      )}
    </svg>
  );
}

function SiteHeader({ page }: { page: Page }) {
  const { t, i18n } = useTranslation();
  const [menuOpen, setMenuOpen] = useState(false);
  useEffect(() => setMenuOpen(false), [page]);
  const changeLanguage = (language: string) => {
    void i18n.changeLanguage(language);
    try {
      localStorage.setItem("lang", language);
    } catch {
      /* storage may be blocked */
    }
  };
  return (
    <header className="site-header">
      <a href="#/" className="site-brand" aria-label={t("site.homeLabel")}>
        <CompassMark />
        <span>
          upcycle<span className="brand-second">compass</span>
        </span>
      </a>
      <nav
        className={`site-nav ${menuOpen ? "is-open" : ""}`}
        id="site-navigation"
        aria-label={t("site.navigation")}
      >
        {(["home", "about", "mission", "how-it-works"] as const).map((item) => (
          <a
            key={item}
            href={item === "home" ? "#/" : `#/${item}`}
            onClick={() => setMenuOpen(false)}
            aria-current={page === item ? "page" : undefined}
          >
            {t(`site.nav.${item}`)}
          </a>
        ))}
      </nav>
      <div className="site-header-actions">
        <select
          aria-label={t("app.language")}
          value={i18n.language.startsWith("hi") ? "hi" : "en"}
          onChange={(e) => changeLanguage(e.target.value)}
          className="site-language"
        >
          <option value="en">EN</option>
          <option value="hi">हिं</option>
        </select>
        <a href="#/compass" className="site-button button-dark header-cta">
          {t("site.openTool")}
          <Arrow diagonal />
        </a>
        <button
          type="button"
          className="menu-toggle"
          aria-controls="site-navigation"
          aria-expanded={menuOpen}
          aria-label={t(menuOpen ? "site.closeMenu" : "site.openMenu")}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <span />
          <span />
        </button>
      </div>
    </header>
  );
}

function IngredientPhoto({ className = "", eager = false }: { className?: string; eager?: boolean }) {
  const { t } = useTranslation();
  return (
    <img
      src="/images/circular-ingredients.webp"
      alt={t("site.imageAlt")}
      width="1122"
      height="1402"
      loading={eager ? "eager" : "lazy"}
      className={`ingredient-photo ${className}`}
    />
  );
}

function PageIntro({
  eyebrow,
  title,
  italic,
  description,
}: {
  eyebrow: string;
  title: string;
  italic: string;
  description: string;
}) {
  return (
    <div className="page-intro site-wrap">
      <p className="eyebrow reveal">{eyebrow}</p>
      <h1 className="display-heading reveal">
        {title}
        <br />
        <em>{italic}</em>
        <span className="orange-dot">.</span>
      </h1>
      <p className="intro-copy reveal">{description}</p>
    </div>
  );
}

function CallToAction() {
  const { t } = useTranslation();
  return (
    <section className="site-cta site-wrap reveal">
      <div className="cta-compass" aria-hidden="true">
        <CompassMark />
      </div>
      <p className="eyebrow">{t("site.ctaEyebrow")}</p>
      <h2>
        {t("site.ctaTitle")}
        <br />
        <em>{t("site.ctaItalic")}</em>
      </h2>
      <a href="#/compass" className="site-button button-orange">
        {t("site.tryTool")}
        <Arrow diagonal />
      </a>
      <p className="cta-note">{t("site.ctaNote")}</p>
    </section>
  );
}

function HomePage() {
  const { t } = useTranslation();
  return (
    <>
      <section className="site-hero site-wrap">
        <div className="hero-copy">
          <p className="eyebrow hero-enter">
            <span className="status-dot" />
            {t("site.heroEyebrow")}
          </p>
          <h1 className="hero-heading hero-enter">
            {t("site.heroLine1")}
            <br />
            {t("site.heroLine2")}
            <br />
            <em>{t("site.heroLine3")}</em>
            <span className="orange-dot">.</span>
          </h1>
          <p className="hero-description hero-enter">{t("site.heroDescription")}</p>
          <div className="hero-buttons hero-enter">
            <a href="#/compass" className="site-button button-dark">
              {t("site.exploreTool")}
              <Arrow diagonal />
            </a>
            <a href="#/how-it-works" className="text-link">
              {t("site.seeHow")}
              <span className="play-mark" aria-hidden="true">
                ↗
              </span>
            </a>
          </div>
          <div className="hero-footnote hero-enter">
            <span className="small-orbit" aria-hidden="true">
              ✳
            </span>
            <span>{t("site.heroFootnote")}</span>
          </div>
        </div>
        <div className="hero-visual hero-enter">
          <div className="hero-image-frame">
            <IngredientPhoto eager />
            <div className="photo-caption">
              <span>{t("site.photoCaption")}</span>
              <span>01 — 05</span>
            </div>
          </div>
          <div className="circular-seal" aria-hidden="true">
            <span>LESS WASTE</span>
            <CompassMark />
            <span>MORE POSSIBILITY</span>
          </div>
          <a href="#/compass" className="hero-result-card">
            <span className="result-icon">
              <LineIcon kind="seed" />
            </span>
            <span className="result-card-copy">
              <span className="micro-label">{t("site.resultEyebrow")}</span>
              <strong>{t("site.resultTitle")}</strong>
              <span>{t("site.resultCaption")}</span>
            </span>
            <span className="result-card-arrow">
              <Arrow diagonal />
            </span>
          </a>
        </div>
      </section>
      <div className="audience-strip site-wrap">
        <p>{t("site.audienceEyebrow")}</p>
        <div>
          <span>{t("site.audience1")}</span>
          <span className="strip-star" aria-hidden="true">
            ✳
          </span>
          <span>{t("site.audience2")}</span>
          <span className="strip-star" aria-hidden="true">
            ✳
          </span>
          <span>{t("site.audience3")}</span>
        </div>
      </div>
      <section className="what-section site-wrap section-space">
        <div className="section-heading reveal">
          <p className="eyebrow">{t("site.whatEyebrow")}</p>
          <h2>
            {t("site.whatTitle")}
            <br />
            <em>{t("site.whatItalic")}</em>
          </h2>
          <p>{t("site.whatDescription")}</p>
        </div>
        <div className="feature-grid">
          {(["seed", "science", "path"] as const).map((kind, i) => (
            <article className="feature-item reveal" key={kind}>
              <span className="feature-number">0{i + 1}</span>
              <LineIcon kind={kind} />
              <h3>{t(`site.feature${i + 1}Title`)}</h3>
              <p>{t(`site.feature${i + 1}Description`)}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="mission-band">
        <div className="site-wrap mission-band-inner">
          <div className="reveal">
            <p className="eyebrow">{t("site.missionEyebrow")}</p>
            <h2>
              {t("site.missionBandTitle")}
              <br />
              <em>{t("site.missionBandItalic")}</em>
            </h2>
            <a href="#/mission" className="text-link light-link">
              {t("site.readMission")}
              <Arrow />
            </a>
          </div>
          <div className="mission-band-right reveal">
            <span className="mission-flower" aria-hidden="true">
              ✳
            </span>
            <p>{t("site.missionBandDescription")}</p>
            <span className="micro-label">{t("site.missionBandCaption")}</span>
          </div>
        </div>
      </section>
      <section className="process-section site-wrap section-space">
        <div className="section-topline reveal">
          <div>
            <p className="eyebrow">{t("site.processEyebrow")}</p>
            <h2>
              {t("site.processTitle")}
              <br />
              <em>{t("site.processItalic")}</em>
            </h2>
          </div>
          <a href="#/how-it-works" className="text-link">
            {t("site.viewProcess")}
            <Arrow diagonal />
          </a>
        </div>
        <ProcessSteps />
      </section>
      <section className="transparency-section site-wrap reveal">
        <div>
          <p className="eyebrow">{t("site.evidenceEyebrow")}</p>
          <h2>
            {t("site.evidenceTitle")}
            <br />
            <em>{t("site.evidenceItalic")}</em>
          </h2>
          <p>{t("site.evidenceDescription")}</p>
          <a href="#/about" className="text-link">
            {t("site.aboutApproach")}
            <Arrow diagonal />
          </a>
        </div>
        <EvidenceLabels />
      </section>
      <CallToAction />
    </>
  );
}

function ProcessSteps() {
  const { t } = useTranslation();
  return (
    <div className="process-grid">
      {[1, 2, 3].map((n) => (
        <article className="process-item reveal" key={n}>
          <div className="process-step-top">
            <span>0{n}</span>
            <Arrow />
          </div>
          <h3>{t(`site.step${n}Title`)}</h3>
          <p>{t(`site.step${n}Description`)}</p>
        </article>
      ))}
    </div>
  );
}

function EvidenceLabels() {
  const { t } = useTranslation();
  return (
    <div className="evidence-labels">
      {["measured", "published", "assumed", "synthetic"].map((tag) => (
        <div key={tag} className={`evidence-row evidence-${tag}`}>
          <span className="evidence-letter" aria-hidden="true">
            {tag[0].toUpperCase()}
          </span>
          <div>
            <strong>{t(`site.evidence.${tag}`)}</strong>
            <p>{t(`site.evidence.${tag}Description`)}</p>
          </div>
          <span className="evidence-row-mark" aria-hidden="true">
            ↗
          </span>
        </div>
      ))}
    </div>
  );
}

function AboutPage() {
  const { t } = useTranslation();
  return (
    <>
      <PageIntro
        eyebrow={t("site.aboutEyebrow")}
        title={t("site.aboutTitle")}
        italic={t("site.aboutItalic")}
        description={t("site.aboutIntro")}
      />
      <section className="about-story site-wrap">
        <div className="about-photo reveal">
          <IngredientPhoto />
          <span className="image-note">{t("site.aboutImageNote")}</span>
        </div>
        <div className="story-copy reveal">
          <p className="eyebrow">{t("site.whoEyebrow")}</p>
          <h2>
            {t("site.whoTitle")}
            <br />
            <em>{t("site.whoItalic")}</em>
          </h2>
          <p>{t("site.whoDescription")}</p>
          <p>{t("site.whoDescription2")}</p>
          <div className="origin-note">
            <CompassMark />
            <div>
              <strong>{t("site.originTitle")}</strong>
              <span>{t("site.originDescription")}</span>
            </div>
          </div>
        </div>
      </section>
      <section className="site-wrap section-space">
        <div className="section-heading reveal">
          <p className="eyebrow">{t("site.beliefEyebrow")}</p>
          <h2>
            {t("site.beliefTitle")}
            <br />
            <em>{t("site.beliefItalic")}</em>
          </h2>
        </div>
        <div className="belief-grid">
          {[1, 2, 3].map((n) => (
            <article className="belief-item reveal" key={n}>
              <span className="micro-label">0{n} /</span>
              <h3>{t(`site.belief${n}Title`)}</h3>
              <p>{t(`site.belief${n}Description`)}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="transparency-section site-wrap reveal">
        <div>
          <p className="eyebrow">{t("site.evidenceEyebrow")}</p>
          <h2>
            {t("site.evidenceTitle")}
            <br />
            <em>{t("site.evidenceItalic")}</em>
          </h2>
          <p>{t("site.aboutEvidence")}</p>
          <a
            href="https://github.com/TusharAnand36/Project_Hack-"
            target="_blank"
            rel="noreferrer"
            className="text-link"
          >
            {t("site.viewSource")}
            <Arrow diagonal />
          </a>
        </div>
        <EvidenceLabels />
      </section>
      <CallToAction />
    </>
  );
}

function MissionPage() {
  const { t } = useTranslation();
  return (
    <>
      <PageIntro
        eyebrow={t("site.missionEyebrow")}
        title={t("site.missionTitle")}
        italic={t("site.missionItalic")}
        description={t("site.missionIntro")}
      />
      <section className="mission-statement site-wrap reveal">
        <span className="mission-flower" aria-hidden="true">
          ✳
        </span>
        <blockquote>{t("site.missionQuote")}</blockquote>
        <p className="micro-label">{t("site.missionQuoteCaption")}</p>
      </section>
      <section className="site-wrap section-space">
        <div className="section-heading reveal">
          <p className="eyebrow">{t("site.commitmentEyebrow")}</p>
          <h2>
            {t("site.commitmentTitle")}
            <br />
            <em>{t("site.commitmentItalic")}</em>
          </h2>
        </div>
        <div className="commitment-list">
          {[1, 2, 3, 4].map((n) => (
            <article className="commitment-item reveal" key={n}>
              <span className="commitment-number">0{n}</span>
              <h3>{t(`site.commitment${n}Title`)}</h3>
              <p>{t(`site.commitment${n}Description`)}</p>
              <Arrow diagonal />
            </article>
          ))}
        </div>
      </section>
      <section className="roadmap-section site-wrap reveal">
        <div>
          <p className="eyebrow">{t("site.roadmapEyebrow")}</p>
          <h2>
            {t("site.roadmapTitle")}
            <br />
            <em>{t("site.roadmapItalic")}</em>
          </h2>
          <p>{t("site.roadmapDescription")}</p>
        </div>
        <ol className="roadmap-list">
          {[1, 2, 3].map((n) => (
            <li key={n}>
              <span className="roadmap-dot" />
              <div>
                <span className="micro-label">{t(`site.roadmap${n}Label`)}</span>
                <h3>{t(`site.roadmap${n}Title`)}</h3>
                <p>{t(`site.roadmap${n}Description`)}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <CallToAction />
    </>
  );
}

function HowPage() {
  const { t } = useTranslation();
  return (
    <>
      <PageIntro
        eyebrow={t("site.processEyebrow")}
        title={t("site.howTitle")}
        italic={t("site.howItalic")}
        description={t("site.howIntro")}
      />
      <section className="site-wrap how-steps">
        <h2 className="sr-only">{t("site.processEyebrow")}</h2>
        <ProcessSteps />
      </section>
      <section className="tool-tour site-wrap section-space">
        <div className="section-heading reveal">
          <p className="eyebrow">{t("site.tourEyebrow")}</p>
          <h2>
            {t("site.tourTitle")}
            <br />
            <em>{t("site.tourItalic")}</em>
          </h2>
        </div>
        <div className="tour-grid">
          {["verdict", "diagnosis", "chains", "cost", "next", "memo"].map((screen, i) => (
            <article className="tour-item reveal" key={screen}>
              <span className="micro-label">0{i + 1} /</span>
              <h3>{t(screen === "memo" ? "memo.title" : `nav.${screen}`)}</h3>
              <p>{t(`site.tour.${screen}`)}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="faq-section site-wrap section-space">
        <div className="reveal">
          <p className="eyebrow">{t("site.faqEyebrow")}</p>
          <h2>
            {t("site.faqTitle")}
            <br />
            <em>{t("site.faqItalic")}</em>
          </h2>
        </div>
        <div className="faq-list">
          {[1, 2, 3, 4].map((n) => (
            <details className="reveal" key={n}>
              <summary>
                {t(`site.faq${n}Question`)}
                <span aria-hidden="true">+</span>
              </summary>
              <p>{t(`site.faq${n}Answer`)}</p>
            </details>
          ))}
        </div>
      </section>
      <CallToAction />
    </>
  );
}

function SiteFooter() {
  const { t } = useTranslation();
  return (
    <footer className="site-footer">
      <div className="site-wrap footer-main">
        <div>
          <a href="#/" className="site-brand">
            <CompassMark />
            <span>
              upcycle<span className="brand-second">compass</span>
            </span>
          </a>
          <p className="footer-description">{t("site.footerDescription")}</p>
        </div>
        <div className="footer-links">
          <span className="micro-label">{t("site.footerExplore")}</span>
          <a href="#/about">{t("site.nav.about")}</a>
          <a href="#/mission">{t("site.nav.mission")}</a>
          <a href="#/how-it-works">{t("site.nav.how-it-works")}</a>
        </div>
        <div className="footer-links">
          <span className="micro-label">{t("site.footerResources")}</span>
          <a href="#/compass">{t("site.openTool")}</a>
          <a href="/open-data-pack.zip" download>
            {t("footer.dataPack")}
          </a>
          <a href="https://github.com/TusharAnand36/Project_Hack-" target="_blank" rel="noreferrer">
            GitHub ↗
          </a>
        </div>
      </div>
      <div className="site-wrap footer-bottom">
        <span>© {new Date().getFullYear()} Upcycle Compass</span>
        <p>{t("site.footerDisclaimer")}</p>
        <span>{t("site.footerMade")}</span>
      </div>
    </footer>
  );
}

export default function Site() {
  const { t } = useTranslation();
  const [page, setPage] = useState<Page>(readPage);
  const mainRef = useRef<HTMLElement>(null);
  const firstRender = useRef(true);
  useEffect(() => {
    const updatePage = () => setPage(readPage());
    window.addEventListener("hashchange", updatePage);
    return () => window.removeEventListener("hashchange", updatePage);
  }, []);
  useEffect(() => {
    document.title =
      page === "home"
        ? t("site.pageTitle")
        : `${t(page === "compass" ? "site.openTool" : `site.nav.${page}`)} · Upcycle Compass`;
    if (!firstRender.current) {
      window.scrollTo({ top: 0, behavior: "instant" });
      mainRef.current?.focus({ preventScroll: true });
    }
    firstRender.current = false;
    if (page === "compass" || !window.IntersectionObserver) return;
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 },
    );
    document.querySelectorAll(".reveal").forEach((element) => {
      if (element.getBoundingClientRect().top > window.innerHeight) element.classList.add("reveal-ready");
      observer.observe(element);
    });
    return () => observer.disconnect();
  }, [page, t]);
  if (page === "compass") return <App />;
  return (
    <div className="marketing-site">
      <a
        href="#site-main"
        className="site-skip"
        onClick={(event) => {
          event.preventDefault();
          mainRef.current?.focus();
        }}
      >
        {t("app.skip")}
      </a>
      <SiteHeader page={page} />
      <main id="site-main" ref={mainRef} tabIndex={-1}>
        {page === "home" ? (
          <HomePage />
        ) : page === "about" ? (
          <AboutPage />
        ) : page === "mission" ? (
          <MissionPage />
        ) : (
          <HowPage />
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
