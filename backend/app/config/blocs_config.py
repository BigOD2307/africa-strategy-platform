"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CONFIGURATION DES 7 BLOCS D'ANALYSE                        ║
║                        Africa Strategy Platform V2                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

Chaque bloc utilise un prompt ultra-détaillé pour produire une analyse approfondie.
Les prompts sont définis dans le module prompts/ et importés ici.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel
from app.config.prompts import (
    BLOC1_PROMPT, BLOC2_PROMPT, BLOC3_PROMPT, BLOC4_PROMPT,
    BLOC5_PROMPT, BLOC6_PROMPT, BLOC7_PROMPT
)


class BlocConfig(BaseModel):
    """Configuration complète d'un bloc d'analyse"""
    id: str
    nom: str
    nom_complet: str
    description: str
    assistant_id: Optional[str] = None  # ID de l'assistant OpenAI spécialisé
    system_prompt: str
    user_prompt_template: str
    rag_queries: List[str]
    validation_rules: dict
    indicateurs: List[str]
    dependencies: List[str] = []  # Blocs dont celui-ci dépend


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DES 7 BLOCS
# ═══════════════════════════════════════════════════════════════════════════════

BLOCS_CONFIG: Dict[str, BlocConfig] = {
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 1 : PESTEL+ - Diagnostic Macro-Durable
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC1": BlocConfig(
        id="BLOC1",
        nom="PESTEL+",
        nom_complet="Analyse PESTEL+ Contextuelle",
        description="Diagnostic complet de l'environnement externe : Politique, Économique, Social, Technologique, Environnemental, Légal, enrichi des dimensions Climat et Biodiversité",
        system_prompt=BLOC1_PROMPT["system_prompt"],
        user_prompt_template=BLOC1_PROMPT["user_prompt_template"],
        rag_queries=BLOC1_PROMPT["rag_queries"],
        validation_rules=BLOC1_PROMPT["validation_rules"],
        indicateurs=[
            "indice_politique", "indice_economique", "indice_social",
            "indice_technologique", "indice_environnement", "indice_legal",
            "indice_climat", "indice_biodiversite", "indice_pestel_global", "indice_durable_global"
        ],
        dependencies=[]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 2 : Risques Climatiques & Transition ESG
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC2": BlocConfig(
        id="BLOC2",
        nom="Risques Climat",
        nom_complet="Risques Climatiques & Transition ESG",
        description="Évaluation des risques climatiques physiques, risques de transition, risques ESG sectoriels et opportunités durables selon le cadre TCFD",
        system_prompt=BLOC2_PROMPT["system_prompt"],
        user_prompt_template=BLOC2_PROMPT["user_prompt_template"],
        rag_queries=BLOC2_PROMPT["rag_queries"],
        validation_rules=BLOC2_PROMPT["validation_rules"],
        indicateurs=[
            "indice_risques_climatiques", "indice_risques_esg",
            "indice_risques_transition", "indice_opportunites_transition", "indice_global_bloc2"
        ],
        dependencies=["BLOC1"]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 3 : Marché & Concurrence
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC3": BlocConfig(
        id="BLOC3",
        nom="Marché & Concurrence",
        nom_complet="Analyse du Marché et de la Concurrence",
        description="Analyse approfondie du marché, structure concurrentielle (5 Forces de Porter + Complémenteurs), cartographie des acteurs et opportunités de différenciation durable",
        system_prompt=BLOC3_PROMPT["system_prompt"],
        user_prompt_template=BLOC3_PROMPT["user_prompt_template"],
        rag_queries=BLOC3_PROMPT["rag_queries"],
        validation_rules=BLOC3_PROMPT["validation_rules"],
        indicateurs=[
            "indice_attractivite", "indice_concurrence",
            "indice_risques_marche", "indice_opportunites_durables", "indice_global_bloc3"
        ],
        dependencies=["BLOC1"]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 4 : Chaîne de Valeur
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC4": BlocConfig(
        id="BLOC4",
        nom="Chaîne de Valeur",
        nom_complet="Analyse de la Chaîne de Valeur Durable",
        description="Cartographie de la chaîne de valeur sectorielle, identification des vulnérabilités et opportunités par maillon, analyse de circularité et traçabilité ESG",
        system_prompt=BLOC4_PROMPT["system_prompt"],
        user_prompt_template=BLOC4_PROMPT["user_prompt_template"],
        rag_queries=BLOC4_PROMPT["rag_queries"],
        validation_rules=BLOC4_PROMPT["validation_rules"],
        indicateurs=[
            "indice_vulnerabilites", "indice_opportunites",
            "indice_circularite", "indice_esg_tracabilite", "indice_global_bloc4"
        ],
        dependencies=["BLOC1"]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 5 : Modèles Durables & ODD
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC5": BlocConfig(
        id="BLOC5",
        nom="Modèles Durables & ODD",
        nom_complet="Modèles Durables et Alignement ODD",
        description="Analyse de matérialité durable, alignement aux 17 ODD, évaluation du potentiel d'impact (IMM) et opportunités de finance durable",
        system_prompt=BLOC5_PROMPT["system_prompt"],
        user_prompt_template=BLOC5_PROMPT["user_prompt_template"],
        rag_queries=BLOC5_PROMPT["rag_queries"],
        validation_rules=BLOC5_PROMPT["validation_rules"],
        indicateurs=[
            "indice_odd", "indice_esg", "indice_climat_mrv",
            "indice_finance_durable", "indice_imm", "indice_global_bloc5"
        ],
        dependencies=["BLOC1", "BLOC2"]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 6 : Cadre Réglementaire
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC6": BlocConfig(
        id="BLOC6",
        nom="Cadre Réglementaire",
        nom_complet="Cadre Réglementaire & Conformité",
        description="Cartographie réglementaire (Taxonomie, MRV, SBTi, CSRD/ESRS, Net Zero), analyse des gaps de conformité et feuille de route d'alignement",
        system_prompt=BLOC6_PROMPT["system_prompt"],
        user_prompt_template=BLOC6_PROMPT["user_prompt_template"],
        rag_queries=BLOC6_PROMPT["rag_queries"],
        validation_rules=BLOC6_PROMPT["validation_rules"],
        indicateurs=[
            "indice_taxonomie", "indice_mrv", "indice_sbti",
            "indice_csrd", "indice_netzero", "indice_global_bloc6"
        ],
        dependencies=["BLOC1", "BLOC2", "BLOC5"]
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # BLOC 7 : Synthèse Stratégique
    # ──────────────────────────────────────────────────────────────────────────
    "BLOC7": BlocConfig(
        id="BLOC7",
        nom="Synthèse Stratégique",
        nom_complet="Synthèse Stratégique Intégrée",
        description="Consolidation des analyses des blocs 1-6, diagnostic SWOT+, feuille de route de transition, options de financement durable et partenariats stratégiques",
        system_prompt=BLOC7_PROMPT["system_prompt"],
        user_prompt_template=BLOC7_PROMPT["user_prompt_template"],
        rag_queries=BLOC7_PROMPT["rag_queries"],
        validation_rules=BLOC7_PROMPT["validation_rules"],
        indicateurs=[
            "IMD", "IRI", "IOD", "IPT", "IAO", "IPF"
        ],
        dependencies=["BLOC1", "BLOC2", "BLOC3", "BLOC4", "BLOC5", "BLOC6"]
    )
}


# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

def get_bloc_config(bloc_id: str) -> Optional[BlocConfig]:
    """Retourne la configuration d'un bloc par son ID"""
    # Normalise l'ID (accepte BLOC1, bloc1, pestel, etc.)
    normalized = bloc_id.upper().replace(" ", "").replace("_", "")
    
    if normalized in BLOCS_CONFIG:
        return BLOCS_CONFIG[normalized]
    
    # Mapping des anciens noms vers les nouveaux
    legacy_mapping = {
        "PESTEL": "BLOC1",
        "PESTEL+": "BLOC1",
        "RISQUESCLIMAT": "BLOC2",
        "RISQUES_CLIMAT": "BLOC2",
        "MARCHE": "BLOC3",
        "MARCHECONCURRENCE": "BLOC3",
        "CHAINEVALEUR": "BLOC4",
        "CHAINE_VALEUR": "BLOC4",
        "ODD": "BLOC5",
        "MODELESDURABLES": "BLOC5",
        "REGLEMENTAIRE": "BLOC6",
        "CADREREGLEMENTAIRE": "BLOC6",
        "SYNTHESE": "BLOC7",
        "SYNTHESESTRATEGIQUE": "BLOC7"
    }
    
    if normalized in legacy_mapping:
        return BLOCS_CONFIG[legacy_mapping[normalized]]
    
    return None


