import { useState } from 'react';
import EntrepreneurConfig from '../components/EntrepreneurConfig';

export default function Home() {
  const [configCompleted, setConfigCompleted] = useState(false);
  const [entrepreneurData, setEntrepreneurData] = useState<any>(null);

  const handleConfigComplete = (data: any) => {
    setEntrepreneurData(data);
    setConfigCompleted(true);
    console.log('Configuration terminée:', data);
    // Ici nous pourrons appeler l'API pour sauvegarder et déclencher l'analyse IA
  };

  if (configCompleted) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              Configuration Terminée ! 🎉
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Votre profil entrepreneur a été enregistré avec succès.
            </p>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-800 mb-2">Récapitulatif :</h3>
              <div className="text-left text-blue-700">
                <p><strong>Secteur :</strong> {entrepreneurData?.secteur}</p>
                <p><strong>Zone :</strong> {entrepreneurData?.zoneGeographique}</p>
                <p><strong>Pays :</strong> {entrepreneurData?.paysInstallation}</p>
                <p><strong>Profil :</strong> {entrepreneurData?.profilOrganisation}</p>
              </div>
            </div>
            <div className="space-x-4">
              <button
                onClick={() => setConfigCompleted(false)}
                className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Modifier
              </button>
              <button
                onClick={() => alert('Prochaine étape : Analyse IA !')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Commencer l'Analyse IA
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Africa Strategy - Configuration Entrepreneur
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Configurez votre profil pour recevoir des analyses IA personnalisées
            et des recommandations adaptées à votre secteur et votre région.
          </p>
        </div>

        {/* Configuration Form */}
        <EntrepreneurConfig onComplete={handleConfigComplete} />

        {/* Footer */}
        <div className="text-center mt-8 text-gray-500">
          <p>Étape essentielle pour des analyses IA pertinentes et contextualisées</p>
        </div>
      </div>
    </div>
  );
}