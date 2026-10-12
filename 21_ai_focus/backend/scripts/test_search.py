from app.database import SessionLocal
from app.models.product import Product
from sqlalchemy import func
from sqlalchemy.orm import joinedload

db = SessionLocal()
try:
    print("=== TESTING POSTGRESQL FUZZY & WORD SIMILARITY SEARCH ===")
    test_typos = ["iphoen", "keybord", "macbok", "headphon", "samsng"]
    for typo in test_typos:
        # word_similarity compares typo against words in the product name
        sim = func.word_similarity(typo, Product.name)
        results = (
            db.query(Product, sim.label("score"))
            .options(joinedload(Product.category))
            .filter(sim > 0.3)
            .order_by(sim.desc())
            .all()
        )
        print(f"\nTypo Search: '{typo}'")
        for prod, score in results:
            print(f"  -> Matched: {prod.name} | Category: {prod.category.name} | Score: {score:.2f}")

    print("\n=== TESTING FULL-TEXT SEARCH (STEMMING & GIN INDEX) ===")
    # Stemming: 'headphones' should match 'headphone', 'running' matches 'run'
    fts_queries = ["smartphone", "wireless", "laptop", "audio"]
    for q in fts_queries:
        fts_match = func.to_tsvector("english", Product.name + " " + func.coalesce(Product.description, "")).op("@@")(
            func.plainto_tsquery("english", q)
        )
        results = db.query(Product).options(joinedload(Product.category)).filter(fts_match).all()
        print(f"\nFTS Query: '{q}' -> Found {len(results)} items:")
        for prod in results:
            print(f"  -> {prod.name} (${prod.price})")

finally:
    db.close()
