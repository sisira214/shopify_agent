import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

COLLECTION_NAME = "shopify_products"
PAGE_LIMIT = 250

# --- CLIENTS ---
openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)

headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

def fetch_all_products():
    products = []
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-10/products.json?limit={PAGE_LIMIT}"

    while url:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()

        products.extend(resp.json()["products"])

        link_header = resp.headers.get("Link")
        if link_header and 'rel="next"' in link_header:
            url = link_header.split(";")[0].strip("<>")
        else:
            url = None

    return products

def main():
    products = fetch_all_products()
    print(f"📦 Found {len(products)} products in Shopify")

    for p in products:
        product_id = p["id"]
        title = p.get("title", "")
        vendor = p.get("vendor", "")
        tags = p.get("tags", "")
        handle = p.get("handle", "")

        raw_html = p.get("body_html") or ""
        soup = BeautifulSoup(raw_html, "html.parser")
        clean_description = soup.get_text(separator=" ")

        variants = p.get("variants", [])
        price = variants[0]["price"] if variants else "0.00"

        text_to_embed = (
            f"Product: {title}. "
            f"Vendor: {vendor}. "
            f"Tags: {tags}. "
            f"Description: {clean_description}"
        )

        embedding = openai_client.embeddings.create(
            input=text_to_embed,
            model="text-embedding-3-small"
        ).data[0].embedding

        payload = {
            "title": title,
            "vendor": vendor,
            "price": price,
            "handle": handle,
            "tags": tags,
            "description": clean_description
        }

        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[{
                "id": product_id,
                "vector": embedding,
                "payload": payload
            }]
        )

        print(f"✅ Backfilled product {product_id}")

    print("🎉 Backfill completed successfully")

if __name__ == "__main__":
    main()
