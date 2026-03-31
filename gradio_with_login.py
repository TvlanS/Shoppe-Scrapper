"""
Gradio UI for ShopeeProductSearch class with login functionality.
"""

import json
import os
import time
import sys
from datetime import datetime

# Check for optional dependencies
GRADIO_AVAILABLE = False
NUMPY_AVAILABLE = False
PANDAS_AVAILABLE = False
PYPROJROOT_AVAILABLE = False
BOTASAURUS_AVAILABLE = False
MAIN_CLASS_AVAILABLE = False

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    print("ERROR: gradio not installed. Please run: pip install gradio")
    sys.exit(1)

try:
    import numpy
    NUMPY_AVAILABLE = True
except ImportError:
    print("WARNING: numpy not installed. Some Gradio components may fail.")

try:
    import pandas
    PANDAS_AVAILABLE = True
except ImportError:
    print("WARNING: pandas not installed. Excel export will not work.")

try:
    import pyprojroot
    root = pyprojroot.here()
    PYPROJROOT_AVAILABLE = True
except ImportError:
    root = os.path.dirname(os.path.abspath(__file__))
    print("WARNING: pyprojroot not installed. Using current directory as root.")

try:
    from utils.botsauce_tools import ScrapeShopee
    from main_class2 import ShopeeProductSearch
    BOTASAURUS_AVAILABLE = True
    MAIN_CLASS_AVAILABLE = True
    DEPS_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Could not import scraper modules: {e}")
    DEPS_AVAILABLE = False

# ── CSS (copied from existing gradio_main.py) ─────────────────────────────────────
CSS = """
/* ── Base ── */
body, .gradio-container {
    font-family: 'DM Mono', 'Fira Mono', monospace !important;
    background: #0d0f14 !important;
    color: #c9d1d9 !important;
}

/* Header */
.header-block {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 8px;
}
.header-block h1 {
    font-size: 1.7rem;
    font-weight: 700;
    color: #f0883e;
    letter-spacing: -0.5px;
    margin: 0 0 6px 0;
}
.header-block p {
    color: #6e7681;
    font-size: 0.85rem;
    margin: 0;
}

/* Stage panels */
.stage-panel {
    border: 1px solid #21262d;
    border-radius: 10px;
    background: #161b22;
    padding: 20px;
    margin-bottom: 4px;
}
.stage-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #f0883e;
    margin-bottom: 12px;
}

/* Buttons */
button.primary-btn {
    background: #f0883e !important;
    color: #0d0f14 !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px;
    padding: 10px 22px !important;
    transition: opacity 0.15s;
}
button.primary-btn:hover { opacity: 0.85; }

button.secondary-btn {
    background: transparent !important;
    color: #58a6ff !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}

/* Status boxes */
.status-ok  { color: #3fb950 !important; font-weight: 600; }
.status-err { color: #f85149 !important; font-weight: 600; }

/* Textareas / code boxes */
textarea, .gr-textbox textarea {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
}
textarea:focus { border-color: #f0883e !important; outline: none !important; }

/* Tab strip */
.tab-nav button {
    color: #8b949e !important;
    border-bottom: 2px solid transparent !important;
    font-size: 0.85rem !important;
}
.tab-nav button.selected {
    color: #f0883e !important;
    border-bottom-color: #f0883e !important;
}

/* Accordion */
.gr-accordion { border-color: #21262d !important; }

/* Slider */
input[type=range] { accent-color: #f0883e; }
"""

def run_login(progress=gr.Progress(track_tqdm=True)):
    """Open browser for manual login."""
    if not DEPS_AVAILABLE:
        return " Dependencies (ScrapeShopee) not installed."

    progress(0.1, desc="Opening browser for login...")
    # Dummy URL, login function just opens the browser and waits
    url = "https://shopee.com.my"
    scraper = ScrapeShopee(url)

    # This will open a browser window and wait 50 seconds for manual login
    progress(0.5, desc="Browser opened. Please login manually within 50 seconds...")
    scraper.run_login()

    progress(1.0, desc="Login session closed.")
    return "Login completed. You can now run the scraper."

