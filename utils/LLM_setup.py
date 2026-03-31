from openai import OpenAI
from utils.config_setup import Config
import os


Config1 = Config()

class LLM:
    def __init__ (
            self,
            database , product):
        
        self.api_key = Config1.api_key
        self.prompt = Config1.prompt
        self.database = database
        self.product = product
        self.website_url = Config1.website_url
    
    def output(self):
        client = OpenAI(api_key=self.api_key, base_url=self.website_url)

        input_content = f" Desired product is : {self.product} from the following database : /n  {self.database}"

        response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": self.prompt},
                            {"role": "user", "content": input_content},
                        ],
                        response_format={
                            'type': 'json_object'
                        },
                        stream=False
                    )
        content = response.choices[0].message.content
        #print(input_content)
        return content # print will return none even if it appears to show since its only visible in the terminal
    