/**
 * Configuration des secteurs d'activité et leurs offres associées
 */

export const secteursEtOffres: Record<string, string[]> = {
  "Agriculture": [
    "Production agricole",
    "Transformation agroalimentaire",
    "Distribution de produits agricoles",
    "Conseil et services agricoles",
    "Équipements agricoles",
    "Semences et intrants",
    "Agriculture biologique",
    "Agroforesterie"
  ],
  "Sylviculture (exploitation forestière)": [
    "Exploitation forestière durable",
    "Bois d'œuvre",
    "Produits forestiers non ligneux",
    "Reboisement et reforestation",
    "Certification forestière"
  ],
  "Pêche et aquaculture": [
    "Pêche artisanale",
    "Pêche industrielle",
    "Aquaculture",
    "Transformation de produits de la mer",
    "Distribution de produits halieutiques"
  ],
  "Industries extractives": [
    "Extraction minière",
    "Extraction pétrolière et gazière",
    "Carrières et matériaux de construction",
    "Traitement et raffinage",
    "Services aux industries extractives"
  ],
  "Industrie et transformation": [
    "Agroalimentaire",
    "Textile et habillement",
    "Chimie et pharmacie",
    "Métallurgie",
    "Électronique et électrique",
    "Plastique et caoutchouc",
    "Bois et papier"
  ],
  "Commerce et distribution": [
    "Commerce de gros",
    "Commerce de détail",
    "E-commerce",
    "Import-export",
    "Distribution spécialisée",
    "Grande distribution"
  ],
  "Éducation et formation": [
    "Enseignement primaire et secondaire",
    "Enseignement supérieur",
    "Formation professionnelle",
    "E-learning",
    "Édition éducative"
  ],
  "Santé": [
    "Hôpitaux et cliniques",
    "Pharmacie",
    "Laboratoires d'analyses",
    "Équipements médicaux",
    "Télémédecine",
    "Assurance santé"
  ],
  "Énergie et environnement": [
    "Énergies renouvelables",
    "Production d'électricité",
    "Distribution d'énergie",
    "Efficacité énergétique",
    "Gestion des déchets",
    "Traitement de l'eau",
    "Services environnementaux"
  ],
  "Transport et logistique": [
    "Transport routier",
    "Transport maritime",
    "Transport aérien",
    "Transport ferroviaire",
    "Logistique et entreposage",
    "Livraison du dernier kilomètre"
  ],
  "Technologie et innovation": [
    "Développement logiciel",
    "Services IT",
    "Intelligence artificielle",
    "Fintech",
    "Agritech",
    "Healthtech",
    "Edtech",
    "Cybersécurité"
  ],
  "Finance et services": [
    "Banque",
    "Microfinance",
    "Assurance",
    "Gestion d'actifs",
    "Services de paiement",
    "Conseil financier"
  ],
  "BTP / Immobilier": [
    "Construction résidentielle",
    "Construction commerciale",
    "Travaux publics",
    "Promotion immobilière",
    "Gestion immobilière",
    "Matériaux de construction"
  ],
  "Tourisme et hôtellerie": [
    "Hôtellerie",
    "Restauration",
    "Agences de voyage",
    "Écotourisme",
    "Tourisme culturel",
    "Loisirs et divertissement"
  ],
  "Communication et médias": [
    "Télécommunications",
    "Médias traditionnels",
    "Médias digitaux",
    "Publicité et marketing",
    "Production audiovisuelle",
    "Édition"
  ]
};

export const secteursList = Object.keys(secteursEtOffres);