def run_pipeline(
    product: str,
    product_list_raw: str,
    product_description: str,
    use_llm: bool,
    cooldown_every: int,
    cooldown_sleep: int,
    sub_sleep: int,
    progress=gr.Progress(track_tqdm=True)
):
    """Run the full pipeline using ShopeeProductSearch class."""
    if not DEPS_AVAILABLE:
        return None, "Dependencies not available."

    if not product.strip():
        return None, " Please enter a product keyword."

    product_list = [p.strip() for p in product_list_raw.split(",") if p.strip()]
    if not product_list:
        return None, "Please enter at least one sub‑product (comma‑separated)."

    progress(0.05, desc="Initializing scraper...")

    try:
        searcher = ShopeeProductSearch(
            product=product,
            product_list=product_list,
            product_description=product_description,
            use_llm=use_llm,
            cooldown_every=cooldown_every,
            cooldown_sleep=cooldown_sleep,
            sub_sleep=sub_sleep,
        )
    except Exception as e:
        return None, f" Failed to initialize: {e}"

    progress(0.1, desc="Scraping main product search...")
    raw = searcher.scrape_main()

    progress(0.3, desc="Filtering products...")
    filtered = searcher.filter_products()

    progress(0.5, desc="Building sub‑product links...")
    sub_links = searcher.build_subproduct_links()

    progress(0.7, desc="Scraping sub‑products (this may take a while)...")
    final = searcher.scrape_subproducts()

    progress(1.0, desc="Pipeline complete!")

    # Return final data as JSON string and success message
    final_json = json.dumps(final, ensure_ascii=False, indent=2)
    msg = f" Pipeline finished. Final data contains {len(final)} shops."
    return final_json, msg

