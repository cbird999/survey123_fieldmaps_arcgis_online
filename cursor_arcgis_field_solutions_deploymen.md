# ArcGIS field solutions deployment plan
_Exported on 4/12/2026 at 09:53:23 PDT from Cursor (3.0.4)_

---

**User**

We need to deploy ArcGIS field solutions and are looking into both Survey123 and Field Maps. Can you assist with creating a plan to deploy these two apps so that field workers can read, create, and update data in theie daily work? We'd like a comprehensive plan from the ground up so we can fully understand the entire workflow and all technological components required. What do you think? Do you have any questions before we build this plan?

---

**Cursor**

We can build a solid end-to-end plan. Here’s a concise take and the questions that will shape it.

## How Survey123 and Field Maps fit together

- **Field Maps** is the primary app for **map-centric work**: navigate, view layers, **create and edit features** (points/lines/polygons), use related records, attachments, and **offline maps**. It’s what most “daily GIS editing in the field” looks like.
- **Survey123** excels at **structured data capture** (forms, repeats, calculations, validation) and is often used for **inspections, audits, or repeatable surveys**. It can create/update features tied to layers depending on how you design the survey and connect it to your GIS.

Together they cover: **browse → capture → update → sync**, with different UX strengths. The plan should spell out **which workflows live in which app** so you don’t duplicate logic or confuse users.

## What a “ground up” plan should cover

1. **Platform** — ArcGIS Online vs **ArcGIS Enterprise** (Portal, hosting server, data stores, federation, SSL, DNS).
2. **Identity** — ArcGIS logins vs **enterprise logins** (SAML/OIDC), groups, roles, **custom roles** for least privilege.
3. **Data** — feature layers (hosted vs registered from enterprise geodatabase), **branch versioning** if needed, domains/subtypes, **related tables**, attachments.
4. **Authoring** — ArcGIS Pro / web maps / forms; **Field Maps Designer** (map, forms, smart forms); **Survey123 Connect** for survey design and publishing.
5. **Sharing** — items, groups, **collaboration** (if multiple portals/orgs), what’s public vs org-only.
6. **Mobile** — Field Maps and Survey123 apps, **offline areas**, basemaps, tile packages if required, device requirements.
7. **Operations** — who publishes, who edits, **backup and recovery**, monitoring, and support for field staff.

I noticed you have material in the workspace about ArcGIS Enterprise ETL; if you’re on Enterprise, the plan will align Portal, services, and mobile sync with that stack.

---

## Questions before we lock the plan (high impact)

1. **ArcGIS Online, ArcGIS Enterprise, or hybrid?** If Enterprise: approximate version and whether Portal is **federated** with Server and which data store(s) you use.
2. **Who signs in?** Built-in accounts, **Active Directory / Azure AD**, or other IdP? Any requirement for **MFA** or conditional access?
3. **Offline**: Must field staff work fully offline? Approximate **map size** and **sync frequency** (daily, hourly)?
4. **Edit model**: Simple editing vs **versioned workflows** (branch versioning)? Any **editor tracking** or **attribute rules** you rely on?
5. **Data**: Mostly **hosted feature layers**, **registered enterprise layers**, or **both**? Any **sensitive** or regulated data (affects hosting and sharing).
6. **Devices**: iOS, Android, or mixed? **MDM** (Intune, etc.)?
7. **Workflow split**: Which tasks are **map-first** (Field Maps) vs **form-first** (Survey123)? Any need for **related inspections** or **repeatable line items** (often leans Survey123).
8. **Basemaps and locators**: Esri default, **your own vector/tiles**, **custom locator**?
9. **Scale**: Rough **number of editors**, **number of maps/surveys**, and whether you have a **pilot** phase.

---

## Direct answer to “What do you think?”

Yes — a single plan that walks from **accounts → data → authoring → sharing → mobile deployment → offline/sync → governance** is the right way to get shared understanding. The main design choice is **clear ownership of workflows** between Field Maps and Survey123 so training and support stay simple.

I’m in **Ask mode**, so I can only advise in text (no edits or implementation). If you answer the questions above (even briefly), the next step is a **structured, end-to-end deployment plan** tailored to your environment. If you want that plan written into a document in your repo, switch to **Agent mode** and say where you want it saved.

If you want to proceed without waiting for answers, say **“assume ArcGIS Enterprise + offline + SAML”** (or your actual combo) and I’ll draft the full plan with explicit assumptions called out.

---

**User**

Thanks. This workflow will be hybrd ArcGIS Online and Enterprise. On Enterprise we will use both hosted feature services as well as non-hosted feature services (data is located in an Enterprise database). We'll need logins for built-in accounts as well as Azure AD with MFA enabled. Field must be able to take these workflows offline. We'd expected daily sync. We will use versioned/branch editing and keep track of editor tracking info. For data hosted and registered layers and we need to take care of a few layers with sensitive data. Field workers will use iOS and Android devices but let's discuss other options too.  We have requirements for both map-first and form-first so we will implement Survey123 and Field Maps. We can use default basemaps. We expect to have a team of 20 field workers with 25 surveys and 25 field maps. Feel free to draft a plan based on my answers - unless you have more questions first.

