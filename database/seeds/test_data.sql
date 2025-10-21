-- Africa Strategy - Données de test
-- Développé par Ousmane Dicko

-- Insertion d'utilisateurs de test
INSERT INTO users (email, password_hash, first_name, last_name, company_name, phone, country, city, sector, company_size, is_active, is_verified) VALUES
('jean.kouassi@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2', 'Jean', 'Kouassi', 'AgriTech Côte d''Ivoire', '+225 07 12 34 56 78', 'Côte d''Ivoire', 'Abidjan', 'Agriculture', 'PME', TRUE, TRUE),
('fatou.diallo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2', 'Fatou', 'Diallo', 'Textile Sénégal', '+221 77 12 34 56 78', 'Sénégal', 'Dakar', 'Textile', 'Grande entreprise', TRUE, TRUE),
('kwame.asante@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8Kz2', 'Kwame', 'Asante', 'Tech Ghana', '+233 24 12 34 56 78', 'Ghana', 'Accra', 'Technologie', 'PME', TRUE, FALSE);

-- Insertion de questionnaires de test
INSERT INTO questionnaires (user_id, title, description, status, responses, completion_percentage, completed_at) VALUES
(
    (SELECT id FROM users WHERE email = 'jean.kouassi@example.com'),
    'Questionnaire ESG Agriculture',
    'Évaluation de la durabilité pour une entreprise agricole en Côte d''Ivoire',
    'completed',
    '{
        "secteur": "Agriculture",
        "pays": "Côte d''Ivoire",
        "taille_entreprise": "PME",
        "nombre_employes": 25,
        "chiffre_affaires": 500000000,
        "devise": "FCFA",
        "questions_esg": {
            "environnemental": {
                "gestion_dechets": true,
                "energie_renouvelable": false,
                "eau_conservation": true,
                "biodiversite": false
            },
            "social": {
                "conditions_travail": true,
                "formation_employes": false,
                "diversite": true,
                "sante_securite": true
            },
            "gouvernance": {
                "transparence": false,
                "ethique": true,
                "conformite": true,
                "gestion_risques": false
            }
        }
    }',
    100,
    NOW() - INTERVAL '2 days'
),
(
    (SELECT id FROM users WHERE email = 'fatou.diallo@example.com'),
    'Questionnaire ESG Textile',
    'Évaluation de la durabilité pour une entreprise textile au Sénégal',
    'completed',
    '{
        "secteur": "Textile",
        "pays": "Sénégal",
        "taille_entreprise": "Grande entreprise",
        "nombre_employes": 150,
        "chiffre_affaires": 2000000000,
        "devise": "FCFA",
        "questions_esg": {
            "environnemental": {
                "gestion_dechets": true,
                "energie_renouvelable": true,
                "eau_conservation": true,
                "biodiversite": true
            },
            "social": {
                "conditions_travail": true,
                "formation_employes": true,
                "diversite": true,
                "sante_securite": true
            },
            "gouvernance": {
                "transparence": true,
                "ethique": true,
                "conformite": true,
                "gestion_risques": true
            }
        }
    }',
    100,
    NOW() - INTERVAL '1 day'
);

-- Insertion d'analyses PESTEL de test
INSERT INTO pestel_analyses (questionnaire_id, political_score, economic_score, social_score, technological_score, environmental_score, legal_score, overall_score, analysis_details, recommendations) VALUES
(
    (SELECT id FROM questionnaires WHERE title = 'Questionnaire ESG Agriculture'),
    7, 6, 8, 5, 4, 6, 6.0,
    '{
        "politique": {
            "score": 7,
            "analyse": "Stabilité politique relative en Côte d''Ivoire avec des réformes agricoles favorables",
            "facteurs_positifs": ["Politiques agricoles favorables", "Stabilité gouvernementale"],
            "facteurs_negatifs": ["Corruption persistante", "Bureaucratie"]
        },
        "economique": {
            "score": 6,
            "analyse": "Économie en croissance mais dépendante des matières premières",
            "facteurs_positifs": ["Croissance économique", "Investissements étrangers"],
            "facteurs_negatifs": ["Dépendance cacao", "Inflation"]
        },
        "social": {
            "score": 8,
            "analyse": "Population jeune et dynamique avec une forte culture entrepreneuriale",
            "facteurs_positifs": ["Population jeune", "Esprit entrepreneurial"],
            "facteurs_negatifs": ["Chômage élevé", "Inégalités"]
        },
        "technologique": {
            "score": 5,
            "analyse": "Adoption technologique limitée dans le secteur agricole",
            "facteurs_positifs": ["Mobile money", "Fintech"],
            "facteurs_negatifs": ["Infrastructure limitée", "Formation insuffisante"]
        },
        "environnemental": {
            "score": 4,
            "analyse": "Défis environnementaux majeurs avec déforestation et changement climatique",
            "facteurs_positifs": ["Conscience environnementale croissante"],
            "facteurs_negatifs": ["Déforestation", "Changement climatique", "Pollution"]
        },
        "legal": {
            "score": 6,
            "analyse": "Cadre légal en amélioration mais complexité administrative",
            "facteurs_positifs": ["Réformes en cours", "Protection des investissements"],
            "facteurs_negatifs": ["Complexité administrative", "Corruption"]
        }
    }',
    '[
        {
            "categorie": "Environnemental",
            "priorite": "Haute",
            "action": "Mettre en place un système de gestion des déchets agricoles",
            "cout_estime": 5000000,
            "duree_estimee": 30,
            "impact_score": 3
        },
        {
            "categorie": "Technologique",
            "priorite": "Moyenne",
            "action": "Formation des employés aux nouvelles technologies agricoles",
            "cout_estime": 2000000,
            "duree_estimee": 60,
            "impact_score": 2
        }
    ]'
);