def export_excel(final_json: str):
    """Export final JSON to Excel."""
    if not final_json:
        return None, "No data to export."

    try:
        import pandas as pd
    except ImportError:
        return None, "pandas not installed (`pip install pandas openpyxl`)."

    data = json.loads(final_json)
    rows = []
    for shop_id, shop in data.items():
        base = {
            "shop_id": shop_id,
            "product_id": shop.get("id"),
            "title": shop.get("title"),
            "price": shop.get("price"),
            "url": shop.get("url"),
        }
        findings = shop.get("Findings", {})
        if findings:
            for subprod, items in findings.items():
                if isinstance(items, dict):
                    for item_id, item_data in items.items():
                        row = base.copy()
                        row["subproduct_category"] = subprod
                        row["subproduct_title"] = item_data.get("title") if isinstance(item_data, dict) else str(item_data)
                        row["subproduct_price"] = item_data.get("price") if isinstance(item_data, dict) else ""
                        rows.append(row)
                else:
                    row = base.copy()
                    row["subproduct_category"] = subprod
                    rows.append(row)
        else:
            rows.append(base)

    df = pd.DataFrame(rows)
    out_path = os.path.join(root, "exports", f"shopee_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_excel(out_path, index=False)
    return out_path, f" Excel exported → `{os.path.basename(out_path)}`"

# ── Build UI ─────────────────────────────────────────────────────────────────────
with gr.Blocks(
    css=CSS,
    title="Shopee Scraper (Class + Login)",
    theme=gr.themes.Base(
        primary_hue=gr.themes.colors.orange,
        neutral_hue=gr.themes.colors.slate,
    ),
) as demo:

    if not DEPS_AVAILABLE:
        gr.Markdown("## ⚠️ Missing Dependencies\nSome required packages are not installed. Please install them using `pip install -r requirements.txt`.\nScraping functionality will be limited.")

    gr.HTML("""
    <div class="header-block">
        <h1>🛒 Shopee Scraper Pipeline</h1>
    </div>
    """)

    # State to hold final JSON data
    state_final = gr.State(None)

    with gr.Tabs():

        # ── TAB 1: Login ─────────────────────────────────────────────────────────
        with gr.Tab("🔐 Login"):
            gr.Markdown(
                "Click the button below to open a browser window where you can log in to Shopee manually. "
                "You have 50 seconds to complete the login. After that, the browser will close and the session will be saved."
            )
            login_btn = gr.Button("🌐 Open Browser for Login", elem_classes="primary-btn")
            login_status = gr.Markdown("")
            login_btn.click(fn=run_login, outputs=login_status)

        # ── TAB 2: Configuration & Run ───────────────────────────────────────────
        with gr.Tab("⚙️ Configure & Run"):

            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML('<div class="stage-label">Pipeline Parameters</div>')

                    product_input = gr.Textbox(
                        label="Main product keyword",
                        placeholder="e.g., drawer slider",
                        value="drawer slider",
                    )

                    product_list_input = gr.Textbox(
                        label="Sub‑products (comma‑separated)",
                        placeholder="e.g., cabinet hinges, drawer handle, soft‑close hinge",
                        value="cabinet hinges",
                        lines=2,
                    )

                    product_desc_input = gr.Textbox(
                        label="Product description / preference",
                        placeholder="e.g., heavy‑duty, 500mm, soft‑close  (leave blank for no preference)",
                    )

                    use_llm_checkbox = gr.Checkbox(
                        label="Use LLM for filtering",
                        value=True,
                    )

                    with gr.Row():
                        cooldown_every_input = gr.Number(
                            label="Cooldown every N shops",
                            value=15,
                            precision=0,
                            minimum=1,
                        )
                        cooldown_sleep_input = gr.Number(
                            label="Cooldown sleep (seconds)",
                            value=15,
                            precision=0,
                            minimum=1,
                        )
                        sub_sleep_input = gr.Number(
                            label="Sleep between sub‑products (seconds)",
                            value=5,
                            precision=0,
                            minimum=1,
                        )

                    run_btn = gr.Button("🚀 Run Full Pipeline", elem_classes="primary-btn")
                    run_status = gr.Markdown("")

                with gr.Column(scale=1):
                    gr.HTML('<div class="stage-label">Pipeline Output</div>')
                    final_json_view = gr.Code(
                        label="Final JSON (first 5 items)",
                        language="json",
                        lines=22,
                        interactive=False,
                    )

            # Wire run button
            run_btn.click(
                fn=run_pipeline,
                inputs=[
                    product_input,
                    product_list_input,
                    product_desc_input,
                    use_llm_checkbox,
                    cooldown_every_input,
                    cooldown_sleep_input,
                    sub_sleep_input,
                ],
                outputs=[state_final, run_status],
            )

            # Update JSON preview when state_final changes
            state_final.change(
                fn=lambda j: json.dumps(dict(list(json.loads(j).items())[:5]), ensure_ascii=False, indent=2) if j else "",
                inputs=[state_final],
                outputs=[final_json_view],
            )
        # ── TAB 3: Export ────────────────────────────────────────────────────────
        with gr.Tab("📤 Export"):
            gr.HTML('<div class="stage-label">Export final dataset</div>')

            with gr.Row():
                with gr.Column():
                    export_btn = gr.Button("📊 Export to Excel (.xlsx)", elem_classes="primary-btn")
                    export_status = gr.Markdown("")
                    excel_file = gr.File(label="Download Excel file", interactive=False)

                with gr.Column():
                    gr.HTML('<div class="stage-label">Final JSON (full)</div>')
                    final_json_full = gr.Code(
                        label="", language="json", lines=20, interactive=False
                    )

            # Show full JSON when state_final changes
            state_final.change(
                fn=lambda j: json.dumps(json.loads(j), ensure_ascii=False, indent=2) if j else "",
                inputs=[state_final],
                outputs=[final_json_full],
            )

            export_btn.click(
                fn=export_excel,
                inputs=[state_final],
                outputs=[excel_file, export_status],
            )

        # ── TAB 4: Load Existing JSON ────────────────────────────────────────────
        with gr.Tab("📂 Load JSON"):
            gr.Markdown("Upload a previously saved JSON file to load into the pipeline.")
            json_upload = gr.File(label="Upload JSON", file_types=[".json"])
            load_btn = gr.Button("Load JSON as final data", elem_classes="secondary-btn")
            load_status = gr.Markdown("")

            def load_json(file):
                if file is None:
                    return None, None, "⚠️ No file uploaded."
                with open(file.name, encoding="utf-8") as f:
                    content = json.dumps(json.load(f))
                return content, content, f"✅ JSON loaded ({os.path.basename(file.name)})"

            load_btn.click(
                fn=load_json,
                inputs=[json_upload],
                outputs=[state_final, final_json_full, load_status],
            )

if __name__ == "__main__":
    demo.launch(share=False, show_error=True)