---

**Cursor**

Skimming your existing Enterprise plan for alignment, then drafting the deployment plan.



Drafting the plan: your requirements are sufficient; we'll note hybrid collaboration patterns as explicit decision points where architecture can branch.



---

**User**

At the end of that plan, add a narrative about #1. It should be a 5-10 sentence paragraph explaining the work required and why this is important. It should sound like speaking to an interview panel. Then add three important questions that would need to be answered about that step in the process.

---

**Cursor**

I’ll append a closing section to the plan that narrates Step 1 (target architecture/hybrid boundary) in an interview-panel tone, then add three critical questions tied to that step.

Added a new closing section to your plan at `c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_hybrid_5cc267dc.plan.md`:

- `Narrative on Step 1 (Target architecture in a hybrid model)` with an interview-panel tone (8 sentences).
- `Three critical questions for Step 1` with the three decision-driving questions.

If you want, I can now do the same style of narrative + questions for Steps 2 and 3 so the whole plan has consistent executive-ready framing.

---

**User**

Yes please do #2 and #3

---

**Cursor**

I’ll extend the plan with matching interview-style narratives and three critical questions for Steps 2 and 3.

Added both requested sections to `c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_hybrid_5cc267dc.plan.md`:

- `Narrative on Step 2 (Identity and access with Azure AD + built-in accounts)`  
  - 8-sentence interview-style paragraph
  - 3 critical Step 2 questions

- `Narrative on Step 3 (Data model, services, and editing governance)`  
  - 8-sentence interview-style paragraph
  - 3 critical Step 3 questions

If you want, I can also tighten all three narratives to a uniform 6-sentence format for presentation slides.

---

**User**

From a technical lead perspective, what does the workflow look like for implementing an Arcgis survey123 project, from initial meetings to deployment? The tech lead needs to understand the overviewof the prcesss very well. GIS analysts will build the surveys and publish needed services etc.

---

**Cursor**


Here is a concise **technical-lead view** of a Survey123 implementation lifecycle. The lead owns **clarity, risk, integration, and delivery**; **GIS analysts** typically own **survey design, publishing, and layer wiring** under standards the lead sets.

---

## 1) Discovery and alignment (initial meetings)

**Purpose:** Turn “we need a survey” into a **bounded, measurable** deliverable.

**Tech lead focus**

- **Stakeholders and decision rights:** Who owns requirements, approvals, and production cutover?
- **System of record:** Where answers land (hosted layer, enterprise GDB via registered service, related tables, attachments).
- **Identity and sharing:** Which Portal/AGOL org, which groups, who can submit vs view results.
- **Offline and connectivity:** Must work fully offline? Attachment sizes? Daily sync expectations?
- **Non-functional requirements:** Performance at peak submit times, retention, PII/sensitive fields, audit needs.
- **Exit criteria:** Definition of done (UAT signoff, training complete, support model).

**Analysts:** Participate to understand data model implications and prototype questions; may sketch draft schema.

---

## 2) Solution design (architecture + data contract)

**Purpose:** Freeze the **integration shape** before heavy XLSForm work.

**Tech lead focus**

- **Feature service design:** Layer(s), relationships, domains, editor tracking, versioning implications if any, who edits what.
- **Survey123 integration pattern:** New records vs updates to existing features; inbox; repeats; URL parameters; any webhooks/automation.
- **Security model:** Layer views for field masking, group-based access, separation of sensitive surveys.
- **Environment strategy:** Dev/test/prod Portal items; naming; migration approach for schema changes.
- **Dependencies:** Basemaps, locators, other apps (Field Maps handoff), ETL boundaries (“ETL-owned” vs “field-owned” fields).

**Analysts:** Draft or validate **schema and publishing path** with the lead (avoid rework).

---

## 3) Build (survey + backing services)

**Purpose:** Implement the form and the GIS plumbing it depends on.

**Tech lead focus**

- **Standards enforcement:** Naming, choice lists source of truth, attachment policy, required fields, versioning of the XLSForm in source control if you use it.
- **Quality gates:** Peer review checklist (validation rules, repeats, performance, localization).
- **Risk items:** Large media, complex repeats, calculations, cross-form consistency.

**Analysts (typical owners)**

- Author in **Survey123 Connect** (XLSForm), test in Connect.
- Publish survey; connect to feature service as designed.
- Configure **Inbox** / submission behavior if required.

---

## 4) Integration and automation (as needed)

**Purpose:** Connect Survey123 outputs to the rest of the business stack.

**Tech lead focus**

- **Downstream consumers:** Dashboards, reports, Power BI, email/PDF feature reports, webhooks, FME/Arcade, Power Automate—whatever your org uses.
- **Idempotency and ops:** Retry behavior, failure alerts, who monitors submissions.
- **Data governance:** PII handling, export restrictions, retention.

