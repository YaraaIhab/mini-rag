from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLAlchemyBase):

    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4, nullable=False)
    
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)
    asset_config = Column(JSONB, nullable=True)


    asset_project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)  # Foreign key to projects.project_id
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    

    project = relationship("Project", back_populates="assets")  # Relationship to Project model (bidirectional)
    chunks = relationship("DataChunk", back_populates="asset")  # Relationship to DataChunk model (bidirectional) 

    __table_args__ = (
        # Index to improve query performance when searching by project ID (faster)
    Index('ix_asset_project_id', asset_project_id),
    Index('ix_asset_type', asset_type)
    )



    
    