-- Insertion d'analyses ESG de test
INSERT INTO esg_analyses (questionnaire_id, environmental_score, social_score, governance_score, overall_score, environmental_details, social_details, governance_details, recommendations) VALUES
(
    (SELECT id FROM questionnaires WHERE title = 'Questionnaire ESG Agriculture'),
    35, 60, 50, 48,
    '{
        "score": 35,
        "analyse": "Performance environnementale faible avec des opportunités d''amélioration significatives",
        "points_forts": ["Gestion basique des déchets"],
        "points_faibles": ["Pas d''énergie renouvelable", "Pas de protection biodiversité"],
        "recommandations": [
            "Installer des panneaux solaires",
            "Mettre en place un programme de conservation de la biodiversité",
            "Optimiser la gestion de l''eau"
        ]
    }',
    '{
        "score": 60,
        "analyse": "Performance sociale correcte avec de bonnes conditions de travail",
        "points_forts": ["Bonnes conditions de travail", "Diversité respectée"],
        "points_faibles": ["Formation des employés insuffisante"],
        "recommandations": [
            "Programme de formation continue",
            "Amélioration des avantages sociaux",
            "Système de feedback employés"
        ]
    }',
    '{
        "score": 50,
        "analyse": "Gouvernance moyenne avec des axes d''amélioration",
        "points_forts": ["Éthique respectée", "Conformité réglementaire"],
        "points_faibles": ["Transparence limitée", "Gestion des risques"],
        "recommandations": [
            "Améliorer la transparence financière",
            "Mettre en place un système de gestion des risques",
            "Code de conduite plus strict"
        ]
    }',
    '[
        {
            "categorie": "Environnemental",
            "priorite": "Critique",
            "action": "Transition vers l''énergie renouvelable",
            "cout_estime": 15000000,
            "duree_estimee": 90,
            "impact_score": 5,
            "description": "Installation de panneaux solaires pour réduire la dépendance aux énergies fossiles"
        },
        {
            "categorie": "Social",
            "priorite": "Haute",
            "action": "Programme de formation des employés",
            "cout_estime": 3000000,
            "duree_estimee": 60,
            "impact_score": 3,
            "description": "Formation continue sur les pratiques agricoles durables"
        }
    ]'
);

-- Insertion de roadmaps de test
INSERT INTO roadmaps (user_id, title, description, current_phase, progress_percentage, phases, milestones) VALUES
(
    (SELECT id FROM users WHERE email = 'jean.kouassi@example.com'),
    'Roadmap Durabilité AgriTech',
    'Plan d''action pour améliorer la durabilité de l''entreprise agricole',
    'quick_wins',
    25,
    '[
        {
            "id": "diagnostic",
            "name": "Diagnostic",
            "status": "completed",
            "description": "Analyse de la situation actuelle"
        },
        {
            "id": "quick_wins",
            "name": "Quick Wins",
            "status": "in_progress",
            "description": "Actions rapides à impact immédiat"
        },
        {
            "id": "transformation",
            "name": "Transformation",
            "status": "locked",
            "description": "Changements structurels majeurs"
        }
    ]',
    '[
        {
            "id": "milestone_1",
            "name": "Diagnostic complet",
            "status": "completed",
            "date": "2024-01-15"
        },
        {
            "id": "milestone_2",
            "name": "Premières améliorations",
            "status": "in_progress",
            "date": "2024-02-15"
        }
    ]'
);

-- Insertion d'étapes de roadmap de test
INSERT INTO roadmap_steps (roadmap_id, title, description, phase, order_index, status, priority, estimated_cost, estimated_duration_days) VALUES
(
    (SELECT id FROM roadmaps WHERE title = 'Roadmap Durabilité AgriTech'),
    'Mise en place du tri des déchets',
    'Installer un système de tri des déchets agricoles',
    'quick_wins',
    1,
    'in_progress',
    'high',
    5000000,
    30
),
(
    (SELECT id FROM roadmaps WHERE title = 'Roadmap Durabilité AgriTech'),
    'Formation des employés',
    'Former l''équipe aux pratiques agricoles durables',
    'quick_wins',
    2,
    'pending',
    'medium',
    2000000,
    60
),
(
    (SELECT id FROM roadmaps WHERE title = 'Roadmap Durabilité AgriTech'),
    'Installation panneaux solaires',
    'Transition vers l''énergie renouvelable',
    'transformation',
    3,
    'locked',
    'critical',
    15000000,
    90
);

-- Insertion de scores de test
INSERT INTO scores (user_id, score_type, score_value, max_score, percentage, badge_level, details) VALUES
(
    (SELECT id FROM users WHERE email = 'jean.kouassi@example.com'),
    'esg',
    48.0,
    100.0,
    48.0,
    'bronze',
    '{
        "environmental": 35,
        "social": 60,
        "governance": 50,
        "trend": "stable",
        "improvement_potential": "high"
    }'
),
(
    (SELECT id FROM users WHERE email = 'jean.kouassi@example.com'),
    'pestel',
    6.0,
    10.0,
    60.0,
    'bronze',
    '{
        "political": 7,
        "economic": 6,
        "social": 8,
        "technological": 5,
        "environmental": 4,
        "legal": 6
    }'
);