**Analysts:** May assist with field maps/links and sample exports; lead usually owns integration contracts with IT.

---

## 5) Test and UAT

**Purpose:** Prove it works for **real devices, real accounts, real data**.

**Tech lead focus**

- **Test matrix:** iOS/Android, offline/online, low bandwidth, large attachments, multiple users submitting concurrently.
- **Security testing:** Correct group membership, no over-sharing, MFA/AAD login path on devices.
- **Versioning/ETL conflict check** if the same layers are loaded by ETL or edited elsewhere.

**Analysts:** Execute functional tests; fix survey/service issues; document known limitations.

---

## 6) Deployment and cutover

**Purpose:** Move to production with **rollback** and **support** clarity.

**Tech lead focus**

- **Promotion process:** How items move dev → prod; who approves; communication plan.
- **Training and job aids:** Short SOPs (install app, sign in, download, submit, recover from sync errors).
- **Support model:** L1 (help desk) vs L2 (GIS) vs vendor; escalation for Portal/auth issues.

**Analysts:** Final publish to prod, verify sharing, hand off documentation.

---

## 7) Operate and improve

**Purpose:** Keep the survey **healthy** after go-live.

**Tech lead focus**

- **Change control:** Schema changes, choice list updates, breaking changes to integrations.
- **Monitoring:** Submission volume, error rates, storage growth (attachments).
- **Periodic review:** Access reviews for sensitive surveys, retire obsolete forms.

**Analysts:** Minor updates, seasonal form tweaks, bug fixes.

---

## What the tech lead should internalize (overview)

1. **Requirements are half the project**—the other half is **where data lives and who can touch it**.  
2. **Survey123 is a client** to your **feature service contract**; weak contracts cause expensive rework.  
3. **Offline, identity, and sensitive data** are the usual failure modes—test them early, not at UAT.  
4. **Publishing** is not “done”; **operational ownership** (updates, access, monitoring) is part of delivery.

---

## Simple RACI-style split (your stated model)

| Area | Tech lead | GIS analysts |
|------|-----------|----------------|
| Stakeholder / risk / integration | Owns | Supports |
| Schema, security, environments | Co-owns / approves | Implements under standards |
| XLSForm, publish, inbox | Advises / reviews | Owns |
| UAT plan, go-live, support | Owns | Executes fixes |

If you want this tailored to **Portal + branch versioning + hybrid AGOL**, say so and I can call out extra decision points (where to publish, inbox with versioned services, collaboration boundaries) in one short add-on section.

---

**User**

What does "Freeze the integration shape" mean?

---

**Cursor**


**“Freeze the integration shape”** means **decide and document how Survey123 will plug into your GIS and the rest of your stack**—then treat those decisions as the **stable contract** that the survey build follows.

**“Integration”** = everything outside the wording of individual questions:

- **Where** the survey is published (Portal vs ArcGIS Online) and **who** can access it (groups, roles).
- **What feature service(s)** it writes to: layer names, geometry type, key fields, relationships, attachments.
- **What each field is for** (including read-only vs editable), **domains/coded values**, and any **editor tracking** or **versioning** rules that affect editing.
- **Behavior class:** mostly **create new features** vs **update existing** (inbox, URL parameters), vs a mix.
- **Downstream use:** dashboards, exports, webhooks, ETL—what consumes the submitted rows and what **must not change** without coordination.

**“Shape”** = the **structure** of that connection—not every label or validation rule, but the **wiring diagram**: tables, keys, cardinality (one survey row → one point vs repeats → related records), and security boundaries.

**“Freeze”** = **lock those decisions for the current release** so analysts can build the XLSForm and publish services **without thrash**. It does not mean you can never change it; it means **changes go through change control** because they ripple (schema, integrations, mobile offline, existing submissions).

**Example:** If you start with “survey creates points in `Inspections` only,” then mid-project switch to “also updates `Assets` via inbox,” you may need **new fields, new relationships, different inbox queries, and different UAT**—that is **integration shape changing** after build started. Freezing it early avoids that cost.

In short: **freeze the integration shape = agree on the data model, service boundaries, and submission pattern before deep survey authoring**, so the form is built against a stable target.

---

**User**

What does inbox, URL parameters mean in "Behavior class: mostly create new features vs update existing (inbox, URL parameters), vs a mix."

---

**Cursor**


Here’s what those terms mean in Survey123 when we talk about **create new** vs **update existing**.

### Create new (typical default)

Each submission **adds** new row(s) in the target layer (and related tables if you use repeats). Nothing is loaded from the layer first unless you add that behavior.

---

### Inbox

**Inbox** is a Survey123 feature where the **field app downloads a list of existing records** from the feature service (based on a query you define), and the user **opens one of those records** in the survey to **view or edit** it, then sends/syncs the update.

- Think: **“work queue”** or **“assigned inspections”** pulled from the layer.
- You configure **who sees what** with the inbox query (e.g., status = open, assigned to me, in my area).
- It’s the main **mobile-friendly** way to do **update existing** at scale without building custom links for every record.

---

