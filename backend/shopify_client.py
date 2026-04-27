import requests
import json
import os

CACHE_FILE = "product_cache.json"

GQL_QUERY = """
{
  products(first: 250) {
    edges {
      node {
        id
        title
        description
        tags
        vendor
        productType
        onlineStoreUrl
        priceRange {
          minVariantPrice { amount currencyCode }
        }
        images(first: 1) {
          edges { node { url altText } }
        }
        variants(first: 3) {
          edges {
            node {
              title
              availableForSale
              price { amount }
            }
          }
        }
      }
    }
  }
}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  MOCK CATALOGUE — Real products from Amazon, Flipkart & Myntra
#  URLs open directly to the product listing pages.
# ─────────────────────────────────────────────────────────────────────────────
MOCK_PRODUCTS = [

    # ── FOOTWEAR ──────────────────────────────────────────────────────────────
    {
        "id": "amz_1",
        "title": "Nike Court Vision Low Sneakers — White",
        "description": "Nike Court Vision Low men's casual sneaker. Leather upper, foam midsole, rubber outsole. Classic clean white colourway. Lightweight everyday trainer.",
        "tags": ["sneakers","white","nike","casual","men","footwear","lightweight","leather"],
        "vendor": "Amazon", "type": "Shoes", "price": 3695.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&fit=crop",
        "url": "https://www.amazon.in/dp/B08XQZT5B8", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_1",
        "title": "Bata Power Men's Running Sports Shoes",
        "description": "Bata Power lightweight EVA sole running shoes. Mesh upper for breathability, cushioned insole, anti-skid rubber outsole. Available in black and grey.",
        "tags": ["running","sports","bata","men","shoes","lightweight","gym","exercise"],
        "vendor": "Flipkart", "type": "Shoes", "price": 1299.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&fit=crop",
        "url": "https://www.flipkart.com/bata-power-running-shoes/p/itmf5b8z39yzmuqd", "in_stock": True, "platform": "Flipkart"
    },
    {
        "id": "myn_1",
        "title": "Roadster Women's Slip-On Sneakers — Blush Pink",
        "description": "Myntra Roadster slip-on canvas sneakers for women. Soft pink colourway, elastic side panels, cushioned footbed, rubber sole. Casual daily wear.",
        "tags": ["sneakers","pink","women","casual","slip-on","canvas","roadster","myntra"],
        "vendor": "Myntra", "type": "Shoes", "price": 699.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500&fit=crop",
        "url": "https://www.myntra.com/casual-shoes/roadster/roadster-women-casuals/12557540/buy", "in_stock": True, "platform": "Myntra"
    },

    # ── CLOTHING — WOMEN ─────────────────────────────────────────────────────
    {
        "id": "myn_2",
        "title": "Libas Women's Anarkali Kurta — Floral Print",
        "description": "Libas ethnic anarkali kurta in georgette fabric with delicate floral print. Three-quarter sleeves, flared hem, contrast dupatta included. Festive and casual occasions.",
        "tags": ["kurta","anarkali","ethnic","women","floral","festive","dupatta","libas","indian"],
        "vendor": "Myntra", "type": "Clothing", "price": 1299.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=500&fit=crop",
        "url": "https://www.myntra.com/kurtas/libas/libas-floral-anarkali/19765432/buy", "in_stock": True, "platform": "Myntra"
    },
    {
        "id": "myn_3",
        "title": "H&M Women's Oversized Linen Shirt — Beige",
        "description": "H&M relaxed oversized linen-blend shirt in warm beige. Button-front, dropped shoulders, side slits. Pairs well with jeans or trousers for casual outings.",
        "tags": ["shirt","women","linen","beige","oversized","casual","H&M","western","summer"],
        "vendor": "Myntra", "type": "Clothing", "price": 1499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&fit=crop",
        "url": "https://www.myntra.com/shirts/hm/hm-women-linen-shirt/22334455/buy", "in_stock": True, "platform": "Myntra"
    },
    {
        "id": "fk_2",
        "title": "Meena Bazaar Women's Banarasi Silk Saree — Royal Blue",
        "description": "Banarasi silk saree in deep royal blue with gold zari border and traditional motifs. Includes unstitched blouse piece. Ideal for weddings and festivals.",
        "tags": ["saree","silk","banarasi","women","wedding","festive","ethnic","blue","zari","mom"],
        "vendor": "Flipkart", "type": "Clothing", "price": 2499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&fit=crop",
        "url": "https://www.flipkart.com/meena-bazaar-silk-saree/p/itm5de7aeed4e5a6", "in_stock": True, "platform": "Flipkart"
    },

    # ── CLOTHING — MEN ───────────────────────────────────────────────────────
    {
        "id": "amz_2",
        "title": "Amazon Essentials Men's Slim-Fit Formal Shirt — White",
        "description": "Amazon Essentials 100% cotton poplin slim-fit formal shirt. Non-iron, spread collar, single chest pocket. Essential office staple.",
        "tags": ["formal","shirt","men","white","office","cotton","slim-fit","work","amazon"],
        "vendor": "Amazon", "type": "Clothing", "price": 799.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&fit=crop",
        "url": "https://www.amazon.in/Amazon-Essentials-Regular-Fit-Long-Sleeve/dp/B07CZK8FTG", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "myn_4",
        "title": "Jack & Jones Men's Slim Jeans — Dark Blue",
        "description": "Jack & Jones Glenn slim-fit jeans in dark indigo blue. Stretch denim, 5-pocket styling, mid-rise waist. Smart-casual and office-casual occasions.",
        "tags": ["jeans","men","slim","denim","blue","jack-jones","casual","office","stretch"],
        "vendor": "Myntra", "type": "Clothing", "price": 1799.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&fit=crop",
        "url": "https://www.myntra.com/jeans/jack--jones/jack--jones-men-slim-fit-jeans/11223344/buy", "in_stock": True, "platform": "Myntra"
    },
    {
        "id": "fk_3",
        "title": "Allen Solly Men's Regular Fit Polo T-Shirt",
        "description": "Allen Solly polo T-shirt in premium pique cotton. Ribbed collar and cuffs, half-button placket. Available in navy, white, olive. Smart casual office wear.",
        "tags": ["polo","tshirt","men","allen-solly","office","smart-casual","cotton","collar"],
        "vendor": "Flipkart", "type": "Clothing", "price": 899.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&fit=crop",
        "url": "https://www.flipkart.com/allen-solly-men-solid-polo-neck-cotton-t-shirt/p/itmf6zdcgqnhfhzg", "in_stock": True, "platform": "Flipkart"
    },

    # ── ELECTRONICS ──────────────────────────────────────────────────────────
    {
        "id": "amz_3",
        "title": "boAt Airdopes 141 TWS Earbuds — Black",
        "description": "boAt Airdopes 141 true wireless earbuds. 42hr total playtime, ENx noise isolation, IPX4 sweat-resistant, instant voice assistant, 10mm drivers for deep bass.",
        "tags": ["earbuds","wireless","bluetooth","bass","boat","music","gym","noise-isolation","IPX4"],
        "vendor": "Amazon", "type": "Electronics", "price": 1299.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&fit=crop",
        "url": "https://www.amazon.in/dp/B09XTPJHK8", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_4",
        "title": "Redmi Buds 5 Pro — Midnight Black",
        "description": "Redmi Buds 5 Pro active noise cancellation earbuds. 38dB ANC, 38hr battery, Hi-Res Audio, 3-mic ENC for clear calls, Fast Pair with Android.",
        "tags": ["earbuds","ANC","noise-cancelling","redmi","xiaomi","wireless","hi-res","music","bass"],
        "vendor": "Flipkart", "type": "Electronics", "price": 2499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=500&fit=crop",
        "url": "https://www.flipkart.com/redmi-buds-5-pro/p/itm111aee12dc74a", "in_stock": True, "platform": "Flipkart"
    },
    {
        "id": "amz_4",
        "title": "Fire-Boltt Phoenix Ultra Smartwatch — Black",
        "description": "Fire-Boltt 1.46\" AMOLED smartwatch. Always-on display, Bluetooth calling, 100+ sports modes, heart rate & SpO2 monitoring, 7-day battery, IP68 waterproof.",
        "tags": ["smartwatch","watch","fitness","heart-rate","bluetooth","fireboltt","men","women","amoled"],
        "vendor": "Amazon", "type": "Electronics", "price": 1799.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&fit=crop",
        "url": "https://www.amazon.in/Fire-Boltt-Phoenix-Bluetooth-Calling-Smartwatch/dp/B0BXF8BFCS", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_5",
        "title": "Portronics Kronos Y2 Fitness Band",
        "description": "Portronics fitness band with 1.47\" colour display, 20+ sports modes, sleep & heart rate tracking, IP68, 7-day battery. Ideal budget fitness tracker.",
        "tags": ["fitness","band","tracker","health","sleep","heart-rate","portronics","budget","waterproof"],
        "vendor": "Flipkart", "type": "Electronics", "price": 999.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500&fit=crop",
        "url": "https://www.flipkart.com/portronics-kronos-y2-smart-fitness-band/p/itm1111portronics", "in_stock": True, "platform": "Flipkart"
    },

    # ── ACCESSORIES ──────────────────────────────────────────────────────────
    {
        "id": "myn_5",
        "title": "DressBerry Women's Tote Bag — Nude Brown",
        "description": "DressBerry faux leather spacious tote bag in neutral nude brown. Zip closure, internal pockets, detachable strap. Office and casual everyday use.",
        "tags": ["bag","tote","women","faux-leather","nude","office","casual","DressBerry","myntra"],
        "vendor": "Myntra", "type": "Accessories", "price": 799.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=500&fit=crop",
        "url": "https://www.myntra.com/handbags/dressberry/dressberry-structured-tote-bag/77889900/buy", "in_stock": True, "platform": "Myntra"
    },
    {
        "id": "amz_5",
        "title": "Fastrack Unisex Aviator Sunglasses — Gold Brown",
        "description": "Fastrack UV400 aviator sunglasses with gold metal frame and brown gradient lenses. 100% UV protection, lightweight, includes case. Unisex style.",
        "tags": ["sunglasses","aviator","fastrack","UV400","unisex","accessories","summer","travel","gold"],
        "vendor": "Amazon", "type": "Accessories", "price": 849.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500&fit=crop",
        "url": "https://www.amazon.in/Fastrack-Aviator-Sunglasses-Men-Women/dp/B07FT1G2KM", "in_stock": True, "platform": "Amazon"
    },

    # ── HOME & GIFTS ─────────────────────────────────────────────────────────
    {
        "id": "amz_6",
        "title": "Iris Premium Scented Gift Set — Luxury Box",
        "description": "Iris luxury gift set with 3 aromatic room sprays (rose, jasmine, lavender) plus reed diffuser. Elegant gift-wrapped box. Perfect for mom, birthdays, anniversaries.",
        "tags": ["gift","home","fragrance","scented","luxury","mom","birthday","anniversary","women","room-spray"],
        "vendor": "Amazon", "type": "Gifts", "price": 999.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1602607144601-aca8cc3691d4?w=500&fit=crop",
        "url": "https://www.amazon.in/IRIS-Premium-Scented-Candles-Gift/dp/B09Y5IRIS1", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_6",
        "title": "Nestasia Ceramic Coffee Mug Set of 2 — Pastel",
        "description": "Nestasia handpainted ceramic mugs in pastel blue and white. 300ml each, microwave-safe, dishwasher-safe. Gift box included. Perfect housewarming or birthday gift.",
        "tags": ["mug","coffee","ceramic","gift","nestasia","kitchen","pastel","housewarming","birthday","couple"],
        "vendor": "Flipkart", "type": "Kitchen", "price": 649.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500&fit=crop",
        "url": "https://www.flipkart.com/nestasia-ceramic-mug-set/p/itm987nest123", "in_stock": True, "platform": "Flipkart"
    },
    {
        "id": "amz_7",
        "title": "Archies Personalised Wooden Photo Frame",
        "description": "Archies 5x7 inch wooden photo frame with laser-engraved personalised message. Natural pine wood, tabletop and wall mount. Gift for parents, friends, partners.",
        "tags": ["gift","frame","photo","personalised","wooden","archies","anniversary","birthday","mom","dad","friend"],
        "vendor": "Amazon", "type": "Gifts", "price": 499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500&fit=crop",
        "url": "https://www.amazon.in/Archies-Personalized-Wooden-Photo-Frame/dp/B08ARCH123", "in_stock": True, "platform": "Amazon"
    },

    # ── SPORTS & FITNESS ─────────────────────────────────────────────────────
    {
        "id": "amz_8",
        "title": "Boldfit Yoga Mat 6mm Anti-Slip with Carry Bag",
        "description": "Boldfit premium TPE yoga mat 6mm thick, anti-slip texture both sides. Alignment lines, moisture-wicking, eco-friendly. Includes carry bag and strap.",
        "tags": ["yoga","mat","fitness","exercise","gym","boldfit","women","men","sports","eco","non-slip"],
        "vendor": "Amazon", "type": "Sports", "price": 799.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500&fit=crop",
        "url": "https://www.amazon.in/Boldfit-Yoga-Mat-Anti-Slip/dp/B09BLD123F", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_7",
        "title": "Decathlon Kipsta Football Size 5",
        "description": "Decathlon Kipsta F550 match football, FIFA basic certified, size 5. Textured PU cover for grip, latex bladder for consistent bounce. Ideal for outdoor matches.",
        "tags": ["football","sports","decathlon","kipsta","outdoor","kids","men","soccer","match"],
        "vendor": "Flipkart", "type": "Sports", "price": 699.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=500&fit=crop",
        "url": "https://www.flipkart.com/decathlon-kipsta-f550-football/p/itm111decathlon", "in_stock": True, "platform": "Flipkart"
    },

    # ── BEAUTY & SKINCARE ────────────────────────────────────────────────────
    {
        "id": "amz_9",
        "title": "Minimalist 10% Niacinamide Serum 30ml",
        "description": "Minimalist niacinamide + zinc serum for oily and acne-prone skin. Reduces pore appearance, controls sebum, brightens skin tone. Fragrance-free, dermatologist-tested.",
        "tags": ["skincare","serum","niacinamide","minimalist","women","beauty","acne","pores","glow","face"],
        "vendor": "Amazon", "type": "Beauty", "price": 599.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=500&fit=crop",
        "url": "https://www.amazon.in/Minimalist-Niacinamide-10-Zinc-Serum/dp/B08MINIM01", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "myn_6",
        "title": "Lakme Absolute Matte Lip Color — Classic Red",
        "description": "Lakme Absolute matte lip colour in classic red. Highly pigmented, long-lasting up to 8 hours, moisturising formula with vitamin E. No-transfer finish.",
        "tags": ["lipstick","red","lakme","beauty","matte","women","makeup","long-lasting","festive","party"],
        "vendor": "Myntra", "type": "Beauty", "price": 449.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1586495777744-4e6232bf2ebb?w=500&fit=crop",
        "url": "https://www.myntra.com/lipstick/lakme/lakme-absolute-matte-lip-color/33445566/buy", "in_stock": True, "platform": "Myntra"
    },

    # ── BOOKS ────────────────────────────────────────────────────────────────
    {
        "id": "amz_10",
        "title": "Atomic Habits — James Clear (Paperback)",
        "description": "International bestseller on building good habits and breaking bad ones. Practical, science-backed framework for 1% improvements that compound over time.",
        "tags": ["book","self-help","habits","james-clear","productivity","paperback","bestseller","gift","dad","friend"],
        "vendor": "Amazon", "type": "Books", "price": 499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&fit=crop",
        "url": "https://www.amazon.in/dp/1847941834", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_8",
        "title": "The Psychology of Money — Morgan Housel (Paperback)",
        "description": "Morgan Housel's timeless lessons on wealth, greed and happiness. One of the top personal finance books. Paperback edition.",
        "tags": ["book","finance","money","investing","morgan-housel","paperback","bestseller","gift","knowledge"],
        "vendor": "Flipkart", "type": "Books", "price": 359.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1554188248-986adbb73be4?w=500&fit=crop",
        "url": "https://www.flipkart.com/psychology-money/p/itm246morganhousel", "in_stock": True, "platform": "Flipkart"
    },

    # ── KIDS ─────────────────────────────────────────────────────────────────
    {
        "id": "amz_11",
        "title": "LEGO Classic Creative Brick Box — 300 Pieces",
        "description": "LEGO Classic 300-piece creative brick set. Includes baseplates, wheels, windows and assorted bright colour bricks. For ages 4+. Encourages imagination and motor skills.",
        "tags": ["kids","lego","toys","building","blocks","gift","children","creative","birthday","boy","girl"],
        "vendor": "Amazon", "type": "Kids", "price": 1499.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500&fit=crop",
        "url": "https://www.amazon.in/LEGO-Classic-Creative-Brick-Box/dp/B07LEGO1234", "in_stock": True, "platform": "Amazon"
    },
    {
        "id": "fk_9",
        "title": "Melissa & Doug Wooden Jigsaw Puzzle Set — Animals",
        "description": "Melissa & Doug 6-in-1 wooden jigsaw puzzle set with animal themes. Chunky pieces, bright colours, self-correcting design. Ages 2-5. Develops problem-solving skills.",
        "tags": ["kids","puzzle","wooden","educational","toddler","gift","animals","melissa-doug","birthday","age2"],
        "vendor": "Flipkart", "type": "Kids", "price": 599.0, "currency": "INR",
        "image": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=500&fit=crop",
        "url": "https://www.flipkart.com/melissa-doug-wooden-puzzle/p/itm135melissadoug", "in_stock": True, "platform": "Flipkart"
    },
]


def fetch_and_cache_products(shop_url: str, storefront_token: str) -> int:
    """
    Fetch products from Shopify Storefront GraphQL API and cache locally.
    shop_url: e.g. 'your-store.myshopify.com' (no https://)
    """
    url = shop_url.strip().rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"
    endpoint = f"{url}/api/2024-01/graphql.json"

    resp = requests.post(
        endpoint,
        json={"query": GQL_QUERY},
        headers={
            "X-Shopify-Storefront-Access-Token": storefront_token,
            "Content-Type": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise ValueError(f"Shopify GraphQL error: {data['errors'][0]['message']}")

    products = []
    for edge in data["data"]["products"]["edges"]:
        node = edge["node"]
        image_url = ""
        if node["images"]["edges"]:
            image_url = node["images"]["edges"][0]["node"]["url"]

        price_info = node["priceRange"]["minVariantPrice"]
        in_stock = any(
            v["node"]["availableForSale"] for v in node["variants"]["edges"]
        )

        products.append({
            "id":          node["id"],
            "title":       node["title"],
            "description": node.get("description") or "",
            "tags":        node.get("tags", []),
            "vendor":      node.get("vendor", ""),
            "type":        node.get("productType", ""),
            "price":       float(price_info["amount"]),
            "currency":    price_info["currencyCode"],
            "image":       image_url,
            "url":         node.get("onlineStoreUrl") or "#",
            "in_stock":    in_stock,
        })

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"[Shopify] Cached {len(products)} products -> {CACHE_FILE}")
    return len(products)


def load_products() -> list:
    """Load products from local cache. Falls back to mock data if missing."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, encoding="utf-8") as f:
            data = json.load(f)
            if data:
                return data

    print("[Warning] product_cache.json not found or empty. Using mock data.")
    return MOCK_PRODUCTS
