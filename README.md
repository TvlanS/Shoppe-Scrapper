# Shopee Scraper Pipeline

A web scraping pipeline for Shopee Malaysia that combines browser automation with LLM-based filtering and sub‑product discovery.

## Features

- **Multi‑stage pipeline**: Scrape → Filter with LLM → Generate sub‑product links → Deep scrape → Export
- **LLM filtering**: Uses LLM (DeepSeek/OpenAI‑compatible) to filter products based on natural‑language descriptions
- **Sub‑product discovery**: For each shop found, search for related products
- **Persistent browser sessions**: Saves login state across runs
- **Rate‑limiting & cooldowns**: Configurable delays to avoid detection
- **Multiple UIs**:
  - `gradio_main.py` – Step‑by‑step pipeline with separate stages
  - `gradio_with_login.py` – Simplified UI with login integration
- **Export options**: JSON and Excel (`.xlsx`) output

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Login to Shopee (required once)
python login.py
# or use the login tab in gradio_with_login.py

# 3. Run the Gradio UI
python gradio_with_login.py
# Open http://localhost:7860 in your browser

# 4. Or use the class directly
python -c "
from main_class2 import ShopeeProductSearch
searcher = ShopeeProductSearch(product='drawer slider', product_list=['cabinet hinges'])
results = searcher.run()
print(f'Found {len(results)} shops')
"
```

**More examples**: See `example_usage.py` for additional usage patterns.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/shopee-scraper.git
cd shopee-scraper

# Install dependencies
pip install -r requirements.txt

# Install optional LLM dependencies (if using LLM filtering)
# Ensure you have API keys configured (see Configuration section)
```

### Requirements

See `requirements.txt` for complete list. Main dependencies:

- `botasaurus`, `botasaurus-humancursor` – Browser automation
- `gradio` – Web UI
- `pandas`, `openpyxl` – Excel export
- `pyprojroot` – Path resolution
- `numpy` – Gradio dependency

## Configuration

### 1. LLM Configuration (Optional)

Input your API key section provided in `config/llm_config.yml`

### 2. Browser Profile

The scraper uses a persistent browser profile located at `profiles/Sapota/`.
First‑time login to Shoppe is optional, login can be performed through the browser via the login feature on Gradio UI to save the log data.

## Usage

### Option 1: Using the Class Directly

```python
from main_class2 import ShopeeProductSearch

# Initialize the pipeline
searcher = ShopeeProductSearch(
    product="drawer slider",           # Main product to search
    product_list=["cabinet hinges"],   # Sub‑products to look for in each shop
    product_description="heavy‑duty, 500mm, soft‑close",  # LLM preference (optional)
    use_llm=True,                      # Enable/disable LLM filtering
    cooldown_every=15,                 # Pause every N shops
    cooldown_sleep=15,                 # Cooldown duration (seconds)
    sub_sleep=5,                       # Sleep between sub‑product requests
)

# Run the full pipeline
results = searcher.run()

# Or run individual steps
searcher.scrape_main()          # Step 1: Main search
searcher.filter_products()      # Step 2: LLM filtering
searcher.build_subproduct_links()  # Step 3: Generate sub‑product URLs
searcher.scrape_subproducts()   # Step 4: Scrape sub‑products

# Results are saved automatically in:
# - main_output/*.json
# - filtered_output/*.json
# - subpoducts_outputs/*.json
# - productssearch_outputs/*.json
```

### Option 2: Gradio UI (Step‑by‑step)

Run the original multi‑stage UI:

```bash
python gradio_main.py
```

This opens a browser‑based interface with four tabs:

1. **Scrape & Filter** – Enter product keyword, scrape, then filter with LLM
2. **Sub‑products & Deep Scrape** – Define sub‑products and run deep scraping
3. **Export** – Export final results to Excel
4. **Load JSON** – Upload previously saved JSON to resume from any stage

### Option 3: Gradio UI with Login Integration

Run the simplified class‑based UI with login:

```bash
python gradio_with_login.py
```

Interface tabs:

1. **🔐 Login** – Open browser for manual Shopee login (required once)
2. **⚙️ Configure & Run** – Set all parameters and run the full pipeline
3. **📤 Export** – Export final data to Excel
4. **📂 Load JSON** – Upload existing JSON

### Option 4: Manual Login Script

If you need to login without the UI:

```bash
python login.py
```

This opens a browser window and waits 50 seconds for you to log in manually.
The session is saved to the browser profile for future use.

## Output Files

Each run generates timestamped JSON files:

1. **Main scrape**: `main_output/{product}_{timestamp}.json`
2. **Filtered products**: `filtered_output/{product}_{timestamp}_filtered.json`
3. **Sub‑product links**: `subpoducts_outputs/{product}_{timestamp}_subproducts.json`
4. **Final results**: `productssearch_outputs/{product}_{timestamp}_productsearch.json`

Excel export creates: `exports/shopee_export_{timestamp}.xlsx`

## Notes & Tips

### Login Requirements
- Shopee requires login for more item cards
- The browser profile persists cookies/sessions

### Rate Limiting
- Adjust `cooldown_every` and `cooldown_sleep` based on your needs
- Longer cooldowns reduce chance of being blocked
- Default: 15‑shop cooldown with 15‑second sleep

### LLM Filtering
- Requires valid API keys in `config/llm_config.yml`
- Set `use_llm=False` to skip LLM filtering
- The LLM receives product titles only (no prices/URLs)

### Error Handling
- CAPTCHA detection with manual resolution prompt
- Invalid shop pages are marked as "Page Unavailable"

## Troubleshooting

### "Dependencies not installed"
Run `pip install -r requirements.txt`

### "No module named 'numpy'"
Gradio requires numpy. Install with `pip install numpy`

### CAPTCHA appears frequently
- Increase cooldown settings
- Ensure you're logged in via the browser profile
- Captcha may appear when using profile for the first search , complete the captcha once and the bot can work      
  seamless for a period of time.

### LLM filtering not working
- Check `config/llm_config.yml` exists and has valid API keys
- Verify internet connection
- Set `use_llm=False` to bypass

## Future Improvements
- Create a dashboard
- Auto Generate report
- 