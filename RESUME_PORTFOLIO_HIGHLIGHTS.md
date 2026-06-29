# Veraflux - Resume & Portfolio Master Highlights

The single working doc for updating the resume and the portfolio site after the solo build and launch of Veraflux. It consolidates everything valuable from `RECRUITER_AUDIT.md` (the exhaustive evidence inventory) and `LINKEDIN_PROFILE.md` (the settled positioning), then folds in net-new findings from a fresh code/doc sweep.

**House rules for any copy drafted here** (carried from `LINKEDIN_PROFILE.md` and `CONTRIBUTING.md`): no em dashes (hyphens / commas / periods only; en dashes in numeric ranges are fine), recommendation-neutral phrasing on anything health-facing (informational, never "what to take"), and keep unit economics / margins out of anything public.

**How to use this doc**
- Section A is the positioning layer: pull the title, headline, and pitch from here.
- Section C is the skill inventory by discipline: tailor a resume by lifting the bullets for the target role's disciplines. Non-coding disciplines (architecture, infra/ops, product, design/UX, strategy) are pulled to the front on purpose, because they are the scarcer and higher-value signal.
- Section F has ready-to-paste resume bullets; Section G has portfolio case-study narratives.
- Section I lists what to verify or represent carefully before anything goes public.
- Everything traces back to `RECRUITER_AUDIT.md` (file:line evidence) and the source docs listed at the end.

---

## Table of Contents

