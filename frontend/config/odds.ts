/**
 * Configuration des Objectifs de Développement Durable (ODD)
 * et leur association par secteur
 */

export interface ODD {
  id: number;
  label: string;
  description: string;
  color: string;
}

export const allODDs: ODD[] = [
  { id: 1, label: "ODD 1 - Pas de pauvreté", description: "Éliminer la pauvreté sous toutes ses formes", color: "#E5243B" },
  { id: 2, label: "ODD 2 - Faim zéro", description: "Éliminer la faim et assurer la sécurité alimentaire", color: "#DDA63A" },
  { id: 3, label: "ODD 3 - Bonne santé et bien-être", description: "Permettre à tous de vivre en bonne santé", color: "#4C9F38" },
  { id: 4, label: "ODD 4 - Éducation de qualité", description: "Assurer une éducation de qualité pour tous", color: "#C5192D" },
  { id: 5, label: "ODD 5 - Égalité entre les sexes", description: "Parvenir à l'égalité des sexes", color: "#FF3A21" },
  { id: 6, label: "ODD 6 - Eau propre et assainissement", description: "Garantir l'accès à l'eau et à l'assainissement", color: "#26BDE2" },
  { id: 7, label: "ODD 7 - Énergie propre et d'un coût abordable", description: "Garantir l'accès à une énergie durable", color: "#FCC30B" },
  { id: 8, label: "ODD 8 - Travail décent et croissance économique", description: "Promouvoir une croissance économique durable", color: "#A21942" },
  { id: 9, label: "ODD 9 - Industrie, innovation et infrastructure", description: "Bâtir une infrastructure résiliente", color: "#FD6925" },
  { id: 10, label: "ODD 10 - Inégalités réduites", description: "Réduire les inégalités dans les pays et d'un pays à l'autre", color: "#DD1367" },
  { id: 11, label: "ODD 11 - Villes et communautés durables", description: "Rendre les villes inclusives et durables", color: "#FD9D24" },
  { id: 12, label: "ODD 12 - Consommation et production responsables", description: "Établir des modes de consommation durables", color: "#BF8B2E" },
  { id: 13, label: "ODD 13 - Mesures relatives à la lutte contre les changements climatiques", description: "Lutter contre les changements climatiques", color: "#3F7E44" },
  { id: 14, label: "ODD 14 - Vie aquatique", description: "Conserver et exploiter durablement les océans", color: "#0A97D9" },
  { id: 15, label: "ODD 15 - Vie terrestre", description: "Préserver et restaurer les écosystèmes terrestres", color: "#56C02B" },
  { id: 16, label: "ODD 16 - Paix, justice et institutions efficaces", description: "Promouvoir des sociétés pacifiques et inclusives", color: "#00689D" },
  { id: 17, label: "ODD 17 - Partenariats pour la réalisation des objectifs", description: "Renforcer les moyens de mise en œuvre", color: "#19486A" }
];

// ODD recommandés par secteur (IDs des ODD)
export const oddParSecteur: Record<string, number[]> = {
  "Agriculture": [1, 2, 8, 12, 13, 15],
  "Sylviculture (exploitation forestière)": [12, 13, 15],
  "Pêche et aquaculture": [2, 14, 12],
  "Industries extractives": [8, 9, 12, 13],
  "Industrie et transformation": [8, 9, 12, 13],
  "Commerce et distribution": [8, 12],
  "Éducation et formation": [4, 5, 8],
  "Santé": [3, 5, 10],
  "Énergie et environnement": [7, 9, 12, 13],
  "Transport et logistique": [9, 11, 13],
  "Technologie et innovation": [8, 9, 17],
  "Finance et services": [1, 8, 10],
  "BTP / Immobilier": [9, 11, 12],
  "Tourisme et hôtellerie": [8, 12, 14],
  "Communication et médias": [4, 9, 16]
};

// Fonction pour obtenir les ODD recommandés pour un secteur
export function getODDsForSecteur(secteur: string): ODD[] {
  const oddIds = oddParSecteur[secteur] || [8, 12, 13]; // Défaut
  return allODDs.filter(odd => oddIds.includes(odd.id));
}

// Fonction pour obtenir un ODD par son ID
export function getODDById(id: number): ODD | undefined {
  return allODDs.find(odd => odd.id === id);
}

