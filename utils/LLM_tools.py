from utils.LLM_setup import LLM
import json


class LLM_toolset:
    def __init__(self, 
                 maindata, 
                 products
            
    ):
        self.maindata = maindata
        self.products = products
        
    def LLM_filter(self):
        DS = LLM(self.maindata, self.products)
        LLM_results = DS.output()
        product_list = json.loads(LLM_results)
        return product_list 