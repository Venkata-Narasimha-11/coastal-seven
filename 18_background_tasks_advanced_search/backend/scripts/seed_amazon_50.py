import re
from app.database import SessionLocal
from app.models.product import Product, Category
from app.services.redis_service import CacheService

def run():
    db = SessionLocal()

    # Clear cache
    CacheService.invalidate_pattern('products:*')
    CacheService.invalidate_pattern('categories:*')

    # Ensure all required categories exist
    required_cats = [
        ('Electronics', 'electronics', 'General electronics and gadgets'),
        ('Fashion', 'fashion', 'Clothing and fashion'),
        ('Audio', 'audio', 'Headphones, earbuds, and speakers'),
        ('Wearables', 'wearables', 'Smartwatches, fitness bands, and rings'),
        ('Laptops & Computers', 'laptops-computers', 'Laptops, desktops, and computing'),
        ('Peripherals', 'peripherals', 'Keyboards, mice, monitors, and webcams'),
        ('Gaming & VR', 'gaming-vr', 'Consoles, VR headsets, and handhelds'),
        ('Cameras & Drones', 'cameras-drones', 'DSLR, mirrorless cameras, and drones'),
        ('Smart Home', 'smart-home', 'Smart speakers, lighting, and automation'),
        ('Accessories', 'accessories', 'Chargers, power banks, cables, and cases'),
    ]
    for c_name, c_slug, c_desc in required_cats:
        c = db.query(Category).filter(Category.name == c_name).first()
        if not c:
            c = Category(name=c_name, slug=c_slug, description=c_desc)
            db.add(c)
    db.commit()

    cats = {c.name: c.id for c in db.query(Category).all()}

    amazon_products = [
        # Audio
        ('Apple AirPods Pro 2 USB-C', 'airpods-pro-2', 'Active Noise Cancellation, Adaptive Audio, Transparency mode, up to 30 hours battery life with USB-C case.', 24900.0, 45, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=500&q=80'),
        ('Sony WH-1000XM5 ANC Headphones', 'sony-wh1000xm5', 'Industry-leading noise cancellation with two processors and 8 microphones, 30-hour battery life.', 29990.0, 30, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&q=80'),
        ('Bose QuietComfort 45 Bluetooth Headphones', 'bose-qc45', 'Iconic quiet, comfort, and sound. TriPort acoustic architecture, lightweight materials for all-day wear.', 22900.0, 20, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80'),
        ('JBL Flip 6 Waterproof Bluetooth Speaker', 'jbl-flip-6', 'IP67 waterproof and dustproof, 12 hours of playtime, bold JBL Original Pro Sound with 2-way speaker system.', 9999.0, 60, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500&q=80'),
        ('Marshall Stanmore III Bluetooth Speaker', 'marshall-stanmore-3', 'Re-engineered for a more immersive experience with wider soundstage and iconic vintage design.', 34999.0, 15, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&q=80'),
        ('Sennheiser Momentum 4 Wireless ANC', 'sennheiser-momentum-4', 'Outstanding 60-hour battery life, customizable sound via Smart Control app, premium lightweight comfort.', 27990.0, 25, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500&q=80'),
        ('Boat Airdopes 141 Bluetooth TWS', 'boat-airdopes-141', '42H Playtime, Beast Mode for Low Latency Gaming, ENx Tech, ASAP Charge, IPX4 Water Resistance.', 1299.0, 150, cats.get('Audio', 1), 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=500&q=80'),

        # Wearables
        ('Apple Watch Ultra 2 Titanium 49mm', 'apple-watch-ultra-2', 'Rugged titanium case, precision dual-frequency GPS, up to 36-hour battery, customizable Action button.', 89900.0, 18, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80'),
        ('Samsung Galaxy Watch 6 Classic LTE', 'galaxy-watch-6-classic', 'Rotating physical bezel, Advanced sleep coaching, Sapphire crystal glass, BIA sensor for body composition.', 36999.0, 35, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=500&q=80'),
        ('Garmin Fenix 7 Pro Sapphire Solar GPS', 'garmin-fenix-7-pro', 'Solar powered charging, built-in LED flashlight, endurance score, top-tier topographic maps.', 94990.0, 12, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=500&q=80'),
        ('Fitbit Charge 6 Fitness Tracker', 'fitbit-charge-6', 'Built-in GPS, YouTube Music controls, Google Maps navigation, 7-day battery life, 40+ exercise modes.', 14999.0, 50, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500&q=80'),
        ('Oura Ring Gen 3 Stealth Horizon', 'oura-ring-gen3', 'Titanium finish smart ring tracking sleep stages, HRV, readiness score, and daily workout strain.', 34900.0, 22, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=500&q=80'),
        ('Noise ColorFit Pulse 3 Smartwatch', 'noise-colorfit-pulse-3', '1.96-inch TFT display, Bluetooth calling, 100+ sports modes, 7-day battery life, heart rate & SpO2.', 1999.0, 80, cats.get('Wearables', 2), 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=500&q=80'),

        # Laptops & Computers
        ('Apple MacBook Pro 16 M3 Max 36GB', 'macbook-pro-16-m3', '16-core CPU, 40-core GPU, Liquid Retina XDR display with ProMotion 120Hz, Space Black finish.', 349900.0, 10, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500&q=80'),
        ('Dell XPS 15 3.5K OLED Core i9 32GB', 'dell-xps-15-oled', '3.5K OLED touchscreen, CNC machined aluminum chassis with carbon fiber palm rest, RTX 4070 GPU.', 229990.0, 14, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500&q=80'),
        ('ASUS ROG Zephyrus G16 OLED Gaming', 'asus-rog-zephyrus-g16', 'Intel Core Ultra 9, RTX 4080 12GB, 2.5K 240Hz ROG Nebula OLED display in Eclipse Gray.', 249990.0, 12, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500&q=80'),
        ('Lenovo ThinkPad X1 Carbon Gen 11', 'thinkpad-x1-carbon-11', 'Ultra-lightweight magnesium alloy chassis, Intel Core i7 13th Gen, legendary ThinkPad keyboard.', 179900.0, 16, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500&q=80'),
        ('HP Spectre x360 2-in-1 Laptop 14 OLED', 'hp-spectre-x360-14', 'OLED touchscreen with stylus pen, Intel Evo Platform, 360-degree gem-cut hinge, Nightfall Black.', 159990.0, 15, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&q=80'),
        ('Apple MacBook Air 15 M3 16GB Starlight', 'macbook-air-15-m3', 'Incredibly thin and fast, fanless silent design, Liquid Retina display, 18-hour battery in Starlight.', 139900.0, 25, cats.get('Laptops & Computers', 5), 'https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=500&q=80'),

        # Peripherals
        ('Logitech MX Master 3S Wireless Mouse', 'logitech-mx-master-3s', '8K DPI any-surface tracking, quiet clicks, MagSpeed electromagnetic scrolling wheel.', 9495.0, 65, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80'),
        ('Keychron Q1 Pro Custom Mechanical Keyboard', 'keychron-q1-pro', 'Full aluminum CNC body, hot-swappable switches, double-gasket design, QMK/VIA programmable.', 18999.0, 28, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80'),
        ('Dell UltraSharp 27 4K USB-C Monitor', 'dell-ultrasharp-27-4k', 'IPS Black technology, 2000:1 contrast ratio, 90W Power Delivery USB-C, 98% DCI-P3 color gamut.', 54990.0, 18, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&q=80'),
        ('Elgato Stream Deck MK.2 Studio 15 Keys', 'elgato-stream-deck-mk2', '15 customizable LCD macro keys for live streaming, editing, and automation workflows.', 14490.0, 32, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500&q=80'),
        ('Logitech Brio 4K Ultra HD Pro Webcam', 'logitech-brio-4k', 'RightLight 3 with HDR, dual noise-cancelling mics, 90-degree field of view with Windows Hello.', 19995.0, 24, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=500&q=80'),
        ('Razer DeathAdder V3 Pro Wireless Mouse', 'razer-deathadder-v3-pro', '63g ultra-lightweight ergonomic mouse, Focus Pro 30K Optical Sensor, 90-hour battery life.', 12999.0, 40, cats.get('Peripherals', 3), 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&q=80'),

        # Gaming & VR
        ('Sony PlayStation 5 Slim 1TB Console', 'sony-ps5-slim', 'Ultra-high speed SSD, ray tracing, haptic feedback on DualSense wireless controller, 4K 120Hz gaming.', 54990.0, 25, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=500&q=80'),
        ('Microsoft Xbox Series X 1TB Console', 'xbox-series-x', '12 teraflops raw graphical processing power, 4K gaming at up to 120 FPS, 1TB custom NVMe SSD.', 49990.0, 20, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=500&q=80'),
        ('Nintendo Switch OLED White Joy-Con', 'nintendo-switch-oled', 'Vibrant 7-inch OLED screen, wide adjustable stand, wired LAN dock, 64GB internal storage.', 31999.0, 30, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1578303512597-8be920959082?w=500&q=80'),
        ('Meta Quest 3 Mixed Reality VR 128GB', 'meta-quest-3-128gb', 'Breakthrough mixed reality with dual color cameras, 4K+ Infinite Display, Snapdragon XR2 Gen 2.', 49990.0, 15, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=500&q=80'),
        ('SteelSeries Arctis Nova Pro Wireless', 'arctis-nova-pro-wireless', 'Active noise cancellation, dual hot-swap battery system, GameDAC Gen 2 high-res audio.', 34999.0, 18, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500&q=80'),
        ('ASUS ROG Ally Z1 Extreme Handheld', 'asus-rog-ally-z1-extreme', 'Windows 11 gaming handheld with AMD Ryzen Z1 Extreme processor, 7 120Hz 1080p touch display.', 59990.0, 14, cats.get('Gaming & VR', 6), 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500&q=80'),

        # Cameras & Drones
        ('Sony Alpha 7 IV Full-Frame Camera', 'sony-a7-iv-body', '33MP BSI full-frame sensor, 4K 60p 10-bit video, real-time eye autofocus, 5-axis image stabilization.', 214990.0, 8, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&q=80'),
        ('DJI Mini 4 Pro Drone with RC 2', 'dji-mini-4-pro', 'Under 249g ultra-lightweight drone, omnidirectional obstacle sensing, 4K 60fps HDR video, 20km transmission.', 99990.0, 16, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1527977966376-1c8408f9f108?w=500&q=80'),
        ('Canon EOS R6 Mark II Mirrorless', 'canon-eos-r6-mark2', '24.2MP CMOS sensor, 40fps continuous shooting, 6K oversampled uncropped 4K 60p video recording.', 249990.0, 9, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500&q=80'),
        ('GoPro HERO12 Black Action Camera 5.3K', 'gopro-hero12-black', 'Incredible 5.3K video resolution, HyperSmooth 6.0 stabilization, waterproof up to 33ft, HDR video.', 37990.0, 35, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1565849904461-04a58ad377e0?w=500&q=80'),
        ('Fujifilm X-T5 Digital Camera Silver', 'fujifilm-xt5-silver', '40.2MP X-Trans CMOS 5 HR sensor, iconic dial operation, 19 film simulation modes, deep learning AF.', 169999.0, 11, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1510127034890-ba27508e9f1c?w=500&q=80'),
        ('DJI Osmo Pocket 3 4K 120fps Gimbal', 'dji-osmo-pocket-3', '1-inch CMOS sensor, 2-inch rotatable OLED touchscreen, 3-axis mechanical stabilization, active tracking.', 53990.0, 22, cats.get('Cameras & Drones', 7), 'https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=500&q=80'),

        # Smart Home
        ('Amazon Echo Dot 5th Gen Alexa', 'echo-dot-5th-gen', 'Deeper bass and clearer vocals, built-in temperature sensor, voice control smart home appliances.', 4499.0, 80, cats.get('Smart Home', 8), 'https://images.unsplash.com/photo-1543512214-318c7553f230?w=500&q=80'),
        ('Philips Hue White & Color Smart Bulbs', 'philips-hue-starter-kit', '16 million colors, sync lights with music and movies, control via Alexa/Google Assistant and app.', 11999.0, 45, cats.get('Smart Home', 8), 'https://images.unsplash.com/photo-1550524514-4b6c23062080?w=500&q=80'),
        ('Roborock S8 Pro Ultra Robot Vacuum', 'roborock-s8-pro-ultra', 'All-in-one dock with auto washing & drying, 6000Pa suction power, dual rubber roller brushes.', 119900.0, 10, cats.get('Smart Home', 8), 'https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500&q=80'),
        ('Google Nest Learning Thermostat 3rd Gen', 'google-nest-thermostat', 'Learns your schedule, automatically adjusts temperature to save energy, remote phone control.', 21990.0, 24, cats.get('Smart Home', 8), 'https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9?w=500&q=80'),
        ('Yale Assure Lock 2 Smart Door Lock', 'yale-assure-lock-2', 'Keyless biometric entry, Apple HomeKit and Wi-Fi smart control, auto-unlock on approach.', 24999.0, 18, cats.get('Smart Home', 8), 'https://images.unsplash.com/photo-1558002038-1055907df827?w=500&q=80'),

        # Accessories
        ('Anker Prime 100W GaN Fast Charger', 'anker-prime-100w-charger', 'Ultra-compact Gallium Nitride 100W fast charger for MacBook, iPhone, iPad, and Android phones.', 5999.0, 75, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500&q=80'),
        ('Anker 737 Power Bank 24K 140W Fast Charge', 'anker-737-powerbank-140w', 'Massive 24,000mAh capacity, 140W two-way fast charging with smart digital color display.', 11999.0, 40, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1609592424109-dd9892f1b177?w=500&q=80'),
        ('Belkin 3-in-1 MagSafe Wireless Stand 15W', 'belkin-3in1-magsafe-stand', 'Fast charge iPhone, Apple Watch, and AirPods simultaneously in seamless premium stainless steel.', 13999.0, 30, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=500&q=80'),
        ('Bellroy Tokyo Work Bag Laptop Briefcase', 'bellroy-tokyo-work-bag', 'Water-resistant recycled fabric, designated padded laptop compartment, internal organization pockets.', 16999.0, 25, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500&q=80'),
        ('Satechi USB-C Multiport Pro 8-in-1 Hub', 'satechi-usbc-multiport-hub', '4K HDMI, Gigabit Ethernet, SD card slots, USB-C Power Delivery pass-through charging.', 7999.0, 50, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1544652478-6653e09f18a2?w=500&q=80'),
        ('Spigen Tough Armor Case for iPhone 15', 'spigen-tough-armor-iphone-15', 'Air Cushion technology for extreme drop protection, tactile buttons, built-in kickstand.', 1999.0, 120, cats.get('Accessories', 4), 'https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=500&q=80')
    ]

    added = 0
    for name, slug, desc, price, stock, cat_id, img in amazon_products:
        existing = db.query(Product).filter(Product.slug == slug).first()
        if not existing:
            prod = Product(
                name=name,
                slug=slug,
                description=desc,
                price=price,
                stock=stock,
                category_id=cat_id,
                image_url=img,
                thumbnail_url=img,
                is_active=True
            )
            db.add(prod)
            added += 1
        else:
            existing.image_url = img
            existing.thumbnail_url = img
            existing.is_active = True

    db.commit()
    total = db.query(Product).filter(Product.is_active == True).count()
    print(f"SUCCESS: Seeded {added} new products. Total active products in database: {total}")

if __name__ == '__main__':
    run()
