# AI Shopping & Deal-Finder Agent — Product & Implementation Plan

**Plan version:** 1.0  
**Last updated:** 26 November 2026  
**Project status:** Planning / implementation not yet started for the API and Angular UI

---

## 1. Product Vision

Build a web application that helps people research products, compare trustworthy online and offline buying options, understand discounts and payment conditions, and make evidence-based purchase decisions.

The first target market is **India**. The system should support Indian retailers and local showrooms first, while keeping the data model flexible enough to support international retailers later.

The application will have three main parts:

1. **Angular 22 frontend** — the user interface for searches, comparison, product details, and saved research.
2. **FastAPI backend** — the API, validation, search lifecycle, data persistence, and integration layer.
3. **LangGraph shopping engine** — the research and reasoning workflow that searches sources, extracts evidence, validates offers, calculates prices, and prepares recommendations.

The existing Python shopping agent is the starting point for the research engine. We will keep it and build the API and UI around it rather than rewrite it from scratch.

## 2. Product Principles

- **Evidence first:** Never invent prices, product links, sellers, ratings, review counts, offers, delivery dates, stock, or showroom details.
- **Exact product matching:** Compare the same model, storage, generation, condition, and other important specifications. Clearly separate non-identical variants.
- **Transparent pricing:** Keep the listed price, shipping, mandatory fees, unconditional discounts, and conditional offers separate.
- **Clear availability:** A search result is not proof of stock. A product page saying “available” is not confirmation of a specific local store's inventory.
- **Visible sources:** Every important extracted fact should link to its supporting source and show when it was checked.
- **No hidden eligibility assumptions:** Bank-card, coupon, exchange, cashback, wallet, and EMI offers must show their eligibility and conditions.
- **Graceful failure:** When a website, search provider, or tool is unavailable, show what could not be verified instead of filling gaps with guesses.
- **Incremental delivery:** Build a basic working server and UI first; add shopping intelligence in small, testable stages.

## 3. Target Users and Main Use Cases

### Primary use cases

- Search for a product within a budget.
- Compare the same product across Indian e-commerce retailers.
- Compare online offers with physical stores in a specified city.
- Understand the real payable price and the conditions behind each offer.
- Find the cheapest verified deal without overlooking seller trust, warranty, or returns.
- Save a search and revisit its results.
- Track a product and receive a notification when its price drops.

### Initial supported product categories

Start with common consumer electronics: smartphones, laptops, tablets, televisions, accessories, and home electronics. Keep the schemas generic so more categories can be added without redesigning the API.

### Initial retailer/source coverage

Prioritize sources relevant to India, based on availability and permitted access:

- Amazon India
- Flipkart
- Croma
- Reliance Digital
- Vijay Sales
- Tata CLiQ
- Official brand stores (for example, Apple and other manufacturers)
- Other credible Indian retailers discovered during research
- Local retailers and physical showrooms in the city requested by the user

A retailer being included in the search plan does not imply that its product page, stock, or offer is accessible or verified.

---

## 4. Technology Stack

| Layer | Planned technology | Responsibility |
|---|---|---|
| Frontend | Angular 22, TypeScript | Search experience, dashboard, comparison and product views |
| UI styling | Tailwind CSS (planned) | Responsive layout and reusable visual styles |
| Frontend state | Angular signals and services | Search state, filters, selected products and UI state |
| API | FastAPI | REST endpoints, validation, orchestration and API documentation |
| Runtime | Python 3.11+ | Existing agent and backend services |
| Agent orchestration | LangGraph + DeepAgents | Multi-stage shopping research workflow |
| LLM providers | NVIDIA Nemotron and Groq | Query understanding, extraction assistance and recommendations |
| Web search | Tavily | Live public-web discovery |
| Page reading | Existing `read_url_content` capability, subject to tool verification | Inspect publicly accessible retailer/product/offer pages |
| Data validation | Pydantic | Typed request, response and deal schemas |
| Database | MongoDB (planned for persistence phase) | Users, searches, results, saved products and price history |
| Queue/cache | Redis (future, when needed) | Durable background jobs, cache and coordination |
| Monitoring | LangSmith + application logs | Traces, errors, latency and workflow observability |
| Testing | pytest + Angular testing tools | Unit, API, integration and UI tests |

### Angular 22 environment requirement

