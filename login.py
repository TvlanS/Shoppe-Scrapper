from utils.botsauce_tools import ScrapeShopee
import json
import os
from datetime import datetime
import pyprojroot
import time
from utils.LLM_tools import LLM_toolset
 

url = rf"https://shopee.com.my/search?keyword=y"

login = ScrapeShopee(url)
login.run_login()

