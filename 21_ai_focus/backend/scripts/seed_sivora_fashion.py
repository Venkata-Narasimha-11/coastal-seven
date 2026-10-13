import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.database import Base, SessionLocal, engine
from app.models import Category, Product, User, UserRole, Order, OrderItem, ChatMessage
from app.utils.auth import get_password_hash
from app.services.rag_service import RAGService
from app.services.ai_cache_service import AICacheService


SIVORA_CATEGORIES = [
    {
        "name": "Ethnic & Couture",
        "slug": "ethnic-couture",
        "description": "Handcrafted bridal lehengas, banarasi silk sarees, regal anarkalis, and festive couture."
    },
    {
        "name": "Western Luxe",
        "slug": "western-luxe",
        "description": "Editorial evening gowns, cocktail dresses, power blazers, and luxury silk ensembles."
    },
    {
        "name": "Luxury Handbags",
        "slug": "luxury-handbags",
        "description": "Italian leather totes, quilted crossbody bags, evening minaudières, and clutches."
    },
    {
        "name": "Fine Jewellery",
        "slug": "fine-jewellery",
        "description": "Handcrafted polki kundan chokers, rose gold diamond bracelets, and heritage jhumkas."
    },
    {
        "name": "Footwear",
        "slug": "footwear",
        "description": "Crystal stiletto pumps, embroidered zardozi juttis, metallic block heels, and mules."
    },
    {
        "name": "Beauty & Fragrances",
        "slug": "beauty-fragrances",
        "description": "SIVORA signature luxury perfumes, velvet matte lip pigments, and royal glow elixirs."
    },
    {
        "name": "Boys Kids Wear",
        "slug": "boys-kids-wear",
        "description": "Royal prince sherwanis, bandhgala suits, tuxedos, and festive kurta sets for boys."
    },
    {
        "name": "Girls Kids Wear",
        "slug": "girls-kids-wear",
        "description": "Fairytale tulle gowns, festive mini lehengas, anarkalis, and birthday party dresses for girls."
    },
]

