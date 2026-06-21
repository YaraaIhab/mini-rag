from enum import Enum

class VectorDBEnum(str, Enum):
    QDRANT = "QDRANT"
    PGVECTOR = "PGVECTOR"

class DistanceMethodEnum(str, Enum):
    COSINE = "cosine"
    DOT = "dot"

class PgvectorTableSchemaEnum(str, Enum):
    ID = "id"
    TEXT = "text"
    VECTOR = "vector"
    CHUNK_ID = "chunk_id"
    METADATA = "metadata"
    _PREFIX = "pgvector"

class PgvectorDistanceMethodEnum(str, Enum):
    COSINE = "vector_cosine_ops"
    DOT = "vector_l2_ops"

class PgvectorIndexTypeEnum(str, Enum):
    IVFFLAT = "ivfflat"
    HNSW = "hnsw"
 