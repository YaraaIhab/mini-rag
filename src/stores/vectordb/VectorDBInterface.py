from abc import ABC, abstractmethod
from typing import List
from models.db_schemes import RetrievedDocument

class VectorDBInterface(ABC):
    @abstractmethod  # abstract methods must be implemented by child classes
    def connect(self):
        """Establish a connection to the vector database. This method should be implemented by the child class to handle the specific connection logic for the chosen vector database."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the connection to the vector database. This method can be implemented by the child class to handle any necessary cleanup when disconnecting from the database."""
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """Check if a collection with the given name exists in the vector database. This method should be implemented by the child class to query the database for the existence of the specified collection."""
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        """List all collections in the vector database. This method should be implemented by the child class to retrieve and return a list of all collections available in the database."""
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str)-> dict:
        """Retrieve information about a specific collection in the vector database. This method should be implemented by the child class to query the database for details about the specified collection, such as its schema, number of vectors, and other relevant metadata."""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        """Delete a specific collection from the vector database. This method should be implemented by the child class to handle the logic for removing the specified collection and its associated data from the database."""
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        """Create a new collection in the vector database. This method should be implemented by the child class to handle the logic for creating a new collection with the specified name and embedding size, which will determine the dimensionality of the vectors stored in that collection."""
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, text: str, vector: list, 
                   metadata: dict= None, record_id: str = None):
        """Insert a single vector into a specified collection in the vector database. This method should be implemented by the child class to handle the logic for adding a new vector along with its associated metadata to the specified collection."""
        pass

    @abstractmethod
    def insert_many(self, collection_name: str, texts: list, vectors: list, 
                    metadata: List = None, record_ids: list = None, batch_size: int = 50):
        """Insert multiple vectors into a specified collection in the vector database. This method should be implemented by the child class to handle the logic for adding multiple new vectors along with their associated metadata to the specified collection."""
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list,limit: int) -> List[RetrievedDocument]:
        """Search for similar vectors in a specified collection based on a given query vector. This method should be implemented by the child class to handle the logic for performing a similarity search in the specified collection and returning the top K most similar vectors along with their associated metadata."""
        pass