Use an Angular 22-compatible Node.js and TypeScript toolchain. The current Angular compatibility table lists Node.js `^22.22.3`, `^24.15.0`, or `^26.0.0`, TypeScript `>=6.0.0 <6.1.0`, and supported RxJS versions. Confirm the exact supported versions again when creating the frontend, and use a currently supported Node.js LTS release where possible.

Reference: [Angular version compatibility](https://angular.dev/reference/versions) and [Angular release schedule](https://angular.dev/reference/releases).

---

## 5. Planned Repository Structure

The intended target structure is a simple monorepo with a separate frontend and backend. Existing Python files will be moved only after a backup and import/path review.

```text
ai-shopping-agent/
├── plan.md
├── README.md
├── .gitignore
├── .env.example
│
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── shopping.py
│   │   │   │   ├── deals.py
│   │   │   │   └── history.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── services/               # Search orchestration and business logic
│   │   ├── graph/                  # LangGraph state, nodes and graph builder
│   │   ├── tools/                  # Search, page reading and local discovery
│   │   ├── repositories/            # Database access (later phase)
│   │   └── tests/
│   ├── fleet/                      # Preserve exported Fleet configuration/skills
│   ├── custom_skills/
│   ├── agent.py                    # Existing agent during initial migration
│   ├── model_provider.py
│   ├── custom_tools.py
│   ├── custom_middleware.py
│   ├── cli.py                      # Keep CLI available during API transition
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   └── app/
    │       ├── core/                # API client, app config and shared services
    │       ├── layout/              # Header, sidebar and page shell
    │       ├── features/
    │       │   ├── dashboard/
    │       │   ├── product-search/
    │       │   ├── search-results/
    │       │   ├── deal-comparison/
    │       │   ├── product-details/
    │       │   ├── saved-products/  # Later phase
    │       │   └── price-tracking/  # Later phase
    │       └── shared/              # Reusable UI components and pipes
    └── ...
```

**Migration rule:** Do not move or rename the current working project files until the existing CLI, provider configuration, Fleet export, skills, and tests are backed up and the import paths are understood. The target tree is a destination, not an instruction to perform a risky bulk move immediately.

---

## 6. Application User Experience

### 6.1 Main navigation

- Dashboard
- Product Search
- Search History (later, once persistence exists)
- Saved Products (later)
- Price Tracking (later)
- Settings (later)

### 6.2 Dashboard

Initial dashboard content:

- Prominent product search form.
- Recent searches (can be session-only in the first version).
- Saved searches/products when accounts and persistence are implemented.
- Summary cards only when backed by real stored data; do not show fake activity or invented savings.

### 6.3 Product search form

Fields should support:

- Product name or natural-language request (required).
- Budget and currency (optional).
- Country/region (default India in the first release).
- City/state or delivery location (optional; required for local showroom search).
- Category (optional).
- Brand preference (optional).
- Variant specifications such as storage, RAM, size, colour, model number, generation, and condition (optional).
- Retailer preferences (optional).

Remember details already entered in the current search conversation. Ask for clarification only when a missing detail materially changes the product match. The user should be able to proceed without specifying a bank card or exchange device; show those offers separately as conditional when discovered.

### 6.4 Search progress

Show meaningful workflow states, for example:

1. Understanding product requirements
2. Planning sources
3. Searching online retailers
4. Checking local stores (when location is provided)
5. Extracting product information
6. Validating offers
7. Comparing deals
8. Preparing recommendations

Progress labels must reflect actual backend events. Do not display a stage as complete unless the backend reports it as complete.

### 6.5 Search results

Display:

- Product name and matched variant
- Retailer and seller
- Listed price
- Shipping and mandatory fees
- Verified unconditional discount
- Standard estimated payable price
- Conditional offers and eligibility
- Rating and review count, when verified
- Seller, warranty, return/replacement details
- Availability and delivery status with clear confidence labels
- Source links and source check time

Provide sorting/filtering by price, retailer, seller, rating, availability, and offer type where the data supports it.

### 6.6 Deal comparison

Show side-by-side comparison cards or a table. Clearly distinguish:

- Lowest verified standard payable price
- Best conditional offer (with eligibility)
- Best-rated listing (only with verified rating/review data)
- Most trustworthy seller (based on documented evidence)
- Best warranty/return option
- Best overall recommendation, explaining trade-offs

### 6.7 Product detail view

Show the extracted product specification, seller, price breakdown, offer terms, warranty, return policy, delivery/stock evidence, and all source links. Mark each important detail as verified, partially verified, or not verified.

### 6.8 Responsive and accessible UI

- Desktop-first comparison layout that also works on mobile.
- Keyboard-friendly controls and visible focus states.
- Semantic headings, form labels, readable contrast, and accessible status messages.
- Loading, empty, error, timeout, and partial-results states.
- No fake sample prices in production views. Development fixtures must be explicitly labelled as demo data.

---

## 7. Backend API Plan

Use a versioned API prefix: `/api/v1`.

| Method and endpoint | Purpose | Priority |
|---|---|---|
| `GET /api/health` | Server/liveness check | MVP |
| `GET /api/v1/health/ready` | Readiness check for required dependencies | Later in backend setup |
| `POST /api/v1/shopping/search` | Validate request and start a shopping search | MVP |
| `GET /api/v1/shopping/search/{search_id}` | Get search status and progress | MVP |
| `GET /api/v1/shopping/search/{search_id}/deals` | Get extracted deal results | MVP |
| `POST /api/v1/shopping/compare` | Compare a supplied set of deal IDs | Later |
| `GET /api/v1/shopping/history` | List the current user's searches | Persistence phase |
| `GET /api/v1/shopping/history/{search_id}` | Retrieve a saved search | Persistence phase |
| `POST /api/v1/products/saved` | Save a product/deal | Persistence phase |
| `GET /api/v1/products/saved` | List saved products | Persistence phase |
| `DELETE /api/v1/products/saved/{saved_id}` | Remove a saved product | Persistence phase |
| `POST /api/v1/price-tracking` | Create a price watch | Price-tracking phase |
| `GET /api/v1/price-tracking` | List price watches | Price-tracking phase |
| `DELETE /api/v1/price-tracking/{watch_id}` | Delete a price watch | Price-tracking phase |

### Search lifecycle

Shopping research can take longer than a normal API request. The API should return a `search_id` and a status. The first local development version may use a simple in-process task runner and polling. Before production, move long-running jobs to a durable worker/queue so jobs survive server restarts and can scale across instances.

Suggested statuses:

- `queued`
- `running`
- `partial`
- `completed`
- `failed`
- `cancelled`

The first frontend can poll the status endpoint. Server-Sent Events (SSE) may be added later for live progress updates.

### API design rules

- Use typed Pydantic request and response schemas.
- Return consistent error objects with a machine-readable error code and human-readable message.
- Validate budget, currency, location and request-size limits.
- Add request IDs and search IDs to logs.
- Do not return API keys, internal prompts, private environment variables, or raw provider credentials.
- Document endpoints through FastAPI's generated OpenAPI documentation.

---

## 8. Structured Data Models

Use Pydantic models and `Decimal` for monetary values rather than binary floating-point numbers.

### 8.1 Core models

**ProductSearchRequest**

- `query`: original user request
- `product_name`: parsed product name, if available
- `category`
- `brand`
- `model_number`
- `specifications`: flexible key/value data for category-specific attributes
- `condition`: for example, new/sealed, refurbished, or used
- `budget_amount` and `currency`
- `country`, `state`, `city`, and optional postal code
- `preferred_retailers`
- `include_local_stores`

**ProductIdentity**

- `canonical_name`
- `brand`
- `model_number`
- `variant_attributes` (storage, RAM, colour, size, generation, etc.)
- `condition`
- `match_confidence`
- `match_notes`

**SourceEvidence**

- `source_name`
- `source_type` (retailer page, official brand page, search result, offer terms, local business listing, etc.)
- `url`
- `checked_at`
- `field_supported`
- `evidence_summary`
- `verification_status`

**ShoppingDeal**

- `deal_id`
- `product_identity`
- `retailer_name`
- `seller_name`
- `product_url`
- `listed_price`
- `currency`
- `shipping_cost`
- `mandatory_fees`
- `verified_unconditional_discount`
- `standard_payable_price`
- `rating` and `review_count`
- `availability_status`
- `delivery_estimate`
- `warranty_details`
- `return_policy`
- `offers[]`
- `source_evidence[]`
- `checked_at`
- `data_completeness`

**Offer**

- `offer_type`: bank instant discount, coupon, cashback, exchange, EMI, wallet, sale, or other
- `discount_amount` or calculation details
- `eligible_payment_method`
- `minimum_purchase`
- `valid_from` and `valid_until`, when known
- `eligibility_conditions`
- `is_conditional`
- `verification_status`
- `source_evidence[]`

**ShoppingSearchResult**

- `search_id`
- `status`
- `progress_stage`
- `product_identity`
- `deals[]`
- `recommendations`
- `warnings[]`
- `started_at`, `completed_at`

### 8.2 Verification and availability enums

Use explicit values instead of ambiguous booleans wherever possible:

- Verification: `verified`, `partially_verified`, `not_verified`, `unavailable`
- Online availability: `in_stock`, `out_of_stock`, `unknown`
- Local store status: `store_listed`, `stock_indicated_online`, `stock_confirmed_by_store`, `not_confirmed`, `not_found`

A local business listing must never be represented as confirmed product inventory.

### 8.3 Price calculation rules

**Standard payable price**:

`listed_price + shipping_cost + mandatory_fees - verified_unconditional_discounts`

If a required value is unknown, do not silently substitute zero. Mark the calculation incomplete or show a clearly labelled estimate with the missing components.

Show conditional benefits separately:

- Bank/card discounts requiring an eligible card
- Coupon codes with eligibility requirements
- Cashback or rewards credited later
- Exchange value and exchange bonus
- EMI savings or no-cost EMI conditions
- Wallet, membership, or app-only benefits

Do not subtract conditional cashback, exchange value, or EMI benefits from the standard payable price. Clearly distinguish upfront payable amount from post-purchase rewards and total financing cost.

---

## 9. Shopping Research Engine — Feature Scope

### 9.1 Live web search

- Search multiple relevant retailers and official brand sources.
- Search for exact product variants and model numbers.
- Search separately for offers and terms.
- Include source URLs and search timestamps in internal results.
- Handle search provider errors, empty results, and rate limits.

### 9.2 Product extraction

Extract, where accessible:

- Product title, brand, exact model and variant
- Storage, RAM, size, colour and other relevant specifications
- Listed price and currency
- Seller/retailer
- Product URL
- Rating and review count
- Shipping and delivery information
- Warranty and return/replacement terms
- Availability information

Do not infer missing facts from a different variant or an unrelated search result.

### 9.3 Product matching and deduplication

- Normalize retailer titles and specification formats.
- Match exact model number and required variant attributes.
- Detect conflicting or incomplete variants.
- Deduplicate the same listing discovered through multiple search queries.
- Keep separate records for sellers offering the same product on a marketplace.

### 9.4 Offer detection and validation

Search for and classify:

- Instant bank/card discounts
- Debit-card and UPI promotions
- Coupon and promo codes
- Cashback and wallet rewards
- Exchange value and exchange bonus
- No-cost EMI and other EMI offers
- Membership/app-only promotions
- Seasonal and retailer campaign offers

For each offer, capture the terms, eligibility, minimum transaction, payment method, maximum discount, validity dates, exclusions, and source. If terms cannot be verified, mark the offer as unverified and do not include it in price calculations.

### 9.5 Local store discovery

- Search for relevant retailers and independent showrooms in the user-specified city.
- Capture store name, address, public contact details, opening hours, and source when available.
- Search for store-specific product pages or local stock indicators where supported.
- Distinguish a store listing from a confirmed quotation or confirmed stock.
- Encourage direct store confirmation when inventory cannot be verified online.
- Never invent a showroom address, phone number, quotation, or stock claim.

### 9.6 Seller and retailer trust

Assess using available evidence such as:

- Official retailer vs marketplace third-party seller
- Seller identity and seller history when publicly available
- Retailer reputation and customer feedback sources
- Return/replacement policy
- Manufacturer warranty and India-warranty status
- Payment and delivery terms

Do not label a seller “verified” or “trusted” without evidence supporting that claim.

### 9.7 Comparison and recommendations

Possible recommendation labels:

- Lowest verified standard payable price
- Best conditional offer
- Highest verified customer rating
- Best documented seller confidence
- Best warranty/returns
- Best overall value

Keep the Value Score separate from the overall recommendation. Where rating and review count are verified and comparable, use a normalized 5-point rating:

`Value Score = normalized_rating × log10(review_count + 1)`

Do not calculate the score if required inputs are missing, and do not treat the score as a substitute for seller, warranty, or availability checks.

---

## 10. LangGraph Architecture Plan

The first API integration may call the existing agent as one graph. Once the API/UI foundation works and tool execution is verified, evolve it into a specialized workflow.

### Target workflow

```text
User Query
    |
    v
Query Understanding
    |
    v
Product Identification
    |
    v
Search Planning
    |
    +-----------------------------+
    |                             |
    v                             v
Online Search                 Local Search
    |                             |
    +--------------+--------------+
                   |
                   v
           Product Extraction
                   |
                   v
            Product Matching
                   |
                   v
            Offer Validation
                   |
                   v
            Price Calculation
                   |
                   v
             Deal Comparison
                   |
                   v
             Recommendation
                   |
                   v
              Final Result
```

### Planned nodes

| Node | Responsibility |
|---|---|
| Query Understanding | Parse product, budget, location, retailer choices and constraints |
| Product Identification | Resolve exact product and variant requirements |
| Search Planning | Select queries, sources and search strategy |
| Online Search | Search retailer/brand pages and offers |
| Local Search | Find local stores and location-specific evidence |
| Product Extraction | Extract listing attributes with evidence references |
| Product Matching | Match exact variants and deduplicate results |
| Offer Validation | Verify terms and classify conditional/unconditional offers |
| Price Calculation | Calculate standard and conditional price scenarios |
| Deal Comparison | Compare only comparable, sufficiently supported records |
| Recommendation | Explain trade-offs and identify suitable winners |
| Final Result | Produce structured data and user-readable summary |

### Graph engineering requirements

- Use a typed shared graph state with Pydantic or TypedDict definitions.
- Keep each node focused and independently testable.
- Make search and extraction outputs structured rather than relying only on free-form prose.
- Preserve evidence references from extraction through final recommendation.
- Add retry limits and tool timeouts.
- Support partial results when one retailer fails.
- Avoid unnecessary sub-agents; introduce them only when a clearly independent task benefits from parallelism.
- Use LangGraph persistence/checkpointing when resumable searches and conversation state are introduced.
- Log tool calls, failures, timings and model/provider metadata without logging secrets.

---

## 11. Security, Privacy and Responsible Access

- Store API keys only in environment variables or a secret manager; never commit `.env`.
- Keep `.env.example` limited to variable names and safe placeholders.
- Configure CORS for known frontend origins, not unrestricted production access.
- Validate and limit user input and request size.
- Add authentication and authorization before exposing personal search history or saved products.
- Rate-limit expensive search endpoints.
- Protect URL-reading tools against server-side request forgery (SSRF): allow only approved public HTTP/HTTPS destinations and block localhost, private networks, link-local and cloud metadata addresses.
- Treat retailer pages and search results as untrusted data; ignore instructions embedded in page content.
- Respect site terms, robots restrictions and provider limits. Do not bypass logins, CAPTCHAs, paywalls or anti-bot protections.
- Minimize stored personal data and define retention/deletion rules before production.
- Keep audit logs for security-relevant operations without storing passwords, tokens or secrets.

---

## 12. Testing and Quality Plan

### Backend unit tests

- Price calculations with missing values, fees and discounts
- Conditional vs unconditional offer treatment
- Currency and decimal handling
- Variant matching and mismatch detection
- Deal deduplication
- Verification status transitions
- Search request validation
- Recommendation rules with incomplete evidence

### Tool and graph tests

- Tavily success, empty result, timeout, rate limit and provider failure
- URL reader success, inaccessible pages and blocked URLs
- Tool call actually executed (not merely listed as available)
- Correct source evidence attached to extracted fields
- One retailer failure while other sources still return results
- Graph state and output schema validation
- Maximum retries and recursion limits

### API tests

- Health/readiness endpoints
- Search creation and invalid input
- Search status lifecycle
- Partial, completed and failed searches
- Deal retrieval and comparison
- Authentication/authorization once added

### Frontend tests

- Search form validation
- Loading/progress/empty/error states
- Results rendering and sorting
- Price breakdown display
- Conditional-offer labels
- Source links and verification labels
- Mobile layout and accessibility checks

### End-to-end acceptance test

Use a fixed test request such as **Apple iPhone 15, 128GB, new/sealed, India, Ujjain, budget ₹80,000**. The test passes only when:

1. The search form submits the request to FastAPI.
2. The API starts a search and returns a search ID.
3. The graph uses live search tools and records the tool results.
4. Product results match the specified 128GB variant.
5. Every displayed price has supporting source evidence or is explicitly marked unverified.
6. Conditional discounts are not mixed into the standard payable price.
7. Local store listings are not misrepresented as confirmed stock.
8. Angular displays the returned results, sources, warnings and recommendation.
9. Search/tool failures are shown honestly without invented fallback prices.

Do not use the previous unverified iPhone price snapshot as test truth. Tests should assert evidence and calculation behavior, not hard-code volatile retailer prices.

---

## 13. Implementation Phases and Acceptance Criteria

The plan intentionally puts a basic server and UI before the full shopping engine. Each phase should leave the project in a runnable state.

### Phase 0 — Project baseline and safety

**Work**
- Review the current `ai-shoping-agent` files and Git status.
- Create/confirm a clean Git checkpoint or backup before restructuring.
- Preserve `fleet/`, `custom_skills/`, provider configuration, tests and CLI.
- Confirm Python 3.11 environment and dependencies.
- Confirm `.env` and other secrets are excluded from Git.
- Fix the debug loop so all loaded tool names are printed.

**Done when**
- Existing CLI still starts and responds.
- Full tool-name list can be inspected.
- Tool availability and tool execution are recorded as separate checks.
- No secrets are committed.

### Phase 1 — Basic FastAPI backend

**Work**
- Add FastAPI and ASGI server dependencies.
- Create backend application entry point and configuration.
- Add `GET /api/health`.
- Add CORS configuration for the local Angular development origin.
- Add a versioned API router and initial Pydantic schemas.
- Add a minimal search endpoint that validates input and returns a clearly labelled placeholder/status response until graph integration is ready.
- Add pytest tests and local run instructions.

**Done when**
- Backend starts locally with one documented command.
- Health endpoint returns a valid JSON response.
- Invalid search requests return useful validation errors.
- OpenAPI docs are available locally.

### Phase 2 — Angular 22 application shell

**Work**
- Create the Angular 22 application with a compatible Node.js/TypeScript toolchain.
- Add routing, app layout, header/sidebar and responsive page shell.
- Build dashboard and product-search pages.
- Build reusable form controls and loading/error/empty states.
- Use clearly labelled demo fixtures only where needed for UI layout.

**Done when**
- Angular app starts locally.
- Dashboard and search form work responsively.
- Form validation is functional.
- No demo data is presented as live retailer data.

### Phase 3 — Connect Angular and FastAPI

**Work**
- Add an Angular API service and typed frontend interfaces.
- Configure development proxy or environment-based API URL.
- Submit search requests to FastAPI.
- Display search ID and status.
- Implement polling for search completion.
- Render a typed response and handle errors.

**Done when**
- User can submit a product request in Angular.
- FastAPI receives and validates it.
- Angular shows the returned status/results without manual API tools.

### Phase 4 — Integrate the existing LangGraph agent

**Work**
- Connect FastAPI search service to the current LangGraph agent.
- Preserve the CLI so backend and graph can be debugged independently.
- Verify that Tavily and URL-reading tools are loaded and callable.
- Add graph input/output schemas and error handling.
- Add truthful progress/status updates.
- Record traces in LangSmith.

**Done when**
- A search submitted in Angular reaches the graph.
- Actual tool calls are visible in logs/traces.
- Tool failures are returned as warnings/errors, not fabricated results.
- A structured graph response reaches Angular.

### Phase 5 — Reliable shopping research capabilities

**Work**
- Complete live search across selected retailers.
- Extract product fields and source evidence.
- Match exact variants and deduplicate listings.
- Detect and validate bank, coupon, cashback, exchange and EMI offers.
- Implement local store discovery.
- Validate seller, warranty, return and availability evidence.
- Handle partial results and unavailable websites.

**Done when**
- A multi-retailer search can return comparable, source-backed deals.
- Each field has an explicit verification status.
- No unsupported price, seller, stock or offer claim is presented as verified.

### Phase 6 — Specialized LangGraph workflow and pricing engine

**Work**
- Introduce typed graph state and focused nodes from Section 10.
- Parallelize online and local search where beneficial.
- Add product matching, offer validation and price calculation stages.
- Add deterministic calculation utilities and recommendation rules.
- Add retry, timeout, checkpoint and partial-result behavior.

**Done when**
- The workflow stages can be tested independently.
- Deal results conform to Pydantic schemas.
- Price calculations pass unit tests.
- Recommendation explanations cite the evidence and trade-offs.

### Phase 7 — Search persistence and user accounts

**Work**
- Add MongoDB repositories and schemas.
- Persist search requests, statuses, results and timestamps.
- Add authentication and user-owned search history.
- Add saved products and saved searches.
- Define retention, export and deletion behavior.

**Done when**
- An authenticated user can retrieve only their own saved data.
- Search history survives backend restarts.
- Database errors are handled safely.

### Phase 8 — Price tracking and notifications

**Work**
- Add product watchlists and target-price rules.
- Schedule recurring price checks with controlled frequency.
- Store price history and source timestamps.
- Notify users about meaningful price changes through configured channels (email first; other channels later).
- Avoid alerting on unverified or incomparable variants.

**Done when**
- A user can create, view and delete a price watch.
- Price history records source and variant identity.
- Notifications are triggered only by validated changes.

### Phase 9 — Production hardening and deployment

**Work**
- Move long-running searches from in-process tasks to a durable queue/worker.
- Add Redis for job coordination/cache where justified.
- Add rate limiting, authentication hardening, SSRF protection and secret management.
- Add structured logs, metrics, error monitoring and LangSmith tracing.
- Add caching with freshness rules and source timestamps.
- Add CI, dependency/security checks and automated test runs.
- Configure production deployment, HTTPS, backups and operational documentation.

**Done when**
- Jobs survive application restarts.
- API and workers can scale independently.
- Monitoring and alerts cover critical failures.
- Deployment and recovery procedures are documented and tested.

---

## 14. Performance, Reliability and Cost Controls

- Set per-provider timeouts and bounded retries.
- Parallelize independent retailer searches without exceeding provider limits.
- Cache search results only with a clear freshness timestamp and expiry policy.
- Do not present stale cached prices as live prices.
- Avoid repeating the same query and page read within one search run.
- Store raw source facts separately from LLM-generated summaries.
- Use deterministic Python functions for calculations; do not ask an LLM to do financial arithmetic.
- Track search latency, provider usage, token usage and errors.
- Support cancellation for searches when practical.
- Set maximum retailers, pages, and search depth per request to control cost.

---

## 15. Non-Goals for the Initial Release

The first release will **not**:

- Buy products or place orders on behalf of the user.
- Handle retailer account logins or payments.
- Bypass CAPTCHAs, anti-bot protections, paywalls or retailer restrictions.
- Guarantee a price match or local-store stock without direct evidence.
- Claim universal coverage of every retailer.
- Require user bank-card or exchange details before showing general offers.
- Build a complex multi-agent system before the basic API/UI and tool execution are reliable.
- Add subscriptions, affiliate monetization or advertising until the core product is useful and trustworthy.

---

## 16. Immediate Next Steps

Work through these in order; do not start all phases simultaneously.

- [ ] Review the existing repository and create a clean Git checkpoint.
- [ ] Confirm the existing CLI and provider setup still work.
- [ ] Fix the tool-name debug indentation and capture the full list.
- [ ] Verify an actual Tavily search invocation and inspect its returned evidence.
- [ ] Add the FastAPI backend skeleton and health endpoint.
- [ ] Test the backend locally before creating the frontend.
- [ ] Create the Angular 22 application and its initial dashboard/search page.
- [ ] Connect the search form to the FastAPI API.
- [ ] Integrate the existing LangGraph agent after the basic API/UI flow works.

**Current immediate milestone:** a locally running FastAPI server and Angular 22 interface where a user can submit a product search and see a valid API response. The response can initially be a clearly labelled placeholder; live shopping research is integrated in the following milestone.

---

## 17. Definition of a Successful First Usable Release

A user can open the Angular application, enter a product and optional budget/location, submit the search, see honest progress, and receive a structured comparison from the FastAPI backend. Each deal displays its product variant, retailer/seller, price breakdown, conditional offers, availability confidence, and source evidence. The user can understand why a recommendation was made and which facts still need confirmation.

The application is successful only when it is useful **and** transparent about uncertainty. A polished UI must never make unverified shopping data look authoritative.
