from ..LLMEnums import OpenAIEnum
from ..LLMInterface import LLMInterface
from openai import OpenAI
import logging
from typing import List, Union


class OpenAIProvider(LLMInterface):

    def __init__(self, api_key: str, api_url: str = None,
                 default_input_max_characters: int = 1000,
                   default_output_max_tokens: int = 1000, 
                   default_temperature: float = 0.1):
                 #default_input_max_charachter is the max number of characters that the provider can handle as input, this is used to truncate the input if it exceeds the limit. This is important to prevent errors and cost.
        
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_output_max_tokens = default_output_max_tokens
        self.default_temperature = default_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None # 3ashan el vector db byehtag el size 

        if self.api_url and len(self.api_url):
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_url)
        else:
            self.client = OpenAI(api_key=self.api_key)

        self.enums = OpenAIEnum

        self.logger = logging.getLogger(__name__)
    
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip() # truncate the input text to the default max characters and remove leading and trailing whitespace
    
    def generate_response(self, prompt: str, chat_history: list = [], max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens is not None else self.default_output_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature

        chat_history.append(self.construct_prompt(prompt = prompt, role = OpenAIEnum.USER.value))
        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message or not response.choices[0].message.content:
            self.logger.error("Error while generating response with OpenAI")
            return None
        
        generated_response = response.choices[0].message.content
        return generated_response

    def embed_text(self, input_text: Union[str, List[str]], document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI client is not initialized.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None

        if isinstance(input_text, str):
            input_text = [input_text]

        response = self.client.embeddings.create(
            model=self.embedding_model_id,
            input=input_text
        )

        if not response or not response.data or len(response.data) == 0:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        return [data.embedding for data in response.data]
          
    
    def construct_prompt(self, prompt: str, role: list):
        return {
            "role": role,
            "content": prompt
        }