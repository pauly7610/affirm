"""Generate mock offers with deterministic embeddings for the prototype."""

from __future__ import annotations

import hashlib
import numpy as np

from app.config import get_settings

CATEGORIES = ["electronics", "travel", "sneakers", "home", "fitness", "gaming", "fashion", "appliances"]

MOCK_OFFERS = [
    # Electronics
    {"merchantName": "Best Buy", "productName": 'MacBook Air M3 15"', "category": "electronics", "totalPrice": 1299, "termMonths": 24, "apr": 0, "monthlyPayment": 54.13, "eligibilityConfidence": "high"},
    {"merchantName": "Best Buy", "productName": "Dell XPS 14 Laptop", "category": "electronics", "totalPrice": 899, "termMonths": 12, "apr": 0, "monthlyPayment": 74.92, "eligibilityConfidence": "high"},
    {"merchantName": "Amazon", "productName": "Samsung Galaxy S25 Ultra", "category": "electronics", "totalPrice": 1199, "termMonths": 24, "apr": 5.99, "monthlyPayment": 53.12, "eligibilityConfidence": "med"},
    {"merchantName": "Apple", "productName": 'iPad Pro 13"', "category": "electronics", "totalPrice": 1099, "termMonths": 12, "apr": 0, "monthlyPayment": 91.58, "eligibilityConfidence": "high"},
    {"merchantName": "Best Buy", "productName": "Sony WH-1000XM6 Headphones", "category": "electronics", "totalPrice": 349, "termMonths": 6, "apr": 0, "monthlyPayment": 58.17, "eligibilityConfidence": "high"},
    {"merchantName": "Newegg", "productName": "ASUS ROG Laptop", "category": "electronics", "totalPrice": 1599, "termMonths": 24, "apr": 9.99, "monthlyPayment": 73.28, "eligibilityConfidence": "med"},
    {"merchantName": "Best Buy", "productName": 'LG C4 65" OLED TV', "category": "electronics", "totalPrice": 1799, "termMonths": 24, "apr": 15.99, "monthlyPayment": 87.45, "eligibilityConfidence": "low"},
    {"merchantName": "Amazon", "productName": "Kindle Scribe", "category": "electronics", "totalPrice": 389, "termMonths": 6, "apr": 0, "monthlyPayment": 64.83, "eligibilityConfidence": "high"},
    # Travel
    {"merchantName": "Expedia", "productName": "Cancún All-Inclusive 5 Nights", "category": "travel", "totalPrice": 2200, "termMonths": 12, "apr": 10.99, "monthlyPayment": 194.22, "eligibilityConfidence": "med"},
    {"merchantName": "Priceline", "productName": "Miami Beach Weekend", "category": "travel", "totalPrice": 680, "termMonths": 6, "apr": 0, "monthlyPayment": 113.33, "eligibilityConfidence": "high"},
    {"merchantName": "Expedia", "productName": "NYC City Break 3 Nights", "category": "travel", "totalPrice": 950, "termMonths": 6, "apr": 5.99, "monthlyPayment": 161.42, "eligibilityConfidence": "high"},
    {"merchantName": "Booking.com", "productName": "Costa Rica Adventure 7 Nights", "category": "travel", "totalPrice": 3100, "termMonths": 18, "apr": 12.99, "monthlyPayment": 189.66, "eligibilityConfidence": "low"},
    {"merchantName": "Southwest Vacations", "productName": "Denver Ski Trip", "category": "travel", "totalPrice": 1450, "termMonths": 12, "apr": 0, "monthlyPayment": 120.83, "eligibilityConfidence": "high"},
    # Sneakers
    {"merchantName": "Nike", "productName": "Air Max Dn", "category": "sneakers", "totalPrice": 160, "termMonths": 4, "apr": 0, "monthlyPayment": 40.00, "eligibilityConfidence": "high"},
    {"merchantName": "Adidas", "productName": "Ultraboost 5", "category": "sneakers", "totalPrice": 190, "termMonths": 4, "apr": 0, "monthlyPayment": 47.50, "eligibilityConfidence": "high"},
    {"merchantName": "Nike", "productName": "Jordan 4 Retro", "category": "sneakers", "totalPrice": 215, "termMonths": 4, "apr": 0, "monthlyPayment": 53.75, "eligibilityConfidence": "med"},
    {"merchantName": "New Balance", "productName": "990v6", "category": "sneakers", "totalPrice": 199, "termMonths": 4, "apr": 0, "monthlyPayment": 49.75, "eligibilityConfidence": "high"},
    # Home
    {"merchantName": "Wayfair", "productName": "Sectional Sofa Set", "category": "home", "totalPrice": 1850, "termMonths": 18, "apr": 5.99, "monthlyPayment": 108.22, "eligibilityConfidence": "med"},
    {"merchantName": "IKEA", "productName": "KALLAX Shelf + Desk Combo", "category": "home", "totalPrice": 420, "termMonths": 6, "apr": 0, "monthlyPayment": 70.00, "eligibilityConfidence": "high"},
    {"merchantName": "Home Depot", "productName": "Dyson V15 Detect Vacuum", "category": "home", "totalPrice": 749, "termMonths": 12, "apr": 0, "monthlyPayment": 62.42, "eligibilityConfidence": "high"},
    {"merchantName": "Wayfair", "productName": "King Mattress + Frame", "category": "home", "totalPrice": 1200, "termMonths": 12, "apr": 9.99, "monthlyPayment": 105.49, "eligibilityConfidence": "med"},
    {"merchantName": "West Elm", "productName": "Mid-Century Dining Table", "category": "home", "totalPrice": 999, "termMonths": 12, "apr": 0, "monthlyPayment": 83.25, "eligibilityConfidence": "high"},
    # Fitness
    {"merchantName": "Peloton", "productName": "Bike+ Bundle", "category": "fitness", "totalPrice": 2495, "termMonths": 24, "apr": 0, "monthlyPayment": 103.96, "eligibilityConfidence": "med"},
    {"merchantName": "REI", "productName": "Garmin Fenix 8 Watch", "category": "fitness", "totalPrice": 899, "termMonths": 12, "apr": 0, "monthlyPayment": 74.92, "eligibilityConfidence": "high"},
    {"merchantName": "Rogue Fitness", "productName": "Home Gym Starter Pack", "category": "fitness", "totalPrice": 1650, "termMonths": 18, "apr": 5.99, "monthlyPayment": 96.50, "eligibilityConfidence": "med"},
    # Gaming
    {"merchantName": "PlayStation", "productName": "PS5 Pro Bundle", "category": "gaming", "totalPrice": 699, "termMonths": 12, "apr": 0, "monthlyPayment": 58.25, "eligibilityConfidence": "high"},
    {"merchantName": "Microsoft", "productName": "Xbox Series X + Game Pass", "category": "gaming", "totalPrice": 559, "termMonths": 12, "apr": 0, "monthlyPayment": 46.58, "eligibilityConfidence": "high"},
    {"merchantName": "Razer", "productName": "Blade 16 Gaming Laptop", "category": "gaming", "totalPrice": 2799, "termMonths": 24, "apr": 15.99, "monthlyPayment": 136.01, "eligibilityConfidence": "low"},
    {"merchantName": "Steam Deck", "productName": "Steam Deck OLED 1TB", "category": "gaming", "totalPrice": 649, "termMonths": 6, "apr": 0, "monthlyPayment": 108.17, "eligibilityConfidence": "high"},
    # Fashion
    {"merchantName": "Nordstrom", "productName": "Canada Goose Parka", "category": "fashion", "totalPrice": 1050, "termMonths": 12, "apr": 10.99, "monthlyPayment": 92.71, "eligibilityConfidence": "med"},
    {"merchantName": "SSENSE", "productName": "Common Projects Sneakers", "category": "fashion", "totalPrice": 425, "termMonths": 4, "apr": 0, "monthlyPayment": 106.25, "eligibilityConfidence": "high"},
    # Appliances
    {"merchantName": "Home Depot", "productName": "Samsung French Door Fridge", "category": "appliances", "totalPrice": 2199, "termMonths": 24, "apr": 5.99, "monthlyPayment": 97.38, "eligibilityConfidence": "med"},
    {"merchantName": "Lowe's", "productName": "LG Washer/Dryer Stack", "category": "appliances", "totalPrice": 1899, "termMonths": 18, "apr": 0, "monthlyPayment": 105.50, "eligibilityConfidence": "high"},
    {"merchantName": "Best Buy", "productName": "Breville Barista Express", "category": "appliances", "totalPrice": 599, "termMonths": 6, "apr": 0, "monthlyPayment": 99.83, "eligibilityConfidence": "high"},
]


