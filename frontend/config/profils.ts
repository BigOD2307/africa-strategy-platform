/**
 * Configuration des profils d'organisation
 * Chaque profil a ses propres modules d'analyse et objectifs
 */

export interface ProfilConfig {
  id: string;
  label: string;
  description: string;
  icon: string;
  modules: string[];
  objectifs: string[];
  champsSpecifiques?: string[];
}

export const profilsConfig: ProfilConfig[] = [
  {
    id: "entrepreneur",
    label: "Entrepreneur en lancement",
    description: "Projet en phase de création ou de démarrage",
    icon: "🚀",
    modules: ["pestel", "marche", "chaine_valeur", "odd", "synthese"],
    objectifs: [
      "Valider l'opportunité de marché",
      "Identifier les facteurs de succès",
      "Structurer le business model durable",
      "Anticiper les risques"
    ]
  },
  {
    id: "pme",
    label: "PME / TPE",
    description: "Petite ou moyenne entreprise déjà opérationnelle",
    icon: "🏢",
    modules: ["pestel", "risques_climat", "marche", "chaine_valeur", "odd", "reglementaire", "synthese"],
    objectifs: [
      "Optimiser les opérations",
      "Améliorer la performance ESG",
      "Accéder aux financements verts",
      "Se différencier sur le marché"
    ]
  },
  {
    id: "entreprise_privee",
    label: "Entreprise privée",
    description: "Structure privée de taille moyenne à grande",
    icon: "🏭",
    modules: ["pestel", "risques_climat", "marche", "chaine_valeur", "odd", "reglementaire", "synthese"],
    objectifs: [
      "Transformation durable",
      "Conformité réglementaire ESG",
      "Optimisation de la chaîne de valeur",
      "Reporting extra-financier"
    ]
  },
  {
    id: "entreprise_publique",
    label: "Entreprise publique",
    description: "Structure appartenant à l'État ou collectivité",
    icon: "🏛️",
    modules: ["pestel", "risques_climat", "marche", "chaine_valeur", "odd", "reglementaire", "synthese"],
    objectifs: [
      "Mission de service public durable",
      "Exemplarité environnementale",
      "Impact social territorial",
      "Transparence et gouvernance"
    ]
  },
  {
    id: "banque",
    label: "Banque / Institution financière",
    description: "Établissement bancaire ou de financement",
    icon: "🏦",
    modules: ["pestel", "risques_climat", "marche", "reglementaire", "synthese"],
    objectifs: [
      "Finance durable et verte",
      "Gestion des risques climatiques",
      "Conformité aux taxonomies",
      "Financement de la transition"
    ],
    champsSpecifiques: ["portefeuille_credits", "encours_verts"]
  },
  {
    id: "collectivite",
    label: "Collectivité territoriale",
    description: "Commune, région ou autre entité territoriale",
    icon: "🏘️",
    modules: ["pestel", "risques_climat", "odd", "reglementaire", "synthese"],
    objectifs: [
      "Développement territorial durable",
      "Adaptation au changement climatique",
      "Services publics responsables",
      "Attractivité du territoire"
    ],
    champsSpecifiques: ["population", "superficie", "budget_annuel"]
  },
  {
    id: "ong",
    label: "ONG / Association",
    description: "Organisation non gouvernementale ou associative",
    icon: "🤝",
    modules: ["pestel", "odd", "chaine_valeur", "synthese"],
    objectifs: [
      "Maximiser l'impact social",
      "Mesurer et communiquer l'impact",
      "Pérenniser les financements",
      "Renforcer les partenariats"
    ],
    champsSpecifiques: ["beneficiaires", "zone_intervention"]
  },
  {
    id: "ministere",
    label: "Ministère / Agence publique",
    description: "Institution gouvernementale ou agence de l'État",
    icon: "⚖️",
    modules: ["pestel", "risques_climat", "reglementaire", "odd", "synthese"],
    objectifs: [
      "Politiques publiques durables",
      "Cadre réglementaire ESG",
      "Planification stratégique nationale",
      "Coordination des acteurs"
    ],
    champsSpecifiques: ["perimetre_competences", "budget_programmes"]
  }
];

// Fonction pour obtenir un profil par son ID
export function getProfilById(id: string): ProfilConfig | undefined {
  return profilsConfig.find(profil => profil.id === id);
}

// Fonction pour obtenir les modules d'analyse pour un profil
export function getModulesForProfil(profilId: string): string[] {
  const profil = getProfilById(profilId);
  return profil?.modules || ["pestel", "marche", "odd", "synthese"];
}

// Labels des modules pour l'affichage
export const modulesLabels: Record<string, string> = {
  pestel: "PESTEL+",
  risques_climat: "Risques Climat",
  marche: "Marché & Concurrence",
  chaine_valeur: "Chaîne de Valeur",
  odd: "Modèles Durables & ODD",
  reglementaire: "Cadre Réglementaire",
  synthese: "Synthèse Stratégique"
};