### URL parameters

**URL parameters** are extra pieces on the **survey URL** that tell Survey123 **how to open** the survey—for example **which existing feature** to load, or **which field values to pre-fill**.

Examples of intent (names vary by setup):

- Open this survey **already focused on** feature `OBJECTID=12345` or a **GlobalID**.
- Pass a **facility ID** or **asset tag** so the form starts with those values set (and you can optionally lock them).

Common pattern: **Field Maps** (or a web map / email / QR code) opens Survey123 with a link that includes parameters so the user doesn’t manually search for the asset.

---

### Why both appear in “behavior class”

- **Inbox** = **batch / queue** of existing records inside the app.  
- **URL parameters** = **deep link** into one survey instance from **outside** Survey123 (map, web page, another app).

A **mix** is common: create new submissions for ad-hoc work, use **inbox** for assigned updates, and use **URL parameters** when the user starts from **Field Maps** on a specific feature.

If you tell me whether you mean **Portal** or **AGOL** and **create-only vs assigned edits**, I can describe the usual inbox query and link pattern for that scenario in one sentence each.

---

**User**

How could we load test surveys?

---

**Cursor**


“Load test surveys” usually means **load-testing the path a submission takes** and the systems it stresses—not tapping the Survey123 mobile UI thousands of times. In practice that is mostly **the feature layer (and sometimes attachments)**, plus **Portal/AGOL auth** if you test through real endpoints.

## 1) Decide what you are proving

Clarify the risk you care about:

- **Write load:** many users **submitting** at once (creates/updates, with or without **attachments**).
- **Read load:** many users **opening** the survey, loading **choices**, or refreshing **Inbox** (feature service **query** load).
- **Mixed:** submit + query + attachment upload (closest to a bad cell day).

Each needs different scripts and success criteria (latency, error rate, queue depth on Enterprise, etc.).

## 2) What to test technically

**Primary bottleneck (most teams):** the **feature service** `applyEdits` (and **addAttachment** if photos/files are large).

**Also include if relevant:**

- **Token acquisition** (Azure AD / Portal OAuth) under concurrency—sometimes auth or reverse proxy fails before GIS does.
- **Attachment size and count**—multipart uploads dominate time and storage.
- **Survey123 web** vs **field app**: web often easier to automate; both should still hit the **same underlying layer** for writes.

**Caution on ArcGIS Online:** aggressive testing can hit **platform throttling**, **credit-related costs**, and may conflict with **organizational acceptable use**; coordinate with Esri support or your Esri rep for high-volume testing on shared SaaS. On **Enterprise**, you own the stack—load tests are more straightforward but still need a **non-production** target or a dedicated test service.

## 3) Practical approaches (from light to heavy)

**A) Scripted REST clients (common, flexible)**  
Use Python (`requests` / `httpx`), **k6**, **Locust**, or **JMeter** to:

1. Obtain a **token** (Portal/AGOL OAuth or generateToken, per your security policy).
2. Call **Apply Edits** on the target layer with realistic JSON payloads (geometry + attributes).
3. Optionally call **Add Attachment** in parallel threads to mimic photos.

Pros: repeatable, measurable. Cons: you must mirror **valid schema**, domains, and required fields.

**B) “Record and replay” style**  
Capture a real successful `applyEdits` (browser dev tools or Fiddler), parameterize IDs, and replay under load. Fast to get realistic payloads.

**C) Soak test (lower rate, long duration)**  
Important for **daily sync** stories: steady submissions over hours to find **connection pool exhaustion**, **DB maintenance windows**, or **log disk** issues.

**D) Inbox / query load**  
Separate script: concurrent **Query** requests with the same filter your Inbox uses. This validates **database indexes**, service max record counts, and gateway timeouts.

## 4) Test data and isolation

- Use a **dedicated layer** or **version** / **branch** / **test environment** so load tests do not corrupt production or trigger downstream ETL.
- Generate **unique keys** (GUIDs) to avoid primary-key collisions during parallel inserts.
- Plan **cleanup** (delete features in batches or truncate test tables if allowed).

## 5) Metrics to capture

- **Success rate** and HTTP error breakdown (498/499 timeouts, 413 payload too large, 503).
- **p50 / p95 / p99** latency for token, applyEdits, addAttachment.
- **Server-side:** DB CPU, service CPU, connection counts, ArcGIS Server logs (if Enterprise).
- **Functional correctness:** sample of created features validates geometry and attributes.

## 6) What load testing usually does *not* replace

- **Offline conflict behavior** (device-side)—complement with a smaller **field pilot** or scripted mobile testing tools if you use them.
- **Human UX** (form logic, validation)—that is functional/UAT, not load.

---

**Bottom line:** treat Survey123 load testing as **concurrent, authenticated writes (and attachment uploads) against the feature service**, plus **Inbox/query** if read paths matter. Automate at the **REST** layer with realistic payloads and run against **Enterprise non-prod** (or AGOL only with org approval and throttling in mind).

