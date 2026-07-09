import uuid
import enum
from sqlalchemy import String, Enum, ForeignKey, LargeBinary, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy import Integer
from app.db.base import Base
from pgvector.sqlalchemy import Vector

class TeamRole(str, enum.Enum):
    admin = "admin"
    business_analyst = "business_analyst"
    data_scientist = "data_scientist"
    project_manager = "project_manager"
    consultant = "consultant"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(384), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    clients: Mapped[list["Client"]] = relationship(back_populates="organization")
    team_members: Mapped[list["TeamMember"]] = relationship(back_populates="organization")


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[TeamRole] = mapped_column(Enum(TeamRole), nullable=False)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)

    organization: Mapped["Organization"] = relationship(back_populates="team_members")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="clients")
    projects: Mapped[list["Project"]] = relationship(back_populates="client")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    
    client: Mapped["Client"] = relationship(back_populates="projects")
    documents: Mapped[list["Document"]] = relationship(back_populates="project")
    reports: Mapped[list["Report"]] = relationship(back_populates="project")


class Document(Base):
    """
    Everything lives in Postgres — no disk/S3 storage.
    raw_content holds the original file bytes (PDF, DOCX, image, etc.) exactly
    as uploaded. extracted_text holds the parsed-out plain text used later for
    RAG chunking/embeddings — kept separate so extraction can be re-run later
    without needing the file to be re-uploaded.
    """
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    content_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "application/pdf"
    raw_content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    embedding_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")

    project: Mapped["Project"] = relationship(back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class Report(Base):
    """
    Generated consulting report text, stored directly in Postgres —
    this is the LangGraph report_generation node's output.
    """
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    case_thread_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="reports")




