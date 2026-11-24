# Shopping Deal-Finder Validation Tests

Use these scenarios to validate future changes and spot regressions. They are designed as configuration-level/manual tests for the Fleet agent; run them with live web tools when a full shopping regression is needed.

## Global acceptance checks

Every scenario should verify:

- No fabricated price, rating, review count, shipping, delivery, seller, warranty, return policy, URL, or discount.
- Exact variants are separated; different RAM/storage/size/colour/model/condition/warranty-region listings are not treated as identical.
- Expired or unverified offers are not presented as active discounts.
- Standard Net Price uses only verified unconditional discounts.
- Conditional Net Price is separate and names eligibility conditions.
- Cashback, exchange, and no-cost EMI are not unconditional price reductions.
- Missing information is shown as `Not available` and not silently filled.
- Each recommendation cites evidence and explains trade-offs.
- International prices are clearly separated from Indian prices and do not hide shipping, currency, tax, import duty, or warranty-region uncertainty.

## Scenario matrix

| # | Scenario | Test query | Expected behavior |
|---:|---|---|---|
| 1 | Laptop under ₹60,000 for programming | “Find the best laptop under ₹60,000 for programming.” | Extract India/INR, laptop, budget, programming specs. Prefer 16GB RAM/SSD/current CPU when possible. Compare Indian retailers. Do not ask a follow-up unless must-have specs are unclear enough to change the result. |
| 2 | iPhone price comparison across Indian platforms | “Compare iPhone 17 prices across Indian shopping websites.” | Ask or state assumptions for storage/variant if needed. Do not compare different storage/colour/region variants as identical. Prioritize Indian retailers and direct links. |
| 3 | Best 4K television under ₹50,000 | “Find the best 4K television under ₹50,000.” | Extract screen/category/budget; if size is missing, either ask if size matters or present size-specific winners. Verify model, panel size, warranty, delivery/install constraints. |
| 4 | Budget wireless headphones under ₹5,000 | “Find wireless headphones with good noise cancellation under ₹5,000.” | Convert vague “good noise cancellation” into filters such as ANC/ENC, battery life, ratings, and review depth. Compare Indian listings and avoid fake/unclear ANC claims. |
| 5 | Missing shipping information | Any product where one retailer lacks shipping data | Mark shipping as `Not available`; do not compute firm Standard Net Price for that listing. It can appear in the table but cannot win Lowest Net Price unless shipping is verified/free. |
| 6 | Expired coupon | A product with a coupon source showing an expired validity date | Classify the coupon as expired and exclude it from both Standard and Conditional Net Price. Mention it only as excluded evidence if helpful. |
| 7 | Different variants | Two listings with different RAM/storage/model/condition | Keep listings separate or mark as non-comparable. Do not deduplicate or choose the cheaper one as equivalent. |
| 8 | International retailer | An Amazon US/Walmart/Best Buy/Newegg listing compared with Indian listings | Show USD and approximate INR separately only with assumptions/source. Keep shipping, import duty, taxes, warranty-region, and return limitations explicit; do not merge with Indian net price unless complete. |

## Static validation status — 2026-11-24

- Existing implementation inspected: `/memories/AGENTS.md`, `/memories/tools.json`, and `/memories/skills/shopping-deal-finder/SKILL.md`.
- No standalone code project or executable test suite was present in the workspace; the implemented tests are therefore documented regression scenarios rather than runnable unit tests.
- The upgraded instructions now map each required scenario to explicit behavior, missing-data handling, offer eligibility, variant separation, and final-output requirements.
- Live regression runs should be executed with current web sources before relying on specific market results, because prices and offers change rapidly.