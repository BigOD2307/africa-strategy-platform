"""
Modèles de base de données pour Africa Strategy
Développé par Ousmane Dicko
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, DECIMAL, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class EntrepreneurConfiguration(Base):
    """Modèle configuration entrepreneur"""
    __tablename__ = "entrepreneur_configurations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    secteur = Column(String(255), nullable=False)
    zone_geographique = Column(String(255), nullable=False)
    profil_organisation = Column(String(255), nullable=False)
    biens_services = Column(JSON, nullable=False, default=[])
    autres_biens_services = Column(Text)
    pays_installation = Column(String(255), nullable=False)
    objectifs_dd = Column(JSON, nullable=False, default=[])
    positionnement_strategique = Column(Text, nullable=False)
    vision_organisation = Column(Text, nullable=False)
    mission_organisation = Column(Text, nullable=False)
    projets_significatifs = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    """Modèle utilisateur (entrepreneur)"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255))
    phone = Column(String(20))
    country = Column(String(100), nullable=False, index=True)
    city = Column(String(100))
    sector = Column(String(100), nullable=False, index=True)
    company_size = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relations
    questionnaires = relationship("Questionnaire", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("ChatbotConversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Questionnaire(Base):
    """Modèle questionnaire"""
    __tablename__ = "questionnaires"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="draft", index=True)  # draft, completed, analyzed
    responses = Column(JSON, nullable=False, default={})
    completion_percentage = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relations
    user = relationship("User", back_populates="questionnaires")
    pestel_analysis = relationship("PestelAnalysis", back_populates="questionnaire", uselist=False, cascade="all, delete-orphan")
    esg_analysis = relationship("EsgAnalysis", back_populates="questionnaire", uselist=False, cascade="all, delete-orphan")


class PestelAnalysis(Base):
    """Modèle analyse PESTEL"""
    __tablename__ = "pestel_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey("questionnaires.id"), nullable=False, index=True)
    political_score = Column(Integer)
    economic_score = Column(Integer)
    social_score = Column(Integer)
    technological_score = Column(Integer)
    environmental_score = Column(Integer)
    legal_score = Column(Integer)
    overall_score = Column(DECIMAL(3, 1))
    analysis_details = Column(JSON, nullable=False, default={})
    recommendations = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    questionnaire = relationship("Questionnaire", back_populates="pestel_analysis")


class EsgAnalysis(Base):
    """Modèle analyse ESG"""
    __tablename__ = "esg_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    questionnaire_id = Column(UUID(as_uuid=True), ForeignKey("questionnaires.id"), nullable=False, index=True)
    environmental_score = Column(Integer)
    social_score = Column(Integer)
    governance_score = Column(Integer)
    overall_score = Column(Integer)
    environmental_details = Column(JSON, nullable=False, default={})
    social_details = Column(JSON, nullable=False, default={})
    governance_details = Column(JSON, nullable=False, default={})
    recommendations = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    questionnaire = relationship("Questionnaire", back_populates="esg_analysis")


class Roadmap(Base):
    """Modèle roadmap"""
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    current_phase = Column(String(100), default="diagnostic")
    progress_percentage = Column(Integer, default=0)
    phases = Column(JSON, nullable=False, default=[])
    milestones = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="roadmaps")
    steps = relationship("RoadmapStep", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapStep(Base):
    """Modèle étape de roadmap"""
    __tablename__ = "roadmap_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    phase = Column(String(100), nullable=False)
    order_index = Column(Integer, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, in_progress, completed, blocked
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    estimated_cost = Column(DECIMAL(10, 2))
    estimated_duration_days = Column(Integer)
    actual_cost = Column(DECIMAL(10, 2))
    actual_duration_days = Column(Integer)
    completion_date = Column(DateTime(timezone=True))
    documents = Column(JSON, nullable=False, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    roadmap = relationship("Roadmap", back_populates="steps")
    documents_rel = relationship("Document", back_populates="roadmap_step", cascade="all, delete-orphan")


class Score(Base):
    """Modèle score"""
    __tablename__ = "scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    score_type = Column(String(50), nullable=False, index=True)  # pestel, esg, overall
    score_value = Column(DECIMAL(5, 2), nullable=False)
    max_score = Column(DECIMAL(5, 2), nullable=False)
    percentage = Column(DECIMAL(5, 2), nullable=False)
    badge_level = Column(String(20))  # bronze, silver, gold, platinum
    details = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="scores")


class ChatbotConversation(Base):
    """Modèle conversation chatbot"""
    __tablename__ = "chatbot_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False)
    messages = Column(JSON, nullable=False, default=[])
    context = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    user = relationship("User", back_populates="conversations")


class Document(Base):
    """Modèle document"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    roadmap_step_id = Column(UUID(as_uuid=True), ForeignKey("roadmap_steps.id"), index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100), nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_status = Column(String(50), default="uploaded")  # uploaded, processing, processed, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relations
    user = relationship("User", back_populates="documents")
    roadmap_step = relationship("RoadmapStep", back_populates="documents_rel")
