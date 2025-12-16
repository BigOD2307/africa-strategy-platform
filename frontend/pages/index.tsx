'use client';

import { useState, useEffect, useCallback } from 'react';
import { secteursEtOffres, secteursList } from '../config/secteurs';
import { allODDs, getODDsForSecteur, ODD } from '../config/odds';
import { paysAfricains, zonesGeographiques, Pays } from '../config/pays';
import { profilsConfig, ProfilConfig, getProfilById } from '../config/profils';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
interface FormData {
  secteur: string;
  profilOrganisation: string;
  paysInstallation: string;
  zoneGeographique: string;
  biensServices: string[];
  autresBiensServices: string;
  objectifsDD: string[];
  autresODD: string;
  visionOrganisation: string;
  missionOrganisation: string;
  projetsSignificatifs: string;
  fichiers: File[];
}

interface SavedConfig {
  formData: FormData;
  savedAt: string;
  configHash: string;
}

// Hash function pour détecter les changements
function hashConfig(data: FormData): string {
  const str = JSON.stringify({
    secteur: data.secteur,
    profilOrganisation: data.profilOrganisation,
    paysInstallation: data.paysInstallation,
    zoneGeographique: data.zoneGeographique,
  });
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

export default function Home() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [configSaved, setConfigSaved] = useState(false);
  const [showEditMode, setShowEditMode] = useState(false);
  
  const [formData, setFormData] = useState<FormData>({
    secteur: '',
    profilOrganisation: '',
    paysInstallation: '',
    zoneGeographique: '',
    biensServices: [],
    autresBiensServices: '',
    objectifsDD: [],
    autresODD: '',
    visionOrganisation: '',
    missionOrganisation: '',
    projetsSignificatifs: '',
    fichiers: []
  });

  // Charger la configuration sauvegardée au démarrage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('africaStrategyConfig');
      if (saved) {
        try {
          const config: SavedConfig = JSON.parse(saved);
          setFormData(prev => ({
            ...prev,
            ...config.formData,
            fichiers: [] // Les fichiers ne peuvent pas être persistés
          }));
          setConfigSaved(true);
          setShowEditMode(true);
        } catch (e) {
          console.error('Erreur chargement config:', e);
        }
      }
    }
  }, []);

  // Mettre à jour les ODD recommandés quand le secteur change
  useEffect(() => {
    if (formData.secteur && !configSaved) {
      const oddsRecommandes = getODDsForSecteur(formData.secteur);
      setFormData(prev => ({
        ...prev,
        objectifsDD: oddsRecommandes.map(odd => odd.label)
      }));
    }
  }, [formData.secteur, configSaved]);

  // Sauvegarder la configuration
  const saveConfiguration = useCallback(() => {
    if (typeof window !== 'undefined') {
      const config: SavedConfig = {
        formData: { ...formData, fichiers: [] },
        savedAt: new Date().toISOString(),
        configHash: hashConfig(formData)
      };
      localStorage.setItem('africaStrategyConfig', JSON.stringify(config));
      setConfigSaved(true);
    }
  }, [formData]);

  // Réinitialiser la configuration
  const resetConfiguration = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('africaStrategyConfig');
      localStorage.removeItem('analysisResult');
      localStorage.removeItem('questionnaireData');
    }
    setFormData({
      secteur: '',
      profilOrganisation: '',
      paysInstallation: '',
      zoneGeographique: '',
      biensServices: [],
      autresBiensServices: '',
      objectifsDD: [],
      autresODD: '',
      visionOrganisation: '',
      missionOrganisation: '',
      projetsSignificatifs: '',
      fichiers: []
    });
    setConfigSaved(false);
    setShowEditMode(false);
    setStep(0);
  };

  // Définition des étapes
  const steps = [
    { id: 'profil', title: "Profil d'organisation", icon: '👤' },
    { id: 'secteur', title: "Secteur d'activité", icon: '🏭' },
    { id: 'localisation', title: 'Localisation', icon: '🌍' },
    { id: 'offres', title: 'Biens & Services', icon: '📦' },
    { id: 'odd', title: 'Objectifs de Développement Durable', icon: '🎯' },
    { id: 'strategie', title: 'Positionnement Stratégique', icon: '🧭' },
    { id: 'fichiers', title: 'Documents complémentaires', icon: '📎' },
    { id: 'validation', title: 'Validation', icon: '✅' }
  ];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    saveConfiguration();

    try {
      // Préparer les données (sans fichiers pour l'instant)
      const submitData = {
        ...formData,
        fichiers: formData.fichiers.map(f => f.name)
      };
      
      // Utiliser le nouvel endpoint progressif
      const response = await fetch(`${API_BASE_URL}/api/analyze/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Erreur: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      // Stocker le session_id pour le polling et les résultats initiaux
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('sessionId', result.session_id);
        sessionStorage.setItem('analysisResult', JSON.stringify({
          session_id: result.session_id,
          metadata: result.metadata,
          blocs: {
            BLOC1: result.bloc1
          }
        }));
        sessionStorage.setItem('questionnaireData', JSON.stringify(formData));
      }
      
      // Rediriger directement vers le dashboard dès que BLOC1 est prêt !
      window.location.href = '/dashboard';
      
    } catch (err: any) {
      setError(err.message || 'Erreur lors de l\'analyse');
      setLoading(false);
    }
    // Note: on ne met pas setLoading(false) ici car on redirige
  };

  // Gestion des fichiers
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setFormData(prev => ({
      ...prev,
      fichiers: [...prev.fichiers, ...files].slice(0, 5) // Max 5 fichiers
    }));
  };

  const removeFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      fichiers: prev.fichiers.filter((_, i) => i !== index)
    }));
  };

  // Obtenir les offres disponibles pour le secteur sélectionné
  const offresDisponibles = formData.secteur ? secteursEtOffres[formData.secteur] || [] : [];
  
  // Obtenir le profil sélectionné
  const selectedProfil = formData.profilOrganisation 
    ? profilsConfig.find(p => p.label === formData.profilOrganisation) 
    : null;

  // L'écran de succès n'est plus nécessaire car on redirige directement
  // Mais on le garde au cas où pour compatibilité
  if (analysisComplete) {
    // Redirection automatique
    if (typeof window !== 'undefined') {
      window.location.href = '/dashboard';
    }
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-600">Redirection vers le dashboard...</p>
        </div>
      </div>
    );
  }

  // Mode édition : afficher le récapitulatif
  if (showEditMode && configSaved) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Africa Strategy</h1>
                <p className="text-sm text-slate-500">Configuration sauvegardée</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium">
                  ✓ Sauvegardée
                </span>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-6 py-8">
          {/* Récapitulatif */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">Récapitulatif de votre configuration</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <span className="text-sm text-slate-500">Profil</span>
                  <p className="font-medium text-slate-900">{formData.profilOrganisation || '-'}</p>
                </div>
                <div>
                  <span className="text-sm text-slate-500">Secteur</span>
                  <p className="font-medium text-slate-900">{formData.secteur || '-'}</p>
                </div>
                <div>
                  <span className="text-sm text-slate-500">Pays</span>
                  <p className="font-medium text-slate-900">{formData.paysInstallation || '-'}</p>
                </div>
                <div>
                  <span className="text-sm text-slate-500">Zone géographique</span>
                  <p className="font-medium text-slate-900">{formData.zoneGeographique || '-'}</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div>
                  <span className="text-sm text-slate-500">Biens & Services</span>
                  <p className="font-medium text-slate-900">
                    {formData.biensServices.length > 0 ? formData.biensServices.join(', ') : '-'}
                    {formData.autresBiensServices && `, ${formData.autresBiensServices}`}
                  </p>
                </div>
                <div>
                  <span className="text-sm text-slate-500">ODD ciblés</span>
                  <p className="font-medium text-slate-900 text-sm">
                    {formData.objectifsDD.length > 0 ? formData.objectifsDD.map(o => o.split(' - ')[0]).join(', ') : '-'}
                  </p>
                </div>
                <div>
                  <span className="text-sm text-slate-500">Vision</span>
                  <p className="font-medium text-slate-900 text-sm line-clamp-2">{formData.visionOrganisation || '-'}</p>
                </div>
              </div>
              </div>
            </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
              <button
              onClick={() => {
                setShowEditMode(false);
                setStep(0);
              }}
              className="flex-1 px-6 py-4 bg-white border-2 border-slate-200 text-slate-700 rounded-xl font-medium hover:border-slate-300 transition-all"
            >
              Modifier la configuration
              </button>
              <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-lg shadow-blue-200 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                'Lancer l\'analyse'
              )}
              </button>
            </div>

          <button
            onClick={resetConfiguration}
            className="mt-4 w-full text-center text-slate-500 hover:text-red-600 text-sm transition-colors"
          >
            Réinitialiser et créer une nouvelle configuration
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              {error}
          </div>
          )}
        </main>
      </div>
    );
  }

  // Formulaire principal
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Africa Strategy</h1>
              <p className="text-sm text-slate-500">Configuration de votre analyse stratégique</p>
            </div>
            <div className="text-sm text-slate-500">
              Étape {step + 1} / {steps.length}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Barre de progression */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {steps.map((s, i) => (
              <div 
                key={s.id}
                className={`flex items-center justify-center w-10 h-10 rounded-full text-lg transition-all ${
                  i < step 
                    ? 'bg-blue-600 text-white' 
                    : i === step 
                      ? 'bg-blue-600 text-white ring-4 ring-blue-100' 
                      : 'bg-slate-200 text-slate-500'
                }`}
              >
                {i < step ? '✓' : s.icon}
              </div>
            ))}
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${((step + 1) / steps.length) * 100}%` }}
            />
          </div>
          <p className="text-center mt-2 text-sm font-medium text-slate-600">{steps[step].title}</p>
        </div>

        {/* Contenu de l'étape */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 mb-6">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
              {error}
            </div>
          )}

          {/* Étape 0: Profil d'organisation */}
          {step === 0 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Quel est votre profil ?</h2>
              <p className="text-slate-500 mb-6">Sélectionnez le type d'organisation qui correspond le mieux à votre situation.</p>
              
              <div className="grid md:grid-cols-2 gap-4">
                {profilsConfig.map((profil) => (
                  <button
                    key={profil.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, profilOrganisation: profil.label })}
                    className={`p-5 text-left border-2 rounded-xl transition-all ${
                      formData.profilOrganisation === profil.label
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <span className="text-2xl mb-2 block">{profil.icon}</span>
                    <span className="font-medium text-slate-900 block">{profil.label}</span>
                    <span className="text-sm text-slate-500">{profil.description}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Étape 1: Secteur d'activité */}
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Secteur d'activité</h2>
              <p className="text-slate-500 mb-6">Sélectionnez votre secteur principal d'activité.</p>
              
              <div className="grid md:grid-cols-2 gap-3">
                {secteursList.map((secteur) => (
                  <button
                    key={secteur}
                    type="button"
                    onClick={() => setFormData({ ...formData, secteur, biensServices: [] })}
                    className={`p-4 text-left border-2 rounded-xl transition-all ${
                      formData.secteur === secteur
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <span className="font-medium text-slate-900">{secteur}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Étape 2: Localisation */}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Localisation</h2>
              <p className="text-slate-500 mb-6">Indiquez votre pays d'installation et votre zone d'intervention.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Pays d'installation</label>
                  <select
                    value={formData.paysInstallation}
                    onChange={(e) => setFormData({ ...formData, paysInstallation: e.target.value })}
                    className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionnez un pays</option>
                    {paysAfricains.map((pays) => (
                      <option key={pays.code} value={pays.nom}>{pays.nom}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Zone géographique ciblée</label>
                  <select
                    value={formData.zoneGeographique}
                    onChange={(e) => setFormData({ ...formData, zoneGeographique: e.target.value })}
                    className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Sélectionnez une zone</option>
                    {zonesGeographiques.map((zone) => (
                      <option key={zone} value={zone}>{zone}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Étape 3: Biens & Services */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Biens & Services proposés</h2>
              <p className="text-slate-500 mb-6">Sélectionnez les biens et services que vous proposez.</p>
              
              {formData.secteur ? (
                <>
                  <div className="space-y-3 mb-6">
                    {offresDisponibles.map((offre) => {
                      const isSelected = formData.biensServices.includes(offre);
                      return (
                        <label
                          key={offre}
                          className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all ${
                            isSelected ? 'border-blue-600 bg-blue-50' : 'border-slate-200 hover:border-slate-300'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData({ ...formData, biensServices: [...formData.biensServices, offre] });
                              } else {
                                setFormData({ ...formData, biensServices: formData.biensServices.filter(b => b !== offre) });
                              }
                            }}
                            className="w-5 h-5 text-blue-600 rounded mr-4"
                          />
                          <span className="text-slate-900">{offre}</span>
                        </label>
                      );
                    })}
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Autre bien ou service (optionnel)</label>
                    <input
                      type="text"
                      value={formData.autresBiensServices}
                      onChange={(e) => setFormData({ ...formData, autresBiensServices: e.target.value })}
                      placeholder="Ex: Drone agricole, service de recyclage..."
                      className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </>
              ) : (
                <div className="text-center py-12 text-slate-500">
                  Veuillez d'abord sélectionner un secteur d'activité
                </div>
              )}
            </div>
          )}

          {/* Étape 4: ODD */}
          {step === 4 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Objectifs de Développement Durable</h2>
              <p className="text-slate-500 mb-6">
                Les ODD recommandés pour votre secteur sont présélectionnés. Vous pouvez les modifier.
              </p>
              
              <div className="space-y-3 mb-6">
                {allODDs.map((odd) => {
                  const isSelected = formData.objectifsDD.includes(odd.label);
                  const isRecommended = getODDsForSecteur(formData.secteur).some(o => o.id === odd.id);
                  return (
                    <label
                      key={odd.id}
                      className={`flex items-center p-4 border-2 rounded-xl cursor-pointer transition-all ${
                        isSelected ? 'border-blue-600 bg-blue-50' : 'border-slate-200 hover:border-slate-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setFormData({ ...formData, objectifsDD: [...formData.objectifsDD, odd.label] });
                          } else {
                            setFormData({ ...formData, objectifsDD: formData.objectifsDD.filter(o => o !== odd.label) });
                          }
                        }}
                        className="w-5 h-5 text-blue-600 rounded mr-4"
                      />
                      <div 
                        className="w-3 h-3 rounded-full mr-3" 
                        style={{ backgroundColor: odd.color }}
                      />
                      <div className="flex-1">
                        <span className="text-slate-900">{odd.label}</span>
                        {isRecommended && (
                          <span className="ml-2 px-2 py-0.5 bg-emerald-100 text-emerald-700 text-xs rounded-full">
                            Recommandé
                          </span>
                        )}
                      </div>
                    </label>
                  );
                })}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">Autres ODD (optionnel)</label>
                <input
                  type="text"
                  value={formData.autresODD}
                  onChange={(e) => setFormData({ ...formData, autresODD: e.target.value })}
                  placeholder="Ex: ODD personnalisé..."
                  className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          )}

          {/* Étape 5: Positionnement Stratégique */}
          {step === 5 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Positionnement Stratégique</h2>
              <p className="text-slate-500 mb-6">Décrivez votre vision, mission et réalisations significatives.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Vision de l'organisation</label>
                  <textarea
                    value={formData.visionOrganisation}
                    onChange={(e) => setFormData({ ...formData, visionOrganisation: e.target.value })}
                    placeholder="Ex: Devenir le leader africain de l'extraction responsable..."
                    rows={3}
                    maxLength={300}
                    className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-slate-400 mt-1">{formData.visionOrganisation.length}/300 caractères</p>
        </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Mission de l'organisation</label>
                  <textarea
                    value={formData.missionOrganisation}
                    onChange={(e) => setFormData({ ...formData, missionOrganisation: e.target.value })}
                    placeholder="Ex: Extraire durablement tout en préservant l'environnement..."
                    rows={3}
                    maxLength={300}
                    className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-slate-400 mt-1">{formData.missionOrganisation.length}/300 caractères</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Projets significatifs réalisés</label>
                  <textarea
                    value={formData.projetsSignificatifs}
                    onChange={(e) => setFormData({ ...formData, projetsSignificatifs: e.target.value })}
                    placeholder="Ex: Certification ISO 14001, programme de reforestation..."
                    rows={4}
                    maxLength={500}
                    className="w-full p-4 border border-slate-300 rounded-xl text-slate-900 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-slate-400 mt-1">{formData.projetsSignificatifs.length}/500 caractères</p>
        </div>
      </div>
            </div>
          )}

          {/* Étape 6: Documents complémentaires */}
          {step === 6 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Documents complémentaires</h2>
              <p className="text-slate-500 mb-6">
                Ajoutez des documents pour enrichir votre analyse (business plan, rapports, images...). 
                <span className="text-slate-400"> Optionnel - Max 5 fichiers</span>
              </p>
              
              <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
                <input
                  type="file"
                  multiple
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label 
                  htmlFor="file-upload"
                  className="cursor-pointer"
                >
                  <div className="text-4xl mb-3">📎</div>
                  <p className="text-slate-700 font-medium mb-1">Cliquez pour ajouter des fichiers</p>
                  <p className="text-sm text-slate-500">PDF, Word, Excel, Images (max 10MB chacun)</p>
                </label>
              </div>
              
              {formData.fichiers.length > 0 && (
                <div className="mt-6 space-y-3">
                  <p className="text-sm font-medium text-slate-700">Fichiers ajoutés :</p>
                  {formData.fichiers.map((file, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xl">📄</span>
                        <span className="text-slate-700">{file.name}</span>
                        <span className="text-xs text-slate-400">({(file.size / 1024).toFixed(1)} KB)</span>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Étape 7: Validation */}
          {step === 7 && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 mb-2">Validation de votre configuration</h2>
              <p className="text-slate-500 mb-6">Vérifiez les informations avant de lancer l'analyse.</p>
              
              <div className="space-y-4 mb-8">
                <div className="p-4 bg-slate-50 rounded-xl">
                  <span className="text-sm text-slate-500">Profil</span>
                  <p className="font-medium text-slate-900">{formData.profilOrganisation || '-'}</p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl">
                  <span className="text-sm text-slate-500">Secteur</span>
                  <p className="font-medium text-slate-900">{formData.secteur || '-'}</p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 rounded-xl">
                    <span className="text-sm text-slate-500">Pays</span>
                    <p className="font-medium text-slate-900">{formData.paysInstallation || '-'}</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-xl">
                    <span className="text-sm text-slate-500">Zone</span>
                    <p className="font-medium text-slate-900">{formData.zoneGeographique || '-'}</p>
                  </div>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl">
                  <span className="text-sm text-slate-500">Biens & Services</span>
                  <p className="font-medium text-slate-900">
                    {formData.biensServices.length > 0 ? formData.biensServices.join(', ') : '-'}
                    {formData.autresBiensServices && `, ${formData.autresBiensServices}`}
                  </p>
                </div>
                <div className="p-4 bg-slate-50 rounded-xl">
                  <span className="text-sm text-slate-500">ODD ciblés</span>
                  <p className="font-medium text-slate-900 text-sm">
                    {formData.objectifsDD.length > 0 ? formData.objectifsDD.map(o => o.split(' - ')[0]).join(', ') : '-'}
                  </p>
                </div>
                {formData.fichiers.length > 0 && (
                  <div className="p-4 bg-slate-50 rounded-xl">
                    <span className="text-sm text-slate-500">Documents joints</span>
                    <p className="font-medium text-slate-900">{formData.fichiers.length} fichier(s)</p>
                  </div>
                )}
              </div>

              {/* Indicateur de modules d'analyse */}
              {selectedProfil && (
                <div className="p-4 bg-blue-50 rounded-xl mb-6">
                  <p className="text-sm font-medium text-blue-900 mb-2">Modules d'analyse pour votre profil :</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedProfil.modules.map(mod => (
                      <span key={mod} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                        {mod === 'pestel' ? 'PESTEL+' : 
                         mod === 'risques_climat' ? 'Risques Climat' :
                         mod === 'marche' ? 'Marché' :
                         mod === 'chaine_valeur' ? 'Chaîne de valeur' :
                         mod === 'odd' ? 'ODD' :
                         mod === 'reglementaire' ? 'Réglementaire' :
                         mod === 'synthese' ? 'Synthèse' : mod}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Boutons de navigation */}
        <div className="flex justify-between">
          <button
            onClick={handleBack}
            disabled={step === 0}
            className={`px-6 py-3 border border-slate-300 text-slate-700 rounded-xl font-medium transition-all ${
              step === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-slate-50'
            }`}
          >
            Précédent
          </button>
          
          {step === steps.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={loading || !formData.secteur || !formData.profilOrganisation}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-lg shadow-blue-200 transition-all disabled:opacity-50 flex items-center gap-3"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyse en cours...
                </>
              ) : (
                'Lancer l\'analyse'
              )}
            </button>
          ) : (
            <button
              onClick={handleNext}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-lg shadow-blue-200 transition-all"
            >
              Suivant
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