def _deterministic_embedding(text: str, dim: int = 384) -> list[float]:
    """Generate a deterministic pseudo-embedding from text via hash seeding."""
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.RandomState(seed)
    vec = rng.randn(dim).astype(np.float32)
    vec = vec / np.linalg.norm(vec)
    return vec.tolist()


def build_offers() -> list[dict]:
    """Return fully-formed offer dicts with IDs, embeddings, disclosures, and reasons."""
    settings = get_settings()
    dim = settings.EMBEDDING_DIM
    offers = []
    for i, raw in enumerate(MOCK_OFFERS):
        offer_id = f"offer-{i+1:03d}"
        embed_text = f"{raw['category']} {raw['merchantName']} {raw['productName']} ${raw['totalPrice']} {raw['apr']}% APR {raw['termMonths']} months"
        embedding = _deterministic_embedding(embed_text, dim)

        confidence = raw["eligibilityConfidence"]
        if confidence == "high":
            reason = "Strong match for your spending profile and payment history."
        elif confidence == "med":
            reason = "Good fit based on your eligibility estimate."
        else:
            reason = "Available option — final terms confirmed at checkout."

        offers.append({
            **raw,
            "id": offer_id,
            "imageUrl": None,
            "embedding": embedding,
            "reason": reason,
            "disclosure": "Final approval happens at checkout.",
        })
    return offers