If you share whether submissions are **create-only** vs **inbox updates**, and whether **attachments** are typical, I can suggest a minimal test matrix (e.g., 10 / 50 / 200 concurrent “submit equivalents”) and what to measure first.

---

**User**

Can explain "Idempotency and ops: Retry behavior, failure alerts, who monitors submissions."

---

**Cursor**


That line is about **what happens when something fails** and **how you avoid duplicating or losing data** when automations or integrations touch Survey123 / feature-layer submissions.

### Idempotency

**Idempotent** means: **doing the same operation more than once has the same effect as doing it once** (no extra side effects).

**Why it matters for surveys**

- If a **webhook**, **Power Automate** flow, **FME** job, or script **times out** or gets a **network error**, the sender often **retries** automatically.
- Without idempotency, a retry can **create duplicate records** (two inspections for one submit), **send duplicate emails**, or **charge/run downstream twice**.

**How teams get idempotency in practice**

- Use a **stable unique id** for each submission (e.g. a **GlobalID** from the feature, or a **submission id** you generate once and store) and have the downstream job **check “have I already processed this id?”** before acting.
- Design automations to be **upsert** or **“process once”** (dedupe table, log table, or flag on the feature).
- Avoid steps like “always insert a new row in SQL” with no natural key unless you dedupe.

Survey123’s own **sync** on the device also relates to “safe retry” (client retries until server acknowledges), but **idempotency** in that bullet was mainly about **integrations you build on top** of submitted data.

---

### Retry behavior

**Retry behavior** answers: **when failures happen, what retries automatically, how many times, how fast, and when to stop.**

You want explicit decisions for:

- **Transient failures** (503, gateway timeout, DNS blip): retry with **backoff** (wait a bit, try again).
- **Permanent failures** (400 bad request, 403 forbidden, schema mismatch): **do not** blindly retry; **alert** and **fix**.

Without a policy, you get either **endless retry loops** or **silent drops**.

---

### Failure alerts

**Failure alerts** means: when something breaks, **someone gets a signal**—not only “it failed in a log somewhere.”

Examples:

- Flow/script **failed run** notification.
- **Threshold alert** (error rate &gt; X% for 10 minutes).
- **Dead letter** queue or “failed submissions” table for manual replay.

Alerts should include **enough context** to act: survey name, feature id, user (if allowed), error code, payload snippet (careful with PII).

---

### Who monitors submissions

This is **operational ownership**, not technology:

- **Who** checks that submissions are arriving (volume normal?).
- **Who** responds when **integrations** fail or **layer** write errors spike.
- **Who** handles **user reports** (“my survey won’t send”).

Often: **GIS** owns the layer and survey config; **IT/integration** owns webhooks/connectors; **help desk** gets first contact with an escalation path.

---

**In one sentence:** define **safe retries** (idempotent downstream handling), **clear retry rules** for transient vs permanent errors, **alerts** when automation breaks, and **named owners** who watch submission health—not just whether the survey “exists.”

---

**User**

Is there a way to monitor survey123 for submission rates, submission/sync errors, etc?

---

**Cursor**


Checking current Esri options for Survey123 monitoring, analytics, and webhooks.




Yes, but it is usually **layered**: Survey123 gives you **some built-in visibility**; **serious operations monitoring** is mostly **feature-service + integration + platform logs**, because **failed syncs that never reach the server** are invisible to server-only tools.

### 1) What Survey123 gives you directly