- [A. Positioning & Narrative](#a-positioning--narrative)
- [B. Proof Bank (Quotable Numbers)](#b-proof-bank-quotable-numbers)
- [C. Skill Inventory by Discipline](#c-skill-inventory-by-discipline)
  - [C1. System Architecture & Systems Design](#c1-system-architecture--systems-design)
  - [C2. Infrastructure, DevOps & Operations](#c2-infrastructure-devops--operations)
  - [C3. Applied AI / LLM / Research Engineering](#c3-applied-ai--llm--research-engineering)
  - [C4. Backend Engineering](#c4-backend-engineering)
  - [C5. Security & Anti-Abuse](#c5-security--anti-abuse)
  - [C6. Frontend & Design Engineering](#c6-frontend--design-engineering)
  - [C7. Product Design & UX](#c7-product-design--ux)
  - [C8. Visual / Brand Design & Design Systems](#c8-visual--brand-design--design-systems)
  - [C9. SEO & Growth Engineering](#c9-seo--growth-engineering)
  - [C10. Product Strategy & Business](#c10-product-strategy--business)
  - [C11. Billing & Monetization Engineering](#c11-billing--monetization-engineering)
  - [C12. Data Analytics & Self-Hosted BI](#c12-data-analytics--self-hosted-bi)
  - [C13. Engineering Process & Documentation](#c13-engineering-process--documentation)
- [D. New Findings Beyond the Audit](#d-new-findings-beyond-the-audit)
- [E. Cross-Cutting Themes](#e-cross-cutting-themes)
- [F. Ready-to-Use Resume Bullets](#f-ready-to-use-resume-bullets)
- [G. Portfolio Case-Study Angles](#g-portfolio-case-study-angles)
- [H. Role-to-Strength Quick Map](#h-role-to-strength-quick-map)
- [I. Accuracy & Honesty Notes](#i-accuracy--honesty-notes)
- [Source Map](#source-map)

---

## A. Positioning & Narrative

The distilled, settled positioning from `LINKEDIN_PROFILE.md`. These are decisions already made and stress-tested; treat them as the default unless a specific target role argues otherwise.

### Identity

- **Who:** Full-stack & applied-AI engineer, graduating UC San Diego June 2026, B.S. Mathematics and Computer Science. Founder of Veraflux; designed, built, shipped, and operates it solo.
- **One-line identity:** "I built every layer of a production research platform on my own, from product strategy and design through the React front end and the retrieval-augmented Python pipeline to the infrastructure behind it."
- **The thread:** a genuine curiosity about clinical research met the engineering. Keep "clinical research" as a curiosity/spark woven near the project, not as a self-label in the identity sentence (it pigeonholes). Drop "healthcare" - claiming clinical research alone is more honest and travels to any domain.

### Title (resume / LinkedIn position)

- Recommended: `Founder, Full-Stack & Applied-AI Engineer`
- Cleaner fallback (if "Applied AI" reads buzzy for a specific audience): `Founder & Full-Stack Engineer`
- Employment: Self-employed, Veraflux, build start to Present.

### Headline (LinkedIn / portfolio hero)

- Recommended: `Founder, Full-Stack & Applied-AI Engineer | Designed and deployed a production research platform end to end | multi-model LLM orchestration + retrieval-augmented, grounded synthesis | React/TypeScript, Node, Python, Postgres`
- Alternate: `Full-Stack Engineer who shipped a production research platform solo, frontend to infrastructure | React, Node, Python, Postgres, applied AI | Founder, Veraflux`

### Top 5 skills (pinned)

`Full-Stack Development` | `Systems Design` | `UI/UX` | `Retrieval-Augmented Generation (RAG)` | `Large Language Models (LLM)`

Rationale: RAG is the most specific, in-demand, defensible AI skill here and an explicit recruiter search term; keep it pinned. The five read as: builds end to end, thinks in systems, designs the surface, specializes in applied AI. If a slot must free up, drop the generic "LLM" before "RAG". Only reconsider RAG for strictly-SWE, zero-AI targets.

### The pitch, three lengths

**One line:** A production platform that pulls live clinical research from PubMed and turns it into evidence-based, fully-cited supplement reports personalized to age, sex, and goal.

**One paragraph:** Veraflux turns any supplement name plus a user's age, sex, and goal into a cited, evidence-graded clinical research report. It runs a roughly ten-stage LLM pipeline across two model vendors plus live PubMed retrieval to produce grounded synthesis where every claim links to a study you can open, then renders it through a sophisticated React reading experience, monetized with Stripe subscriptions and surfaced to search through a hand-built technical-SEO stack. Three services (React/TypeScript SPA, Express/TypeScript API, Python/FastAPI pipeline) ship as one Docker unit on Railway. Built and operated solo, frontend to infrastructure.

**One minute (builder voice):** "I always read the studies myself before trying a supplement, and wished for an unbiased tool that just condensed them. So I built one. The hard part is the part you do not see: the studies that matter for a goal get buried because PubMed ranks by how much gets published, not relevance, so a big chunk of the build is the retrieval - categorizing each supplement, then running faceted searches that surface 150+ candidate studies, narrowed to the ~50 that hold up. Filtering that many with rigor cannot happen in one pass, so it runs in stages: retrieve, select, synthesize, every claim grounded to a real source. I built the whole thing solo, from the design and interface to the pipeline to the infrastructure that keeps it running."

### Voice split (for any public posts)

- **Company / consumer voice:** evidence-forward, trust-first, AI deliberately not foregrounded (leading with "AI-generated" dents trust on health content).
- **Personal / builder voice:** the applied-AI engineering is a credential, not a risk. Contrast vs a chatbot only on scale and rigor (more sources, deeper selection, multi-stage), never "a chatbot can't / skips."

### Settled framing decisions (do not re-litigate)

- **Lead with the research/synthesis pipeline, not the backend.** It is the most differentiated work and the hottest hiring lane. The intro plus backend/frontend sections still establish full-stack breadth, so leading with the pipeline does not pigeonhole as ML-only. Backend-first is a per-application variant for backend/platform roles only.
- **Shipped + ongoing, both.** Lead with "shipped to production" (proof it is real and deployed). Breadth retained via "I built every layer." The failure mode to avoid is present-progressive-only ("I'm building...") with no shipped anchor, which reads as vaporware.
- **Differentiators, not table stakes.** Lead "what it does" with the genuine wedges: plain-language accessibility, personalization (age/sex/goal), head-to-head comparison, stack-interaction analysis. Rigor (citation grounding, verification pass) is carried as engineering substance, not as a product adjective.
- **State infra confidently; never advertise inexperience.** "First time building production infra" framing is rejected - it undercuts the exact thing you want read as solid. "Most I've ever taken on / learned" is fine (signals scope, not incompetence).
- **Do not name SiteHive duration.** Use present-perfect ("I've also worked as...") since the calendar span was not continuously worked. Name the device (Hexanode) for concreteness; optional embedded-tooling add (TeraTerm, STM32CubeProgrammer) for STM32/ARM firmware keywords.

### SiteHive line (prior experience, keep light)

> I've also worked as a test engineer for SiteHive, an Australian IoT company, running firmware updates and connectivity diagnostics on their Hexanode devices and validating each unit before shipment to customers.

Working close to the hardware sharpened the reliability and QA instincts brought to software. Shuttle-driver and Helyx-tutor roles deliberately omitted.

### Open questions to resolve before publishing

1. Confirm the `150-200 candidate studies` and `~237 / 200+ programmatic pages` figures are accurate and comfortable to surface; otherwise go qualitative ("a large candidate pool" / "a large set of programmatic pages"). See Section I.
2. Title: `Founder, Full-Stack & Applied-AI Engineer` vs the cleaner `Founder & Full-Stack Engineer`.
3. Whether to promote the analytics / admin-dashboard line into the main description for a data angle, or keep the description shorter.

---

## B. Proof Bank (Quotable Numbers)

Quantified anchors for resume bullets and portfolio copy. Verify the flagged ones (Section I) before public use.

- **3 services, 1 deploy unit, 2 languages** (TypeScript + Python) co-located in a single Docker container on Railway, FastAPI bound to loopback, only Express public.
- **~10 distinct LLM stages** per advanced report (screener, synonym generator, synonym validator, supplement profiler, multi-faceted PubMed retrieval, advanced selector, landmark selector, saturation check, synthesizer, evidence rater, executive-summary pass) plus a parallel safety branch.
- **2 model vendors, 4 model tiers** assigned by task: Gemini 2.5 Flash Lite (cheap classification), Gemini 2.5 Flash + extended thinking (multi-constraint selection), Claude Sonnet 4.6 (synthesis), Claude Haiku 4.5 (cheap post-pass).
- **~$0.25-0.30 measured cost per advanced report**, reconciled to the Anthropic bill to the cent ($2.49 computed = $2.49 actual, verified 2026-05-06).
- **49 named prompt-engineering patterns/anti-patterns** across 17 iteration phases (`pipeline/PROMPT_DESIGN.md`).
- **20 Postgres tables, 31 indexes/unique constraints, 19 migrations** named to narrate a phased rollout (`phase_0_data_foundation` through `phase_5_3_admin_audit`).
- **~237 indexable URLs** programmatically generated (12 static + 192 glossary terms + 33 supplement landings); **45 routes prerendered** for non-JS crawlers via headless Chromium.
- **6+ schema.org JSON-LD types** hand-built (BreadcrumbList, FAQPage, DefinedTerm/Set, MedicalWebPage, DietarySupplement, Article, WebPage, Organization, WebSite/SearchAction).
- **A 16-page in-app `/admin` BI suite** backed by ~31 endpoints (a from-scratch Mixpanel + Metabase substitute).
- **~26 hand-drawn custom SVG icons** that fully replaced Lucide (zero `lucide-react` imports remain), plus a custom WebGL fragment-shader hero gradient.
- **60 uses of `useReducedMotion()` across 29 files** - accessibility designed in, not bolted on.
- **PRIVATE (do not surface publicly):** 78-94% modeled gross margin across tiers; aggregate margin modeled 70% -> 91% as users scale 100 -> 10k. Usable in interviews and finance/founding-role conversations only.

---

## C. Skill Inventory by Discipline

Each subsection: a one-line "what this signals," then the strongest concrete highlights. The non-coding disciplines lead. Every claim is defensible against `RECRUITER_AUDIT.md` evidence (file:line there).

### C1. System Architecture & Systems Design

*Signals: the ability to design a coherent multi-service system and make defensible tradeoffs - the scarcest, highest-leverage non-coding engineering skill.*

- **Three-service, single-deploy-unit topology.** React SPA + Express API + FastAPI pipeline as one Docker image on Railway, with FastAPI on loopback (not internet-reachable) behind a shared-secret, Express as the only public surface. One healthcheck, one env set, one deploy. A deliberate "monolith of services" choice that minimizes operational surface for a solo operator.
- **Clear trust and responsibility boundaries.** Deterministic code owns data flow and validation; LLMs own only narrow judgment calls; the LLM subsystem is treated as untrusted and re-validated at the server boundary (cohort-delta output re-checked against server-held caps and PMID membership "so a misconfigured pipeline build can't slip a malformed response past us").
- **Incremental-refresh architecture (cohort-delta) as a first-class design.** Rather than full monthly regeneration, a cohort-updater LLM emits per-PMID KEEP/REMOVE/REPLACE/ADD/IGNORE decisions and only the synthesizer re-runs, skipping the expensive ~100K-token selection pass (roughly $0.19 vs ~$0.30 for a full cold-gen). Bounded by six independent drift ceilings (version mismatch, admin force, retraction, cohort age >365d, delta count >=6, per-type staleness) with a state-transition invariant table specifying which fields each path sets.
- **A surveillance engine that keeps reports current as a background concern.** A per-supplement worker (scheduled by user activity, not a global cron) watches PubMed for new and retracted studies, triages each for materiality, and signals when a cached report should refresh, so reports stay live without users re-requesting them and without full regeneration. The "living research file" property is an architecture decision, not a feature bolt-on, and it underpins the annual-pricing thesis.
- **Cache as a per-key state machine.** An 8-branch on-access refresh decision tree routes each request into serve / ttl_bump / cold_gen / cohort_delta, first-match-wins, with documented deliberate deviations from the spec ordering.
- **Cross-language contract discipline.** Age buckets, pipeline version, and goal enums are byte-mirrored across Python, server TS, and client TS with explicit version locks and build-time sync scripts - an architect's awareness of the multi-service drift problem plus a tooling solution for it.
- **Scaling thesis built into the design.** Margin improves with scale because cache-hit rate climbs and per-supplement surveillance burn is fixed per supplement (not per user); the architecture was shaped around that economic property, not just correctness.
- **Designed for graceful degradation by default.** Fail-open everywhere except where output is irreplaceable (synthesizers), with an articulated rule for when to fail open vs closed.

### C2. Infrastructure, DevOps & Operations

*Signals: can stand up, deploy, observe, and operate a real production system solo - infra setup, not just code.*

- **Deployment pipeline.** Dockerfile with the full headless-Chromium dependency set + a Python venv to sidestep PEP 668 (a comment traces it to a real puppeteer "exit code 127" incident); build-time secret injection via ARG (Vite bakes env at build, and a build script queries Postgres; Railway hides service vars from the build step unless declared as ARG); disciplined `.dockerignore` for image hygiene and secret-leak prevention; migrations applied at boot under `set -e` with a `SKIP_MIGRATE` escape hatch; `railway.toml` healthcheck config.
- **Email infrastructure (designed end-to-end; see `EMAIL_INFRASTRUCTURE_SETUP.md`).** Provider selection with cost modeling (Resend vs SES across 3k-500k emails/month, with the documented break-even where SES wins at ~100k/mo and why switching is a no-one-way-door); a single sending domain with SPF/DKIM/DMARC DNS (start `p=none`, tighten to `p=quarantine`); least-privilege API key (sending-only, domain-scoped); reply-to architecture (set per-message via SDK since neither Supabase nor Resend expose a reply-to field) plus free Cloudflare Email Routing for inbound `support@`; a key-rotation runbook naming all three update points; and email-client rendering constraints encoded (inline styles only, two font weights to avoid synthetic-bold mismatch, no web fonts, 600px max). Three email flows unified on one domain/provider. *Honesty caveat: the two lifecycle senders (public-subscription and retention) are provider-gated stubs - the queueing, dedup-clock, single-use token, and unsubscribe infrastructure is built and exercised, and the last-mile send is a documented ready-to-wire integration; Supabase auth email is the one flow live today.*
- **Request-timeout cascade tuned to real workloads.** A deliberate layered chain (pipeline fetch 360s, Express request budget ~390s, Node `server.requestTimeout` 420s, Vite dev proxy 420s) ordered so application timeouts fire before transport timeouts, motivated by a production incident where a legitimate 4:20 cold-gen tripped Node 18's default 300s timeout and closed the socket mid-response while the server logged success. (Net-new vs audit.)
- **Observability.** Cross-service request-ID propagation via AsyncLocalStorage (one ID flows through Express -> fetch -> FastAPI ContextVar, no `req` threading); structured JSON logging (pino + pythonjsonlogger) with secret redaction; Sentry wired but no-op-safe and PII-off by default; a DB-backed `/healthz` that races `SELECT 1` against a 3s ceiling so a slow Postgres can't hang the probe into a restart loop.
- **Background work.** Event-driven surveillance worker (scheduled by user activity, not cron) with atomic cursor advancement and exponential failure backoff; a chunked, lock-friendly retention-cleanup worker (5000-row `ctid` batches with inter-batch sleeps sized under the statement timeout); a GitHub Actions weekly cron using the Anthropic Batch API at 50% off with a concurrency guard.
- **Config as a tunable surface.** Surveillance and cost-cap constants read from env via a validated `readPositiveInt` with documented defaults and warn-on-invalid, so production behavior is tunable without redeploy.
- **Operational docs that read like a working SRE's.** A 212-line `RUNBOOK.md` (symptom-driven playbooks, copy-paste SQL, an honest "when to wake the founder" heuristic) and a `DEPLOYMENT.md` with an env-var matrix, a `DATABASE_URL` query-param deep-dive, rollback + secret-rotation procedures, and DR with explicit RTO (~30 min) / RPO (<=24h free, minutes with PITR).
- **Three-phase graceful shutdown.** SIGTERM drains in-flight requests against a hard 10s deadline, then stops DB-writing workers before releasing Prisma and the Chromium pool, logging per-resource.

### C3. Applied AI / LLM / Research Engineering

*Signals: production RAG and LLM orchestration with correctness, cost, and evaluation built in - the differentiated, in-demand specialization.*

- **Multi-stage, multi-model pipeline.** ~10 single-responsibility stages, each loading a versioned prompt; deliberate two-vendor assignment by task (cheap Gemini for classification/selection, Claude for synthesis), with documented "never Flash Lite for multi-constraint reasoning" boundaries and per-stage extended-thinking budgets calibrated to reasoning complexity.
- **The core engineering challenge: needle-in-a-haystack retrieval.** Minority-topic studies (erectile-dysfunction data for citrulline) must survive selection against a dominant area (exercise performance). Solved with a split PubMed search (goal-filtered + unfiltered), selector floors paired with ceilings (a discovered allocation law: floors alone let the model dump surplus into the easiest category), a forced 3-pass selection algorithm, and a Jaccard-overlap saturation diagnostic that flags faceted-search design gaps.
- **Goal-specific prompt specialization (five parallel variants).** Five goal-specialized selector + synthesizer prompt pairs (cognitive, performance, sleep, weight, immune), each with bespoke retrieval facets, mechanism pathways, and per-section coverage minimums, with every mandatory synthesizer facet held in lock-step with the PubMed query terms as an invariant (a missing search term makes the synthesizer report "Not addressed"). Maintaining five parallel prompt families under one evaluation harness is substantial applied-AI craft beyond a single generic pipeline.
- **Strict citation grounding / anti-hallucination.** Paragraph-level `citation_ids` arrays (no inline markers, a documented hallucination risk); procedural coverage verification (a numbered inventory -> audit -> resolve algorithm beat a declarative "cross-check your draft" that left 5-9 uncited abstracts); code-side guards that reject PMID-shaped or year tokens and merge only model-returned IDs that exist in the source map; literature-scoped absence claims ("None of the available studies..." not "No X exists").
- **A genuinely novel safety-pipeline design.** Two-tier grounding: common side effects are abstract-only (Tier 1), but drug interactions / contraindications / upper limits require supplementing abstracts with training knowledge (Tier 2), because no one runs trials on dangerous drug combos and ULs live in monographs, not PubMed. Four mandatory source-transparency prefixes make AI-vs-literature provenance auditable in the output.
- **Evidence-quality rating extracted into a separate cheap call** to remove the synthesizer's self-assessment bias, with ~13 calibration anchors and a dual-rating object that converts hidden uncertainty into a logged signal; code-level caps where LLM self-calibration is unreliable.
- **The self-improving prompt-iteration loop (standout).** `iterate.py` runs a closed loop: run tests -> extract coverage metrics -> an LLM agent root-causes and implements non-structural fixes -> re-run -> a structured keep/revert verdict, with git auto-commit on keep and hard-reset + failure-context injection on revert, fail-closed verdict parsing, structural-change gating to human review, and plateau detection. A user-editable strategy file steers every analyze/fix/evaluate prompt (human-in-the-loop).
- **Cost engineering.** Anthropic ephemeral prompt caching via a byte-identical system/user split (~14% off Claude cost); correct Gemini implicit-cache accounting in telemetry; the Batch API for background refresh (50% off); per-call telemetry as `Decimal` matching the Postgres column under SQL SUM; an unknown-model guard so cost never silently drops to $0.
- **Retrieval engineering depth.** Multi-faceted parallel search with deterministic merge ordering; round-robin interleave across LLM-planned research domains (anti-bias data-structure choice); a supplementation-context filter solving the dual-identity-compound problem (citrulline as biomarker vs intervention); landmark retrieval using publication-type membership as a citation-count proxy; Pydantic-constrained inputs that block PubMed query injection; dual-signal retraction detection across two inconsistent PubMed predicates.

### C4. Backend Engineering

*Signals: senior-grade concurrency, correctness, and resilience instincts in a solo codebase.*

- **Cross-instance concurrency control with Postgres advisory locks**, keys SHA-256-namespaced to avoid cross-type collision, with documented connection-pooler affinity awareness (session locks need the same physical connection, which Supabase's session pooler preserves but the transaction pooler does not; xact-lock variants added for that reason). Two-layer dedup: in-process promise map + DB advisory lock.
- **A per-supplement-per-day cost circuit-breaker.** A defensive USD ceiling (default $100/day, env-tunable) keyed by (supplement, date) in UTC; over-cap accesses are demoted to serving cached / ttl-bumped results rather than failing, with surveillance (background) cost tracked in a separate column so background work can't push a popular supplement over the user-facing cap. The residual cross-variant race is documented and accepted as a bounded-overage tradeoff. Designing a runaway-cost circuit breaker is exactly the instinct an LLM-product platform hire should have.
- **"Claim first, refund on failure" usage accounting.** Quota is incremented in one atomic Postgres statement (`INSERT ... ON CONFLICT ... DO UPDATE ... WHERE count < limit RETURNING`) that eliminates read-then-write double-spend, with a compensating decrement on pipeline failure. Closed two named race surfaces from the legacy increment. (Net-new vs audit.)
- **Cache-replay billing fairness.** A cache hit byte-identical to the user's saved copy is a "replay" that does not consume quota or burn the free-report flag; a hit that differs (a real cohort delta) does count.
- **The main orchestration route as a correctness exercise.** ~494 lines ordered: boundary validation -> profile fetch with retry -> age-bucket gate -> fail-closed screener -> parallel cache+usage+prior fetch -> cache-replay logic -> tier/quota gate -> parallel safety+advanced via settled Promise.all -> citation sanitization -> fire-and-forget cache write -> version + surveillance bootstrap -> library save -> usage increment, with the invariant "library save must succeed before charging quota; if usage increment fails after save, accept the freebie rather than delete the report."
- **Narrow-write cache semantics.** The executive-summary upsert touches only that one field and deliberately does not bump freshness/version columns, with a comment forbidding future "tidying" because drift detection must ignore the post-pass. (Net-new vs audit.)
- **Schema and migration craft.** Postgres-native types (Decimal(10,6) for cost, JSONB, TEXT[]); append-only audit/version tables; a window-function dedup before a type-changing bucket backfill; an intentionally-unenforced FK where two writers race; a timestamp-precision fix migration; partial unique indexes chosen with documented reasoning.
- **Resilience patterns.** Corrupted-row tolerance (a bad cached row falls through to a miss rather than 500ing); disconnect-tolerant responses for already-committed work; a singleton PrismaClient preventing 9x pool multiplication; retry on pgBouncer P1001/P2024 with a clean 503 on permanent failure; a long-lived Chromium pool with crash self-healing.

### C5. Security & Anti-Abuse

*Signals: defense-in-depth and abuse-resistance designed for a real public surface, including payments and an anonymous capture endpoint.*

- **Cloudflare Turnstile CAPTCHA on the anonymous capture surface** with a written threat model: per-IP rate limiting is defeated by botnets rotating across thousands of residential IPs, so Turnstile shifts the cost to solving a challenge per request. Fail-open in local dev (no secret), fail-closed in production on network error or timeout (5s cap), end-user-IP binding to make stolen-token replay harder, and a boot-time `assertTurnstileConfiguredInProd()` guard so a misconfigured deploy fails loudly. (Net-new vs audit.)
- **Double opt-in on the public-subscription flow.** A migration added `confirmed_at` + single-use `confirmation_token`, closing an "open-relay shape" where one POST could subscribe an arbitrary third party's email; pre-cutover rows grandfathered as confirmed; a partial unique index keeps the token column cleanly nullable. (Net-new vs audit.)
- **Stripe webhook metadata-tampering cross-check.** Before honoring `subscription.metadata.userId`, the handler verifies the subscription's customer matches the `stripeCustomerId` stored for that user, so a dashboard edit or key compromise can't redirect refund/dispute events to rewrite an arbitrary victim's tier. (Net-new vs audit.)
- **Plan-swap preview-binding cache.** An in-memory, short-TTL cache binds a proration preview quote to the subsequent swap call so a stale or attacker-supplied quote can't be replayed; the live re-preview rejects with 409 on >50-cent drift. (Net-new vs audit.)
- **The standard hardening stack, done well.** Helmet + a fully-pinned CSP (report-only by default with a `/api/csp-report` collector, flip via `CSP_ENFORCE`); a hand-written Permissions-Policy denying camera/mic/geolocation with `payment` scoped to Stripe; a defense-in-depth Origin/Referer anti-CSRF guard exempting the Stripe webhook; pipeline shared-secret auth with constant-time comparison and fail-loud config; input validation as a prompt-injection/DoS boundary; secret redaction in logs; tiered, key-aware rate limiting (six limiters keyed by user id or IP so a Pro user behind corporate NAT isn't throttled with strangers).
- **Admin mutation surface.** Triple-layered CSRF defense (an `X-Admin-Action` header forcing a preflight the allowlist rejects, on top of bearer auth and the origin check) and an append-only audit log whose API makes actor-spoofing impossible (actor and request id read server-side, never from caller args).
- **Hardened single-use retention-email refresh tokens** (atomically consumed in a transaction, bound to both user and supplement, LLM-authored email bodies URL-stripped to defuse prompt-injection-via-abstract, an in-memory sliding-window limit before the DB lookup to deter enumeration).
- **Privacy/GDPR.** A centralized, transactional right-to-erasure helper that hard-deletes PII and anonymizes telemetry to keep aggregates; a documented retention-policy matrix; a per-event prop allow-list so analytics can't leak un-whitelisted keys.

### C6. Frontend & Design Engineering

*Signals: advanced React, hand-built UI primitives, and the judgment to know when the obvious API is wrong.*

- **The citation + glossary text-enrichment engine (the FE crown jewel).** A two-stage, zero-overlap pipeline that parses AI prose and injects interactive, accessible React nodes: a 16-pattern statistical-notation parser (p-values, Cohen's d/g, HR/OR/RR, CIs, I-squared, NNT, PK params, with Unicode handling), first-occurrence-per-paragraph glossary matching with overlap resolution, full keyboard/ARIA on every injected node, and a bidirectional citation backlink graph ("Cited in: Cognitive, Safety").
- **Production-grade floating-UI positioning by hand** (no Floating UI / Popper): flip-when-overflowing, re-measure-after-render correction, reposition on scroll/resize, and re-finding a detached anchor by data attribute after a React remount - the hardest UI-bug category, handled defensively. Responsive surface morphing (desktop popover vs mobile bottom sheet).
- **Knowing when the obvious API is wrong.** `useReportScrollspy` documents three IntersectionObserver failure modes and chooses a rAF-throttled scroll handler instead; the collapse system uses the CSS Grid 1fr/0fr trick because framer's height:auto mis-measures nested margins; a `CompactHeader` portals to body to escape transform-containing-blocks.
- **Sophisticated React architecture.** A deliberately-ordered six-provider tree where ordering is load-bearing; `ServiceStatusContext` built on `useSyncExternalStore` (the React 18 concurrent-safe primitive) driving a degraded-service mesh with auto-retry; dual-consumer contexts (a strict hook that throws + an optional no-op hook) so the same components render in a report and on the marketing page.
- **Hydration-aware SSR/SSG handling.** A prerendered DOM that matches every browser's pre-Supabase first render (zero hydration mismatch), a one-bit session-marker cookie to serve the SPA shell vs prerendered marketing HTML and kill the anon-landing flash, and an auth-flash-prevention pattern in the navbar.
- **Build/TS rigor.** Strict mode + `tsc && vite build` so typecheck gates the build; route-level code splitting (the entire admin + Recharts subtree lazy-loaded); discriminated unions for report params.
- **Error handling as a product surface.** Window-level safety net, loop-proof error shipping with `keepalive`, animated error states with retry + prefilled support mailto, and 11 raw Supabase errors translated to context-specific copy.

### C7. Product Design & UX

*Signals: design judgment and information architecture, not just implementation - taste encoded as decisions.*

- **The "delivered artifact" report mental model.** The report is designed as a delivered artifact (a lab-result printout, a premium analytics export), explicitly escaping two prior failures: the "wall of accordion cards" and the bare-prose "Notion page." One dominant frame wraps subordinate tiles under one uniform tint recipe. Naming the failure modes and the governing metaphor is design-leadership articulation.
- **Just-in-time data collection.** The search card never blocks on missing demographics; age/sex are collected inline at the moment the user picks a goal to generate. Do not gate, collect where it's needed. (Under-weighted in audit.)
- **Progressive disclosure tuned per device.** Mobile collapses all sections from a cover sheet; desktop keeps section 1 open; "collapse all" pulls the viewport back to the top so the user isn't stranded. A long synthesis wait is covered by an 8-stage progress narrative with timed reassurance copy personalized to the supplement and goal.
- **Responsive component families from one source of truth.** Three TOC renderings (right rail, horizontal pills, masked-scroll pills) all driven by one scrollspy state.
- **Documented composition discipline.** Home-page rhythm is a taught system (a cap on dramatic full-bleed sections per page, deliberate alignment and tell-vs-show variety so no two sections repeat their format), and responsive layout is quantified rather than eyeballed (a padding-layer analysis that recovered ~16% of reading width on mobile). Composition judgment written down as rules is design leadership, not just taste.
- **Cross-page adoption guidance (restraint as a deliverable).** The design docs tell future contributors when not to reuse the artifact frame ("a library is a collection of artifacts, not one artifact").
- **Accessibility as a design input.** WCAG AA mandated at the token level with a tracked contrast audit; reduced-motion honored in 60 call sites; evidence bars pair the visual with an aria-label; a skip-link + programmatic-focus pattern; a mobile hover-stickiness fix; safe-area insets for the iPhone home indicator.
- **Honest, non-alarming information design.** A safety-at-a-glance badge maps evidence quality to green/amber and deliberately never uses safety-red (the rating measures evidence strength, not risk); a category filter that scrolls-and-flashes rather than hiding categories (hiding hurts SEO and orientation).

### C8. Visual / Brand Design & Design Systems

*Signals: original visual craft and systems thinking, with an explicit anti-template philosophy - rare in an engineer.*

- **The positional section-color system (the signature idea).** Report section color is assigned by position, not by content, so every report reads green -> sky -> violet -> yellow -> red regardless of topic. A genuinely original information-design decision and the portfolio centerpiece, with a documented dual-system fallback.
- **The anti-AI-template philosophy (the differentiator).** An explicit forbidden vocabulary (no animated gradients, glassmorphism, glow blobs, particles, stretched gradient text, pastel pricing-card gradients, "wall of citations" wallpaper, fake testimonials). A "brand-tint hover sandwich" rule. A documented color journey with rejected steps (burnt-brown -> burnt-orange, rejected for "the Hollywood teal+orange cliche," -> electric lime). Stripe/Linear/Vercel as the named aesthetic target. Restraint is itself the skill (zero glassmorphism, zero gratuitous effects across ~17,200 lines of CSS).
- **A hand-built editorial icon set that fully replaced Lucide** (~26 purpose-drawn marks, zero `lucide-react` imports), documented at the path-coordinate level (a magnifier handle starting at the stroke edge; a "1" raised one unit to correct its bottom-heavy foot), with a reusable masking system and a dev-only icon-review harness.
- **A token architecture as single source of truth.** CSS custom properties for every color/shadow/radius/easing (hardcoding forbidden), a quantified tokenization migration (inline rgba cut 55%, hardcoded brand teal cut 100%), semantic tokens computed via `color-mix()` so dark mode auto-tracks, and a registered `@property` for animatable custom properties (CSS Houdini).
- **Design-systems discipline taught as catalogues and constraints.** A fixed container-shape vocabulary (a small set of named recipes with explicit adjacency rules: pick from the catalogue, do not invent one-offs), a reusable ordinal evidence-strength primitive, a documented dark-mode transformation pattern (backgrounds invert, brand teal lightens and saturates, semantic tones lighten 30-40%, not just raw token overrides), and a color-blind hue-spacing analysis keeping the five report tones at least 60 degrees apart on the wheel. Writing the rules other contributors must follow, and the accessibility math behind them, is the design-systems skill.
- **A custom WebGL hero shader** (a hand-written GLSL "braided flow" with premultiplied-alpha screen blending and per-fragment dither to kill banding), responsive to viewport aspect, theme-aware with a 300ms eased palette cross-fade, DPR-capped, off-screen-paused, and reduced-motion-frozen, with a static SVG fallback.
- **A programmatic brand-asset pipeline** (favicon supersampling, Puppeteer-rendered OG cards with an in-memory brand-color-swap tool, a procedural grain texture baked with an SVG lighting filter) and print-design parity (the PDF shares the web design language and tone tokens).
- **Generative vector art with mathematical rigor** (106 parallel striation paths offset from one slope curve with verified tangent continuity at each Bezier join).

### C9. SEO & Growth Engineering

*Signals: a full technical-SEO stack normally owned by a dedicated team plus a CMS, hand-built for a CSR SPA.*

- **Build-time prerendering for non-JS crawlers (standout).** Headless Chromium drives each route, scrolls to trip every framer-motion in-view observer, and writes per-route static HTML, with engineered hydration safety (Supabase HTTP/WebSocket blocked during capture so the page settles to the anonymous state).
- **Programmatic SEO at scale.** ~237 URLs from data files (33 supplement landings + 192-term clinical glossary + static), propagated automatically through sitemap, prerender, and routing via build-time slug-mirroring sync scripts.
- **The full technical stack.** A type-safe per-route metadata system; 6+ schema.org JSON-LD types via builder functions; a server-generated dynamic XML sitemap with honest changefreq/priority; IndexNow instant indexing (hand-built client + on-deploy automation); per-route OG cards with a WebP pipeline and spec-accurate dual-format emission; true HTTP 404s (no soft-404) via an allowlist; a 301 www->apex redirect.
- **YMYL / E-E-A-T handling (the health-content differentiator).** Organization bylines that refuse fake "Dr. X" personas; centralized review dates feeding both the visible byline and JSON-LD `lastReviewed`; a canonical Methodology transparency page; structured data that deliberately avoids medical/effect claims (legal/regulatory awareness in an SEO build).
- **Content-quality discipline that protects the paywall.** "Coverage, not findings": free pages surface what the literature covers, not conclusions, so a naive visitor can't conclude the free page replaces the paid report, gated by two-test (paywall + actionability) authoring rules.
- **A real growth loop.** An anonymous per-supplement "notify me when new evidence appears" capture tied to the surveillance engine (now hardened with Turnstile + double opt-in, see C5), plus build-time overview prefetch that eliminates the per-pageview DB hit on SEO traffic.

### C10. Product Strategy & Business

*Signals: rigorous, quantified product thinking - segmentation, positioning, roadmap, and a legal boundary.*

- **Four-segment targeting matrix** (health-conscious / fitness / age-related-decline / newcomers), each with motivation, trust trigger, key feature, and price sensitivity, plus a cross-cutting "people on medication" variant.
- **A competitive-differentiator inventory rated by funnel-surface status** (C1-C5 vs ChatGPT, E1-E12 vs Examine.com, each Strong / Half-surfaced / Not surfaced) - positioning turned into an actionable backlog, flagging the sharpest wedge (extract-specific dosing) as currently invisible.
- **A 5-level positioning hierarchy + recommendation-neutrality legal framing** (lead with Trust, then Cost avoidance, Stack analysis, Personalization, Convenience), with an explicit "informational, not a recommendation engine" boundary and banned-vs-safe phrasing lists.
- **A per-segment feature-value matrix (1-5 scoring)** as a prioritization framework, and a pipeline-marketability assessment tying engineering to revenue ("the reports are the engine; features are the transmission").
- **Conversion architecture with iteration history** (5-second/10-second audience tests, "trust before conversion," a per-location copy table recording why prior iterations were rejected).

### C11. Billing & Monetization Engineering

*Signals: production Stripe depth well beyond a checkout button, plus pricing-strategy rigor.*

- **Three-tier pricing with deliberate anchoring** (Free / Starter $5 / Pro $15), engineered to sit below each segment's deliberation threshold with Pro as a 3x anchor; annual tiers at a chosen 17% discount with round-number psychology; a rigorous memo rejecting Lifetime and PAYG with dollar math; a documented "scam gimmick sniff test" of dark patterns to avoid; deferred-decision discipline with trigger-based revisit rules.
- **In-app plan-swap with proration preview and live drift detection** (a preview -> swap two-step, re-previewed at execute time, rejecting on >50-cent drift; bound by a preview-cache, see C5).
- **A directional proration policy as a decision matrix** (upgrades and monthly->annual charge immediately; downgrades and annual->monthly defer to period end via a Stripe Subscription Schedule, no mid-cycle clawback) - a revenue-protection decision encoded.
- **Full webhook coverage with idempotency** (7 event types, distinct sub-state branches; returns 200 even on handler error to prevent retry storms; idempotent upserts), refund/chargeback auto-downgrade with full/partial discrimination, card-decline detection across multiple Stripe error shapes, and Stripe-API-version-resilient field-access shims.
- **A price-map single source of truth that "cannot drift"** (every price ID maps to both tier and interval, built from env), tier and interval persisted atomically, and operator caveats documented like a finance/ops handbook.
- **Billing period anchored to each user's account-creation day** (not the calendar month), correctly handling month-length edges.

### C12. Data Analytics & Self-Hosted BI

*Signals: a built-from-scratch analytics + BI platform (a Mixpanel/Amplitude/Metabase substitute) entirely in the project's own Postgres.*

- **A six-layer self-hosted observability stack with no third-party processor** (structured logs -> per-run telemetry -> business events + client errors -> frontend instrumentation -> admin dashboard -> privacy/retention).
- **A governed event schema** (a 24-name compile-time TS union + runtime rejection, a per-event PII allow-list, a 4KB cap, identity attached server-side so clients can't spoof it) and stable cross-build client-error fingerprinting (`sha256(message + first stack frame)` with line/column stripped).
- **Hand-written analytical SQL.** A conversion funnel via per-visitor `BOOL_OR`; a weekly retention cohort matrix rendered as a heatmap; two-grain cost attribution (per-call vs per-user-facing-report, fanning out via `parent_request_id`) with p50/p95/max; per-LLM-call breakdown via a JSONB lateral join; cost by run-kind and by goal; cache-hit-rate cross-checked from two independent sources.
- **A 16-page Recharts admin dashboard** (Overview, Funnel, Retention, Pipeline, Revenue, Supplements, Quota, FeatureGates, Users, Errors, Surveillance, RefreshFailures, Cost-Cap, Audit) backed by ~31 endpoints, with a click-through drill-down that expands every child run's per-stage cost ("click a report, see why it cost what it cost") and a per-user lifetime-reports + lifetime-LLM-cost view.
- **Production-grade frontend product instrumentation** (a 200-event capped queue, 5s debounce, beacon-flush on pagehide, DNT no-op, offline requeue, identity stitching across the anon->auth boundary) across ~20 instrumented event sources covering the full funnel.
- **Unit economics modeled and reconciled.** Cost decomposed to per-stage/per-token/per-model; caching savings quantified; per-tier margin and an aggregate P&L at 100/1k/10k users; a runnable re-measurement recipe so the analysis is reproducible. (Keep margin figures private per house rules.)

### C13. Engineering Process & Documentation

*Signals: the discipline of a senior individual contributor or lead - process and docs as deliverables.*

- **Documentation as an engineering artifact.** A large developer doc, a 727-line empirical prompt-engineering playbook, an 855-line design system doc, a 509-line color-rationale doc, a strategy doc, an on-call runbook, and a deployment runbook with RTO/RPO. Each captures rejected alternatives and the specific bug that motivated a rule - the clearest "thinks like a senior lead" signal in the repo.
- **Trunk-based workflow with CI gates.** `main` auto-deploys to Railway; short-lived `<area>/<desc>` feature branches; a PR-checks workflow (typecheck + client/server build + prettier + eslint) is the safety net, and merging straight to main is explicitly called out as bypassing it. Husky + lint-staged pre-commit formatting.
- **Documentation-in-the-same-PR as a definition of done** (architecture / API / schema / pipeline / pricing / routing changes update the developer and deployment docs in the same PR).
- **An npm-workspaces monorepo with a rich composed build chain** (slug sync -> prisma generate -> overview prefetch -> client build -> server build -> prerender) and 20+ operational npm scripts.
- **A pragmatic, honest testing posture.** No unit tests, stated plainly; the pipeline is validated through end-to-end tests with LLM-assisted output comparison plus the self-improving iteration loop (see C3) - a sophisticated evaluation harness in place of brittle unit tests for non-deterministic output. Documented internal testing utilities (account-reset procedures, the admin CSRF-header requirement, webhook-race notes).

---

## D. New Findings Beyond the Audit

Items surfaced in this pass that are not in `RECRUITER_AUDIT.md` (or that it under-weights). They are already woven into Section C; collected here as the explicit delta.

1. **Email infrastructure as a designed system** (`EMAIL_INFRASTRUCTURE_SETUP.md`, omitted from the audit's doc list): provider cost-modeling, SPF/DKIM/DMARC DNS, least-privilege keys, reply-to architecture + Cloudflare inbound routing, key-rotation runbook, email-client rendering constraints, a shared-helper design unifying three flows. (C2) Caveat: lifecycle senders are provider-gated stubs; auth email is live.
2. **Cloudflare Turnstile CAPTCHA** with a documented botnet threat model, fail-open-dev / fail-closed-prod modes, IP-binding, timeout, and a boot guard. (C5)
3. **Double opt-in** migration that closed an open-relay shape on the anonymous capture surface, with grandfathering and a partial unique index. (C5)
4. **Stripe webhook metadata-tampering cross-check** (customer-to-stored-customer verification before honoring metadata). (C5/C11)
5. **Plan-swap preview-binding cache** preventing stale/replayed proration quotes. (C5/C11)
6. **Request-timeout cascade** (360s/390s/420s + Vite proxy) tuned to a real cold-gen incident. (C2)
7. **"Claim first, refund on failure" atomic usage increment** closing two named race surfaces. (C4)
8. **Narrow-write cache semantics** for the executive-summary upsert, with a comment forbidding future "tidying." (C4)
9. **Just-in-time demographics collection** as a UX principle (do not gate input). (C7)
10. **Config tunability** for surveillance/cost-cap constants via validated env overrides. (C2)
11. **Engineering-process discipline** made explicit (trunk-based + CI gates, conventional commits, docs-as-definition-of-done). (C13)

Also noted, for accuracy: **`CLAUDE.md` is referenced across the repo (README, CONTRIBUTING, the audit's "rule N" citations) but is gitignored and not present on disk.** Treat the design-rule content as living in `DESIGN_SYSTEM.md` / `COLOR_DESIGN.md`; do not cite `CLAUDE.md` as a portfolio artifact.

---

## E. Cross-Cutting Themes

The meta-signals that recur across every service and are themselves rare in a solo project. Good portfolio "about this project" framing.

1. **Senior-grade systems instincts in a solo build.** Advisory locks, cost circuit-breakers, request-ID tracing, three-phase shutdown, an 8-branch cache state machine, a self-improving prompt loop. Staff-level patterns, not bootcamp patterns.
2. **Honesty engineered into the product.** Citation grounding that forbids hallucinated references, literature-scoped absence claims, a no-fabricated-stats rule extended even to mockup data, recommendation-neutrality, "coverage not findings" content discipline, bylines that refuse fake personas. The promise is enforced in code, not marketing.
3. **The anti-AI-template philosophy.** A named forbidden vocabulary, a hand-built icon set that removed Lucide entirely, a Stripe/Linear/Vercel target across web and print. Counter-cultural taste, documented and enforced.
4. **Resilience and graceful degradation as the default**, with an articulated rule for when to fail open vs closed.
5. **Self-improving and self-observing systems** (the prompt loop, the six-layer observability stack, the surveillance engine, saturation/drift diagnostics).
6. **Cost-consciousness as first-class engineering** (measured unit economics reconciled to the bill, dual-vendor caching, the Batch API, cost caps, incremental refresh).
7. **Cross-language contract discipline** (enums/version/buckets byte-mirrored across three languages with sync tooling).

---

## F. Ready-to-Use Resume Bullets

Defensible against the evidence in `RECRUITER_AUDIT.md`. No em dashes; adapt numbers as the project evolves; confirm flagged figures (Section I).

**Headline / founder (top of resume)**
- Solo-designed, built, shipped, and operate Veraflux, a production three-service web platform (React/TypeScript SPA, Node/Express API, Python/FastAPI research pipeline) that turns live clinical literature into cited, evidence-graded supplement reports personalized to age, sex, and goal. Owned the full arc from product strategy, positioning, and pricing through design and engineering to deployment and operations.

**Applied AI / LLM**
- Designed and built a ~10-stage LLM pipeline (Gemini + Claude) that retrieves live PubMed literature and synthesizes cited, evidence-graded reports with strict citation grounding (zero hallucinated references) and a novel two-tier safety-knowledge supplementation model.
- Built a self-improving prompt-iteration harness that uses an LLM agent to test, root-cause, and fix prompt regressions with git-checkpointed keep/revert verdicts; codified 49 empirical prompt-engineering patterns across 17 iteration phases.
- Cut per-report LLM cost via Anthropic ephemeral prompt caching and correct Gemini implicit-cache accounting; reconciled modeled cost to the vendor bill to the cent (~$0.25-0.30/report).
- Engineered incremental "cohort-delta" report refresh that re-synthesizes only when new studies materially change findings, skipping the expensive ~100K-token selection pass.

**Architecture / Backend / Platform / SRE**
- Architected a three-service system deployed as a single Docker unit on Railway (Express public, FastAPI loopback-only), with cross-service request-ID tracing via AsyncLocalStorage, a three-phase graceful-shutdown drain, and a layered request-timeout cascade tuned to a real production incident.
- Implemented cross-instance concurrency control with Postgres advisory locks (session + transaction scoped, connection-pooler-affinity aware) plus per-supplement daily cost circuit-breakers for an LLM-backed product.
- Built an 8-branch on-access cache-refresh state machine over a 4-tier Postgres cache, atomic "claim-first, refund-on-failure" quota accounting, and event-driven background workers with atomic cursor advancement.

**Security**
- Hardened a public anonymous-capture surface against rotating-proxy botnets with Cloudflare Turnstile (fail-closed in production, IP-bound, boot-guarded) and double opt-in, and closed a Stripe webhook metadata-tampering vector with a customer-identity cross-check.

**Frontend / Design Engineering**
- Built a text-enrichment engine that parses AI-synthesized prose and injects accessible, interactive citation superscripts and glossary popovers (16-pattern statistical-notation parser, hand-rolled floating-UI positioning, full keyboard/ARIA).
- Authored a from-scratch design system: CSS-token architecture with auto-tracking dark mode, a centralized framer-motion language (reduced-motion in 60 call sites across 29 files), a hand-built icon set that fully replaced Lucide, and a custom WebGL hero shader.

**SEO / Growth**
- Hand-built a full technical-SEO stack for a CSR SPA: ~237 programmatic URLs, build-time headless-Chromium prerendering with engineered hydration safety, a dynamic XML sitemap, IndexNow instant indexing, per-route OG/WebP cards, true HTTP 404s, and a complete YMYL/E-E-A-T story across 6+ schema.org types.

**Infrastructure / DevOps**
- Stood up and operate the full production stack solo: Docker + Railway deploy (two runtimes, one container), boot-time migrations, a DB-backed healthcheck, Sentry + structured logging, scheduled Batch-API background jobs, and a transactional email architecture (Resend, SPF/DKIM/DMARC, Cloudflare inbound routing).

**Product / Business / Data**
- Authored the product strategy: four-segment targeting, a competitive-differentiator inventory rated by funnel-surface status, a recommendation-neutrality legal boundary, and a feature-value matrix driving roadmap prioritization.
- Built an in-app Stripe plan-swap flow with proration preview and live price-drift protection, plus a directional proration policy that protects revenue on downgrades.
- Built a self-hosted analytics + BI platform (no third-party processor): a governed event schema, hand-written funnel and weekly-retention-cohort SQL, two-grain LLM cost attribution, and a 16-page Recharts admin dashboard.

---

## G. Portfolio Case-Study Angles

Five deep-dive narratives that make strong portfolio pieces. Each foregrounds a non-coding skill (architecture / product / design / research judgment) with the engineering as proof. Structure each as: the problem, the insight, the build, the tradeoff.

1. **"Beating PubMed's volume bias" (research + retrieval architecture).** The problem: the studies that matter for a goal get buried because PubMed ranks by publication volume, not relevance, and minority-topic evidence dies under a dominant research area. The insight: retrieval is the real product, not the model. The build: faceted searches, split goal-filtered/unfiltered queries, selector floors paired with ceilings, a multi-pass selection algorithm, a saturation diagnostic. The tradeoff (precision vs recall): cut noise aggressively without dropping the one rare study that matters. Strong for AI/ML and research-engineer audiences.

2. **"Keeping a non-deterministic model honest" (correctness engineering).** The problem: an LLM will confidently cite studies it never saw. The build: paragraph-level citation IDs, a procedural coverage-verification algorithm that beat the declarative version, code-side guards that reject hallucinated IDs and PMID/year tokens, literature-scoped absence claims, and a separate calibrated evidence-rater to remove self-assessment bias. The theme: trust enforced in code at multiple layers.

3. **"The report as a delivered artifact" (product + visual design).** The problem: AI content reads as a template - the "wall of accordion cards" or a bare "Notion page." The insight: design the report like a lab-result printout or premium analytics export. The build: the positional section-color system (color as a flow signal, not a content semantic), one dominant frame over subordinate tiles, a hand-built icon set, and a forbidden-vocabulary anti-template philosophy executed against a Stripe/Linear/Vercel target across web and print. The portfolio centerpiece for design-engineer / product-design audiences.

4. **"A report that stays current without re-spending" (systems design + FinOps).** The problem: clinical evidence changes, but full monthly regeneration is expensive and wasteful. The build: a surveillance engine that watches PubMed per supplement, a cohort-delta refresh that re-synthesizes only when new studies materially change findings (skipping the ~100K-token selection pass), six drift ceilings bounding how far a cached report can wander, and per-supplement cost circuit-breakers. The theme: an architecture shaped by unit economics, where margin improves with scale by design.

5. **"Building my own Mixpanel + Metabase" (data + platform).** The problem: a solo founder needs product analytics and BI without paying for or trusting a third-party processor. The build: a six-layer self-hosted observability stack in the project's own Postgres, a governed event schema with server-side identity, hand-written funnel and retention-cohort SQL, two-grain LLM cost attribution, and a 16-page Recharts admin console with cost drill-downs. Strong for data-analyst / analytics-engineer / founding-engineer audiences.

A sixth, lighter angle if a security/infra story is wanted: **"Hardening a public growth surface"** (Turnstile botnet defense + double opt-in + webhook identity cross-check + the timeout cascade incident) - a tidy defense-in-depth narrative.

---

## H. Role-to-Strength Quick Map

Tailoring index: for a target role, lead with these disciplines and the single best talking point.

| Target role | Lead with (Section C) | Single best talking point |
| --- | --- | --- |
| AI / Applied-AI / LLM Engineer | C3, C1 | The self-improving prompt-iteration loop with git-checkpointed keep/revert verdicts |
| ML Infra / Platform-with-AI | C1, C2, C3 | Cohort-delta incremental refresh + per-supplement cost circuit-breaker |
| Backend Engineer | C4, C1 | Advisory locks with pooler-affinity awareness + the 8-branch cache state machine |
| Platform / DevOps / SRE | C2, C1 | Single-container dual-runtime topology + graceful shutdown + the timeout-cascade incident |
| Frontend Engineer | C6, C7 | The citation + glossary text-enrichment engine |
| Design Engineer / UI Platform | C8, C6, C7 | The positional section-color system + the WebGL shader + hand-built design system |
| Product Designer | C7, C8 | The "delivered artifact" report model and the anti-AI-template philosophy |
| SEO / Growth Engineer | C9 | Build-time prerendering with hydration safety + programmatic SEO at ~237 URLs |
| Product Manager | C10 | The competitive-differentiator inventory rated by funnel-surface status |
| Growth / Monetization | C10, C11 | Pricing psychology + the in-app plan-swap proration flow |
| Data Analyst / Analytics Engineer | C12 | Self-hosted funnel + weekly retention cohorts + two-grain cost attribution |
| Security Engineer | C5 | Turnstile botnet defense + webhook identity cross-check + double opt-in |
| Founding Engineer | C1, C2, C10, C11 | End-to-end ownership: strategy and pricing through architecture to operations |

---

## I. Accuracy & Honesty Notes

Represent these carefully. Overstating any of them is the fastest way to lose credibility in an interview.

- **Two stats to confirm before public use:** `150-200 candidate studies` per supplement and `~237 / 200+ programmatic pages`. If not comfortable, go qualitative. (Flagged in `LINKEDIN_PROFILE.md` open questions.)
- **Email lifecycle senders are stubbed.** The public-subscription and retention emailers are provider-gated stubs: the queueing, dedup, single-use-token, unsubscribe, and abuse-protection infrastructure is built and exercised, and the Resend integration is documented and ready to wire, but they do not send today. Only Supabase auth email (signup confirm, password reset) is live. Frame as "designed and built the full email architecture; auth email live, lifecycle senders ready to wire," not "sends lifecycle emails to users."
- **Margins / unit economics are private.** Per house rules, keep the 78-94% margin and the P&L out of public profiles, posts, and the portfolio site. They are usable in interviews and finance/founding-role conversations.
- **Recommendation-neutrality on anything health-facing.** Informational only ("what the evidence says," compare, check interactions), never "what to take." This is a legal boundary baked into the product; keep it in the copy too.
- **The "basic" pipeline tier is dormant.** The server never calls it in production; describe the live path (advanced + safety + stack), not the legacy Haiku basic tier, unless specifically discussing model-tiering history.
- **`CLAUDE.md` is not a citable artifact** (gitignored, absent on disk). Reference design rules via `DESIGN_SYSTEM.md` / `COLOR_DESIGN.md`.
- **No em dashes** in any drafted copy (project rule). En dashes in numeric ranges are fine.
- **Solo, but built on managed services.** "Solo" is accurate for design and engineering; be ready to note the leverage (Supabase auth/Postgres, Stripe, Railway, the model vendors) rather than implying everything including infra primitives was from scratch. The from-scratch claims that hold strongly: the pipeline, the design system, the SEO stack, the analytics/BI layer, the billing logic, the security hardening.

---

## Source Map

What backs this document, for re-verification:

- **`RECRUITER_AUDIT.md`** (879 lines) - the exhaustive evidence inventory with file:line citations across all three services; the backbone of Section C. Built from deep reads of `client/`, `server/`, `pipeline/`, `DEVELOPER_DOCS.md`, `PRODUCT_STRATEGY.md`, `pipeline/PROMPT_DESIGN.md`, `DESIGN_SYSTEM.md`, `COLOR_DESIGN.md`, `RUNBOOK.md`, `DEPLOYMENT.md`, CI config, and infra files.
- **`LINKEDIN_PROFILE.md`** (234 lines) - all of Section A (positioning, voice, settled framing, open questions).
- **`README.md`** - the canonical architecture diagram, stack, and pipeline description.
- **`EMAIL_INFRASTRUCTURE_SETUP.md`** (509 lines) - the email-infra findings in C2/D (this doc was absent from the audit's coverage).
- **`CONTRIBUTING.md` / `TESTING.md`** - the engineering-process and testing-posture findings in C13.
- **Fresh code sweep** (this pass) - Turnstile (`server/src/lib/turnstile.ts`), the double-opt-in migration (`.../20260606000000_public_subscription_double_optin`), the webhook identity cross-check (`webhookStripe.ts`), the plan-swap preview cache (`subscriptionSwap.ts`), the timeout cascade (`server/src/index.ts`), atomic usage accounting (`server/src/db/usage.ts`), and narrow-write cache semantics (`cache.ts`).
- For deeper evidence on any Section C line, the matching section number in `RECRUITER_AUDIT.md` carries the exact file:line.
