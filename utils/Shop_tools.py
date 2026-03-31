import re
import urllib.parse
import emoji

class ProductScraper:
            
            def __init__(
                        self,
                        items,
            ):
                self.items = items

            def scrapping_contents(self):
                products = {}
                for i, item in enumerate(self.items):
                    # --- URL & IDs (your existing logic) ---
                    a_tag = item.select_one("a.contents")
                    href = a_tag["href"] if a_tag else None
                    full_url = f"https://shopee.com.my{href}" if href else None

                    name_match = re.search(r"/(.*?)-i", href) if href else None
                    shopid_match = re.search(r"-i\.(\d+)\.(\d+)", href) if href else None

                    raw_name = name_match.group(1) if name_match else None
                    shop_id = shopid_match.group(1) if shopid_match else None
                    item_id = shopid_match.group(2) if shopid_match else None

                    if raw_name:
                        name = re.sub(r'-', " ", raw_name)
                        name = urllib.parse.unquote(name)
                        name = emoji.replace_emoji(name, replace=" ").strip()
                    else:
                        name = None

                    # --- Price ---
                    price_rm = item.select_one("span.text-base\\/5")
                    price = f"{price_rm.get_text(strip=True)}" if price_rm else None

                    # --- Rating & Sold ---
                    rating = item.select_one(".text-shopee-black87.text-xs\\/sp14")
                    sold = item.select_one(".truncate.text-shopee-black87.text-xs")
                    
                    # --- Location ---
                    location = item.select_one("[aria-label^='location-']")
                    loc_text = location["aria-label"].replace("location-", "") if location else None

                    products[i + 1] = {
                        "title": name,
                        "url": full_url,
                        "shop_id": shop_id,
                        "item_id": item_id,
                        "price": price,
                        "rating": rating.get_text(strip=True) if rating else None,
                        "sold": sold.get_text(strip=True) if sold else None,
                        "location": loc_text,
                    }
                return products
            
           
                 
                 
            
    
                 
                 