- **Survey123 website (survey owner):** **Analyze / Data** views so you can **see responses**, build reports, and spot **gaps** (e.g., “we expected 40 today, we see 12”). That is **operational awareness**, not full observability.
- **Webhooks (after a successful write):** Survey123 supports **Survey123 webhooks** (on the form item) and **feature layer webhooks** (on the layer). They fire when records are **added/edited on the feature layer** (e.g. `addData` / `editData` style events). Those are excellent for **“submission succeeded”** automation and **counting successes** if you forward them to Power Automate, logging, SIEM, etc.  
  Docs: [Webhooks—ArcGIS Survey123](https://doc.arcgis.com/en/survey123/browser/analyze-results/webhooks.htm), [Automate workflows with Webhooks (Developer)](https://developers.arcgis.com/documentation/app-builders/low-code/arcgis-survey123/automate-workflows-with-webhooks/).

**Limitation:** Webhooks typically reflect **server-accepted** submissions. They do **not** by themselves tell you **why a phone failed to send** while offline.

### 2) Submission rates (reliable pattern)

Treat the **feature layer as the source of truth**:

- **Scheduled query** (Notebook, FME, script, database view): count features **per day/hour** using **creation date** or **editor tracking** fields.
- Compare to **expected volume** (baseline) and alert on anomalies.

This measures **what landed in GIS**, not “attempts.”

### 3) Sync / submission errors

**Server-visible errors (Enterprise especially):**

- **ArcGIS Server / hosting logs** for failed **`applyEdits`**, timeouts, auth failures (when requests actually hit the service).
- **Reverse proxy / load balancer** logs if you terminate TLS in front of Portal.

**Client-visible errors (the hard part):**

- Failed sends often show **only in the Survey123 field app** (outbox / send errors) until the user is back online. Monitoring options:
  - **Training + help desk** with a clear “capture screenshot / error text” path.
  - **MDM / mobile diagnostics** (org-dependent).
  - **Pilot metrics**: periodic checks of **pending outbox** counts in the field (manual or structured check-ins).

There is **no single Esri “Survey123 Grafana dashboard”** for all client sync failures in every deployment; teams usually **combine** webhooks + layer metrics + platform logs + support process.

### 4) ArcGIS Online vs Enterprise

- **ArcGIS Online:** org-level **status** and **activity** exist, but **fine-grained per-survey error telemetry** is still usually **webhook + layer analytics**, not a dedicated ops console.
- **ArcGIS Enterprise:** you can add **ArcGIS Monitor** (and your usual **DB/VM monitoring**) for **service health**; Survey123-specific client sync remains the same gap as above.

### 5) Practical “minimum viable monitoring” stack

1. **Layer:** daily/hourly counts by `created_date` or editor tracking → **rate dashboard + alert**.  
2. **Webhook** on successful submit → **increment metric** or **log row** (Power Automate → Data warehouse / Application Insights, etc.).  
3. **Enterprise:** **server log** alerts on **applyEdits** 5xx/spikes.  
4. **Support:** defined process for **outbox failures** and **schema/token** issues.

If you say whether you are **Portal + registered GDB** or **hosted only**, I can narrow which logs (Server vs hosted data store) matter most for failed writes.

---

**User**

Do we need to publish gis services to develop a survey123 survey?

---

**Cursor**


**Short answer:** You don’t need a separately published GIS service **just to design** a survey, but you **do** need a **feature layer** (a place for answers to go) **before the survey is a real, deployable solution** in your org.

### Designing vs deploying

| Phase | Need a published feature service? |
|--------|-----------------------------------|
| **Authoring in Survey123 Connect** (XLSForm, logic, testing on your machine) | **No** — you build the form locally. |
| **Publishing the survey** to ArcGIS Online / Portal so others can use it | **Yes, in practice** — submissions must target a **feature layer** (unless you’re only doing something very limited like a non-spatial pattern, which is uncommon for field GIS). |

### Two common patterns

1. **Survey123 creates the layer for you**  
   When you publish, Survey123 can **create a hosted feature layer** that matches your form. You did not have to publish a map service from ArcGIS Pro first; **publishing the survey** is what creates/attaches that service.

2. **Survey uses an existing layer** (your case often)  
   If the survey must write to **your** schema (enterprise GDB, domains, relationships, versioning, etc.), something must **already exist**: a **feature service** published from Pro/Server (or an existing hosted layer). Analysts **point the survey** at that service. So for that pattern, **yes — the service (or hosted layer) must exist** before or as you wire the survey to it.

### Takeaway for a tech lead

- **Development:** analysts can iterate in Connect **without** a production service.  
- **Integration with your GDB / branch versioning / editor tracking:** you typically need a **published feature service** (or clear plan to create a hosted layer) that matches the **frozen integration shape** before you lock the survey for UAT.

So: **no** for “can we start building the form?” **Yes** for “can we run this for real against our authoritative data?” — either Survey123-hosted layer or **your** published feature service, depending on design.

---

**User**

What are the advantages to publishing the layer first, and then connecting the survey to it?

---

**Cursor**


Publishing the **feature layer first**, then binding Survey123 to it, is usually the better fit when GIS is the **system of record** or when you share data across apps. Advantages:

### 1) **You own the schema**

- Domains, subtypes, field types, nullability, relationships, and attachment behavior are defined in the **geodatabase / Pro**, then reflected in the service.
- The survey **maps to your model** instead of the tool inventing field names and types that may not match enterprise standards or ETL.

### 2) **Same layer for Field Maps, Pro, dashboards, and Survey123**

- One **feature service** can back **map editing**, **form-first capture**, and **office workflows**.
- Avoids duplicate layers (“Survey123 copy” vs “Field Maps copy”) that drift and complicate reporting.

### 3) **Enterprise capabilities up front**

- **Editor tracking**, **branch versioning**, topology, attribute rules, and DB constraints are applied where they matter—before the survey goes live.
- Survey123 behavior is validated against **real** editing rules, not a simplified hosted schema.

### 4) **Clear boundary with ETL and other loads**

- You can document which fields are **ETL-owned** vs **field-editable** and enforce that at the **service/GDB** level.
- Reduces the risk that survey publishes create a layer that **ETL or other jobs don’t know about**.

### 5) **Security and sensitive data**

- **Feature layer views**, group sharing, and service-level permissions can be designed **before** the survey exists.
- Easier to prove **least privilege** and audit paths for sensitive attributes.

### 6) **Test the service without the survey**

- You can verify **applyEdits**, performance, offline/replica behavior, and auth **in Pro or a simple client** before adding XLSForm complexity.
- Failures are easier to isolate: **service vs form logic**.

### 7) **Change control**

- Schema changes follow your **GIS release process** (Pro overwrite, guided migration), with a clear impact on **both** Field Maps and Survey123.
- Survey-only republishing is less likely to accidentally redefine storage in ways that break downstream systems.

### 8) **Operations and monitoring**

- Webhooks, layer queries for submission counts, and server logs all target **one known service** that is already in your ops catalog.

---

**Tradeoff (why teams sometimes skip it):** For **small, standalone** surveys with no enterprise GDB, no other apps, and no ETL, letting Survey123 **create** a hosted layer is faster. For your hybrid Enterprise + versioning + Field Maps + sensitive layers, **publish first, connect second** is usually the right default.

**Summary:** publishing first puts **data model, governance, reuse, and operations** in the lead; connecting the survey second keeps Survey123 as a **client** to a stable, shared service rather than the place where the authoritative schema is born.

---

**User**

What's a repeat in Survey123?

---

**Cursor**


In Survey123, a **repeat** is a **block of questions that the same person can answer more than once in a single submission**—like adding **many rows** of the same kind of information without starting a new survey.

### Plain analogy

Think of the main survey as **one parent record** (for example, one **site visit** or one **inspection header**). A repeat is for **multiple line items** under that visit—for example **several defects**, **several photos with captions each**, **several species observed**, or **several equipment readings**.

### How it shows up in the app

The user typically sees **“Add” / “+”** (or similar) to add another instance of that section. Each instance is one **iteration** of the repeat.

### How it relates to your GIS data

When the survey is tied to a feature layer:

- The **main form** often maps to the **primary feature** (e.g., a point or polygon).
- **Repeats** often map to **related records** in a **related table** (one-to-many), so each repeat iteration can become **one related row** linked to the parent feature.

(Exact behavior depends on how the survey is designed and published; the important idea is **one submission, many child records**.)

### Why repeats matter technically

- They drive **schema** (parent + related table, relationships).
- They affect **performance** and **offline** behavior (more data per submit).
- They affect **reporting** (you summarize or flatten many related rows).

### Contrast

- **No repeat:** one fixed set of fields, answered once per submission.
- **Repeat:** the same sub-form structure, **0 to N times**, still **one** submit when the user sends the survey.

If you describe a workflow (e.g., “one asset, many inspection line items”), I can say whether a repeat is the right pattern versus separate surveys or related layers edited in Field Maps.

---

**User**

Give a quick example of a repeat question for a utility please.

---

**Cursor**


**Scenario (water utility):** One **work order** is a single **hydrant inspection** (parent feature: location, WO #, inspector, date). While there, the crew may find **several separate issues**—each needs its own row of details.

**Repeat:** “For each issue observed on this hydrant, capture issue type, severity, notes, and a photo.” The crew taps **Add** for issue 2, issue 3, etc., but still sends **one** survey.

**XLSForm-style sketch** (what analysts put in the **survey** sheet):

| type        | name           | label                          |
|------------|----------------|--------------------------------|
| begin repeat | issues       | Issues found on this hydrant   |
| select_one issue_type | issue_type | Issue type                  |
| integer    | severity       | Severity (1–5)                 |
| text       | notes          | Notes                          |
| image      | photo          | Photo                          |
| end repeat | issues         |                                |

In the database, that often becomes **one hydrant inspection record** plus **many related “issue” records**—one per repeat.

**Another quick utility example:** **pole inspection** with a repeat for **each defect** (guy wire, crossarm, insulator) on the same pole. Same idea: one asset visit, many child records.

---

**User**

 FYI I have confirmation that this workflow will take place with only ArcGIS online.

---

**Cursor**


Thanks for the update. Treating this workflow as **ArcGIS Online only** simplifies the architecture in several ways and changes a few assumptions from a hybrid / Enterprise picture.

### What simplifies

- **Single platform of record** for maps, surveys, and hosted layers: one **ArcGIS Online organization**, one set of groups and sharing rules, one URL/sign-in experience for Field Maps and Survey123.
- No **Portal + Server + federated hosting** operations for this program: no Enterprise-specific publishing path, no on‑prem feature service URLs for these apps (unless you separately add registered services later, which you’re not doing here).
- **Collaboration** is mostly **groups, items, and hosted feature layers** inside the org—not distributed collaboration between Portal and AGOL.

### What to re-check vs your earlier Enterprise-oriented goals

- **Branch versioning** is an **Enterprise geodatabase** pattern. **Hosted feature layers in ArcGIS Online** use ArcGIS’s **hosted** editing model, not enterprise **branch versioning** in the same sense. If “versioned editing” was a hard requirement, you’d need to align expectations with **what AGOL hosted layers support** (standard versioning of history is different from enterprise branch versioning).
- **Editor tracking** can still be relevant on layers that support it; confirm per layer type in your org’s setup.
- **“Registered” enterprise GDB layers** are **out of scope** for this AGOL-only workflow unless you later **publish or sync** data into **hosted** layers (that becomes a separate data pipeline decision).

### Operational implications (AGOL)

- **Credits** (storage, feature storage, analysis if used) and **org limits** matter for ~25 maps, ~25 surveys, attachments, and offline areas.
- **Identity**: Azure AD + MFA is still common—via **enterprise logins** (SAML/OIDC) configured on the **ArcGIS Online org**, not Portal.
- **Sensitive data**: rely on **org security**, **sharing**, **feature layer views**, **conditional access** to the org, and organizational policy on **cloud-hosted** data.

### Plan document

Your written plan in [field_maps_survey123_hybrid_5cc267dc.plan.md](c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_hybrid_5cc267dc.plan.md) still describes a **hybrid** model. If you want that file to match reality, switch to **Agent mode** and ask to **retitle and revise** it for **ArcGIS Online only** (and to replace Enterprise branching/versioning language with AGOL-appropriate editing and data rules).

If you want, next message we can align on one sentence: **“Is 100% of the authoritative data for these 50 items living only in AGOL hosted layers?”** That determines backup, ETL, and reporting expectations.

---

**User**

Can you take the @.cursor/plans/field_maps_survey123_hybrid_5cc267dc.plan.md plan and create a new one for ArcGIS Online only? Can you also add the technical lead overview for a Survey123 lifecycle, with ArcGIS Online in mind, including steps 1-7 above, as well as the answers to the questions I asked related to that?

---

**Cursor**


Reading the hybrid plan and creating an ArcGIS Online–only plan that incorporates the Survey123 technical-lead lifecycle and your Q&A.




Creating the ArcGIS Online–only plan file with adapted architecture, todos, narratives, the Survey123 technical-lead lifecycle (steps 1–7), and consolidated Q&A.




Here’s what was added.

### New plan file

**Path:** [c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_arcgis_online_plan.md](c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_arcgis_online_plan.md)

**Contents:**

1. **AGOL-only scope** — Single org as system of record; no Portal/Enterprise for this workflow; note that **enterprise branch versioning** doesn’t apply to standard hosted layers the same way; optional pointer to your ETL plan only if data is refreshed **into** AGOL from elsewhere.

2. **Updated sections 1–10** — Architecture diagram for AGOL + identity + mobile; hosted layers and views; Field Maps and Survey123 chains; sensitive data; devices; phased rollout; ops (credits, monitoring, backup/export); deliverables.

3. **Technical lead Survey123 lifecycle (steps 1–7)** — Discovery → design (integration shape) → build → integration → UAT → cutover → operate, with **ArcGIS Online** called out (groups, hosted layers, webhooks, credits).

4. **RACI table** — Lead vs analysts for AGOL.

5. **Reference Q&A** — Consolidated answers for: freezing integration shape; inbox vs URL parameters; load testing; idempotency/retries/alerts/monitoring; monitoring submission rates/errors; whether you must publish services to develop; publish-layer-first benefits; repeats + utility hydrant example.

6. **Interview-style narratives + three questions each** — Rewritten for **Step 1 (AGOL architecture)**, **Step 2 (identity on AGOL)**, and **Step 3 (hosted data governance)** — no hybrid/branch-versioning wording in those narratives.

7. **Frontmatter todos** — Six tasks aligned to AGOL-only delivery (architecture, identity, hosted governance, Field Maps package, Survey123 package, pilot).

The original hybrid plan file is **unchanged**. If you want the hybrid doc to point to this new plan or to be archived, say how you’d like that cross-link phrased.

---

**User**

@.cursor/plans/field_maps_survey123_arcgis_online_plan.md:44-65 This flowchart can not be viewed correctly - I just see the text.

---

**Cursor**


Checking the diagram block in the file for formatting or syntax issues.




Cursor’s Markdown preview often doesn’t render Mermaid—it shows the fenced block as plain text. Replacing the Mermaid block with an ASCII diagram that displays in any viewer, and adding a brief note that GitHub/Mermaid.live can render the original if needed.




Removing the HTML `<details>` block — it may render as raw HTML in some viewers. Using an ASCII diagram plus a short "Optional Mermaid" code block.




Here’s what was going wrong and what we changed.

### Why you only saw text

**Cursor’s Markdown preview usually does not render Mermaid.** Fenced ` ```mermaid ` blocks are shown as source, not as a diagram. That’s expected in many editors, not a mistake in your syntax.

### What we changed

1. **Primary figure** — Replaced the diagram with an **ASCII flow** inside a ` ```text ` block so it shows as a normal monospace diagram in Cursor and anywhere else.
2. **Short note** — Explained that previews often skip Mermaid and pointed to [Mermaid Live Editor](https://mermaid.live) for a graphical version.
3. **Optional Mermaid** — Left the original Mermaid block **below** the ASCII figure so it still works on **GitHub** (if you push the file) or when pasted into mermaid.live.

Updates are in [field_maps_survey123_arcgis_online_plan.md](c:\Users\cbird\Documents\gis_jobs\.cursor\plans\field_maps_survey123_arcgis_online_plan.md) under section 1.

