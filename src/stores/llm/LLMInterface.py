from abc import ABC, abstractmethod

class LLMInterface(ABC):

    @abstractmethod  # abstract methods must be implemented by child classes
    def set_generation_model(self, model_id: str):
        """Set the generation model to be used for generating responses. This method should be implemented by the child class to set the appropriate model based on the provided model_id."""
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Set the embedding model to be used for generating embeddings. This method should be implemented by the child class to set the appropriate model based on the provided model_id."""
        pass

    @abstractmethod
    def generate_response(self, prompt: str, chat_history: list = None, max_output_tokens: int= None, temperature: float = None):
        """Generate a response based on the provided prompt and any additional parameters. This method should be implemented by the child class to generate a response using the set generation model."""
        pass

    @abstractmethod
    def embed_text(self, input_text, document_type:str = None):
        """Generate an embedding based on the provided input text. This method should be implemented by the child class to generate an embedding using the set embedding model."""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: list):
        """Construct a prompt based on the provided query and context chunks. This method should be implemented by the child class to construct a prompt that can be used for generating a response."""
        pass