SIVORA_PRODUCTS = [
    # =========================================================================
    # 1. ETHNIC & COUTURE (15 Products)
    # =========================================================================
    {
        "category_slug": "ethnic-couture",
        "name": "SIVORA Crimson Velvet Bridal Lehenga",
        "slug": "sivora-crimson-velvet-bridal-lehenga",
        "price": Decimal("34999.00"),
        "stock": 8,
        "description": "Exquisite deep crimson micro-velvet lehenga set intricately hand-embroidered with antique zardozi, dabka, and Swarovski crystals. Paired with a sweetheart neckline blouse and dual organza dupattas.",
        "image_url": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Royal Banarasi Kanjeevaram Silk Saree",
        "slug": "royal-banarasi-kanjeevaram-silk-saree",
        "price": Decimal("18499.00"),
        "stock": 14,
        "description": "Handwoven pure mulberry silk saree featuring opulent gold and silver zari brocade motifs with a heavy royal temple border and grand pallu.",
        "image_url": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Ivory & Rose Gold Organza Anarkali Set",
        "slug": "ivory-rose-gold-organza-anarkali-set",
        "price": Decimal("12999.00"),
        "stock": 10,
        "description": "Ethereal floor-length flared anarkali suit crafted from pure organza silk with mukaish work and delicate scalloped borders. Includes matching churidar and scalloped dupatta.",
        "image_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Emerald Raw Silk Peplum Sharara Suite",
        "slug": "emerald-raw-silk-peplum-sharara-suite",
        "price": Decimal("15999.00"),
        "stock": 6,
        "description": "Rich emerald green raw silk peplum tunic embellished with gota patti and mirror work, paired with a tiered flared sharara and chiffon dupatta.",
        "image_url": "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Midnight Navy Embroidered Kurta Set",
        "slug": "midnight-navy-embroidered-kurta-set",
        "price": Decimal("9499.00"),
        "stock": 12,
        "description": "Classic royal silk blend bandhgala kurta adorned with subtle tonal resham thread work, paired with tapered churidar pants and pocket square.",
        "image_url": "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Pastel Peach Chikankari Georgette Lehenga",
        "slug": "pastel-peach-chikankari-georgette-lehenga",
        "price": Decimal("24999.00"),
        "stock": 9,
        "description": "Delicate Lucknowi Chikankari hand embroidery on pure georgette adorned with pearl beads and baby sequins, paired with a sheer back blouse.",
        "image_url": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Royal Blue Paithani Silk Heritage Saree",
        "slug": "royal-blue-paithani-silk-heritage-saree",
        "price": Decimal("16899.00"),
        "stock": 11,
        "description": "Traditional Maharashtrian Paithani silk saree woven with real gold zari peacocks and kaleidoscope floral pallu.",
        "image_url": "https://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Marigold Yellow Haldi Mirror Work Anarkali",
        "slug": "marigold-yellow-haldi-mirror-work-anarkali",
        "price": Decimal("11499.00"),
        "stock": 15,
        "description": "Vibrant festive sunflower yellow tiered anarkali dress accented with real mirror embroidery along the neckline and cuffs.",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Ruby Red Zari Embroidered Velvet Shawl",
        "slug": "ruby-red-zari-embroidered-velvet-shawl",
        "price": Decimal("7999.00"),
        "stock": 20,
        "description": "Heavy royal micro-velvet bridal wrap shawl bordered with intricate tilla Kashmiri embroidery and fringed tassels.",
        "image_url": "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Lavender Foil Print Georgette Sharara Set",
        "slug": "lavender-foil-print-georgette-sharara-set",
        "price": Decimal("13500.00"),
        "stock": 8,
        "description": "Contemporary lilac georgette short peplum top with silver foil accents, paired with voluminous pleated sharara pants.",
        "image_url": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Turquoise Chanderi Silk Angrakha Kurta",
        "slug": "turquoise-chanderi-silk-angrakha-kurta",
        "price": Decimal("8299.00"),
        "stock": 14,
        "description": "Mughal-style wrap angrakha tunic in lightweight Chanderi silk with side fabric dori ties and handcrafted latkans.",
        "image_url": "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Golden Tissue Silk Designer Drape Saree",
        "slug": "golden-tissue-silk-designer-drape-saree",
        "price": Decimal("21999.00"),
        "stock": 7,
        "description": "Modern pre-draped champagne gold metallic tissue saree with sculpted pleats and an embellished crystal bustier blouse.",
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Plum Purple Silk Brocade Sherwani Set",
        "slug": "plum-purple-silk-brocade-sherwani-set",
        "price": Decimal("28500.00"),
        "stock": 6,
        "description": "Groom's luxury raw silk sherwani featuring heritage Banarasi brocade weave, jeweled button closures, and matching stole.",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Mint Green Lucknowi Sequin Lehenga",
        "slug": "mint-green-lucknowi-sequin-lehenga",
        "price": Decimal("26999.00"),
        "stock": 8,
        "description": "Refreshing pastel mint green ceremonial lehenga with tonal resham floral vines and translucent twinkling sequins.",
        "image_url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "ethnic-couture",
        "name": "Mustard Yellow Bandhani Silk Festive Saree",
        "slug": "mustard-yellow-bandhani-silk-festive-saree",
        "price": Decimal("14299.00"),
        "stock": 13,
        "description": "Authentic Gujarati tie-and-dye bandhani saree on pure gajji silk with hand-woven zari borders and heavy pallu.",
        "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 2. WESTERN LUXE (15 Products)
    # =========================================================================
    {
        "category_slug": "western-luxe",
        "name": "SIVORA Noir Satin Slip Evening Gown",
        "slug": "sivora-noir-satin-slip-evening-gown",
        "price": Decimal("11499.00"),
        "stock": 9,
        "description": "Sensual bias-cut heavy silk satin maxi gown featuring a draped cowl neckline, delicate criss-cross back straps, and an elegant side thigh slit.",
        "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Champagne Sequin Cocktail Midi Dress",
        "slug": "champagne-sequin-cocktail-midi-dress",
        "price": Decimal("8999.00"),
        "stock": 15,
        "description": "Shimmering all-over micro-sequin bodycon dress designed for gala evenings and red carpet events with structural padded shoulders and sweetheart contouring.",
        "image_url": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Milano Tailored Double-Breasted Wool Blazer",
        "slug": "milano-tailored-double-breasted-wool-blazer",
        "price": Decimal("14299.00"),
        "stock": 7,
        "description": "Sharp Italian tailored oversized blazer with gold-crested buttons, peaked lapels, and premium cupro interior lining.",
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Burgundy Velvet Corset Top",
        "slug": "burgundy-velvet-corset-top",
        "price": Decimal("4999.00"),
        "stock": 20,
        "description": "Structured boned corset top made with plush Italian cotton velvet, sweetheart bustline, and back lace-up cinch detailing.",
        "image_url": "https://images.unsplash.com/photo-1508427953056-b00b8d78ebf5?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Emerald Draped One-Shoulder Maxi Dress",
        "slug": "emerald-draped-one-shoulder-maxi-dress",
        "price": Decimal("12500.00"),
        "stock": 11,
        "description": "Dramatic Grecian-inspired asymmetric draped gown crafted from fluid emerald jersey fabric with a gathered waist and sweep train.",
        "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Parisian Plissé Metallic Trench Coat",
        "slug": "parisian-plisse-metallic-trench-coat",
        "price": Decimal("16999.00"),
        "stock": 6,
        "description": "Statement weather-resistant micro-pleated metallic trench coat featuring a double storm flap, self-tie belt, and horn buttons.",
        "image_url": "https://images.unsplash.com/photo-1550614000-4895a10e1bfd?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Ivory Silk Charmeuse Cowl Neck Camisole",
        "slug": "ivory-silk-charmeuse-cowl-neck-camisole",
        "price": Decimal("3899.00"),
        "stock": 25,
        "description": "Versatile layering staple made from 100% 22-momme pure mulberry silk with adjustable spaghetti straps.",
        "image_url": "https://images.unsplash.com/photo-1492707892479-7bc8d5a4ee93?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "High-Waisted Wide Leg Tailored Trousers",
        "slug": "high-waisted-wide-leg-tailored-trousers",
        "price": Decimal("6499.00"),
        "stock": 18,
        "description": "Floor-skimming pleated wool crepe trousers with clean pressed creases, deep slant pockets, and a clean hook-bar waistband.",
        "image_url": "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Midnight Starburst Velvet Wrap Mini Dress",
        "slug": "midnight-starburst-velvet-wrap-mini-dress",
        "price": Decimal("7899.00"),
        "stock": 16,
        "description": "Deep midnight blue stretch velvet mini dress sprinkled with iridescent crystal constellations and a flattering tulip hem.",
        "image_url": "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Rose Gold Metallic Short Suit Set",
        "slug": "rose-gold-metallic-short-suit-set",
        "price": Decimal("15500.00"),
        "stock": 8,
        "description": "Two-piece modern party power suit featuring an unlined tailored boyfriend jacket and matching pleated high-rise shorts in metallic brocade.",
        "image_url": "https://images.unsplash.com/photo-1485230895905-ec40ba36b9bc?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Sculpted Off-Shoulder Mermaid Gown",
        "slug": "sculpted-off-shoulder-mermaid-gown",
        "price": Decimal("19999.00"),
        "stock": 5,
        "description": "Body-contouring scuba crepe black tie gown with structured fold-over off-shoulder cuffs and a fishtail hemline.",
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Sapphire Blue Satin Asymmetrical Midi Skirt",
        "slug": "sapphire-blue-satin-asymmetrical-midi-skirt",
        "price": Decimal("5499.00"),
        "stock": 17,
        "description": "Fluid satin midi skirt featuring an asymmetrical handkerchief hemline and hidden elastic comfort waistband.",
        "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Cashmere Blend Turtleneck Luxury Sweater",
        "slug": "cashmere-blend-turtleneck-luxury-sweater",
        "price": Decimal("8999.00"),
        "stock": 14,
        "description": "Ultra-soft Mongolian 70% wool and 30% cashmere fine-knit turtleneck sweater with ribbed cuffs and drop shoulders.",
        "image_url": "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Tuscan Tan Genuine Suede Moto Jacket",
        "slug": "tuscan-tan-genuine-suede-moto-jacket",
        "price": Decimal("18999.00"),
        "stock": 7,
        "description": "Buttery soft goat suede biker jacket detailed with asymmetrical gunmetal hardware, epaulettes, and buckled waist tabs.",
        "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "western-luxe",
        "name": "Crystal Trimmed Tuxedo Dinner Jacket",
        "slug": "crystal-trimmed-tuxedo-dinner-jacket",
        "price": Decimal("17499.00"),
        "stock": 6,
        "description": "Single-breasted smoking jacket with black satin peak lapels outlined in hand-set baguette crystal trim.",
        "image_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 3. LUXURY HANDBAGS (15 Products)
    # =========================================================================
    {
        "category_slug": "luxury-handbags",
        "name": "SIVORA Royale Quilted Leather Crossbody",
        "slug": "sivora-royale-quilted-leather-crossbody",
        "price": Decimal("18999.00"),
        "stock": 11,
        "description": "Handcrafted full-grain nappa leather bag with chevron quilting, 24K gold-plated SIVORA monogram lock, and convertible chain shoulder strap.",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Florentine Structured Leather Tote",
        "slug": "florentine-structured-leather-tote",
        "price": Decimal("21499.00"),
        "stock": 8,
        "description": "Spacious everyday luxury work tote crafted from pebbled calfskin with dual rolled top handles, laptop compartment, and gold padlock charm.",
        "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Crystal Embellished Evening Minaudière",
        "slug": "crystal-embellished-evening-minaudiere",
        "price": Decimal("8499.00"),
        "stock": 14,
        "description": "Hard-shell evening clutch drenched in pave crystals with a cabochon stone clasp and detachable snake chain.",
        "image_url": "https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Croco-Embossed Baguette Shoulder Bag",
        "slug": "croco-embossed-baguette-shoulder-bag",
        "price": Decimal("6999.00"),
        "stock": 18,
        "description": "90s archival silhouette in glossy crocodile embossed vegan leather with sleek minimalist hardware.",
        "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Monaco Micro Leather Top-Handle Bag",
        "slug": "monaco-micro-leather-top-handle-bag",
        "price": Decimal("12999.00"),
        "stock": 10,
        "description": "Cute architectural micro bag crafted from structured box calf leather with a magnetic flap and crossbody strap.",
        "image_url": "https://images.unsplash.com/photo-1591561954557-26941169b49e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Verona Slouchy Woven Leather Hobo",
        "slug": "verona-slouchy-woven-leather-hobo",
        "price": Decimal("17500.00"),
        "stock": 9,
        "description": "Intricate hand-woven lambskin leather shoulder hobo featuring buttery soft slouch and spacious suede-lined interior.",
        "image_url": "https://images.unsplash.com/photo-1575032617751-6ddec2089882?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Parisian Pearl-Encrusted Box Clutch",
        "slug": "parisian-pearl-encrusted-box-clutch",
        "price": Decimal("9999.00"),
        "stock": 12,
        "description": "Opulent hardcase bridal clutch decorated with graduated faux pearls and faceted crystal clasp.",
        "image_url": "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Roma Pebble Leather Laptop Work Satchel",
        "slug": "roma-pebble-leather-laptop-work-satchel",
        "price": Decimal("19899.00"),
        "stock": 7,
        "description": "Executive structured business bag equipped with 15-inch padded laptop sleeve, key leash, and luggage trolley strap.",
        "image_url": "https://images.unsplash.com/photo-1527385352018-3c26dd6c3916?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Gold Chain Quilted Nappa Flap Bag",
        "slug": "gold-chain-quilted-nappa-flap-bag",
        "price": Decimal("16499.00"),
        "stock": 13,
        "description": "Timeless diamond-quilted shoulder purse with chunky gourmette gold chain and turn-lock medallion.",
        "image_url": "https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Emerald Green Exotic Croc Clutch",
        "slug": "emerald-green-exotic-croc-clutch",
        "price": Decimal("7299.00"),
        "stock": 16,
        "description": "High-shine embossed envelope clutch in deep forest green with magnetic snap closure and interior zip compartment.",
        "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Vintage Metallic Envelope Evening Clutch",
        "slug": "vintage-metallic-envelope-evening-clutch",
        "price": Decimal("6499.00"),
        "stock": 20,
        "description": "Sleek champagne gold mirror finish metallic clutch with clean geometric flap and drop-in chain.",
        "image_url": "https://images.unsplash.com/photo-1574634534894-89d7576c8259?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "SIVORA Monogram Jacquard Travel Duffle",
        "slug": "sivora-monogram-jacquard-travel-duffle",
        "price": Decimal("22999.00"),
        "stock": 6,
        "description": "Luxury weekend travel holdall in water-resistant monogram canvas with natural vachetta leather trim and brass padlock.",
        "image_url": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Minimalist Butter Leather Crescent Bag",
        "slug": "minimalist-butter-leather-crescent-bag",
        "price": Decimal("11899.00"),
        "stock": 15,
        "description": "Understated ergonomic half-moon shoulder bag in supple glove-tanned leather with hidden zip closure.",
        "image_url": "https://images.unsplash.com/photo-1605733513597-a8f8341084e6?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Artisanal Brass Metal Potli Bag",
        "slug": "artisanal-brass-metal-potli-bag",
        "price": Decimal("5999.00"),
        "stock": 19,
        "description": "Festive heirloom potli pouch crafted with antique gold filigree wirework, silk drawstring, and pearl pom-poms.",
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "luxury-handbags",
        "name": "Diamond Quilted Camera Crossbody",
        "slug": "diamond-quilted-camera-crossbody",
        "price": Decimal("8999.00"),
        "stock": 17,
        "description": "Compact everyday camera bag with twin zipper compartments, leather tassel pull, and adjustable webbed strap.",
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 4. FINE JEWELLERY (15 Products)
    # =========================================================================
    {
        "category_slug": "fine-jewellery",
        "name": "SIVORA Maharani Polki Kundan Choker",
        "slug": "sivora-maharani-polki-kundan-choker",
        "price": Decimal("22999.00"),
        "stock": 5,
        "description": "Heritage royal necklace handcrafted with uncut polki kundan stones, green emerald drops, and freshwater basra pearls on 22K gold-foiled brass.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "18K Rose Gold Diamond Tennis Bracelet",
        "slug": "18k-rose-gold-diamond-tennis-bracelet",
        "price": Decimal("29999.00"),
        "stock": 6,
        "description": "Dazzling continuous line of precision-cut lab diamonds set in high-polish 18K rose gold with double safety clasp.",
        "image_url": "https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Temple Gold Chandbali Jhumkas",
        "slug": "temple-gold-chandbali-jhumkas",
        "price": Decimal("7499.00"),
        "stock": 15,
        "description": "Traditional south Indian temple architecture inspired crescent chandbali earrings with delicate ruby accents and hanging pearl clusters.",
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Celestial Emerald Cut Cocktail Ring",
        "slug": "celestial-emerald-cut-cocktail-ring",
        "price": Decimal("5999.00"),
        "stock": 22,
        "description": "Statement cocktail ring featuring an 8-carat emerald-cut Zambian simulated emerald hugged by trillion-cut accent stones in sterling silver.",
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "South Sea Pearl Multi-Strand Necklace",
        "slug": "south-sea-pearl-multi-strand-necklace",
        "price": Decimal("18500.00"),
        "stock": 8,
        "description": "Five graduated strands of luminous white cultured South Sea pearls finished with an ornate diamond-set filigree clasp.",
        "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Uncut Diamond & Ruby Floral Maang Tikka",
        "slug": "uncut-diamond-ruby-floral-maang-tikka",
        "price": Decimal("8999.00"),
        "stock": 14,
        "description": "Bridal forehead jewel featuring floral motifs set with uncut polki diamonds and a pear-shaped Burmese ruby drop.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Antique 22K Peacock Kada Bangles (Pair)",
        "slug": "antique-22k-peacock-kada-bangles-pair",
        "price": Decimal("24999.00"),
        "stock": 7,
        "description": "Pair of handcrafted screw-clasp kada bangles with hand-carved royal peacock finials and matte antique polish.",
        "image_url": "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Solitaire Moissanite Drop Pendant with Chain",
        "slug": "solitaire-moissanite-drop-pendant-with-chain",
        "price": Decimal("11499.00"),
        "stock": 16,
        "description": "Classic 2-carat round brilliant cut VVS1 moissanite pendant suspended from a 14K white gold box chain.",
        "image_url": "https://images.unsplash.com/photo-1598560917505-59a3ad559071?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Sapphire & Diamond Art Deco Drop Earrings",
        "slug": "sapphire-diamond-art-deco-drop-earrings",
        "price": Decimal("14999.00"),
        "stock": 9,
        "description": "Geometric 1920s vintage-inspired chandelier drops with calibre-cut blue sapphires and micro pave diamond halos.",
        "image_url": "https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Royal Meenakari Enamelled Choker Necklace",
        "slug": "royal-meenakari-enamelled-choker-necklace",
        "price": Decimal("16800.00"),
        "stock": 10,
        "description": "Reversible bridal choker with vibrant pink-and-green Jaipur Meenakari enamel art on reverse and kundan on front.",
        "image_url": "https://images.unsplash.com/photo-1600003014755-ba31aa59c4b6?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Contemporary Rose Gold Geometric Cuff",
        "slug": "contemporary-rose-gold-geometric-cuff",
        "price": Decimal("9299.00"),
        "stock": 18,
        "description": "Modern minimalist open-ended wrist cuff with brushed rose gold finish and bezel-set baguette cubic zirconia ends.",
        "image_url": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Nizam Pearl Haar with Emerald Pendant",
        "slug": "nizam-pearl-haar-with-emerald-pendant",
        "price": Decimal("21500.00"),
        "stock": 6,
        "description": "Hyderabadi regal layered mala consisting of seven strings of seed pearls centering an engraved Columbian emerald pendant.",
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Dainty Baguette Diamond Eternity Band",
        "slug": "dainty-baguette-diamond-eternity-band",
        "price": Decimal("8499.00"),
        "stock": 20,
        "description": "Stackable full eternity ring featuring channel-set step-cut baguette diamonds in solid 925 sterling silver.",
        "image_url": "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Jadau Kundan Passa Hair Accessory",
        "slug": "jadau-kundan-passa-hair-accessory",
        "price": Decimal("6999.00"),
        "stock": 13,
        "description": "Mughal side jhoomar / passa crafted with crescent motifs, tiny seed pearl cascades, and green stone drop beads.",
        "image_url": "https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "fine-jewellery",
        "name": "Gold Filigree Chandelier Party Earrings",
        "slug": "gold-filigree-chandelier-party-earrings",
        "price": Decimal("5499.00"),
        "stock": 25,
        "description": "Ultra-lightweight laser-cut gold lace danglers with movement and shine for festive evenings.",
        "image_url": "https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 5. FOOTWEAR (15 Products)
    # =========================================================================
    {
        "category_slug": "footwear",
        "name": "SIVORA Starlight Crystal Pointed Stiletto Pumps",
        "slug": "sivora-starlight-crystal-pointed-stiletto-pumps",
        "price": Decimal("11999.00"),
        "stock": 10,
        "description": "Cinderella-inspired 100mm Italian satin pumps with a sculpted pointed toe and glittering crystal starburst buckle.",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Royal Zardozi Handcrafted Bridal Juttis",
        "slug": "royal-zardozi-handcrafted-bridal-juttis",
        "price": Decimal("4499.00"),
        "stock": 25,
        "description": "Pure leather jutti cushioned with double memory foam, hand-embroidered with gold dabka, sequins, and pearl beads.",
        "image_url": "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Metallic Rose Gold Strappy Block Heel Sandals",
        "slug": "metallic-rose-gold-strappy-block-heel-sandals",
        "price": Decimal("6499.00"),
        "stock": 16,
        "description": "Modern 75mm block heel sandals with delicate cross straps and ankle buckle in mirror-finish metallic rose gold vegan leather.",
        "image_url": "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Champagne Silk Bow D'Orsay Bridal Heels",
        "slug": "champagne-silk-bow-dorsay-bridal-heels",
        "price": Decimal("9999.00"),
        "stock": 12,
        "description": "Romantic cutout D'Orsay silhouette adorned with a dramatic pleated silk dupioni bow on the heel counter.",
        "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Milanese Leather Penny Loafers",
        "slug": "milanese-leather-penny-loafers",
        "price": Decimal("8499.00"),
        "stock": 15,
        "description": "Supple black burnished calfskin loafers with traditional apron stitching, leather lining, and stacked wooden heel.",
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Golden Mirror Work Mojari Slip-ons",
        "slug": "golden-mirror-work-mojari-slip-ons",
        "price": Decimal("3999.00"),
        "stock": 22,
        "description": "Hand-stitched Punjabi mojari with genuine camel leather sole and shimmering reflective mirror cutwork.",
        "image_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Glass Slipper Lucite Sculptural Mules",
        "slug": "glass-slipper-lucite-sculptural-mules",
        "price": Decimal("7899.00"),
        "stock": 14,
        "description": "Clear transparent vinyl upper with a flared clear perspex kitten heel and cushioned nude leather insole.",
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Velvet Embroidered Khussa Shoes",
        "slug": "velvet-embroidered-khussa-shoes",
        "price": Decimal("4299.00"),
        "stock": 20,
        "description": "Burgundy velvet festive slip-on shoes with turned-up toe and intricate gold thread embroidery.",
        "image_url": "https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Ankle Strap Platform High Heels",
        "slug": "ankle-strap-platform-high-heels",
        "price": Decimal("8999.00"),
        "stock": 13,
        "description": "70s revival 120mm block heel platform pumps with adjustable slim ankle strap in glossy jet black patent.",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Nude Patent Leather Pointed Office Pumps",
        "slug": "nude-patent-leather-pointed-office-pumps",
        "price": Decimal("6999.00"),
        "stock": 18,
        "description": "Ergonomic 65mm mid-heel pointed toe pumps with arch support cushion for all-day boardroom comfort.",
        "image_url": "https://images.unsplash.com/photo-1560343090-f0409e92791a?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Crystal Fringe Metallic Heeled Sandals",
        "slug": "crystal-fringe-metallic-heeled-sandals",
        "price": Decimal("10500.00"),
        "stock": 9,
        "description": "Showstopping silver metallic stiletto sandals with swaying rhinestone fringe along the ankle strap.",
        "image_url": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Cognac Brown Italian Brogues for Men",
        "slug": "cognac-brown-italian-brogues-for-men",
        "price": Decimal("12499.00"),
        "stock": 11,
        "description": "Full brogue wingtip dress shoes Goodyear-welted in Italy with burnished cognac calf leather and waxed laces.",
        "image_url": "https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Satin Kitten Heel Pointed Mules",
        "slug": "satin-kitten-heel-pointed-mules",
        "price": Decimal("5999.00"),
        "stock": 17,
        "description": "Emerald green jewel-toned satin backless slip-on mules with a 45mm comfortable kitten heel.",
        "image_url": "https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Silver Shimmer Strappy Wedge Sandals",
        "slug": "silver-shimmer-strappy-wedge-sandals",
        "price": Decimal("4999.00"),
        "stock": 21,
        "description": "Glittering silver metallic criss-cross straps on a lightweight cork-lined espadrille wedge heel.",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "footwear",
        "name": "Bohemian Kolhapuri Leather Wedges",
        "slug": "bohemian-kolhapuri-leather-wedges",
        "price": Decimal("3799.00"),
        "stock": 24,
        "description": "Hand-braided vegetable-tanned tan leather Kolhapuri toe-ring strap mounted on a modern comfort wedge.",
        "image_url": "https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 6. BEAUTY & FRAGRANCES (15 Products)
    # =========================================================================
    {
        "category_slug": "beauty-fragrances",
        "name": "SIVORA Sultan Royal Oud Eau De Parfum (100ml)",
        "slug": "sivora-sultan-royal-oud-eau-de-parfum",
        "price": Decimal("8999.00"),
        "stock": 30,
        "description": "Hypnotic oriental fragrance opening with saffron and Bulgarian rose, deepening into smoky Cambodian oud and amber woods. 24-hour long-lasting sillage.",
        "image_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "24K Golden Radiance Youth Elixir Serum",
        "slug": "24k-golden-radiance-youth-elixir-serum",
        "price": Decimal("4299.00"),
        "stock": 35,
        "description": "Infused with genuine 24K colloidal gold flakes, rosehip seed oil, and botanical peptides for an instant glass-skin dewy luminescence.",
        "image_url": "https://images.unsplash.com/photo-1526947425960-945c6e72858f?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "SIVORA Velvet Matte Luxe Lip Vault (Set of 4)",
        "slug": "sivora-velvet-matte-luxe-lip-vault",
        "price": Decimal("3799.00"),
        "stock": 40,
        "description": "Weightless hydrating matte lipsticks in four iconic couture shades: Royal Ruby, Bombay Nude, Berry Sangria, and Terracotta Rose.",
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Rose & Jasmine Botanical Bath & Body Oil",
        "slug": "rose-jasmine-botanical-bath-body-oil",
        "price": Decimal("2999.00"),
        "stock": 28,
        "description": "Silky fast-absorbing body oil infused with cold-pressed sweet almond oil, steam-distilled Kannauj roses, and wild Indian jasmine.",
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Kashmir Saffron Illuminating Night Cream",
        "slug": "kashmir-saffron-illuminating-night-cream",
        "price": Decimal("3499.00"),
        "stock": 32,
        "description": "Rich Ayurvedic restorative cream blended with pure Grade-A Kashmiri saffron threads, sandalwood, and hyaluronic acid.",
        "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "French Vanilla & Amber Cashmere EDP (50ml)",
        "slug": "french-vanilla-amber-cashmere-edp",
        "price": Decimal("6499.00"),
        "stock": 25,
        "description": "Warm and sensual gourmand perfume with Madagascar vanilla bean, golden amber, roasted tonka bean, and spun sugar.",
        "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Rose Quartz Sculpting Face Roller & Gua Sha",
        "slug": "rose-quartz-sculpting-face-roller-gua-sha",
        "price": Decimal("2199.00"),
        "stock": 45,
        "description": "Natural Brazilian rose quartz dual-ended facial massager and heart-shaped gua sha tool to boost lymphatic drainage.",
        "image_url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Royal Silk Finish Translucent Setting Powder",
        "slug": "royal-silk-finish-translucent-setting-powder",
        "price": Decimal("2799.00"),
        "stock": 38,
        "description": "Micro-milled oil-control blurring powder that locks makeup for 16 hours with zero flashback.",
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Midnight Jasmine Hair & Scalp Treatment Elixir",
        "slug": "midnight-jasmine-hair-scalp-treatment-elixir",
        "price": Decimal("2499.00"),
        "stock": 30,
        "description": "Nourishing overnight hair potion containing bhringraj, amla, cold-pressed moringa oil, and intoxicating Mogra jasmine aroma.",
        "image_url": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "18K Gold Infused Glow Hydrating Mist",
        "slug": "18k-gold-infused-glow-hydrating-mist",
        "price": Decimal("1999.00"),
        "stock": 50,
        "description": "Refreshing botanical face spritz infused with damask rosewater, aloe vera, niacinamide, and micro-fine gold pearls.",
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Sandalwood & Bergamot Artisanal Cologne",
        "slug": "sandalwood-bergamot-artisanal-cologne",
        "price": Decimal("5499.00"),
        "stock": 26,
        "description": "Crisp woody citrus fragrance blending Calabrian bergamot, green cardamom, and creamy Mysore sandalwood.",
        "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Couture Eyeshadow Palette (16 Jewel Shades)",
        "slug": "couture-eyeshadow-palette-16-jewel-shades",
        "price": Decimal("4599.00"),
        "stock": 34,
        "description": "High-pigment luxury eyeshadow palette featuring velvety mattes, metallic duo-chromes, and wet-look glitter foils.",
        "image_url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Camellia Berry Plumping Lip Sleep Mask",
        "slug": "camellia-berry-plumping-lip-sleep-mask",
        "price": Decimal("1899.00"),
        "stock": 48,
        "description": "Ultra-cushiony leave-on lip treatment with shea butter, peptides, and antioxidant berry complex for pillowy soft lips.",
        "image_url": "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Neroli Blossom Luxury Hand & Nail Cream",
        "slug": "neroli-blossom-luxury-hand-nail-cream",
        "price": Decimal("1699.00"),
        "stock": 55,
        "description": "Non-greasy velvet hand moisturizer with orange blossom essence, sweet almond oil, and keratin to strengthen nails.",
        "image_url": "https://images.unsplash.com/photo-1515688594390-b649af70d282?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "beauty-fragrances",
        "name": "Ayurvedic Kumkumadi Miraculous Beauty Fluid",
        "slug": "ayurvedic-kumkumadi-miraculous-beauty-fluid",
        "price": Decimal("3899.00"),
        "stock": 30,
        "description": "Time-honored saffron and 26 precious Himalayan herbs facial oil formula that reduces hyperpigmentation and restores royal radiance.",
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 7. BOYS KIDS WEAR (15 Products)
    # =========================================================================
    {
        "category_slug": "boys-kids-wear",
        "name": "Prince Royal Silk Embroidered Sherwani Set",
        "slug": "prince-royal-silk-embroidered-sherwani-set",
        "price": Decimal("5999.00"),
        "stock": 16,
        "description": "Majestic raw silk kids sherwani adorned with handcrafted zardozi motifs on collar and cuffs, paired with silk churidar pants.",
        "image_url": "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Little Gentleman 3-Piece Tuxedo Suit with Bowtie",
        "slug": "little-gentleman-3-piece-tuxedo-suit",
        "price": Decimal("4999.00"),
        "stock": 20,
        "description": "Classic black-tie three piece suit for boys including structured satin lapel blazer, waistcoat, trousers, and pre-tied satin bowtie.",
        "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Mustard Yellow Kurta Dhoti Set for Toddlers",
        "slug": "mustard-yellow-kurta-dhoti-set-toddlers",
        "price": Decimal("2999.00"),
        "stock": 25,
        "description": "Festive cotton silk kurta with gold border trim and ready-to-wear elasticated stitched dhoti for hassle-free celebration.",
        "image_url": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Pastel Mint Cotton Linen Nehru Jacket Set",
        "slug": "pastel-mint-cotton-linen-nehru-jacket-set",
        "price": Decimal("3499.00"),
        "stock": 22,
        "description": "Breathable mint green printed cotton kurta and churidar paired with a contrasting floral Modi/Nehru waistcoat jacket.",
        "image_url": "https://images.unsplash.com/photo-1503945438517-f65904a52ce6?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Navy Blue Velvet Blazer with Gold Crest",
        "slug": "navy-blue-velvet-blazer-gold-crest",
        "price": Decimal("4299.00"),
        "stock": 18,
        "description": "Plush royal navy velvet blazer embroidered with an imperial crown crest on chest pocket and polished brass buttons.",
        "image_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Royal Brocade Bandhgala Suit for Boys",
        "slug": "royal-brocade-bandhgala-suit-boys",
        "price": Decimal("5499.00"),
        "stock": 14,
        "description": "Banarasi gold and wine brocade closed-neck jacket paired with slim trousers for weddings and celebrations.",
        "image_url": "https://images.unsplash.com/photo-1485546246426-74dc88dec4d9?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Marigold Festive Silk Kurta & Pajama Set",
        "slug": "marigold-festive-silk-kurta-pajama-set",
        "price": Decimal("2799.00"),
        "stock": 26,
        "description": "Bright celebratory yellow chanderi silk kurta with delicate thread mirror work and cotton drawstring bottoms.",
        "image_url": "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "British Heritage Tweed Check Suspender Set",
        "slug": "british-heritage-tweed-check-suspender-set",
        "price": Decimal("3899.00"),
        "stock": 19,
        "description": "Charming vintage ensemble with beige houndstooth check trousers, leather clip-on suspenders, and crisp white poplin shirt.",
        "image_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Peach Floral Printed Festive Kurta Set",
        "slug": "peach-floral-printed-festive-kurta-set",
        "price": Decimal("2499.00"),
        "stock": 28,
        "description": "Soothing pastel peach soft organic cotton kurta printed with vintage botanicals, paired with white pajamas.",
        "image_url": "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Classic White Formal Shirt & Pleated Chino Combo",
        "slug": "classic-white-formal-shirt-pleated-chino-combo",
        "price": Decimal("2899.00"),
        "stock": 24,
        "description": "Crisp Egyptian cotton spread-collar shirt paired with tailored khaki stretch chinos and braided belt.",
        "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Royal Jodhpuri Riding Breeches & Kurta",
        "slug": "royal-jodhpuri-riding-breeches-kurta",
        "price": Decimal("4599.00"),
        "stock": 12,
        "description": "Aristocratic short angrakha jacket paired with flaring flared Jodhpuri breeches in raw silk.",
        "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Embroidered Pathani Suit Set for Boys",
        "slug": "embroidered-pathani-suit-set-boys",
        "price": Decimal("3299.00"),
        "stock": 21,
        "description": "Comfortable emerald green cotton linen pathani tunic with chest flap pockets, shirt collar, and pleated salwar.",
        "image_url": "https://images.unsplash.com/photo-1543332164-6e82f355badc?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Little Prince Zari Embroidered Mojaris",
        "slug": "little-prince-zari-embroidered-mojaris",
        "price": Decimal("1999.00"),
        "stock": 30,
        "description": "Cushioned ethnic slip-on shoes for boys with golden zari work and round toe for comfortable party wear.",
        "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Casual Denim Bomber Jacket with Sherpa Collar",
        "slug": "casual-denim-bomber-jacket-sherpa-collar",
        "price": Decimal("3199.00"),
        "stock": 23,
        "description": "Rugged yet plush washed blue denim zip-up jacket lined with warm faux sheepskin fleece.",
        "image_url": "https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "boys-kids-wear",
        "name": "Organic Cotton Striped Romper & Bow Set",
        "slug": "organic-cotton-striped-romper-bow-set",
        "price": Decimal("2199.00"),
        "stock": 35,
        "description": "Baby boys premium gentleman one-piece romper with mock vest, collar, snap buttons, and attached mini bowtie.",
        "image_url": "https://images.unsplash.com/photo-1519764622345-23439dd774f7?w=800&auto=format&fit=crop&q=80",
    },

    # =========================================================================
    # 8. GIRLS KIDS WEAR (15 Products)
    # =========================================================================
    {
        "category_slug": "girls-kids-wear",
        "name": "Fairytale Pastel Pink Butterfly Net Lehenga",
        "slug": "fairytale-pastel-pink-butterfly-net-lehenga",
        "price": Decimal("6499.00"),
        "stock": 15,
        "description": "Whimsical dream lehenga crafted with multi-layer soft net, 3D embroidered floral butterflies, and ruffled dupattas for girls.",
        "image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Princess Sparkle Multi-Tier Tulle Ball Gown",
        "slug": "princess-sparkle-multi-tier-tulle-ball-gown",
        "price": Decimal("5299.00"),
        "stock": 18,
        "description": "Floor-sweeping birthday party gown with glitter sequin bodice, fluffy multi-tier cascading tulle skirt, and giant back bow.",
        "image_url": "https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Canary Yellow Haldi Mirror Work Frock",
        "slug": "canary-yellow-haldi-mirror-work-frock",
        "price": Decimal("3199.00"),
        "stock": 24,
        "description": "Twirl-worthy celebratory flared dress with handmade mirror lace borders, cotton lining, and comfortable zipper back.",
        "image_url": "https://images.unsplash.com/photo-1516627145497-ae6968895b74?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Crimson Velvet Embroidered Festive Anarkali",
        "slug": "crimson-velvet-embroidered-festive-anarkali",
        "price": Decimal("4799.00"),
        "stock": 16,
        "description": "Warm plush micro-velvet anarkali suit decorated with gold gota patti and zardozi for Diwali and wedding receptions.",
        "image_url": "https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Ivory & Rose Gold Organza Peplum Sharara Set",
        "slug": "ivory-rose-gold-organza-peplum-sharara-set",
        "price": Decimal("4499.00"),
        "stock": 19,
        "description": "Chic contemporary ethnic ensemble featuring a lightweight organza flared peplum top and tiered matching sharara pants.",
        "image_url": "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Lavender Sequin Birthday Party Tutu Dress",
        "slug": "lavender-sequin-birthday-party-tutu-dress",
        "price": Decimal("3899.00"),
        "stock": 22,
        "description": "Enchanting lilac party dress featuring high-density micro-sequins, flutter sleeves, and fluffy French tulle skirt.",
        "image_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Floral Jacquard Banarasi Pattu Pavadai Set",
        "slug": "floral-jacquard-banarasi-pattu-pavadai-set",
        "price": Decimal("3999.00"),
        "stock": 20,
        "description": "Traditional south Indian silk langa voni dress woven with pure zari temple borders for festivals and naming ceremonies.",
        "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Cinderella Blue Satin Princess Gown",
        "slug": "cinderella-blue-satin-princess-gown",
        "price": Decimal("5899.00"),
        "stock": 14,
        "description": "Dreamy powder blue ball gown with off-shoulder organza wrap, corset-style lace back, and crystal sparkle overlay.",
        "image_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Peach Chikankari Cotton Flared Kurta Set",
        "slug": "peach-chikankari-cotton-flared-kurta-set",
        "price": Decimal("2999.00"),
        "stock": 26,
        "description": "Soft breathable pure mulmul cotton kurta with authentic handmade shadow work chikankari and flared palazzo pants.",
        "image_url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Ruby Red Velvet Holiday Smocked Dress",
        "slug": "ruby-red-velvet-holiday-smocked-dress",
        "price": Decimal("3699.00"),
        "stock": 21,
        "description": "Classic vintage European-style festive smocked dress in soft stretch velvet with Peter Pan collar and pearl buttons.",
        "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Mint Green Embroidered Cap Sleeve Gown",
        "slug": "mint-green-embroidered-cap-sleeve-gown",
        "price": Decimal("4199.00"),
        "stock": 17,
        "description": "Pastel mint evening party gown with floral thread-work bodice and satin-lined horsehair braid voluminous hemline.",
        "image_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Golden Tissue Flared Festive Frock",
        "slug": "golden-tissue-flared-festive-frock",
        "price": Decimal("3499.00"),
        "stock": 23,
        "description": "Shimmering champagne metallic tissue dress with soft pure cotton inner lining so it remains 100% itch-free.",
        "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Sparkly Pink Ballerina Shoes with Bow",
        "slug": "sparkly-pink-ballerina-shoes-bow",
        "price": Decimal("1899.00"),
        "stock": 32,
        "description": "Cushioned party bellies with all-over fine glitter, elastic midfoot strap for secure fit, and rhinestone bow charm.",
        "image_url": "https://images.unsplash.com/photo-1516585427167-9f4af9627e6c?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Floral Tiered Cotton Maxi Dress",
        "slug": "floral-tiered-cotton-maxi-dress",
        "price": Decimal("2599.00"),
        "stock": 29,
        "description": "Sunny summer cottagecore tiered dress in printed organic cotton with smocked bodice and flutter straps.",
        "image_url": "https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=800&auto=format&fit=crop&q=80",
    },
    {
        "category_slug": "girls-kids-wear",
        "name": "Handcrafted Pearl Tiara & Floral Wand Gift Set",
        "slug": "handcrafted-pearl-tiara-floral-wand-gift-set",
        "price": Decimal("1499.00"),
        "stock": 40,
        "description": "Regal princess birthday accessory set with crystal pearl crown tiara headband and ribbon star wand.",
        "image_url": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?w=800&auto=format&fit=crop&q=80",
    },
]


def refresh_catalog():
    print("=" * 60)
    print("REMOVING ALL OLD PRODUCTS & RE-SEEDING SIVORA LUXURY CATALOG")
    print("8 CATEGORIES x 15 PRODUCTS = 120 TOTAL LUXURY PRODUCTS")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Clear existing orders and chat messages that reference old products
        print("Clearing order items, orders, and chat messages...")
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(ChatMessage).delete()

        # 2. Clear old products & old categories
        print("Deleting old products and categories...")
        db.query(Product).delete()
        db.query(Category).delete()
        db.commit()



        # 4. Insert SIVORA Categories
        print("\nCreating SIVORA Luxury Categories...")
        cat_map = {}
        for cdata in SIVORA_CATEGORIES:
            cat = Category(**cdata)
            db.add(cat)
            db.commit()
            db.refresh(cat)
            cat_map[cdata["slug"]] = cat.id
            print(f"  + Category: {cat.name} ({cat.slug})")

        # 5. Insert SIVORA Products
        print(f"\nSeeding {len(SIVORA_PRODUCTS)} SIVORA Luxury Products (15 per category)...")
        for pdata in SIVORA_PRODUCTS:
            cat_slug = pdata.pop("category_slug")
            cat_id = cat_map[cat_slug]
            prod = Product(
                category_id=cat_id,
                thumbnail_url=pdata["image_url"],
                is_active=True,
                **pdata
            )
            db.add(prod)
        db.commit()
        print("All 120 Products successfully inserted into database.")

        # 6. Re-index ChromaDB Vector Store
        print("\nRefreshing ChromaDB Semantic Vector Database...")
        try:
            client = RAGService.get_client()
            try:
                client.delete_collection("products_catalog")
                print("  - Cleared old ChromaDB 'products_catalog' collection.")
            except Exception:
                pass
            RAGService._collection = None
            indexed_count = RAGService.index_all_products(db)
            print(f"  + Re-indexed {indexed_count} SIVORA luxury products in ChromaDB!")
        except Exception as e:
            print(f"  ! ChromaDB indexing notice: {e}")

        # 7. Clear Redis AI Cache
        print("\nFlushing Redis AI Query Cache...")
        try:
            from app.services.redis_service import CacheService
            CacheService.delete_pattern("categories:*")
            CacheService.delete_pattern("products:*")
            CacheService.delete_pattern("ai:*")
            print("  + Redis cache cleared.")
        except Exception as e:
            print(f"  ! Redis cache notice: {e}")

        print("\n" + "=" * 60)
        print("SUCCESS: SIVORA Luxury Fashion Catalog Refresh Complete!")
        print(f"Total Categories: {len(SIVORA_CATEGORIES)}")
        print(f"Total Products:   {len(SIVORA_PRODUCTS)}")
        print("=" * 60)

    except Exception as exc:
        db.rollback()
        print(f"ERROR refreshing catalog: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    refresh_catalog()
