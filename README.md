
# Shopify Agent 🛍️🤖

A Python-based AI agent designed to interact with Shopify data and tools — including indexing products, recommending items, handling webhooks, and providing an interactive **Streamlit** UI. This project combines product indexing, retrieval, and AI-driven logic to help build intelligent Shopify-centric assistants.

---

## 🚀 Overview

**Shopify Agent** is a flexible agent that demonstrates how to build AI-powered Shopify utilities using Python. It provides:

- Product indexing and retrieval
- AI recommendation logic
- Integration with Shopify webhooks
- Jupyter notebooks illustrating workflows and usage

This project is ideal for powering custom conversational commerce workflows or prototyping AI agents on Shopify data.

---

## 🧠 Key Features

✔ Product indexing into store data  
✔ Shopify webhook helpers  
✔ Recommender logic (AI-based suggestions)  
✔ Jupyter notebooks for experimentation  
✔ Designed for extension to larger apps

---


## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/sisira214/shopify_agent.git
cd shopify_agent
````

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

*(If there’s no `requirements.txt`, manually install common libs like `streamlit`, `requests`, `pandas`, etc.)*

---

## ⚙️ Configuration

Depending on your use case, set up environment variables or config files to connect to:

* Shopify API (key/secret/store domain)
* AI model provider (if recommendations use external APIs)
* Any indexing or vector store credentials

Example `.env`:

```env
SHOPIFY_API_KEY="your_api_key"
SHOPIFY_API_SECRET="your_api_secret"
SHOPIFY_STORE_DOMAIN="your_store.myshopify.com"
AI_API_KEY="your_ai_provider_key"
```

Here is a **clean, corrected, and GitHub-ready version** of the **Installation** and **Usage** sections, rewritten clearly while keeping the original steps and intent intact.

You can paste this **directly into your README.md**.

---


## ▶️ Usage

### 1. Start the Vector Database (Qdrant)

```bash
docker run --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  qdrant/qdrant:latest
```

### 2. Run the Backend API

```bash
uvicorn agent_api:app --reload --port 8000
```

### 3. Run the Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

Once running, the Streamlit UI will open in your browser, allowing you to interact with the Shopify agent using indexed product data and AI-powered recommendations.




---

## 📁 Notebooks & Scripts

Below is a summary of the main scripts and notebooks:

| File                 | Purpose                                     |
| -------------------- | ------------------------------------------- |
| `backfill_qdrant.py` | Script to populate a Qdrant or vector index |
| `demo.ipynb`         | Notebook walk-through of basic agent usage  |
| `demo1.ipynb`        | Alternate demo notebook                     |
| `langgraph_agent.py` | Core agent logic (graph / LLM based)        |
| `populate_store.py`  | Import sample product data into an index    |
| `product_indexer.py` | Extract and index product catalog           |
| `recommender.py`     | AI-driven recommender engine                |
| `shopify_tools.py`   | Helpers for Shopify API integrations        |
| `shopify_webhook.py` | Webhook handling utilities                  |
| `streamlit.py`       | Streamlit UI frontend                       |

---

## 🧠 How It Works

1. **Product Indexing:** Scripts like `product_indexer.py` process Shopify product data and populate a vector/keyword index for fast retrieval.
2. **Agent Logic:** `langgraph_agent.py` implements agent behavior — fetching relevant context and generating recommendations or responses.
3. **Interactive UI:** The `streamlit.py` script provides a user interface to interact with the agent — including search, recommendations, and visual tools.
4. **Webhooks & Tools:** Utility modules help handle Shopify webhooks and API interactions if deployed as part of a larger app.

---

## 🤝 Contributing

Contributions are welcome! You can help by:

* Improving agent logic and workflows
* Adding real Shopify API integration
* Expanding the Streamlit UI with new features
* Adding tests, demo scenarios, or deployment configs

Please open issues or pull requests on GitHub.

---

## 📜 License

This project is licensed under the **MIT License** — see the `LICENSE` file for details.

```
