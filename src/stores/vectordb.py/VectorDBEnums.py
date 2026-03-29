from enum import Enum

class VectorDBEnum(str, Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnum(str, Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot_product"