/**
 * Configuration des pays africains et zones géographiques
 */

export interface Pays {
  nom: string;
  code: string;
  zone: string;
}

export const paysAfricains: Pays[] = [
  // Afrique de l'Ouest
  { nom: "Bénin", code: "BJ", zone: "Afrique de l'Ouest" },
  { nom: "Burkina Faso", code: "BF", zone: "Afrique de l'Ouest" },
  { nom: "Cap-Vert", code: "CV", zone: "Afrique de l'Ouest" },
  { nom: "Côte d'Ivoire", code: "CI", zone: "Afrique de l'Ouest" },
  { nom: "Gambie", code: "GM", zone: "Afrique de l'Ouest" },
  { nom: "Ghana", code: "GH", zone: "Afrique de l'Ouest" },
  { nom: "Guinée", code: "GN", zone: "Afrique de l'Ouest" },
  { nom: "Guinée-Bissau", code: "GW", zone: "Afrique de l'Ouest" },
  { nom: "Liberia", code: "LR", zone: "Afrique de l'Ouest" },
  { nom: "Mali", code: "ML", zone: "Afrique de l'Ouest" },
  { nom: "Mauritanie", code: "MR", zone: "Afrique de l'Ouest" },
  { nom: "Niger", code: "NE", zone: "Afrique de l'Ouest" },
  { nom: "Nigeria", code: "NG", zone: "Afrique de l'Ouest" },
  { nom: "Sénégal", code: "SN", zone: "Afrique de l'Ouest" },
  { nom: "Sierra Leone", code: "SL", zone: "Afrique de l'Ouest" },
  { nom: "Togo", code: "TG", zone: "Afrique de l'Ouest" },
  
  // Afrique du Nord
  { nom: "Algérie", code: "DZ", zone: "Afrique du Nord" },
  { nom: "Égypte", code: "EG", zone: "Afrique du Nord" },
  { nom: "Libye", code: "LY", zone: "Afrique du Nord" },
  { nom: "Maroc", code: "MA", zone: "Afrique du Nord" },
  { nom: "Tunisie", code: "TN", zone: "Afrique du Nord" },
  
  // Afrique centrale
  { nom: "Cameroun", code: "CM", zone: "Afrique centrale" },
  { nom: "République centrafricaine", code: "CF", zone: "Afrique centrale" },
  { nom: "Tchad", code: "TD", zone: "Afrique centrale" },
  { nom: "Congo", code: "CG", zone: "Afrique centrale" },
  { nom: "République démocratique du Congo", code: "CD", zone: "Afrique centrale" },
  { nom: "Guinée équatoriale", code: "GQ", zone: "Afrique centrale" },
  { nom: "Gabon", code: "GA", zone: "Afrique centrale" },
  { nom: "São Tomé-et-Príncipe", code: "ST", zone: "Afrique centrale" },
  
  // Afrique de l'Est
  { nom: "Burundi", code: "BI", zone: "Afrique de l'Est" },
  { nom: "Comores", code: "KM", zone: "Afrique de l'Est" },
  { nom: "Djibouti", code: "DJ", zone: "Afrique de l'Est" },
  { nom: "Érythrée", code: "ER", zone: "Afrique de l'Est" },
  { nom: "Éthiopie", code: "ET", zone: "Afrique de l'Est" },
  { nom: "Kenya", code: "KE", zone: "Afrique de l'Est" },
  { nom: "Madagascar", code: "MG", zone: "Afrique de l'Est" },
  { nom: "Malawi", code: "MW", zone: "Afrique de l'Est" },
  { nom: "Maurice", code: "MU", zone: "Afrique de l'Est" },
  { nom: "Mozambique", code: "MZ", zone: "Afrique de l'Est" },
  { nom: "Rwanda", code: "RW", zone: "Afrique de l'Est" },
  { nom: "Seychelles", code: "SC", zone: "Afrique de l'Est" },
  { nom: "Somalie", code: "SO", zone: "Afrique de l'Est" },
  { nom: "Soudan du Sud", code: "SS", zone: "Afrique de l'Est" },
  { nom: "Soudan", code: "SD", zone: "Afrique de l'Est" },
  { nom: "Tanzanie", code: "TZ", zone: "Afrique de l'Est" },
  { nom: "Ouganda", code: "UG", zone: "Afrique de l'Est" },
  { nom: "Zambie", code: "ZM", zone: "Afrique de l'Est" },
  { nom: "Zimbabwe", code: "ZW", zone: "Afrique de l'Est" },
  
  // Afrique australe
  { nom: "Angola", code: "AO", zone: "Afrique australe" },
  { nom: "Botswana", code: "BW", zone: "Afrique australe" },
  { nom: "Eswatini", code: "SZ", zone: "Afrique australe" },
  { nom: "Lesotho", code: "LS", zone: "Afrique australe" },
  { nom: "Namibie", code: "NA", zone: "Afrique australe" },
  { nom: "Afrique du Sud", code: "ZA", zone: "Afrique australe" }
];

export const zonesGeographiques = [
  "Afrique de l'Ouest",
  "Afrique du Nord",
  "Afrique centrale",
  "Afrique de l'Est",
  "Afrique australe",
  "Afrique (continent entier)",
  "International"
];

// Fonction pour obtenir la liste des pays d'une zone
export function getPaysParZone(zone: string): Pays[] {
  if (zone === "Afrique (continent entier)" || zone === "International") {
    return paysAfricains;
  }
  return paysAfricains.filter(pays => pays.zone === zone);
}

// Fonction pour obtenir un pays par son code
export function getPaysByCode(code: string): Pays | undefined {
  return paysAfricains.find(pays => pays.code === code);
}

// Liste des noms de pays pour les dropdowns
export const paysNomsList = paysAfricains.map(p => p.nom);

