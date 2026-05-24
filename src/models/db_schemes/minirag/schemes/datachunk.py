from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from pydantic import BaseModel

class DataChunk(SQLAlchemyBase):

    __tablename__ = "chunks"

    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_order = Column(Integer, nullable=False)

    chunk_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)  # Foreign key to projects.project_id
    chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)  # Foreign key to assets.asset_id

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    project = relationship("Project", back_populates="chunks")  # Relationship to Project model (bidirectional)
    asset = relationship("Asset", back_populates="chunks")  # Relationship to Asset model (bidirectional)

    __table_args__ = (
    # Index to improve query performance when searching by project ID (faster)
    Index('ix_chunk_project_id', chunk_project_id),
    Index('ix_chunk_asset_id', chunk_asset_id)
    )

class RetrievedDocument(BaseModel):
# schema for retrived documents from the db (3ashan matala3sh kol el output el tale3 w atala3 el text wl score bas)
    text: str
    score: float