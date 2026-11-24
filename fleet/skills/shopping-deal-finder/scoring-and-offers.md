# Shopping Deal-Finder Scoring and Offer Rules

## Price calculations

**Standard Net Price**

```text
Standard Net Price = Base Price + Shipping Cost - Verified Unconditional Discounts
```

Use this only when base price and shipping are verified. If shipping is not available, do not produce a firm Standard Net Price; show the base price and mark shipping as missing.

**Conditional Net Price**

```text
Conditional Net Price = Standard Net Price - Eligible Conditional Discounts
```

Use this only when the terms are visible and the user's eligibility is known or explicitly assumed. State the condition next to the price, e.g. “₹54,999 if paid with eligible HDFC credit card, max discount ₹3,000”.

**Taxes and additional charges**

- If GST/tax is included in the listed Indian price, no separate tax adjustment is needed.
- If customs, import duty, platform fees, installation, or handling charges are not included or not visible, keep them separate as `Not available` or “additional charges may apply”.
- For international retailers, keep original currency and approximate INR separately only when a source or clearly stated exchange-rate assumption is available. Do not merge international prices with Indian prices without shipping, import duty, warranty-region, and return limitations.

## Offer classification

| Offer type | Count in Standard Net Price? | Count in Conditional Net Price? | Notes |
|---|---:|---:|---|
| Unconditional instant discount | Yes | Yes | Must be visible and applicable without special eligibility. |
| Bank/card/debit/UPI discount | No | Yes, if eligible | Verify card/payment method, minimum spend, maximum cap, and validity. |
| Coupon code | Yes only if universally applicable | Yes if user/app/account-specific | Expired or unverified codes do not apply. |
| Cashback | No | Usually no | Show separately because payout timing and eligibility vary. |
| Exchange offer | No | Scenario only | Requires user's old device/product condition and quoted value. |
| No-cost EMI | No | No | It changes financing cost, not base net price; show separately. |
| Platform coins/wallet rewards | No | Scenario only | Treat like cashback unless instantly redeemed and verified. |
| Expired offer | No | No | Mention only to explain exclusion if relevant. |
| Unverified offer | No | No | Show as unverified, not as a discount. |

## Rating normalization and Value Score

Normalize ratings to a 5-point scale before scoring:

```text
normalized_rating_5 = rating / rating_scale * 5
Value Score = normalized_rating_5 × log10(review_count + 1)
```

Use Value Score only when both rating and review count are verified for the listing or product. Keep it separate from overall recommendation score. Review volume can reduce uncertainty but is not proof of quality; explain that high review count may reflect popularity, age, or marketplace exposure.

## Recommendation score

Only calculate a final overall recommendation score when these essential inputs are verified: exact variant match, base price, shipping/free-shipping status, seller/retailer identity, product rating, review count, delivery timeline, return/replacement policy, warranty, and availability.

If any essential input is missing, do not produce a numeric overall score. Instead, rank qualitatively and list missing inputs.

When complete, use this weighted score out of 100:

| Factor | Weight | How to score |
|---|---:|---|
| Price competitiveness | 25 | Lowest verified Standard Net Price gets 100; others scale by `lowest_net_price / listing_net_price × 100`, capped at 100. |
| Product specification match | 20 | Exact model/variant and must-have specs score highest; penalize missing or weaker specs. |
| Seller/retailer credibility | 15 | Official retailer/brand, verified seller rating, fulfilment reputation, and clear availability. |
| Customer feedback strength | 15 | Use normalized rating and review depth, with caution for very low review counts. |
| Delivery timeline | 10 | Faster, verified delivery scores higher; unknown delivery reduces completeness. |
| Return and warranty quality | 10 | Clear replacement/return window and manufacturer warranty score higher. |
| Offer certainty | 5 | Unconditional verified discounts score highest; conditional or unclear offers score lower. |

```text
Recommendation Score = Σ(weight × factor_score/100)
```

## Winner selection

- **Lowest Net Price:** lowest complete Standard Net Price, not conditional price unless the user asked for that condition.
- **Highest Customer Rating:** highest verified rating; break ties using review count and rating confidence.
- **Best Overall Value:** highest complete recommendation score, or qualitative winner if scores are unavailable.
- **Most Trusted Seller:** strongest verified retailer/seller credibility and fulfilment confidence.
- **Best Warranty and Return Policy:** clearest, strongest manufacturer warranty plus return/replacement terms.

The final recommendation should explain why the winner beats alternatives and whether a cheaper listing carries trade-offs in seller reliability, warranty, returns, delivery, availability, or variant match.