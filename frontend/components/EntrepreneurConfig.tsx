import React, { useState } from 'react';

interface EntrepreneurConfigProps {
  onComplete: (data: any) => void;
}

const EntrepreneurConfig: React.FC<EntrepreneurConfigProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
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

  const steps = [
    { title: 'Secteur d\'activité', field: 'secteur' },
    { title: 'Zone géographique', field: 'zoneGeographique' },
    { title: 'Profil d\'organisation', field: 'profilOrganisation' },
    { title: 'Biens ou services proposés', field: 'biensServices' },
    { title: 'Autres biens ou services', field: 'autresBiensServices' },
    { title: 'Pays d\'installation', field: 'paysInstallation' },
    { title: 'Objectifs de Développement Durable', field: 'objectifsDD' },
    { title: 'Positionnement stratégique', field: 'positionnementStrategique' },
    { title: 'Vision de l\'organisation', field: 'visionOrganisation' },
    { title: 'Mission de l\'organisation', field: 'missionOrganisation' },
    { title: 'Projets significatifs réalisés', field: 'projetsSignificatifs' }
  ];

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

  const pays = ['Côte d\'Ivoire']; // Pour commencer, seulement Côte d'Ivoire

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMultiSelect = (field: string, value: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked
        ? [...(prev[field as keyof typeof prev] as string[]), value]
        : (prev[field as keyof typeof prev] as string[]).filter((item: string) => item !== value)
    }));
  };

  const nextStep = async () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Dernière étape : sauvegarder en base de données
      try {
        const response = await fetch('/api/configuration/entrepreneur', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          throw new Error('Erreur lors de la sauvegarde');
        }

        const result = await response.json();
        console.log('Configuration sauvegardée:', result);
        alert('Configuration sauvegardée avec succès ! ID: ' + result.id);

        // Appeler la fonction de completion
        onComplete(formData);
      } catch (error) {
        console.error('Erreur lors de la sauvegarde:', error);
        alert('Erreur lors de la sauvegarde: ' + (error instanceof Error ? error.message : 'Erreur inconnue'));
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepContent = () => {
    const step = steps[currentStep];

    switch (step.field) {
      case 'secteur':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Choisissez votre secteur d'activité</h3>
            <div className="grid grid-cols-2 gap-3">
              {secteurs.map((secteur) => (
                <label key={secteur} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="secteur"
                    value={secteur}
                    checked={formData.secteur === secteur}
                    onChange={(e) => handleInputChange('secteur', e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{secteur}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'zoneGeographique':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Dans quelle zone géographique opérez-vous ?</h3>
            <div className="grid grid-cols-2 gap-3">
              {zonesGeographiques.map((zone) => (
                <label key={zone} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="zoneGeographique"
                    value={zone}
                    checked={formData.zoneGeographique === zone}
                    onChange={(e) => handleInputChange('zoneGeographique', e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{zone}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'profilOrganisation':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Quel est votre profil d'organisation ?</h3>
            <div className="space-y-3">
              {profilsOrganisation.map((profil) => (
                <label key={profil} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="profilOrganisation"
                    value={profil}
                    checked={formData.profilOrganisation === profil}
                    onChange={(e) => handleInputChange('profilOrganisation', e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{profil}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'biensServices':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Quels biens ou services proposez-vous ?</h3>
            <p className="text-sm text-gray-600">Sélectionnez un ou plusieurs éléments</p>
            <div className="grid grid-cols-2 gap-3 max-h-96 overflow-y-auto">
              {getBiensServicesForSecteur().map((item) => (
                <label key={item} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.biensServices.includes(item)}
                    onChange={(e) => handleMultiSelect('biensServices', item, e.target.checked)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{item}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'autresBiensServices':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Autres biens ou services (optionnel)</h3>
            <p className="text-sm text-gray-600">Si vos produits/services ne figurent pas dans la liste précédente</p>
            <textarea
              value={formData.autresBiensServices}
              onChange={(e) => handleInputChange('autresBiensServices', e.target.value)}
              placeholder="Décrivez vos autres biens ou services..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={4}
            />
          </div>
        );

      case 'paysInstallation':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Pays d'installation</h3>
            <div className="space-y-3">
              {pays.map((paysItem) => (
                <label key={paysItem} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="radio"
                    name="paysInstallation"
                    value={paysItem}
                    checked={formData.paysInstallation === paysItem}
                    onChange={(e) => handleInputChange('paysInstallation', e.target.value)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{paysItem}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'objectifsDD':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Objectifs de Développement Durable (ODD)</h3>
            <p className="text-sm text-gray-600">Sélectionnez les ODD auxquels votre activité contribue</p>
            <div className="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto">
              {objectifsDD.map((odd) => (
                <label key={odd} className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.objectifsDD.includes(odd)}
                    onChange={(e) => handleMultiSelect('objectifsDD', odd, e.target.checked)}
                    className="text-blue-600"
                  />
                  <span className="text-sm">{odd}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'positionnementStrategique':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Positionnement stratégique</h3>
            <p className="text-sm text-gray-600">Décrivez vos avantages concurrentiels et votre valeur unique</p>
            <textarea
              value={formData.positionnementStrategique}
              onChange={(e) => handleInputChange('positionnementStrategique', e.target.value)}
              placeholder="Quels sont vos avantages concurrentiels ? Quelle valeur unique apportez-vous ?..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={6}
            />
          </div>
        );

      case 'visionOrganisation':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Vision de l'organisation</h3>
            <p className="text-sm text-gray-600">Que voulez-vous accomplir dans 5 ou 10 ans ?</p>
            <textarea
              value={formData.visionOrganisation}
              onChange={(e) => handleInputChange('visionOrganisation', e.target.value)}
              placeholder="Ex: Devenir la première entreprise agricole durable en Afrique de l'Ouest..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={4}
            />
          </div>
        );

      case 'missionOrganisation':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Mission de l'organisation</h3>
            <p className="text-sm text-gray-600">Quel est le rôle concret de votre entreprise dans la société ?</p>
            <textarea
              value={formData.missionOrganisation}
              onChange={(e) => handleInputChange('missionOrganisation', e.target.value)}
              placeholder="Ex: Fournir aux agriculteurs des outils technologiques pour améliorer leur productivité..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={4}
            />
          </div>
        );

      case 'projetsSignificatifs':
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Projets significatifs réalisés</h3>
            <p className="text-sm text-gray-600">Listez vos projets ou réalisations majeurs</p>
            <textarea
              value={formData.projetsSignificatifs}
              onChange={(e) => handleInputChange('projetsSignificatifs', e.target.value)}
              placeholder="Ex: Participation à un programme gouvernemental, collaboration avec une ONG, lancement d'un produit innovant..."
              className="w-full p-3 border rounded-lg resize-none"
              rows={6}
            />
          </div>
        );

      default:
        return null;
    }
  };

  const getBiensServicesForSecteur = () => {
    const secteurBiens: { [key: string]: string[] } = {
      'Agriculture': ['produits vivriers', 'engrais', 'matériel agricole', 'semences', 'services de conseil agricole'],
      'Sylviculture (exploitation forestière)': ['bois d\'œuvre', 'bois de chauffage', 'services de reboisement', 'produits forestiers non ligneux'],
      'Pêche et aquaculture': ['poissons frais', 'produits transformés', 'équipements aquacoles', 'services de formation'],
      'Industrie et transformation': ['produits manufacturés', 'transformation alimentaire', 'services industriels', 'équipements industriels'],
      'Commerce et distribution': ['produits alimentaires', 'vêtements', 'matériel de construction', 'produits électroniques'],
      'Éducation et formation': ['formations professionnelles', 'services éducatifs', 'matériel pédagogique', 'programmes de formation'],
      'Santé': ['services médicaux', 'médicaments', 'équipements médicaux', 'services de prévention'],
      'Énergie et environnement': ['énergie solaire', 'solutions environnementales', 'services de consulting énergétique', 'équipements écologiques'],
      'Transport et logistique': ['services de transport', 'logistique', 'entreposage', 'distribution'],
      'Technologie et innovation': ['développement d\'applications', 'services numériques', 'automatisation', 'solutions technologiques'],
      'Finance et services': ['services financiers', 'consulting', 'services administratifs', 'gestion de projet'],
      'BTP / Immobilier': ['construction', 'services immobiliers', 'matériaux de construction', 'aménagement urbain'],
      'Tourisme et hôtellerie': ['services hôteliers', 'organisation d\'événements', 'services touristiques', 'hébergement'],
      'Communication et médias': ['services de communication', 'production média', 'marketing digital', 'relations publiques']
    };

    return secteurBiens[formData.secteur] || [];
  };

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-bold text-gray-800">Configuration Entrepreneur</h2>
          <span className="text-sm text-gray-600">
            Étape {currentStep + 1} sur {steps.length}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Step Content */}
      <div className="mb-8">
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={prevStep}
          disabled={currentStep === 0}
          className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-400 transition-colors"
        >
          Précédent
        </button>

        <button
          onClick={nextStep}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {currentStep === steps.length - 1 ? 'Terminer' : 'Suivant'}
        </button>
      </div>
    </div>
  );
};

export default EntrepreneurConfig;