MOCK_PLANS = [
    {
        "id": "plan-001",
        "merchantName": "Apple",
        "productName": 'MacBook Pro 14"',
        "remainingBalance": 812.00,
        "monthlyPayment": 83.25,
        "nextPaymentDate": "2026-03-01",
        "totalPaid": 1186.00,
        "totalAmount": 1998.00,
        "termMonths": 24,
        "apr": 0,
    },
    {
        "id": "plan-002",
        "merchantName": "Peloton",
        "productName": "Bike+ Monthly",
        "remainingBalance": 1247.00,
        "monthlyPayment": 103.96,
        "nextPaymentDate": "2026-03-15",
        "totalPaid": 1248.00,
        "totalAmount": 2495.00,
        "termMonths": 24,
        "apr": 0,
    },
    {
        "id": "plan-003",
        "merchantName": "Wayfair",
        "productName": "Sectional Sofa",
        "remainingBalance": 432.88,
        "monthlyPayment": 108.22,
        "nextPaymentDate": "2026-03-10",
        "totalPaid": 1417.12,
        "totalAmount": 1850.00,
        "termMonths": 18,
        "apr": 5.99,
    },
]

MOCK_INSIGHTS = [
    {
        "id": "ins-001",
        "text": "You save more when plans stay under $50/mo.",
        "type": "saving",
        "sparklineData": [42, 38, 45, 36, 32, 29, 34],
    },
    {
        "id": "ins-002",
        "text": "You often choose 0% APR. Keep it up.",
        "type": "behavior",
        "sparklineData": None,
    },
    {
        "id": "ins-003",
        "text": "Next month: projected obligations $112.",
        "type": "projection",
        "sparklineData": [95, 102, 108, 112, 115, 112, 110],
    },
]

MOCK_USER = {
    "name": "Paul Carpenter",
    "spendingPower": 1200,
    "activePlansCount": 3,
    "paymentStatus": "excellent",
    "accountHealth": "strong",
}

MOCK_ELIGIBILITY = {
    "spendingPower": 1200,
    "explanation": "This is an estimate based on your payment history and profile. Final approval happens at checkout.",
    "lastRefreshed": "2026-02-25T10:30:00Z",
}


if __name__ == "__main__":
    offers = build_offers()
    print(f"Generated {len(offers)} offers across {len(set(o['category'] for o in offers))} categories")
    for o in offers[:3]:
        print(f"  {o['id']}: {o['merchantName']} — {o['productName']} (${o['monthlyPayment']}/mo, {o['apr']}% APR)")
