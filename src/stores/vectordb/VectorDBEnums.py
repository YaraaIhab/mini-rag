from enum import Enum

class VectorDBEnum(str, Enum):
    QDRANT = "QDRANT"

class DistanceMethodEnum(str, Enum):
    COSINE = "cosine"
    DOT = "dot"