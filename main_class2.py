from utils.botsauce_tools import ScrapeShopee
import json
import os
from datetime import datetime
import pyprojroot
import time
from utils.LLM_tools import LLM_toolset
import copy

root = pyprojroot.here()


class ShopeeProductSearch:

    def __init__(
        self,
        product: str,
        product_list: list[str],
        product_description: str = "no preference",
        use_llm: bool = True,
        cooldown_every: int = 15,
        cooldown_sleep: int = 15,
        sub_sleep: int = 5,
    ):
        self.product = product
        self.product_list = product_list
        self.product_description = product_description
        self.use_llm = use_llm
        self.cooldown_every = cooldown_every
        self.cooldown_sleep = cooldown_sleep
        self.sub_sleep = sub_sleep

        self.product_clean = product.replace(" ", "_")
        self.now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        # Output paths
        self.main_path = root / "main_output"         / f"{self.product_clean}_{self.now}.json"
        self.filtered_path = root / "filtered_output" / f"{self.product_clean}_{self.now}_filtered.json"
        self.subproducts_path = root / "subpoducts_outputs" / f"{self.product_clean}_{self.now}_subproducts.json"
        self.productsearch_path = root / "productssearch_outputs" / f"{self.product_clean}_{self.now}_productsearch.json"

        self._ensure_dirs()

        # State
        self.raw_data: dict = {}
        self.filtered_data: dict = {}
        self.subproduct_links: dict = {}
        self.final_data: dict = {}

    def _ensure_dirs(self):
        for path in [self.main_path, self.filtered_path, self.subproducts_path, self.productsearch_path]:
            os.makedirs(path.parent, exist_ok=True)
        print("Output directories ready.")

    @staticmethod
    def _build_url(keyword: str, shop_id: str | None = None) -> str:
        encoded = keyword.replace(" ", "%20")
        url = f"https://shopee.com.my/search?keyword={encoded}"
        if shop_id:
            url += f"&shop={shop_id}"
        return url

    @staticmethod
    def _save_json(data: dict, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def scrape_main(self) -> dict:
        """Step 1 – Scrape main product search results."""
        url = self._build_url(self.product)
        self.raw_data = ScrapeShopee(url).run_main()
        self._save_json(self.raw_data, self.main_path)
        print(f"Main scrape done — {len(self.raw_data)} products saved.")
        return self.raw_data

    def filter_products(self) -> dict:
        """Step 2 – Filter products (LLM or pass-through)."""
        if self.use_llm:
            data_for_llm = {k: {k: v.get("title")} for k, v in self.raw_data.items()}
            llm = LLM_toolset(data_for_llm, self.product_description)
            kept_ids = llm.LLM_filter()
            self.filtered_data = {id_: self.raw_data[id_] for id_ in kept_ids if id_ in self.raw_data}
            print(f"LLM kept {len(self.filtered_data)} / {len(self.raw_data)} products.")
        else:
            self.filtered_data = self.raw_data.copy()
            print(f"LLM skipped — using all {len(self.filtered_data)} products.")

        self._save_json(self.filtered_data, self.filtered_path)
        return self.filtered_data

    def build_subproduct_links(self) -> dict:
        """Step 3 – Generate sub-product search URLs per shop."""
        self.subproduct_links = {}

        for id_, item in self.filtered_data.items():
            shop_id = item.get("shop_id")
            entry = {
                "id":    id_,
                "title": item.get("title"),
                "price": item.get("price"),
                "url":   item.get("url"),
                "subproducts": {
                    sub: self._build_url(sub, shop_id)
                    for sub in self.product_list
                },
            }
            self.subproduct_links[shop_id] = entry

        self._save_json(self.subproduct_links, self.subproducts_path)
        print(f"Sub-product URLs built for {len(self.subproduct_links)} shops.")
        return self.subproduct_links

    def scrape_subproducts(self) -> dict:
        """Step 4 – Scrape each sub-product URL with cooldown logic."""
        self.final_data = copy.deepcopy(self.subproduct_links)

        total_shops = len(self.final_data)
        num_subproducts = len(self.product_list)
        total_jobs = total_shops * num_subproducts
        shop_count = 0
        total_done = 0
        start = time.time()

        for shop_id, items in self.final_data.items():
            for subproduct, link in items.get("subproducts", {}).items():
                findings = ScrapeShopee(link).run_sub()
                time.sleep(self.sub_sleep)

                if shop_count > 0 and shop_count % self.cooldown_every == 0:
                    print(f"Cooldown — sleeping {self.cooldown_sleep}s …")
                    time.sleep(self.cooldown_sleep)

                items.setdefault("Findings", {})[subproduct] = findings
                total_done += 1

            shop_count += 1

            # ETA: remaining jobs * sub_sleep + remaining cooldowns * cooldown_sleep
            remaining_jobs = total_jobs - total_done
            remaining_shops = total_shops - shop_count
            remaining_cooldowns = remaining_shops // self.cooldown_every
            eta_seconds = (remaining_jobs * self.sub_sleep) + (remaining_cooldowns * self.cooldown_sleep)
            eta_min = round(eta_seconds / 60, 1)

            pct = (total_done / total_jobs) * 100
            print(f"Shops done: {shop_count} | Progress: {pct:.1f}% | ETA: {eta_min} min")

        elapsed = (time.time() - start) / 60
        print(f"Sub-product scrape finished in {elapsed:.1f} minutes.")

        self._save_json(self.final_data, self.productsearch_path)
        return self.final_data

    def run(self) -> dict:
        """Run the full pipeline end-to-end."""
        self.scrape_main()
        self.filter_products()
        try: 
            self.build_subproduct_links()
            self.scrape_subproducts()
        except Exception as e:
            print(f"Error during sub-product processing: {e}")
        print("Pipeline complete.")

        output = self.final_data if self.final_data else self.subproduct_links
        return output
    
    
if __name__ == "__main__":
    # With LLM filtering (default)
    searcher = ShopeeProductSearch(
        product="PSU",
        product_list=[],
        product_description="PSU suitable for GPU / Graphic card",
        use_llm=True,
    )
    results = searcher.run()
