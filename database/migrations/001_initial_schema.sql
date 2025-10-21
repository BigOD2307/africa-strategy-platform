-- Africa Strategy Database Schema
-- Développé par Ousmane Dicko

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table de configuration entrepreneur
CREATE TABLE IF NOT EXISTS entrepreneur_configurations (
    id SERIAL PRIMARY KEY,
    secteur VARCHAR(255) NOT NULL,
    zone_geographique VARCHAR(255) NOT NULL,
    profil_organisation VARCHAR(255) NOT NULL,
    biens_services JSONB NOT NULL DEFAULT '[]'::jsonb,
    autres_biens_services TEXT,
    pays_installation VARCHAR(255) NOT NULL,
    objectifs_dd JSONB NOT NULL DEFAULT '[]'::jsonb,
    positionnement_strategique TEXT NOT NULL,
    vision_organisation TEXT NOT NULL,
    mission_organisation TEXT NOT NULL,
    projets_significatifs TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour la table entrepreneur_configurations
CREATE INDEX IF NOT EXISTS idx_entrepreneur_configurations_created_at ON entrepreneur_configurations(created_at);

-- Trigger pour mettre à jour updated_at sur entrepreneur_configurations
CREATE TRIGGER update_entrepreneur_configurations_updated_at BEFORE UPDATE ON entrepreneur_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Table des utilisateurs (entrepreneurs)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(255),
    phone VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    sector VARCHAR(100) NOT NULL,
    company_size VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Table des questionnaires
CREATE TABLE questionnaires (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'draft', -- draft, completed, analyzed
    responses JSONB NOT NULL DEFAULT '{}',
    completion_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Table des analyses PESTEL
CREATE TABLE pestel_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questionnaire_id UUID NOT NULL REFERENCES questionnaires(id) ON DELETE CASCADE,
    political_score INTEGER CHECK (political_score >= 0 AND political_score <= 10),
    economic_score INTEGER CHECK (economic_score >= 0 AND economic_score <= 10),
    social_score INTEGER CHECK (social_score >= 0 AND social_score <= 10),
    technological_score INTEGER CHECK (technological_score >= 0 AND technological_score <= 10),
    environmental_score INTEGER CHECK (environmental_score >= 0 AND environmental_score <= 10),
    legal_score INTEGER CHECK (legal_score >= 0 AND legal_score <= 10),
    overall_score DECIMAL(3,1),
    analysis_details JSONB NOT NULL DEFAULT '{}',
    recommendations JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des analyses ESG
CREATE TABLE esg_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    questionnaire_id UUID NOT NULL REFERENCES questionnaires(id) ON DELETE CASCADE,
    environmental_score INTEGER CHECK (environmental_score >= 0 AND environmental_score <= 100),
    social_score INTEGER CHECK (social_score >= 0 AND social_score <= 100),
    governance_score INTEGER CHECK (governance_score >= 0 AND governance_score <= 100),
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    environmental_details JSONB NOT NULL DEFAULT '{}',
    social_details JSONB NOT NULL DEFAULT '{}',
    governance_details JSONB NOT NULL DEFAULT '{}',
    recommendations JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des roadmaps
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    current_phase VARCHAR(100) DEFAULT 'diagnostic',
    progress_percentage INTEGER DEFAULT 0,
    phases JSONB NOT NULL DEFAULT '[]',
    milestones JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des étapes de roadmap
CREATE TABLE roadmap_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    phase VARCHAR(100) NOT NULL,
    order_index INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, blocked
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    estimated_cost DECIMAL(10,2),
    estimated_duration_days INTEGER,
    actual_cost DECIMAL(10,2),
    actual_duration_days INTEGER,
    completion_date TIMESTAMP WITH TIME ZONE,
    documents JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des scores
CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_type VARCHAR(50) NOT NULL, -- pestel, esg, overall
    score_value DECIMAL(5,2) NOT NULL,
    max_score DECIMAL(5,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    badge_level VARCHAR(20), -- bronze, silver, gold, platinum
    details JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des conversations chatbot
CREATE TABLE chatbot_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    messages JSONB NOT NULL DEFAULT '[]',
    context JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table des documents uploadés
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    roadmap_step_id UUID REFERENCES roadmap_steps(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    upload_status VARCHAR(50) DEFAULT 'uploaded', -- uploaded, processing, processed, error
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour optimiser les performances
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_country ON users(country);
CREATE INDEX idx_users_sector ON users(sector);
CREATE INDEX idx_questionnaires_user_id ON questionnaires(user_id);
CREATE INDEX idx_questionnaires_status ON questionnaires(status);
CREATE INDEX idx_pestel_analyses_questionnaire_id ON pestel_analyses(questionnaire_id);
CREATE INDEX idx_esg_analyses_questionnaire_id ON esg_analyses(questionnaire_id);
CREATE INDEX idx_roadmaps_user_id ON roadmaps(user_id);
CREATE INDEX idx_roadmap_steps_roadmap_id ON roadmap_steps(roadmap_id);
CREATE INDEX idx_roadmap_steps_status ON roadmap_steps(status);
CREATE INDEX idx_scores_user_id ON scores(user_id);
CREATE INDEX idx_scores_score_type ON scores(score_type);
CREATE INDEX idx_chatbot_conversations_user_id ON chatbot_conversations(user_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);

-- Triggers pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questionnaires_updated_at BEFORE UPDATE ON questionnaires
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pestel_analyses_updated_at BEFORE UPDATE ON pestel_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_esg_analyses_updated_at BEFORE UPDATE ON esg_analyses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roadmaps_updated_at BEFORE UPDATE ON roadmaps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roadmap_steps_updated_at BEFORE UPDATE ON roadmap_steps
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chatbot_conversations_updated_at BEFORE UPDATE ON chatbot_conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
