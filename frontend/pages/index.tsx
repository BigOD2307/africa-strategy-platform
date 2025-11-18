'use client';

import { useState } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [formData, setFormData] = useState({
    secteur: '',
    zoneGeographique: '',
    profilOrganisation: '',
    biensServices: [] as string[],
    autresBiensServices: '',
    paysInstallation: '',
    objectifsDD: [] as string[],
    positionnementStrategique: '',
    visionOrganisation: '',
    missionOrganisation: '',
    projetsSignificatifs: ''
  });

  const secteurs = [
    'Agriculture', 'Sylviculture (exploitation forestière)', 'Pêche et aquaculture',
    'Industrie et transformation', 'Commerce et distribution', 'Éducation et formation',
    'Santé', 'Énergie et environnement', 'Transport et logistique',
    'Technologie et innovation', 'Finance et services', 'BTP / Immobilier',
    'Tourisme et hôtellerie', 'Communication et médias'
  ];

  const zonesGeographiques = [
    'Afrique de l\'Ouest', 'Afrique du Nord', 'Afrique centrale',
    'Afrique australe', 'Amérique du Nord', 'Amérique du Sud',
    'Europe', 'Asie', 'Océanie'
  ];

  const profilsOrganisation = [
    'Entrepreneur en lancement (projet en phase de création)',
    'Entreprise privée (structure déjà opérationnelle)',
    'Entreprise publique (structure appartenant à l\'État)'
  ];

  const objectifsDD = [
    'ODD 1 : Pas de pauvreté', 'ODD 2 : Faim zéro', 'ODD 3 : Bonne santé et bien-être',
    'ODD 4 : Éducation de qualité', 'ODD 7 : Énergie propre et d\'un coût abordable',
    'ODD 8 : Travail décent et croissance économique', 'ODD 9 : Industrie, innovation et infrastructure',
    'ODD 13 : Lutte contre les changements climatiques'
  ];

  const steps = [
    { title: 'Secteur d\'activité', field: 'secteur', options: secteurs },
    { title: 'Zone géographique', field: 'zoneGeographique', options: zonesGeographiques },
    { title: 'Profil d\'organisation', field: 'profilOrganisation', options: profilsOrganisation },
    { title: 'Pays d\'installation', field: 'paysInstallation', type: 'text' },
    { title: 'Objectifs de Développement Durable', field: 'objectifsDD', options: objectifsDD, multiple: true },
    { title: 'Positionnement stratégique', field: 'positionnementStrategique', type: 'textarea' },
    { title: 'Vision de l\'organisation', field: 'visionOrganisation', type: 'textarea' },
    { title: 'Mission de l\'organisation', field: 'missionOrganisation', type: 'textarea' },
    { title: 'Projets significatifs réalisés', field: 'projetsSignificatifs', type: 'textarea' }
  ];

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      handleSubmit();
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

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000);
      
      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      const analysisData = result.data || result.analyses || result;
      
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('analysisResult', JSON.stringify(analysisData));
        sessionStorage.setItem('questionnaireData', JSON.stringify(formData));
      }
      
      setAnalysisComplete(true);
    } catch (err: any) {
      setError(err.message || 'Erreur lors de l\'analyse');
    } finally {
      setLoading(false);
    }
  };

  const currentStepData = steps[step];

  if (analysisComplete) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '48px', maxWidth: '512px', width: '100%', textAlign: 'center', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb' }}>
          <div style={{ marginBottom: '32px' }}>
            <div style={{ width: '80px', height: '80px', backgroundColor: '#dcfce7', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 24px' }}>
              <svg style={{ width: '48px', height: '48px', color: '#22c55e' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              </div>
            <h1 style={{ fontSize: '30px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>Analyse Terminée</h1>
            <p style={{ color: '#6b7280', fontSize: '18px' }}>Votre analyse IA est prête. Consultez les résultats détaillés dans le dashboard.</p>
            </div>
              <button
            onClick={() => window.location.href = '/dashboard'}
            style={{
              padding: '16px 32px',
              backgroundColor: '#2563eb',
              color: 'white',
              borderRadius: '12px',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '500',
              fontSize: '16px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1d4ed8'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2563eb'}
          >
            Voir le Dashboard
              </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
        {/* Header */}
      <div style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb', position: 'sticky', top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: '896px', margin: '0 auto', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', marginBottom: '4px' }}>Africa Strategy</h1>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>Configuration Entrepreneur</p>
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              Étape {step + 1} / {steps.length}
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '896px', margin: '0 auto', padding: '48px 24px' }}>
        {/* Progress Bar */}
        <div style={{ marginBottom: '40px' }}>
          <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '8px' }}>
            <div
              style={{
                backgroundColor: '#2563eb',
                height: '8px',
                borderRadius: '9999px',
                width: `${((step + 1) / steps.length) * 100}%`,
                transition: 'width 0.3s'
              }}
            />
          </div>
        </div>

        {/* Form Card */}
        <div style={{ backgroundColor: 'white', borderRadius: '16px', padding: '40px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '32px' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>{currentStepData.title}</h2>

          {error && (
            <div style={{ marginBottom: '24px', padding: '16px', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '12px' }}>
              <p style={{ color: '#991b1b', fontSize: '14px' }}>{error}</p>
            </div>
          )}

          {currentStepData.type === 'textarea' ? (
            <textarea
              value={formData[currentStepData.field as keyof typeof formData] as string}
              onChange={(e) => setFormData({ ...formData, [currentStepData.field]: e.target.value })}
              style={{
                width: '100%',
                padding: '16px',
                border: '1px solid #d1d5db',
                borderRadius: '12px',
                resize: 'none',
                fontSize: '16px',
                fontFamily: 'inherit',
                minHeight: '200px'
              }}
              rows={10}
              placeholder={`Décrivez votre ${currentStepData.title.toLowerCase()}...`}
            />
          ) : currentStepData.type === 'text' ? (
            <input
              type="text"
              value={formData[currentStepData.field as keyof typeof formData] as string}
              onChange={(e) => setFormData({ ...formData, [currentStepData.field]: e.target.value })}
              style={{
                width: '100%',
                padding: '16px',
                border: '1px solid #d1d5db',
                borderRadius: '12px',
                fontSize: '16px',
                fontFamily: 'inherit'
              }}
              placeholder={`Entrez votre ${currentStepData.title.toLowerCase()}...`}
            />
          ) : currentStepData.multiple ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {currentStepData.options?.map((option) => {
                const isSelected = (formData[currentStepData.field as keyof typeof formData] as string[]).includes(option);
                return (
                  <label
                    key={option}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      padding: '16px',
                      border: `2px solid ${isSelected ? '#2563eb' : '#e5e7eb'}`,
                      borderRadius: '12px',
                      cursor: 'pointer',
                      backgroundColor: isSelected ? '#eff6ff' : 'white',
                      transition: 'all 0.2s'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={(e) => {
                        const current = formData[currentStepData.field as keyof typeof formData] as string[];
                        if (e.target.checked) {
                          setFormData({ ...formData, [currentStepData.field]: [...current, option] });
                        } else {
                          setFormData({ ...formData, [currentStepData.field]: current.filter((item) => item !== option) });
                        }
                      }}
                      style={{ marginRight: '16px', width: '20px', height: '20px', cursor: 'pointer' }}
                    />
                    <span style={{ color: '#374151', flex: 1 }}>{option}</span>
                  </label>
                );
              })}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {currentStepData.options?.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => setFormData({ ...formData, [currentStepData.field]: option })}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '16px',
                    border: `2px solid ${formData[currentStepData.field as keyof typeof formData] === option ? '#2563eb' : '#e5e7eb'}`,
                    borderRadius: '12px',
                    backgroundColor: formData[currentStepData.field as keyof typeof formData] === option ? '#eff6ff' : 'white',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    fontSize: '16px',
                    color: '#374151'
                  }}
                  onMouseOver={(e) => {
                    if (formData[currentStepData.field as keyof typeof formData] !== option) {
                      e.currentTarget.style.borderColor = '#d1d5db';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (formData[currentStepData.field as keyof typeof formData] !== option) {
                      e.currentTarget.style.borderColor = '#e5e7eb';
                    }
                  }}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Navigation Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <button
            onClick={handleBack}
            disabled={step === 0}
            style={{
              padding: '12px 24px',
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              color: '#374151',
              borderRadius: '12px',
              cursor: step === 0 ? 'not-allowed' : 'pointer',
              fontWeight: '500',
              opacity: step === 0 ? 0.5 : 1,
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              if (step !== 0) {
                e.currentTarget.style.backgroundColor = '#f9fafb';
              }
            }}
            onMouseOut={(e) => {
              if (step !== 0) {
                e.currentTarget.style.backgroundColor = 'white';
              }
            }}
          >
            Précédent
          </button>
          <button
            onClick={(e) => {
              e.preventDefault();
              if (!loading) {
                handleNext();
              }
            }}
            disabled={loading}
            style={{
              padding: '12px 32px',
              backgroundColor: '#2563eb',
              color: 'white',
              borderRadius: '12px',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '500',
              opacity: loading ? 0.5 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              if (!loading) {
                e.currentTarget.style.backgroundColor = '#1d4ed8';
              }
            }}
            onMouseOut={(e) => {
              if (!loading) {
                e.currentTarget.style.backgroundColor = '#2563eb';
              }
            }}
          >
            {loading ? (
              <>
                <div style={{ width: '20px', height: '20px', border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                Analyse en cours...
              </>
            ) : step === steps.length - 1 ? (
              'Terminer et Analyser'
            ) : (
              'Suivant'
            )}
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