def get_all_blocs() -> List[BlocConfig]:
    """Retourne la liste ordonnée de tous les blocs"""
    return [BLOCS_CONFIG[f"BLOC{i}"] for i in range(1, 8)]


def get_bloc_ids() -> List[str]:
    """Retourne la liste des IDs de blocs"""
    return [f"BLOC{i}" for i in range(1, 8)]


def get_blocs_for_profil(profil: str) -> List[str]:
    """
    Retourne les IDs des blocs applicables selon le profil utilisateur.
    
    Profils supportés:
    - Entrepreneur en lancement: analyse simplifiée
    - PME: analyse complète
    - Banque: focus risques et réglementaire
    - Collectivité: focus ODD et réglementaire
    - ONG: focus ODD et impact
    - Ministère: focus politique et réglementaire
    - Entreprise privée: analyse complète
    - Entreprise publique: analyse complète
    """
    profil_blocs = {
        "entrepreneur": ["BLOC1", "BLOC3", "BLOC5", "BLOC7"],
        "pme": ["BLOC1", "BLOC2", "BLOC3", "BLOC4", "BLOC5", "BLOC6", "BLOC7"],
        "banque": ["BLOC1", "BLOC2", "BLOC3", "BLOC6", "BLOC7"],
        "collectivite": ["BLOC1", "BLOC2", "BLOC5", "BLOC6", "BLOC7"],
        "ong": ["BLOC1", "BLOC2", "BLOC5", "BLOC7"],
        "ministere": ["BLOC1", "BLOC2", "BLOC3", "BLOC5", "BLOC6", "BLOC7"],
        "entreprise_privee": ["BLOC1", "BLOC2", "BLOC3", "BLOC4", "BLOC5", "BLOC6", "BLOC7"],
        "entreprise_publique": ["BLOC1", "BLOC2", "BLOC3", "BLOC4", "BLOC5", "BLOC6", "BLOC7"],
    }
    
    # Normaliser le profil
    profil_key = profil.lower().replace(" ", "_").replace("'", "").replace("-", "_")
    
    # Chercher une correspondance
    for key in profil_blocs:
        if key in profil_key or profil_key in key:
            return profil_blocs[key]
    
    # Par défaut, tous les blocs
    return get_bloc_ids()


def get_bloc_dependencies(bloc_id: str) -> List[str]:
    """Retourne les IDs des blocs dont dépend le bloc spécifié"""
    config = get_bloc_config(bloc_id)
    if config:
        return config.dependencies
    return []


def get_execution_order(bloc_ids: List[str]) -> List[str]:
    """
    Retourne les blocs dans l'ordre d'exécution optimal
    en respectant les dépendances.
    """
    # Ordre naturel : BLOC1 → BLOC7
    all_ordered = get_bloc_ids()
    
    # Filtrer et ordonner
    return [bloc for bloc in all_ordered if bloc in bloc_ids]


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION DES ASSISTANTS OPENAI
# ═══════════════════════════════════════════════════════════════════════════════

# Ces IDs seront remplis lors de la création des assistants dans OpenAI
ASSISTANT_IDS = {
    "BLOC1": None,  # ID de l'assistant PESTEL+
    "BLOC2": None,  # ID de l'assistant Risques Climat
    "BLOC3": None,  # ID de l'assistant Marché
    "BLOC4": None,  # ID de l'assistant Chaîne de Valeur
    "BLOC5": None,  # ID de l'assistant ODD
    "BLOC6": None,  # ID de l'assistant Réglementaire
    "BLOC7": None,  # ID de l'assistant Synthèse
    "MAIN": None,   # ID de l'assistant principal (orchestrateur)
}


def set_assistant_id(bloc_id: str, assistant_id: str):
    """Définit l'ID de l'assistant OpenAI pour un bloc"""
    if bloc_id in ASSISTANT_IDS:
        ASSISTANT_IDS[bloc_id] = assistant_id
        if bloc_id in BLOCS_CONFIG:
            BLOCS_CONFIG[bloc_id].assistant_id = assistant_id


def get_assistant_id(bloc_id: str) -> Optional[str]:
    """Retourne l'ID de l'assistant OpenAI pour un bloc"""
    return ASSISTANT_IDS.get(bloc_id)
