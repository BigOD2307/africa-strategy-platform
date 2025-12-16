'use client';

import { useState, useEffect, ReactNode, useCallback } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
} from 'chart.js';
import { Radar, Bar, Doughnut } from 'react-chartjs-2';
import Chatbot from '@/components/Chatbot';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement
);

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ═══════════════════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════════════════

type TabType = 'overview' | 'bloc1' | 'bloc2' | 'bloc3' | 'bloc4' | 'bloc5' | 'bloc6' | 'bloc7';

interface BlocStatus {
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: any;
}

const TABS = [
  { id: 'overview' as TabType, blocId: '', label: 'Vue d\'ensemble', icon: '📊' },
  { id: 'bloc1' as TabType, blocId: 'BLOC1', label: 'PESTEL+', icon: '🌍' },
  { id: 'bloc2' as TabType, blocId: 'BLOC2', label: 'Risques Climat', icon: '🌡️' },
  { id: 'bloc3' as TabType, blocId: 'BLOC3', label: 'Marché', icon: '📈' },
  { id: 'bloc4' as TabType, blocId: 'BLOC4', label: 'Chaîne de Valeur', icon: '🔗' },
  { id: 'bloc5' as TabType, blocId: 'BLOC5', label: 'ODD & Durabilité', icon: '🎯' },
  { id: 'bloc6' as TabType, blocId: 'BLOC6', label: 'Réglementaire', icon: '⚖️' },
  { id: 'bloc7' as TabType, blocId: 'BLOC7', label: 'Synthèse', icon: '📋' },
];

const PESTEL_DIMENSIONS = [
  { id: 'politique', label: 'Politique', icon: '🏛️', color: 'blue' },
  { id: 'economique', label: 'Économie', icon: '💰', color: 'green' },
  { id: 'social', label: 'Social', icon: '👥', color: 'purple' },
  { id: 'technologique', label: 'Technologie', icon: '💻', color: 'cyan' },
  { id: 'environnement', label: 'Environnement', icon: '🌿', color: 'emerald' },
  { id: 'legal', label: 'Légal', icon: '⚖️', color: 'amber' },
  { id: 'climat', label: 'Climat', icon: '🌡️', color: 'orange' },
  { id: 'biodiversite', label: 'Biodiversité', icon: '🦋', color: 'lime' },
];

// ═══════════════════════════════════════════════════════════════════════════════
// UI COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

const ScoreCard = ({ label, value, color = 'blue', interpretation }: { label: string; value: number | string; color?: string; interpretation?: string }) => {
  const numValue = typeof value === 'number' ? value : parseInt(String(value)) || 0;
  const bgColors: Record<string, string> = {
    blue: 'from-blue-600 to-blue-700',
    red: 'from-red-500 to-red-600',
    green: 'from-green-600 to-green-700',
    amber: 'from-amber-500 to-amber-600',
    purple: 'from-purple-600 to-purple-700',
    orange: 'from-orange-500 to-orange-600',
    cyan: 'from-cyan-600 to-cyan-700',
    emerald: 'from-emerald-600 to-emerald-700',
    lime: 'from-lime-600 to-lime-700',
    slate: 'from-slate-700 to-slate-800',
  };
  return (
    <div className={`bg-gradient-to-br ${bgColors[color] || bgColors.blue} rounded-xl p-4 text-white shadow-lg`}>
      <p className="text-xs text-white/80 uppercase font-medium truncate">{label}</p>
      <p className="text-3xl font-bold mt-1">{numValue}<span className="text-lg text-white/70">/100</span></p>
      {interpretation && <p className="text-xs text-white/70 mt-2 line-clamp-2">{interpretation}</p>}
    </div>
  );
};

const Section = ({ icon, title, children, className = '' }: { icon: string; title: string; children: ReactNode; className?: string }) => (
  <div className={`bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden ${className}`}>
    <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-5 py-4 border-b border-slate-200">
      <h4 className="font-bold text-slate-800 flex items-center gap-2">
        <span className="text-xl">{icon}</span> {title}
      </h4>
    </div>
    <div className="p-5">{children}</div>
  </div>
);

const IndicatorCard = ({ indicator }: { indicator: any }) => (
  <div className="bg-slate-50 rounded-lg p-4 border border-slate-100">
    <div className="flex items-start justify-between gap-3">
      <div className="flex-1">
        <p className="font-semibold text-slate-800">{indicator.nom || indicator.name}</p>
        <p className="text-sm text-slate-500 mt-1">
          Valeur: <span className="font-medium text-slate-700">{indicator.valeur_brute} {indicator.unite}</span>
          {indicator.source && <span className="ml-2 text-slate-400">• Source: {indicator.source}</span>}
        </p>
        {indicator.commentaire && <p className="text-sm text-slate-600 mt-2 italic">{indicator.commentaire}</p>}
      </div>
      <div className="flex flex-col items-end gap-1">
        <span className={`px-3 py-1 rounded-full text-sm font-bold ${
          indicator.score_normalise >= 70 ? 'bg-green-100 text-green-700' :
          indicator.score_normalise >= 50 ? 'bg-amber-100 text-amber-700' :
          'bg-red-100 text-red-700'
        }`}>
          {indicator.score_normalise}/100
        </span>
        {indicator.poids_sectoriel && (
          <span className="text-xs text-slate-400">Poids: {indicator.poids_sectoriel}</span>
        )}
      </div>
    </div>
    {indicator.odd_associes && indicator.odd_associes.length > 0 && (
      <div className="flex gap-1 mt-3">
        {indicator.odd_associes.map((odd: number) => (
          <span key={odd} className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">ODD {odd}</span>
        ))}
      </div>
    )}
  </div>
);

const NewsCard = ({ item }: { item: any }) => (
  <div className={`rounded-lg p-4 border ${
    item.type === 'Opportunité' || item.type === 'opportunite' 
      ? 'bg-green-50 border-green-200' 
      : 'bg-red-50 border-red-200'
  }`}>
    <div className="flex items-start justify-between gap-3">
      <div className="flex-1">
        <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold mb-2 ${
          item.type === 'Opportunité' || item.type === 'opportunite'
            ? 'bg-green-200 text-green-800' 
            : 'bg-red-200 text-red-800'
        }`}>
          {item.type}
        </span>
        <p className="font-semibold text-slate-800">{item.titre || item.title}</p>
        <p className="text-sm text-slate-600 mt-1">{item.impact_sectoriel || item.impact}</p>
        {item.source && <p className="text-xs text-slate-400 mt-2">Source: {item.source}</p>}
      </div>
      {item.score_normalise && (
        <span className={`px-2 py-1 rounded text-sm font-bold ${
          item.score_normalise >= 60 ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
        }`}>
          {item.score_normalise}
        </span>
      )}
    </div>
  </div>
);

const LoadingBloc = ({ name, icon }: { name: string; icon: string }) => (
  <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
    <span className="text-5xl block mb-4">{icon}</span>
    <h3 className="text-xl font-semibold text-slate-900 mb-2">{name}</h3>
    <p className="text-slate-500 mb-4">Génération en cours par l'Assistant IA...</p>
    <div className="flex items-center justify-center gap-2">
      <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  </div>
);

// Helper pour convertir n'importe quelle valeur en string affichable
const toDisplayString = (val: any): string => {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string') return val;
  if (typeof val === 'number' || typeof val === 'boolean') return String(val);
  if (Array.isArray(val)) return val.map(toDisplayString).join(', ');
  if (typeof val === 'object') {
    // Pour les objets, extraire les valeurs clés
    const keys = Object.keys(val);
    if (keys.length === 0) return '';
    // Chercher des clés communes
    if (val.description) return val.description;
    if (val.texte) return val.texte;
    if (val.analyse) return val.analyse;
    if (val.nom) return val.nom;
    if (val.titre) return val.titre;
    // Sinon, lister les clés
    return keys.map(k => `${k}: ${toDisplayString(val[k])}`).join(' | ');
  }
  return String(val);
};

// Composant pour afficher n'importe quelle donnée de manière sécurisée
const SafeDisplay = ({ data, className = '' }: { data: any; className?: string }) => {
  if (data === null || data === undefined) return null;
  
  // String simple
  if (typeof data === 'string') {
    return <span className={className}>{data}</span>;
  }
  
  // Nombre ou booléen
  if (typeof data === 'number' || typeof data === 'boolean') {
    return <span className={className}>{String(data)}</span>;
  }
  
  // Tableau
  if (Array.isArray(data)) {
    if (data.length === 0) return null;
    return (
      <ul className={`space-y-1 ${className}`}>
        {data.map((item, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="text-blue-500">•</span>
            <SafeDisplay data={item} />
          </li>
        ))}
      </ul>
    );
  }
  
  // Objet
  if (typeof data === 'object') {
    const entries = Object.entries(data).filter(([k]) => !k.startsWith('_'));
    if (entries.length === 0) return null;
    
    return (
      <div className={`space-y-2 ${className}`}>
        {entries.map(([key, value]) => (
          <div key={key} className="bg-slate-50 rounded p-3">
            <p className="font-medium text-slate-700 capitalize mb-1">{key.replace(/_/g, ' ')}</p>
            <div className="text-sm text-slate-600">
              <SafeDisplay data={value} />
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  return <span className={className}>{String(data)}</span>;
};

// Composant pour afficher un élément de risque/opportunité
const RiskOpportunityCard = ({ item, type }: { item: any; type: 'risk' | 'opportunity' }) => {
  const bgColor = type === 'risk' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200';
  const textColor = type === 'risk' ? 'text-red-800' : 'text-green-800';
  
  // Extraire le titre et la description
  const getTitle = () => {
    if (typeof item === 'string') return item;
    return item.nom || item.type || item.titre || item.name || 'Élément';
  };
  
  const getDescription = () => {
    if (typeof item === 'string') return null;
    return item.description || item.analyse || item.detail || item.commentaire;
  };
  
  const getScore = () => {
    if (typeof item !== 'object') return null;
    return item.score || item.score_normalise || item.niveau;
  };

  // Si c'est un objet complexe sans titre évident, afficher toutes ses propriétés
  const renderComplexObject = () => {
    if (typeof item !== 'object' || item === null) return null;
    const entries = Object.entries(item).filter(([k]) => 
      !['nom', 'type', 'titre', 'name', 'description', 'analyse', 'detail', 'score', 'score_normalise', 'niveau'].includes(k)
    );
    if (entries.length === 0) return null;
    
    return (
      <div className="mt-2 space-y-1">
        {entries.map(([key, value]) => (
          <div key={key} className="text-sm">
            <span className="font-medium text-slate-600 capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
            <span className="text-slate-700">{toDisplayString(value)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className={`${bgColor} border rounded-lg p-4`}>
      <p className={`font-semibold ${textColor}`}>{getTitle()}</p>
      {getDescription() && (
        <p className="text-sm text-slate-600 mt-1">{getDescription()}</p>
      )}
      {getScore() && (
        <span className={`inline-block mt-2 px-2 py-1 ${type === 'risk' ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'} rounded text-xs font-bold`}>
          Score: {getScore()}
        </span>
      )}
      {renderComplexObject()}
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL
// ═══════════════════════════════════════════════════════════════════════════════

export default function Dashboard() {
  const [blocsData, setBlocsData] = useState<Record<string, any>>({});
  const [blocsStatus, setBlocsStatus] = useState<Record<string, BlocStatus>>({});
  const [questionnaireData, setQuestionnaireData] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [activePestelDim, setActivePestelDim] = useState('politique');
  const [chatOpen, setChatOpen] = useState(false);
  const [globalProgress, setGlobalProgress] = useState(0);
  const [allCompleted, setAllCompleted] = useState(false);

  // Polling
  const pollStatus = useCallback(async (sid: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze/status/${sid}`);
      if (!response.ok) return false;
      const data = await response.json();
      
      setBlocsStatus(data.blocs || {});
      setGlobalProgress(data.progress || 0);
      
      const newBlocsData: Record<string, any> = {};
      if (data.blocs) {
        Object.entries(data.blocs).forEach(([blocId, blocStatus]: [string, any]) => {
          if (blocStatus.status === 'completed' && blocStatus.result) {
            newBlocsData[blocId] = blocStatus.result;
          }
        });
      }
      setBlocsData(prev => ({ ...prev, ...newBlocsData }));
      if (data.status === 'completed') {
        setAllCompleted(true);
        return true;
      }
      return false;
    } catch (err) {
      console.error('Erreur polling:', err);
      return false;
    }
  }, []);

  // Init
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const sid = sessionStorage.getItem('sessionId');
    const storedAnalysis = sessionStorage.getItem('analysisResult');
    const storedForm = sessionStorage.getItem('questionnaireData');
    
    if (storedForm) {
      try { setQuestionnaireData(JSON.parse(storedForm)); } catch (e) { /* ignore */ }
    }
    if (storedAnalysis) {
      try {
        const parsed = JSON.parse(storedAnalysis);
        if (parsed.blocs) {
          setBlocsData(parsed.blocs);
          const initialStatus: Record<string, BlocStatus> = {};
          Object.keys(parsed.blocs).forEach(blocId => {
            initialStatus[blocId] = { status: 'completed', result: parsed.blocs[blocId] };
          });
          setBlocsStatus(initialStatus);
          if (Object.keys(parsed.blocs).length >= 7) {
            setAllCompleted(true);
            setGlobalProgress(100);
          }
        }
      } catch (e) {
        console.error('Erreur parsing:', e);
      }
    }
    if (sid) setSessionId(sid);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (!sessionId || allCompleted) return;
    pollStatus(sessionId);
    const interval = setInterval(async () => {
      const isDone = await pollStatus(sessionId);
      if (isDone) clearInterval(interval);
    }, 3000);
    return () => clearInterval(interval);
  }, [sessionId, allCompleted, pollStatus]);

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 1: PESTEL+ - STRUCTURE CORRECTE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc1 = (data: any) => {
    if (!data) return <p className="text-slate-500">Données PESTEL+ non disponibles.</p>;

    // Extraire les données selon la vraie structure
    const indices = data.indices || {};
    const indicateurs = data.indicateurs || {};
    const analyses = data.analyses || {};
    const actualites = data.actualites_signaux || [];
    const synthese = data.synthese_strategique || {};
    const oddMapping = data.odd_mapping || {};

    // Score et interprétation de la dimension active
    const dimIndex = indices[activePestelDim] || {};
    const dimIndicateurs = indicateurs[activePestelDim] || [];
    const dimAnalyse = analyses.pestel_plus?.[activePestelDim] || 
                       analyses.climat?.[activePestelDim === 'climat' ? 'risques_physiques' : ''] ||
                       analyses.biodiversite?.[activePestelDim === 'biodiversite' ? 'etat_capital_naturel' : ''] ||
                       '';

    // Données pour le radar
    const radarLabels = PESTEL_DIMENSIONS.map(d => d.label);
    const radarScores = PESTEL_DIMENSIONS.map(d => indices[d.id]?.score || 50);

    const radarData = {
      labels: radarLabels,
      datasets: [{
        label: 'Score PESTEL',
        data: radarScores,
        backgroundColor: 'rgba(30, 58, 138, 0.2)',
        borderColor: 'rgba(30, 58, 138, 0.8)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(30, 58, 138, 1)',
      }]
    };

    // Données pour le bar chart
    const barData = {
      labels: radarLabels,
      datasets: [{
        label: 'Score',
        data: radarScores,
        backgroundColor: radarScores.map(s => s >= 70 ? '#22c55e' : s >= 50 ? '#f59e0b' : '#ef4444'),
        borderRadius: 6,
      }]
    };

    const dimConfig = PESTEL_DIMENSIONS.find(d => d.id === activePestelDim);

    return (
      <div className="space-y-6">
        {/* Header avec navigation des dimensions */}
        <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-amber-400 rounded-full flex items-center justify-center text-2xl">🌍</div>
            <div>
              <h2 className="text-2xl font-bold">BLOC 1 — Analyse PESTEL+ Durable</h2>
              <p className="text-blue-200 text-sm">Analyse de l'environnement externe - {data.metadata?.pays || 'Pays'}</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            {PESTEL_DIMENSIONS.map((dim) => (
              <button
                key={dim.id}
                onClick={() => setActivePestelDim(dim.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                  activePestelDim === dim.id 
                    ? 'bg-white text-blue-900 shadow-md' 
                    : 'bg-blue-800/50 text-blue-100 hover:bg-blue-700'
                }`}
              >
                <span>{dim.icon}</span> {dim.label}
              </button>
            ))}
          </div>
        </div>

        {/* Indices globaux - 6 indices selon la spécification */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <ScoreCard 
            label="I_PESTEL" 
            value={indices.pestel_global?.score || indices.I_PESTEL || 0} 
            color="blue"
            interpretation={indices.pestel_global?.interpretation}
          />
          <ScoreCard 
            label="I_Climat" 
            value={indices.climat?.score || indices.I_CLIMAT || 0} 
            color="orange"
            interpretation={indices.climat?.interpretation}
          />
          <ScoreCard 
            label="I_Biodiv" 
            value={indices.biodiversite?.score || indices.I_BIODIV || 0} 
            color="lime"
            interpretation={indices.biodiversite?.interpretation}
          />
          <ScoreCard 
            label="I_Macro" 
            value={indices.macro?.score || indices.I_MACRO || indices.macro_economique?.score || 0} 
            color="purple"
            interpretation={indices.macro?.interpretation}
          />
          <ScoreCard 
            label="I_Actu" 
            value={indices.actualites?.score || indices.I_ACTU || indices.signaux?.score || 0} 
            color="cyan"
            interpretation={indices.actualites?.interpretation}
          />
          <ScoreCard 
            label="I_Global_B1" 
            value={indices.global_bloc1?.score || indices.I_GLOBAL_BLOC1 || indices.durable_global?.score || 0} 
            color="slate"
            interpretation={indices.global_bloc1?.interpretation}
          />
        </div>

        {/* Graphiques côte à côte */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Section icon="🎯" title="Vue Radar PESTEL+">
            <div className="h-80">
              <Radar 
                data={radarData} 
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } },
                  plugins: { legend: { display: false } }
                }} 
              />
            </div>
          </Section>
          <Section icon="📊" title="Comparaison des dimensions">
            <div className="h-80">
              <Bar 
                data={barData} 
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  indexAxis: 'y',
                  scales: { x: { max: 100 } },
                  plugins: { legend: { display: false } }
                }} 
              />
            </div>
          </Section>
        </div>

        {/* Dimension active - Détail */}
        <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl p-6 text-white">
          <div className="flex items-center gap-4 mb-4">
            <span className="text-4xl">{dimConfig?.icon}</span>
            <div>
              <h3 className="text-2xl font-bold">{dimConfig?.label}</h3>
              <p className="text-slate-300">{dimIndex.interpretation || 'Analyse en cours...'}</p>
            </div>
            <div className="ml-auto text-right">
              <p className="text-5xl font-bold">{dimIndex.score || 'N/A'}</p>
              <p className="text-slate-400">/100</p>
            </div>
          </div>
        </div>

        {/* Indicateurs de la dimension */}
        <Section icon="📋" title={`Indicateurs ${dimConfig?.label || ''}`}>
          {dimIndicateurs.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {dimIndicateurs.map((ind: any, i: number) => (
                <IndicatorCard key={ind.id || i} indicator={ind} />
              ))}
            </div>
          ) : (
            <p className="text-slate-500 italic">Aucun indicateur disponible pour cette dimension.</p>
          )}
        </Section>

        {/* Analyse textuelle */}
        <Section icon="📝" title={`Analyse ${dimConfig?.label || ''}`}>
          {dimAnalyse ? (
            <p className="text-slate-700 leading-relaxed">{dimAnalyse}</p>
          ) : (
            <p className="text-slate-500 italic">Analyse textuelle non disponible.</p>
          )}
          
          {/* Analyses spécifiques climat/biodiversité */}
          {activePestelDim === 'climat' && analyses.climat && (
            <div className="mt-4 space-y-3">
              {analyses.climat.risques_physiques && (
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                  <p className="font-semibold text-orange-800 mb-1">🌊 Risques physiques</p>
                  <p className="text-slate-700 text-sm">{analyses.climat.risques_physiques}</p>
                </div>
              )}
              {analyses.climat.risques_transition && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="font-semibold text-amber-800 mb-1">⚡ Risques de transition</p>
                  <p className="text-slate-700 text-sm">{analyses.climat.risques_transition}</p>
                </div>
              )}
              {analyses.climat.opportunites && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="font-semibold text-green-800 mb-1">💡 Opportunités</p>
                  <p className="text-slate-700 text-sm">{analyses.climat.opportunites}</p>
                </div>
              )}
            </div>
          )}
          
          {activePestelDim === 'biodiversite' && analyses.biodiversite && (
            <div className="mt-4 space-y-3">
              {analyses.biodiversite.etat_capital_naturel && (
                <div className="bg-lime-50 border border-lime-200 rounded-lg p-4">
                  <p className="font-semibold text-lime-800 mb-1">🌳 État du capital naturel</p>
                  <p className="text-slate-700 text-sm">{analyses.biodiversite.etat_capital_naturel}</p>
                </div>
              )}
              {analyses.biodiversite.pressions_menaces && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="font-semibold text-red-800 mb-1">⚠️ Pressions et menaces</p>
                  <p className="text-slate-700 text-sm">{analyses.biodiversite.pressions_menaces}</p>
                </div>
              )}
              {analyses.biodiversite.opportunites_nature_based && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                  <p className="font-semibold text-emerald-800 mb-1">🌱 Solutions basées sur la nature</p>
                  <p className="text-slate-700 text-sm">{analyses.biodiversite.opportunites_nature_based}</p>
                </div>
              )}
            </div>
          )}
        </Section>

        {/* Actualités et signaux */}
        <Section icon="📰" title="Actualités & Signaux faibles">
          {actualites.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {actualites.map((item: any, i: number) => (
                <NewsCard key={i} item={item} />
              ))}
            </div>
          ) : (
            <p className="text-slate-500 italic">Aucune actualité disponible.</p>
          )}
        </Section>

        {/* Synthèse stratégique */}
        <Section icon="🎯" title="Synthèse stratégique">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Facteurs clés de succès */}
            {synthese.facteurs_cles_succes?.length > 0 && (
              <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
                <h5 className="font-bold text-emerald-800 mb-3">✅ Facteurs clés de succès</h5>
                <ul className="space-y-2">
                  {synthese.facteurs_cles_succes.map((f: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-emerald-500">•</span> {f}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Risques CT */}
            {synthese.risques_prioritaires_ct?.length > 0 && (
              <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                <h5 className="font-bold text-red-800 mb-3">⚠️ Risques court terme</h5>
                <ul className="space-y-2">
                  {synthese.risques_prioritaires_ct.map((r: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-red-500">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Risques MT */}
            {synthese.risques_structurels_mt?.length > 0 && (
              <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                <h5 className="font-bold text-orange-800 mb-3">🔶 Risques moyen terme</h5>
                <ul className="space-y-2">
                  {synthese.risques_structurels_mt.map((r: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-orange-500">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Opportunités */}
            {synthese.opportunites_durables?.length > 0 && (
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                <h5 className="font-bold text-blue-800 mb-3">💡 Opportunités durables</h5>
                <ul className="space-y-2">
                  {synthese.opportunites_durables.map((o: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-blue-500">•</span> {o}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Avantages compétitifs */}
            {synthese.avantages_competitifs?.length > 0 && (
              <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                <h5 className="font-bold text-purple-800 mb-3">🏆 Avantages compétitifs</h5>
                <ul className="space-y-2">
                  {synthese.avantages_competitifs.map((a: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-purple-500">•</span> {a}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Recommandations */}
            {synthese.recommandations_immediates?.length > 0 && (
              <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200">
                <h5 className="font-bold text-cyan-800 mb-3">🚀 Recommandations immédiates</h5>
                <ul className="space-y-2">
                  {synthese.recommandations_immediates.map((r: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                      <span className="text-cyan-500">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Section>

        {/* Marché Carbone */}
        {(analyses.marche_carbone || data.marche_carbone) && (
          <Section icon="💨" title="Marché Carbone">
            <SafeDisplay data={analyses.marche_carbone || data.marche_carbone} />
          </Section>
        )}

        {/* ODD Mapping */}
        {oddMapping.odd_identifies?.length > 0 && (
          <Section icon="🎯" title="Mapping ODD">
            <div className="flex flex-wrap gap-3 mb-4">
              {oddMapping.odd_identifies.map((odd: number) => (
                <span 
                  key={odd} 
                  className={`px-4 py-2 rounded-lg font-bold ${
                    oddMapping.odd_prioritaires?.includes(odd)
                      ? 'bg-blue-600 text-white' 
                      : 'bg-blue-100 text-blue-800'
                  }`}
                >
                  ODD {odd}
                </span>
              ))}
            </div>
            {oddMapping.justification && (
              <p className="text-slate-600 text-sm mt-3">{oddMapping.justification}</p>
            )}
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC1
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 2: RISQUES CLIMAT - STRUCTURE RÉELLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc2 = (data: any) => {
    if (!data) return <LoadingBloc name="Risques Climat" icon="🌡️" />;

    const indices = data.indices || {};
    const indicateurs = data.indicateurs || {};
    const analyses = data.analyses || {};
    const synthese = data.synthese_strategique || {};
    const matrice = data.matrice_risques_opportunites || [];
    
    // Extraire les indicateurs par catégorie (structure réelle)
    const risquesClimatiques = Array.isArray(indicateurs.risques_climatiques) ? indicateurs.risques_climatiques : [];
    const risquesESG = Array.isArray(indicateurs.risques_esg) ? indicateurs.risques_esg : [];
    const risquesTransition = Array.isArray(indicateurs.risques_transition) ? indicateurs.risques_transition : [];
    const opportunitesTransition = Array.isArray(indicateurs.opportunites_transition) ? indicateurs.opportunites_transition : [];

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🌡️</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 2 — Risques Climat & Transition</h2>
              <p className="text-orange-100">Comprendre les risques physiques et de transition</p>
            </div>
          </div>
        </div>

        {/* Indices - 4 indices selon la spécification */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ScoreCard 
            label="I_RisquePhy" 
            value={indices.risques_climatiques?.score || indices.risque_physique?.score || indices.I_RISQUEPHY || 0} 
            color="red" 
            interpretation={indices.risques_climatiques?.interpretation || indices.risque_physique?.interpretation}
          />
          <ScoreCard 
            label="I_RisqueTrans" 
            value={indices.risques_transition?.score || indices.risque_transition?.score || indices.I_RISQUETRANS || 0} 
            color="orange" 
            interpretation={indices.risques_transition?.interpretation || indices.risque_transition?.interpretation}
          />
          <ScoreCard 
            label="I_OpportunitéClimat" 
            value={indices.opportunites_transition?.score || indices.opportunite_climat?.score || indices.I_OPPORTUNITECLIMAT || 0} 
            color="green" 
            interpretation={indices.opportunites_transition?.interpretation || indices.opportunite_climat?.interpretation}
          />
          <ScoreCard 
            label="I_Global_B2" 
            value={indices.global_bloc2?.score || indices.I_GLOBAL_B2 || 0} 
            color="blue" 
            interpretation={indices.global_bloc2?.interpretation}
          />
        </div>

        {/* Risques climatiques */}
        <Section icon="🌊" title="Risques climatiques (IPCC)">
          {risquesClimatiques.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {risquesClimatiques.map((r: any, i: number) => (
                <IndicatorCard key={i} indicator={r} />
              ))}
            </div>
          ) : analyses.risques_climatiques ? (
            <SafeDisplay data={analyses.risques_climatiques} />
          ) : (
            <p className="text-slate-500 italic">Données des risques climatiques en cours de génération...</p>
          )}
        </Section>

        {/* Risques ESG */}
        <Section icon="🌱" title="Risques ESG sectoriels">
          {risquesESG.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {risquesESG.map((r: any, i: number) => (
                <IndicatorCard key={i} indicator={r} />
              ))}
            </div>
          ) : analyses.risques_esg ? (
            <SafeDisplay data={analyses.risques_esg} />
          ) : (
            <p className="text-slate-500 italic">Analyse ESG en cours...</p>
          )}
        </Section>

        {/* Risques de transition */}
        <Section icon="⚡" title="Risques de transition">
          {risquesTransition.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {risquesTransition.map((r: any, i: number) => (
                <IndicatorCard key={i} indicator={r} />
              ))}
            </div>
          ) : analyses.risques_transition ? (
            <SafeDisplay data={analyses.risques_transition} />
          ) : (
            <p className="text-slate-500 italic">Analyse des risques de transition en cours...</p>
          )}
        </Section>

        {/* Sensibilité sectorielle au climat */}
        <Section icon="🎯" title="Sensibilité sectorielle au climat">
          {(analyses.sensibilite_sectorielle || data.sensibilite_sectorielle) ? (
            <SafeDisplay data={analyses.sensibilite_sectorielle || data.sensibilite_sectorielle} />
          ) : risquesESG.length > 0 ? (
            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
              <p className="text-slate-700">
                Le secteur présente une sensibilité {indices.risques_esg?.niveau || 'modérée'} aux enjeux climatiques.
                {indices.risques_esg?.interpretation && <span className="block mt-2 text-sm">{indices.risques_esg.interpretation}</span>}
              </p>
            </div>
          ) : (
            <p className="text-slate-500 italic">Analyse de sensibilité sectorielle en cours...</p>
          )}
        </Section>

        {/* Opportunités d'adaptation & mitigation */}
        <Section icon="💡" title="Opportunités d'adaptation & mitigation">
          {opportunitesTransition.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {opportunitesTransition.map((o: any, i: number) => (
                <IndicatorCard key={i} indicator={o} />
              ))}
            </div>
          ) : analyses.opportunites ? (
            <SafeDisplay data={analyses.opportunites} />
          ) : (
            <p className="text-slate-500 italic">Identification des opportunités en cours...</p>
          )}
        </Section>

        {/* Matrice risques/opportunités */}
        {matrice.length > 0 && (
          <Section icon="📊" title="Matrice Risques & Opportunités">
            <div className="grid md:grid-cols-2 gap-4">
              {matrice.map((item: any, i: number) => (
                <div key={i} className={`p-4 rounded-lg border ${item.type === 'Risque' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${item.type === 'Risque' ? 'bg-red-200 text-red-800' : 'bg-green-200 text-green-800'}`}>
                      {item.type}
                    </span>
                    <span className="text-xs text-slate-500">{item.horizon}</span>
                  </div>
                  <p className="font-semibold text-slate-800">{item.element}</p>
                  <div className="flex gap-4 mt-2 text-xs text-slate-600">
                    <span>Probabilité: <strong>{item.probabilite}</strong></span>
                    <span>Impact: <strong>{item.impact}</strong></span>
                  </div>
                  {item.action_requise && <p className="text-sm text-slate-600 mt-2 italic">{item.action_requise}</p>}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Synthèse */}
        {synthese && Object.keys(synthese).length > 0 && (
          <Section icon="📋" title="Synthèse stratégique Climat">
            <SafeDisplay data={synthese} />
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC2
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 3: MARCHÉ & CONCURRENCE - STRUCTURE RÉELLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc3 = (data: any) => {
    if (!data) return <LoadingBloc name="Marché & Concurrence" icon="📈" />;

    const indices = data.indices || {};
    const structureSectorielle = data.structure_sectorielle || {};
    const analyseConcurrentielle = data.analyse_concurrentielle || {};
    const acteursDominants = Array.isArray(data.acteurs_dominants) ? data.acteurs_dominants : [];
    const indicateurs = data.indicateurs || {};
    const analyses = data.analyses || {};
    const positionnement = data.positionnement_recommande || {};
    const synthese = data.synthese_strategique || {};

    // Forces de Porter (structure réelle)
    const forcesPorter = analyseConcurrentielle.forces_porter || {};
    const complementeurs = analyseConcurrentielle.complementeurs || {};
    
    // Construire les données du radar Porter
    const getPorterScore = (force: any): number => {
      if (typeof force === 'number') return force * 20; // Multiplier si score sur 5
      if (typeof force === 'object' && force?.score) return force.score * 20;
      return 50;
    };

    const porterData = {
      labels: ['Rivalité', 'Nouveaux entrants', 'Substituts', 'Pouvoir clients', 'Pouvoir fournisseurs', 'Complémenteurs'],
      datasets: [{
        label: 'Force',
        data: [
          getPorterScore(forcesPorter.rivalite),
          getPorterScore(forcesPorter.nouveaux_entrants),
          getPorterScore(forcesPorter.substituts),
          getPorterScore(forcesPorter.pouvoir_clients),
          getPorterScore(forcesPorter.pouvoir_fournisseurs),
          getPorterScore(complementeurs.technologiques),
        ],
        backgroundColor: 'rgba(234, 179, 8, 0.2)',
        borderColor: 'rgba(234, 179, 8, 0.8)',
        borderWidth: 2,
      }]
    };

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-500 to-amber-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">📈</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 3 — Marché, Concurrence & Modèle Sectoriel</h2>
              <p className="text-yellow-100">Comprendre la dynamique économique du secteur</p>
            </div>
          </div>
        </div>

        {/* Indices - 5 indices selon la spécification */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <ScoreCard 
            label="I_Attractivité" 
            value={indices.attractivite?.score || indices.I_ATTRACTIVITE || 0} 
            color="green" 
            interpretation={indices.attractivite?.interpretation}
          />
          <ScoreCard 
            label="I_Concurrence" 
            value={indices.concurrence?.score || indices.I_CONCURRENCE || 0} 
            color="red" 
            interpretation={indices.concurrence?.interpretation}
          />
          <ScoreCard 
            label="I_PressionSubst" 
            value={indices.risques_marche?.score || indices.pression_substituts?.score || indices.I_PRESSIONSUBST || 0} 
            color="orange" 
            interpretation={indices.risques_marche?.interpretation || indices.pression_substituts?.interpretation}
          />
          <ScoreCard 
            label="I_Partenariat" 
            value={indices.opportunites_durables?.score || indices.partenariat?.score || indices.I_PARTENARIAT || 0} 
            color="purple" 
            interpretation={indices.opportunites_durables?.interpretation || indices.partenariat?.interpretation}
          />
          <ScoreCard 
            label="I_Global_B3" 
            value={indices.global_bloc3?.score || indices.I_GLOBAL_B3 || 0} 
            color="blue" 
            interpretation={indices.global_bloc3?.interpretation}
          />
        </div>

        {/* Structure sectorielle */}
        {structureSectorielle && Object.keys(structureSectorielle).length > 0 && (
          <Section icon="🏭" title="Structure sectorielle">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500">Code ISIC</p>
                <p className="font-bold text-slate-800">{structureSectorielle.code_isic} - {structureSectorielle.description}</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-4">
                <p className="text-sm text-slate-500">Croissance</p>
                <p className="font-bold text-slate-800">Historique: {structureSectorielle.croissance_historique} → Projetée: {structureSectorielle.croissance_projetee}</p>
              </div>
            </div>
            {structureSectorielle.tendances_cles && (
              <div className="mt-4">
                <p className="font-semibold text-slate-700 mb-2">Tendances clés:</p>
                <div className="flex flex-wrap gap-2">
                  {structureSectorielle.tendances_cles.map((t: string, i: number) => (
                    <span key={i} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">{t}</span>
                  ))}
                </div>
              </div>
            )}
            {structureSectorielle.caracteristiques && (
              <div className="mt-4">
                <SafeDisplay data={structureSectorielle.caracteristiques} />
              </div>
            )}
          </Section>
        )}

        {/* Forces de Porter */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Section icon="⚔️" title="5 Forces de Porter">
            <div className="h-72">
              <Radar 
                data={porterData} 
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  scales: { r: { beginAtZero: true, max: 100, ticks: { stepSize: 20 } } },
                  plugins: { legend: { display: false } }
                }} 
              />
            </div>
          </Section>
          
          <Section icon="📊" title="Détail des forces">
            <div className="space-y-3">
              {Object.entries(forcesPorter).map(([key, val]: [string, any]) => (
                <div key={key} className="bg-slate-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-slate-800 capitalize">{key.replace(/_/g, ' ')}</p>
                    <span className="px-2 py-1 bg-amber-100 text-amber-800 rounded text-sm font-bold">
                      {typeof val === 'object' ? val.score : val}/5
                    </span>
                  </div>
                  {typeof val === 'object' && val.analyse && (
                    <p className="text-sm text-slate-600 mt-1">{val.analyse}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>
        </div>

        {/* Complémenteurs */}
        {Object.keys(complementeurs).length > 0 && (
          <Section icon="🤝" title="Complémenteurs">
            <div className="grid md:grid-cols-3 gap-4">
              {Object.entries(complementeurs).map(([key, val]: [string, any]) => (
                <div key={key} className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-semibold text-purple-800 capitalize">{key}</p>
                    <span className="px-2 py-1 bg-purple-200 text-purple-800 rounded text-sm font-bold">
                      {typeof val === 'object' ? val.score : val}/5
                    </span>
                  </div>
                  {typeof val === 'object' && val.analyse && (
                    <p className="text-sm text-slate-600">{val.analyse}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Acteurs dominants */}
        {acteursDominants.length > 0 && (
          <Section icon="🏢" title="Acteurs dominants">
            <div className="grid md:grid-cols-2 gap-4">
              {acteursDominants.map((acteur: any, i: number) => (
                <div key={i} className={`rounded-lg p-4 border ${
                  acteur.type === 'Leader' ? 'bg-blue-50 border-blue-200' :
                  acteur.type === 'Challenger' ? 'bg-purple-50 border-purple-200' :
                  acteur.type === 'Niche' ? 'bg-emerald-50 border-emerald-200' :
                  'bg-slate-50 border-slate-200'
                }`}>
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-bold text-slate-800">{acteur.nom}</p>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      acteur.type === 'Leader' ? 'bg-blue-200 text-blue-800' :
                      acteur.type === 'Challenger' ? 'bg-purple-200 text-purple-800' :
                      acteur.type === 'Niche' ? 'bg-emerald-200 text-emerald-800' :
                      'bg-slate-200 text-slate-800'
                    }`}>
                      {acteur.type}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">Part de marché: <strong>{acteur.parts_marche_estimees}</strong></p>
                  <p className="text-sm text-slate-600">Modèle: {acteur.modele_economique}</p>
                  {acteur.forces && (
                    <div className="mt-2">
                      <p className="text-xs font-semibold text-green-700">Forces:</p>
                      <p className="text-xs text-slate-600">{acteur.forces.join(', ')}</p>
                    </div>
                  )}
                  {acteur.faiblesses && (
                    <div className="mt-1">
                      <p className="text-xs font-semibold text-red-700">Faiblesses:</p>
                      <p className="text-xs text-slate-600">{acteur.faiblesses.join(', ')}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Facteurs clés de succès sectoriels */}
        <Section icon="🏆" title="Facteurs clés de succès sectoriels">
          {(synthese.facteurs_concurrence || synthese.facteurs_cles_succes || data.facteurs_cles_succes) ? (
            <div className="flex flex-wrap gap-3">
              {(synthese.facteurs_concurrence || synthese.facteurs_cles_succes || data.facteurs_cles_succes || []).map((f: any, i: number) => (
                <span key={i} className="px-4 py-2 bg-emerald-100 text-emerald-800 rounded-lg font-medium">
                  {toDisplayString(typeof f === 'string' ? f : f.nom || f.facteur || f)}
                </span>
              ))}
            </div>
          ) : (
            <div className="bg-slate-50 rounded-lg p-4 border">
              <p className="text-slate-600 text-sm">
                Les facteurs clés de succès dans ce secteur incluent l'innovation, la qualité de service, 
                la capacité d'adaptation et les partenariats stratégiques.
              </p>
            </div>
          )}
        </Section>

        {/* Analyses */}
        {analyses && Object.keys(analyses).length > 0 && (
          <Section icon="📝" title="Analyses">
            <SafeDisplay data={analyses} />
          </Section>
        )}

        {/* Positionnement recommandé */}
        {positionnement && Object.keys(positionnement).length > 0 && (
          <Section icon="🎯" title="Positionnement recommandé">
            <SafeDisplay data={positionnement} />
          </Section>
        )}

        {/* Synthèse */}
        {synthese && Object.keys(synthese).length > 0 && (
          <Section icon="📋" title="Synthèse stratégique Marché">
            <SafeDisplay data={synthese} />
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC3
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 4: CHAÎNE DE VALEUR - ROBUSTE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc4 = (data: any) => {
    if (!data) return <LoadingBloc name="Chaîne de Valeur" icon="🔗" />;

    const indices = data.indices || {};
    const indicateurs = data.indicateurs || {};
    const analyses = data.analyses || {};
    const synthese = data.synthese_strategique || {};
    
    // Extraction robuste des données
    const getArray = (key: string): any[] => {
      const val = data[key] || indicateurs[key] || analyses[key];
      return Array.isArray(val) ? val : [];
    };

    const acteurs = getArray('acteurs') || getArray('acteurs_cles') || getArray('segments');
    const vulnerabilites = getArray('vulnerabilites') || getArray('vulnerabilites_esg') || getArray('risques');
    const opportunites = getArray('opportunites') || getArray('opportunites_innovation');

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🔗</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 4 — Chaîne de Valeur Durable</h2>
              <p className="text-green-100">Analyser le fonctionnement de la chaîne de valeur (ISIC × Pays × Marché)</p>
            </div>
          </div>
        </div>

        {/* Indices - 5 indices selon la spécification */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <ScoreCard 
            label="I_CapacitéValeur" 
            value={indices.capacite_valeur?.score || indices.capacite?.score || indices.I_CAPACITEVALEUR || 0} 
            color="green" 
            interpretation={indices.capacite_valeur?.interpretation || indices.capacite?.interpretation}
          />
          <ScoreCard 
            label="I_RisquesValeur" 
            value={indices.risques_valeur?.score || indices.risques?.score || indices.I_RISQUESVALEUR || 0} 
            color="red" 
            interpretation={indices.risques_valeur?.interpretation || indices.risques?.interpretation}
          />
          <ScoreCard 
            label="I_Innovation" 
            value={indices.innovation?.score || indices.I_INNOVATION || 0} 
            color="cyan" 
            interpretation={indices.innovation?.interpretation}
          />
          <ScoreCard 
            label="I_Circularité" 
            value={indices.circularite?.score || indices.I_CIRCULARITE || 0} 
            color="purple" 
            interpretation={indices.circularite?.interpretation}
          />
          <ScoreCard 
            label="I_Global_B4" 
            value={indices.global_bloc4?.score || indices.I_GLOBAL_B4 || 0} 
            color="blue" 
            interpretation={indices.global_bloc4?.interpretation}
          />
        </div>

        {/* Indicateurs par catégorie */}
        {Object.keys(indicateurs).length > 0 && (
          <Section icon="📊" title="Indicateurs Chaîne de Valeur">
            {Object.entries(indicateurs).map(([key, val]) => (
              <div key={key} className="mb-4">
                <h5 className="font-semibold text-slate-700 capitalize mb-2">{key.replace(/_/g, ' ')}</h5>
                {Array.isArray(val) ? (
                  <div className="grid md:grid-cols-2 gap-3">
                    {val.map((item: any, i: number) => (
                      <IndicatorCard key={i} indicator={item} />
                    ))}
                  </div>
                ) : (
                  <SafeDisplay data={val} />
                )}
              </div>
            ))}
          </Section>
        )}

        {/* Acteurs */}
        {acteurs.length > 0 && (
          <Section icon="👥" title="Acteurs et activités clés">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {acteurs.map((a: any, i: number) => (
                <div key={i} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                  <p className="font-semibold text-slate-800">{toDisplayString(typeof a === 'object' ? a.nom || a.segment || a.acteur : a)}</p>
                  {typeof a === 'object' && <SafeDisplay data={Object.fromEntries(Object.entries(a).filter(([k]) => !['nom', 'segment', 'acteur'].includes(k)))} />}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Vulnérabilités ESG/climat de la chaîne */}
        <Section icon="⚠️" title="Vulnérabilités ESG/climat de la chaîne">
          {vulnerabilites.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {vulnerabilites.map((v: any, i: number) => (
                <div key={i} className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="font-semibold text-red-800">{toDisplayString(typeof v === 'object' ? v.nom || v.type || v.titre : v)}</p>
                  {typeof v === 'object' && <SafeDisplay data={Object.fromEntries(Object.entries(v).filter(([k]) => !['nom', 'type', 'titre'].includes(k)))} />}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 italic">Analyse des vulnérabilités en cours...</p>
          )}
        </Section>

        {/* Opportunités de circularité, digitalisation, innovation */}
        <Section icon="💡" title="Opportunités de circularité, digitalisation, innovation">
          {opportunites.length > 0 ? (
            <div className="grid md:grid-cols-2 gap-4">
              {opportunites.map((o: any, i: number) => (
                <div key={i} className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="font-semibold text-green-800">{toDisplayString(typeof o === 'object' ? o.nom || o.type || o.titre : o)}</p>
                  {typeof o === 'object' && <SafeDisplay data={Object.fromEntries(Object.entries(o).filter(([k]) => !['nom', 'type', 'titre'].includes(k)))} />}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 italic">Identification des opportunités en cours...</p>
          )}
        </Section>

        {/* Mapping ISIC */}
        <Section icon="🗂️" title="Mapping ISIC → GRI/SASB">
          {(data.mapping_isic || data.isic_mapping || analyses.mapping_isic) ? (
            <SafeDisplay data={data.mapping_isic || data.isic_mapping || analyses.mapping_isic} />
          ) : data.metadata?.secteur_isic ? (
            <div className="bg-slate-50 rounded-lg p-4 border">
              <p className="text-sm text-slate-600">
                <strong>Secteur ISIC:</strong> {data.metadata.secteur_isic}
              </p>
              <p className="text-xs text-slate-500 mt-2">
                Le mapping détaillé vers GRI/SASB sera disponible en Phase 2/3.
              </p>
            </div>
          ) : (
            <p className="text-slate-500 italic">Mapping ISIC en cours de préparation...</p>
          )}
        </Section>

        {/* Analyses */}
        {Object.keys(analyses).length > 0 && (
          <Section icon="📝" title="Analyses">
            <SafeDisplay data={analyses} />
          </Section>
        )}

        {/* Synthèse */}
        {Object.keys(synthese).length > 0 && (
          <Section icon="📋" title="Synthèse stratégique">
            <SafeDisplay data={synthese} />
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC4
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 5: ODD & DURABILITÉ - STRUCTURE RÉELLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc5 = (data: any) => {
    if (!data) return <LoadingBloc name="ODD & Durabilité" icon="🎯" />;

    const indices = data.indices || {};
    const analyseOdd = data.analyse_odd || {};
    const analyseMaterialite = data.analyse_materialite_esg || {};
    const analyseClimatMrv = data.analyse_climat_mrv || {};
    const analyseFinance = data.analyse_finance_durable || {};
    const analyseImm = data.analyse_imm || {};
    const modelesDurables = Array.isArray(data.modeles_durables) ? data.modeles_durables : [];
    const synthese = data.synthese_strategique || {};
    const analyses = data.analyses || {};

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🎯</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 5 — Modèles Durables / ODD / Économie Circulaire</h2>
              <p className="text-blue-100">Positionner l'entreprise vers un modèle d'affaires durable</p>
            </div>
          </div>
        </div>

        {/* Indices - 5 indices selon la spécification */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <ScoreCard 
            label="I_ODD" 
            value={indices.odd?.score || indices.I_ODD || 0} 
            color="blue" 
            interpretation={indices.odd?.interpretation} 
          />
          <ScoreCard 
            label="I_ModèleDurable" 
            value={indices.esg?.score || indices.modele_durable?.score || indices.I_MODELEDURABLE || 0} 
            color="green" 
            interpretation={indices.esg?.interpretation || indices.modele_durable?.interpretation} 
          />
          <ScoreCard 
            label="I_ImpactPositif" 
            value={indices.imm?.score || indices.impact_positif?.score || indices.I_IMPACTPOSITIF || 0} 
            color="emerald" 
            interpretation={indices.imm?.interpretation || indices.impact_positif?.interpretation} 
          />
          <ScoreCard 
            label="I_RisqueImpact" 
            value={indices.finance_durable?.score || indices.risque_impact?.score || indices.I_RISQUEIMPACT || 0} 
            color="orange" 
            interpretation={indices.finance_durable?.interpretation || indices.risque_impact?.interpretation} 
          />
          <ScoreCard 
            label="I_Global_B5" 
            value={indices.global_bloc5?.score || indices.I_GLOBAL_B5 || 0} 
            color="slate" 
            interpretation={indices.global_bloc5?.interpretation} 
          />
        </div>

        {/* Analyse ODD */}
        {Object.keys(analyseOdd).length > 0 && (
          <Section icon="🎯" title="Analyse ODD">
            {/* ODD Prioritaires Secteur */}
            {analyseOdd.odd_prioritaires_secteur && (
              <div className="mb-4">
                <h5 className="font-semibold text-slate-700 mb-2">ODD prioritaires (Secteur)</h5>
                <div className="flex flex-wrap gap-3">
                  {analyseOdd.odd_prioritaires_secteur.map((odd: any, i: number) => (
                    <div key={i} className="bg-blue-100 rounded-lg p-3 text-center">
                      <span className="text-2xl font-bold text-blue-800">ODD {odd.odd}</span>
                      <p className="text-xs text-blue-600">{odd.pertinence} - Score: {odd.score}</p>
                      {odd.justification && <p className="text-xs text-slate-600 mt-1">{odd.justification}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Synthèse alignement */}
            {analyseOdd.synthese_alignement && (
              <div className="mb-4">
                <h5 className="font-semibold text-slate-700 mb-2">Synthèse alignement</h5>
                <div className="grid md:grid-cols-3 gap-3">
                  {analyseOdd.synthese_alignement.map((item: any, i: number) => (
                    <div key={i} className="bg-slate-50 rounded-lg p-3 border">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-slate-800">ODD {item.odd}</span>
                        <span className="px-2 py-1 bg-blue-200 text-blue-800 rounded text-sm">{item.score_combine}/100</span>
                      </div>
                      <p className="text-xs text-slate-600">{item.recommandation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Gaps et ODD recommandés */}
            {(analyseOdd.gaps_identifies || analyseOdd.odd_recommandes) && (
              <div className="grid md:grid-cols-2 gap-4">
                {analyseOdd.gaps_identifies && (
                  <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                    <p className="font-semibold text-red-800 mb-2">Gaps identifiés</p>
                    <ul className="text-sm text-slate-700 space-y-1">
                      {analyseOdd.gaps_identifies.map((g: string, i: number) => <li key={i}>• {g}</li>)}
                    </ul>
                  </div>
                )}
                {analyseOdd.odd_recommandes && (
                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <p className="font-semibold text-green-800 mb-2">ODD recommandés</p>
                    <div className="flex flex-wrap gap-2">
                      {analyseOdd.odd_recommandes.map((o: string, i: number) => (
                        <span key={i} className="px-3 py-1 bg-green-200 text-green-800 rounded-full text-sm font-medium">{o}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </Section>
        )}

        {/* Analyse Matérialité ESG */}
        {Object.keys(analyseMaterialite).length > 0 && (
          <Section icon="🌱" title="Matérialité ESG">
            <div className="grid md:grid-cols-3 gap-4">
              {/* Enjeux Environnementaux */}
              {analyseMaterialite.enjeux_environnementaux && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-3">🌿 Environnement</p>
                  {analyseMaterialite.enjeux_environnementaux.map((e: any, i: number) => (
                    <div key={i} className="flex items-center justify-between mb-2 text-sm">
                      <span className="text-slate-700">{e.enjeu}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        e.materialite === 'Critique' ? 'bg-red-200 text-red-800' :
                        e.materialite === 'Élevée' ? 'bg-orange-200 text-orange-800' :
                        'bg-yellow-200 text-yellow-800'
                      }`}>{e.score}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Enjeux Sociaux */}
              {analyseMaterialite.enjeux_sociaux && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-3">👥 Social</p>
                  {analyseMaterialite.enjeux_sociaux.map((e: any, i: number) => (
                    <div key={i} className="flex items-center justify-between mb-2 text-sm">
                      <span className="text-slate-700">{e.enjeu}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        e.materialite === 'Critique' ? 'bg-red-200 text-red-800' :
                        e.materialite === 'Élevée' ? 'bg-orange-200 text-orange-800' :
                        'bg-yellow-200 text-yellow-800'
                      }`}>{e.score}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Enjeux Gouvernance */}
              {analyseMaterialite.enjeux_gouvernance && (
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <p className="font-semibold text-purple-800 mb-3">🏛️ Gouvernance</p>
                  {analyseMaterialite.enjeux_gouvernance.map((e: any, i: number) => (
                    <div key={i} className="flex items-center justify-between mb-2 text-sm">
                      <span className="text-slate-700">{e.enjeu}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        e.materialite === 'Critique' ? 'bg-red-200 text-red-800' :
                        e.materialite === 'Élevée' ? 'bg-orange-200 text-orange-800' :
                        'bg-yellow-200 text-yellow-800'
                      }`}>{e.score}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Risques et Opportunités ESG */}
            {(analyseMaterialite.risques_esg || analyseMaterialite.opportunites_esg) && (
              <div className="grid md:grid-cols-2 gap-4 mt-4">
                {analyseMaterialite.risques_esg && (
                  <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                    <p className="font-semibold text-red-800 mb-2">⚠️ Risques ESG</p>
                    <ul className="text-sm text-slate-700 space-y-1">
                      {analyseMaterialite.risques_esg.map((r: string, i: number) => <li key={i}>• {r}</li>)}
                    </ul>
                  </div>
                )}
                {analyseMaterialite.opportunites_esg && (
                  <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                    <p className="font-semibold text-green-800 mb-2">💡 Opportunités ESG</p>
                    <ul className="text-sm text-slate-700 space-y-1">
                      {analyseMaterialite.opportunites_esg.map((o: string, i: number) => <li key={i}>• {o}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </Section>
        )}

        {/* Analyse Climat MRV */}
        {Object.keys(analyseClimatMrv).length > 0 && (
          <Section icon="🌡️" title="Profil Climat & MRV">
            <SafeDisplay data={analyseClimatMrv} />
          </Section>
        )}

        {/* Analyse Finance Durable */}
        {Object.keys(analyseFinance).length > 0 && (
          <Section icon="💰" title="Finance Durable">
            <SafeDisplay data={analyseFinance} />
          </Section>
        )}

        {/* Analyse IMM */}
        {Object.keys(analyseImm).length > 0 && (
          <Section icon="📊" title="Impact Measurement & Management (IMM)">
            <SafeDisplay data={analyseImm} />
          </Section>
        )}

        {/* Modèles Durables */}
        {modelesDurables.length > 0 && (
          <Section icon="♻️" title="Modèles économiques durables">
            <div className="grid md:grid-cols-2 gap-4">
              {modelesDurables.map((m: any, i: number) => (
                <div key={i} className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                  <p className="font-bold text-emerald-800 mb-2">{m.modele}</p>
                  <p className="text-sm text-slate-600 mb-2">{m.description}</p>
                  <div className="flex gap-2 flex-wrap">
                    <span className="px-2 py-1 bg-emerald-200 text-emerald-800 rounded text-xs">Applicabilité: {m.applicabilite}</span>
                  </div>
                  {m.potentiel && <p className="text-xs text-slate-500 mt-2">{m.potentiel}</p>}
                  {m.recommandation && <p className="text-xs text-emerald-600 mt-1 font-medium">→ {m.recommandation}</p>}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Analyses textuelles */}
        {Object.keys(analyses).length > 0 && (
          <Section icon="📝" title="Analyses">
            <div className="space-y-3">
              {Object.entries(analyses).map(([key, val]) => (
                <div key={key} className="bg-slate-50 rounded-lg p-4 border">
                  <p className="font-semibold text-slate-700 capitalize mb-1">{key.replace(/_/g, ' ')}</p>
                  <p className="text-sm text-slate-600">{toDisplayString(val)}</p>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Synthèse */}
        {Object.keys(synthese).length > 0 && (
          <Section icon="📋" title="Synthèse stratégique">
            <SafeDisplay data={synthese} />
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC5
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 6: RÉGLEMENTAIRE - STRUCTURE RÉELLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc6 = (data: any) => {
    if (!data) return <LoadingBloc name="Cadre Réglementaire" icon="⚖️" />;

    const indices = data.indices || {};
    const contexte = data.contexte_reglementaire || {};
    const analyseTaxonomie = data.analyse_taxonomie || {};
    const analyseMrv = data.analyse_mrv || {};
    const analyseSbti = data.analyse_sbti || {};
    const analyseCsrd = data.analyse_csrd || {};
    const analyseNetzero = data.analyse_netzero || {};
    const syntheseRegl = data.synthese_reglementaire || {};
    const orientations = data.orientations_strategiques || {};

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-violet-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">⚖️</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 6 — Cadre Réglementaire & Transition Durable</h2>
              <p className="text-purple-100">Comprendre les obligations réglementaires et la transition exigée</p>
            </div>
          </div>
        </div>

        {/* Indices */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <ScoreCard label="I_Taxonomie" value={indices.taxonomie?.score || 0} color="blue" interpretation={indices.taxonomie?.interpretation} />
          <ScoreCard label="I_MRV" value={indices.mrv?.score || 0} color="green" interpretation={indices.mrv?.interpretation} />
          <ScoreCard label="I_SBTi" value={indices.sbti?.score || 0} color="cyan" interpretation={indices.sbti?.interpretation} />
          <ScoreCard label="I_CSRD" value={indices.csrd?.score || 0} color="purple" interpretation={indices.csrd?.interpretation} />
          <ScoreCard label="I_NetZero" value={indices.netzero?.score || 0} color="emerald" interpretation={indices.netzero?.interpretation} />
          <ScoreCard label="I_Global_B6" value={indices.global_bloc6?.score || 0} color="slate" interpretation={indices.global_bloc6?.interpretation} />
        </div>

        {/* Contexte réglementaire */}
        {Object.keys(contexte).length > 0 && (
          <Section icon="🌍" title="Contexte réglementaire">
            <div className="grid md:grid-cols-3 gap-4">
              {/* International */}
              {contexte.international && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-2">🌐 International</p>
                  {contexte.international.accords_climat && (
                    <div className="mb-2">
                      <p className="text-xs font-medium text-slate-600 mb-1">Accords climat:</p>
                      <ul className="text-xs text-slate-700 space-y-1">
                        {contexte.international.accords_climat.map((a: string, i: number) => <li key={i}>• {a}</li>)}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              {/* Régional */}
              {contexte.regional_africain && (
                <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                  <p className="font-semibold text-amber-800 mb-2">🌍 Régional Africain</p>
                  <SafeDisplay data={contexte.regional_africain} />
                </div>
              )}
              {/* National */}
              {contexte.national && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-2">🏛️ National</p>
                  {contexte.national.cdn && (
                    <div className="text-xs text-slate-700">
                      <p><strong>Atténuation:</strong> {contexte.national.cdn.objectifs_attenuation}</p>
                      <p><strong>Adaptation:</strong> {contexte.national.cdn.objectifs_adaptation}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Analyse Taxonomie */}
        {Object.keys(analyseTaxonomie).length > 0 && (
          <Section icon="📜" title="Analyse Taxonomie">
            <div className="grid md:grid-cols-2 gap-4">
              {/* Score global */}
              <div className="bg-slate-50 rounded-lg p-4 border">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-semibold text-slate-700">Score global Taxonomie</span>
                  <span className="text-2xl font-bold text-blue-600">{analyseTaxonomie.score_global || 0}/100</span>
                </div>
                {analyseTaxonomie.implications_strategiques && (
                  <p className="text-sm text-slate-600">{analyseTaxonomie.implications_strategiques}</p>
                )}
              </div>
              {/* DNSH */}
              {analyseTaxonomie.dnsh && (
                <div className="bg-slate-50 rounded-lg p-4 border">
                  <p className="font-semibold text-slate-700 mb-2">Critères DNSH</p>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    {Object.entries(analyseTaxonomie.dnsh).map(([key, val]: [string, any]) => (
                      <div key={key} className="flex items-center justify-between bg-white p-2 rounded">
                        <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className={`font-bold ${(val?.score || 0) >= 60 ? 'text-green-600' : 'text-orange-600'}`}>
                          {val?.score || 0}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Analyse MRV */}
        {Object.keys(analyseMrv).length > 0 && (
          <Section icon="📊" title="Analyse MRV (Mesure, Reporting, Vérification)">
            <div className="mb-4">
              <div className="flex items-center gap-4 mb-3">
                <span className="text-lg font-semibold text-slate-700">Score global MRV:</span>
                <span className="text-2xl font-bold text-green-600">{analyseMrv.score_global || 0}/100</span>
              </div>
            </div>
            {/* Gap Assessment */}
            {analyseMrv.gap_assessment && (
              <div className="mb-4">
                <p className="font-semibold text-slate-700 mb-2">Gap Assessment par Scope</p>
                <div className="grid md:grid-cols-3 gap-3">
                  {analyseMrv.gap_assessment.map((gap: any, i: number) => (
                    <div key={i} className={`rounded-lg p-3 border ${
                      gap.priorite === 'Élevée' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                    }`}>
                      <p className="font-bold text-slate-800">{gap.scope}</p>
                      <p className="text-xs text-slate-600">Gap: <strong>{gap.gap}</strong></p>
                      <p className="text-xs text-slate-600">Priorité: <strong>{gap.priorite}</strong></p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Feuille de route */}
            {analyseMrv.feuille_route && <SafeDisplay data={analyseMrv.feuille_route} />}
          </Section>
        )}

        {/* Analyse SBTi */}
        {Object.keys(analyseSbti).length > 0 && (
          <Section icon="🎯" title="Analyse SBTi">
            <div className="flex items-center gap-4 mb-3">
              <span className="text-lg font-semibold text-slate-700">Score global SBTi:</span>
              <span className="text-2xl font-bold text-cyan-600">{analyseSbti.score_global || 0}/100</span>
            </div>
            <SafeDisplay data={analyseSbti} />
          </Section>
        )}

        {/* Analyse CSRD */}
        {Object.keys(analyseCsrd).length > 0 && (
          <Section icon="📋" title="Analyse CSRD/ESRS">
            <div className="flex items-center gap-4 mb-3">
              <span className="text-lg font-semibold text-slate-700">Score global CSRD:</span>
              <span className="text-2xl font-bold text-purple-600">{analyseCsrd.score_global || 0}/100</span>
            </div>
            {/* ESRS Pertinents */}
            {analyseCsrd.esrs_pertinents && (
              <div className="mb-4">
                <p className="font-semibold text-slate-700 mb-2">Standards ESRS pertinents</p>
                <div className="flex flex-wrap gap-2">
                  {analyseCsrd.esrs_pertinents.map((esrs: any, i: number) => (
                    <span key={i} className={`px-3 py-1 rounded-full text-sm font-medium ${
                      esrs.priorite === 'Haute' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {esrs.standard} - {esrs.intitule}
                    </span>
                  ))}
                </div>
              </div>
            )}
            <SafeDisplay data={Object.fromEntries(Object.entries(analyseCsrd).filter(([k]) => !['score_global', 'esrs_pertinents'].includes(k)))} />
          </Section>
        )}

        {/* Analyse Net Zero */}
        {Object.keys(analyseNetzero).length > 0 && (
          <Section icon="🌍" title="Analyse Net Zero">
            <div className="flex items-center gap-4 mb-3">
              <span className="text-lg font-semibold text-slate-700">Score global Net Zero:</span>
              <span className="text-2xl font-bold text-emerald-600">{analyseNetzero.score_global || 0}/100</span>
            </div>
            <SafeDisplay data={analyseNetzero} />
          </Section>
        )}

        {/* Synthèse réglementaire */}
        {Object.keys(syntheseRegl).length > 0 && (
          <Section icon="📋" title="Synthèse réglementaire">
            <div className="grid md:grid-cols-2 gap-4">
              {syntheseRegl.obligations_prioritaires && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-2">📌 Obligations prioritaires</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {syntheseRegl.obligations_prioritaires.map((o: string, i: number) => <li key={i}>• {o}</li>)}
                  </ul>
                </div>
              )}
              {syntheseRegl.risques_reglementaires && (
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <p className="font-semibold text-red-800 mb-2">⚠️ Risques réglementaires</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {syntheseRegl.risques_reglementaires.map((r: string, i: number) => <li key={i}>• {r}</li>)}
                  </ul>
                </div>
              )}
              {syntheseRegl.opportunites && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-2">💡 Opportunités</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {syntheseRegl.opportunites.map((o: string, i: number) => <li key={i}>• {o}</li>)}
                  </ul>
                </div>
              )}
              {syntheseRegl.preparation_phase2 && (
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <p className="font-semibold text-purple-800 mb-2">🚀 Préparation Phase 2</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {syntheseRegl.preparation_phase2.map((p: string, i: number) => <li key={i}>• {p}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Orientations stratégiques */}
        {Object.keys(orientations).length > 0 && (
          <Section icon="🎯" title="Orientations stratégiques">
            <div className="grid md:grid-cols-3 gap-4">
              {orientations.court_terme_6mois && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-2">📅 Court terme (6 mois)</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {orientations.court_terme_6mois.map((a: string, i: number) => <li key={i}>• {a}</li>)}
                  </ul>
                </div>
              )}
              {orientations.moyen_terme_12mois && (
                <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                  <p className="font-semibold text-amber-800 mb-2">📅 Moyen terme (12 mois)</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {orientations.moyen_terme_12mois.map((a: string, i: number) => <li key={i}>• {a}</li>)}
                  </ul>
                </div>
              )}
              {orientations.long_terme_24mois && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-2">📅 Long terme (24 mois)</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {orientations.long_terme_24mois.map((a: string, i: number) => <li key={i}>• {a}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC6
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // BLOC 7: SYNTHÈSE - STRUCTURE RÉELLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderBloc7 = (data: any) => {
    if (!data) return <LoadingBloc name="Synthèse Stratégique" icon="📋" />;

    const intro = data.introduction_executive || {};
    const consolidation = data.consolidation_indices || {};
    const swot = data.diagnostic_swot_plus || {};
    const positionnement = data.positionnement_strategique || {};
    const feuilleRoute = data.feuille_route_transition || {};
    const cartographie = data.cartographie_risques_opportunites || {};
    const financement = data.options_financement || {};
    const partenariats = data.partenariats_alliances || {};
    const conclusion = data.conclusion_strategique || {};

    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-slate-700 to-slate-900 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-4xl">📋</span>
            <div>
              <h2 className="text-2xl font-bold">BLOC 7 — Rapport Intégré de Synthèse (Phase 1)</h2>
              <p className="text-slate-300">Vision stratégique intégrée et orientation vers la transition</p>
            </div>
          </div>
        </div>

        {/* Introduction Executive */}
        {Object.keys(intro).length > 0 && (
          <Section icon="📝" title="Introduction Executive">
            <div className="space-y-4">
              {intro.profil_resume && (
                <div className="bg-slate-50 rounded-lg p-4 border">
                  <p className="font-semibold text-slate-700 mb-1">Profil</p>
                  <p className="text-sm text-slate-600">{intro.profil_resume}</p>
                </div>
              )}
              {intro.objectif_analyse && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-1">🎯 Objectif</p>
                  <p className="text-sm text-slate-700">{intro.objectif_analyse}</p>
                </div>
              )}
              {intro.vision_synthetique && (
                <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
                  <p className="font-semibold text-emerald-800 mb-1">👁️ Vision synthétique</p>
                  <p className="text-sm text-slate-700">{intro.vision_synthetique}</p>
                </div>
              )}
              {intro.enjeux_majeurs && (
                <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                  <p className="font-semibold text-amber-800 mb-2">⚡ Enjeux majeurs</p>
                  <ul className="text-sm text-slate-700 space-y-1">
                    {intro.enjeux_majeurs.map((e: string, i: number) => <li key={i}>• {e}</li>)}
                  </ul>
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Consolidation des indices */}
        {Object.keys(consolidation).length > 0 && (
          <Section icon="📊" title="Consolidation des indices (Blocs 1-6)">
            {/* Indices des blocs */}
            {consolidation.blocs_1_6 && (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
                {consolidation.blocs_1_6.map((bloc: any, i: number) => (
                  <div key={i} className="bg-slate-50 rounded-lg p-3 border text-center">
                    <span className="text-xs text-slate-500">{bloc.bloc}</span>
                    <p className="font-semibold text-slate-700 text-sm">{bloc.indice}</p>
                    <span className="text-2xl font-bold text-blue-600">{bloc.score}</span>
                    <p className="text-xs text-slate-500 mt-1">{bloc.interpretation}</p>
                  </div>
                ))}
              </div>
            )}
            {/* Indices de synthèse BLOC7 */}
            {consolidation.indices_synthese_bloc7 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {Object.entries(consolidation.indices_synthese_bloc7).map(([key, val]: [string, any]) => (
                  <div key={key} className={`rounded-lg p-3 border text-center ${
                    (val?.score || 0) >= 75 ? 'bg-green-50 border-green-200' :
                    (val?.score || 0) >= 50 ? 'bg-amber-50 border-amber-200' :
                    'bg-red-50 border-red-200'
                  }`}>
                    <span className="text-xs font-bold text-slate-600">{key}</span>
                    <p className="text-2xl font-bold">{val?.score || 0}</p>
                    <span className="text-xs text-slate-500">{val?.niveau}</span>
                  </div>
                ))}
              </div>
            )}
            {consolidation.commentaire_global && (
              <p className="text-sm text-slate-600 mt-4 italic">{consolidation.commentaire_global}</p>
            )}
          </Section>
        )}

        {/* SWOT+ */}
        {Object.keys(swot).length > 0 && (
          <Section icon="🎯" title="Diagnostic SWOT+">
            <div className="grid md:grid-cols-2 gap-4">
              {/* Forces */}
              {swot.forces && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-3">💪 Forces</p>
                  {swot.forces.map((f: any, i: number) => (
                    <div key={i} className="mb-2 text-sm text-slate-700 bg-white rounded p-2">
                      <p className="font-medium">{f.element}</p>
                      <span className="text-xs text-slate-500">Confiance: {f.score_confiance}% | Source: {f.source_bloc}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Faiblesses */}
              {swot.faiblesses && (
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <p className="font-semibold text-red-800 mb-3">⚠️ Faiblesses</p>
                  {swot.faiblesses.map((f: any, i: number) => (
                    <div key={i} className="mb-2 text-sm text-slate-700 bg-white rounded p-2">
                      <p className="font-medium">{f.element}</p>
                      <span className="text-xs text-slate-500">Criticité: {f.criticite} | Urgence: {f.urgence}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Opportunités */}
              {swot.opportunites && (
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <p className="font-semibold text-blue-800 mb-3">💡 Opportunités</p>
                  {swot.opportunites.map((o: any, i: number) => (
                    <div key={i} className="mb-2 text-sm text-slate-700 bg-white rounded p-2">
                      <p className="font-medium">{o.element}</p>
                      <span className="text-xs text-slate-500">Potentiel: {o.potentiel} | Horizon: {o.horizon}</span>
                    </div>
                  ))}
                </div>
              )}
              {/* Menaces */}
              {swot.menaces && (
                <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
                  <p className="font-semibold text-amber-800 mb-3">⚡ Menaces</p>
                  {swot.menaces.map((m: any, i: number) => (
                    <div key={i} className="mb-2 text-sm text-slate-700 bg-white rounded p-2">
                      <p className="font-medium">{m.element}</p>
                      <span className="text-xs text-slate-500">Probabilité: {m.probabilite} | Impact: {m.impact}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* Tendances */}
            {swot.tendances && (
              <div className="mt-4 bg-purple-50 rounded-lg p-4 border border-purple-200">
                <p className="font-semibold text-purple-800 mb-2">📈 Tendances</p>
                <div className="flex flex-wrap gap-2">
                  {swot.tendances.map((t: any, i: number) => (
                    <span key={i} className={`px-3 py-1 rounded-full text-sm ${
                      t.direction === 'Positive' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'
                    }`}>
                      {t.element} ({t.vitesse})
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Section>
        )}

        {/* Positionnement stratégique */}
        {Object.keys(positionnement).length > 0 && (
          <Section icon="🏢" title="Positionnement stratégique">
            <SafeDisplay data={positionnement} />
          </Section>
        )}

        {/* Feuille de route */}
        {Object.keys(feuilleRoute).length > 0 && (
          <Section icon="🗺️" title="Feuille de route Transition">
            <div className="space-y-4">
              {Object.entries(feuilleRoute).map(([axeKey, axe]: [string, any]) => (
                <div key={axeKey} className="bg-slate-50 rounded-lg p-4 border">
                  <p className="font-bold text-slate-800 mb-2">{axeKey.replace(/_/g, ' ').toUpperCase()}</p>
                  {axe.objectif && <p className="text-sm text-slate-600 mb-3">🎯 {axe.objectif}</p>}
                  {axe.actions && (
                    <div className="grid md:grid-cols-2 gap-2">
                      {axe.actions.map((action: any, i: number) => (
                        <div key={i} className="bg-white rounded p-3 border text-sm">
                          <p className="font-medium text-slate-800">{action.id}. {action.description}</p>
                          <div className="flex gap-2 mt-1 flex-wrap">
                            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{action.horizon}</span>
                            {action.kpi && <span className="text-xs text-slate-500">KPI: {action.kpi}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Cartographie risques/opportunités */}
        {Object.keys(cartographie).length > 0 && (
          <Section icon="📊" title="Cartographie Risques & Opportunités">
            <div className="grid md:grid-cols-2 gap-4">
              {cartographie.matrice_risques && (
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <p className="font-semibold text-red-800 mb-3">⚠️ Matrice des risques</p>
                  {cartographie.matrice_risques.map((r: any, i: number) => (
                    <div key={i} className="mb-3 bg-white rounded p-3 border text-sm">
                      <p className="font-medium text-slate-800">{r.risque}</p>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        <span className="px-2 py-0.5 bg-slate-200 rounded text-xs">{r.categorie}</span>
                        <span className={`px-2 py-0.5 rounded text-xs ${r.probabilite === 'Haute' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'}`}>
                          P: {r.probabilite}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs ${r.impact === 'Critique' ? 'bg-red-200 text-red-800' : 'bg-orange-200 text-orange-800'}`}>
                          I: {r.impact}
                        </span>
                      </div>
                      {r.mitigation && <p className="text-xs text-slate-500 mt-1">→ {r.mitigation}</p>}
                    </div>
                  ))}
                </div>
              )}
              {cartographie.matrice_opportunites && (
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <p className="font-semibold text-green-800 mb-3">💡 Matrice des opportunités</p>
                  {cartographie.matrice_opportunites.map((o: any, i: number) => (
                    <div key={i} className="mb-3 bg-white rounded p-3 border text-sm">
                      <p className="font-medium text-slate-800">{o.opportunite}</p>
                      <div className="flex gap-2 mt-1 flex-wrap">
                        <span className="px-2 py-0.5 bg-slate-200 rounded text-xs">{o.categorie}</span>
                        <span className="px-2 py-0.5 bg-blue-200 text-blue-800 rounded text-xs">Potentiel: {o.potentiel}</span>
                        <span className="px-2 py-0.5 bg-green-200 text-green-800 rounded text-xs">{o.horizon}</span>
                      </div>
                      {o.actions && <p className="text-xs text-slate-500 mt-1">→ {o.actions}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Section>
        )}

        {/* Options de financement */}
        {Object.keys(financement).length > 0 && (
          <Section icon="💰" title="Options de financement">
            <div className="mb-4">
              <span className="text-lg font-semibold text-slate-700">Score IPF (Préparation Financement):</span>
              <span className="ml-2 text-2xl font-bold text-emerald-600">{financement.score_ipf || 0}/100</span>
            </div>
            <SafeDisplay data={Object.fromEntries(Object.entries(financement).filter(([k]) => k !== 'score_ipf'))} />
          </Section>
        )}

        {/* Partenariats */}
        {Object.keys(partenariats).length > 0 && (
          <Section icon="🤝" title="Partenariats & Alliances">
            <SafeDisplay data={partenariats} />
          </Section>
        )}

        {/* Conclusion stratégique */}
        {Object.keys(conclusion).length > 0 && (
          <Section icon="🏁" title="Conclusion stratégique">
            {conclusion.message_synthese && (
              <div className="bg-slate-700 text-white rounded-lg p-4 mb-4">
                <p className="text-lg">{conclusion.message_synthese}</p>
              </div>
            )}
            {/* Prochaines étapes */}
            {conclusion.prochaines_etapes && (
              <div className="mb-4">
                <p className="font-semibold text-slate-700 mb-2">🚀 Prochaines étapes</p>
                <div className="grid md:grid-cols-3 gap-3">
                  {conclusion.prochaines_etapes.map((etape: any, i: number) => (
                    <div key={i} className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                      <p className="font-medium text-blue-800">{etape.action}</p>
                      <p className="text-xs text-slate-600">Délai: {etape.delai}</p>
                      <p className="text-xs text-slate-600">Responsable: {etape.responsable}</p>
                      <p className="text-xs text-slate-500">Budget: {etape.budget_estime}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Métriques de suivi */}
            {conclusion.metriques_suivi && (
              <div className="bg-slate-50 rounded-lg p-4 border">
                <p className="font-semibold text-slate-700 mb-2">📊 Métriques de suivi</p>
                <SafeDisplay data={conclusion.metriques_suivi} />
              </div>
            )}
          </Section>
        )}

        {/* Debug */}
        <details className="bg-white rounded-xl border overflow-hidden">
          <summary className="px-6 py-4 cursor-pointer font-medium text-slate-600 hover:bg-slate-50">
            🔍 Voir les données brutes BLOC7
          </summary>
          <div className="p-6 bg-slate-50 overflow-auto max-h-96">
            <pre className="text-xs text-slate-600">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </details>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // VUE D'ENSEMBLE
  // ═══════════════════════════════════════════════════════════════════════════

  const renderOverview = () => {
    const completedCount = Object.values(blocsStatus).filter(b => b.status === 'completed').length;
    
    return (
      <div className="space-y-6">
        {/* Progress */}
        {!allCompleted && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="font-semibold text-blue-900">Analyse en cours</p>
                <p className="text-sm text-blue-600">{completedCount}/7 blocs complétés</p>
              </div>
              <span className="text-2xl font-bold text-blue-600">{globalProgress}%</span>
            </div>
            <div className="w-full bg-blue-100 rounded-full h-3">
              <div className="bg-blue-600 h-3 rounded-full transition-all" style={{ width: `${globalProgress}%` }} />
            </div>
          </div>
        )}

        {/* Config */}
        {questionnaireData && (
          <Section icon="⚙️" title="Configuration de l'analyse">
            <div className="grid md:grid-cols-4 gap-4">
              <div className="bg-slate-50 rounded-lg p-4"><p className="text-slate-500 text-sm">Secteur</p><p className="font-semibold text-slate-800">{questionnaireData.secteur || 'N/A'}</p></div>
              <div className="bg-slate-50 rounded-lg p-4"><p className="text-slate-500 text-sm">Profil</p><p className="font-semibold text-slate-800">{questionnaireData.profilOrganisation || 'N/A'}</p></div>
              <div className="bg-slate-50 rounded-lg p-4"><p className="text-slate-500 text-sm">Pays</p><p className="font-semibold text-slate-800">{questionnaireData.paysInstallation || 'N/A'}</p></div>
              <div className="bg-slate-50 rounded-lg p-4"><p className="text-slate-500 text-sm">Zone</p><p className="font-semibold text-slate-800">{questionnaireData.zoneGeographique || 'N/A'}</p></div>
            </div>
          </Section>
        )}

        {/* Blocs status */}
        <Section icon="📊" title="Progression des 7 blocs">
          <div className="grid md:grid-cols-4 lg:grid-cols-7 gap-3">
            {TABS.filter(t => t.id !== 'overview').map((tab) => {
              const hasData = !!blocsData[tab.blocId];
              const status = blocsStatus[tab.blocId]?.status || 'pending';
              return (
                <button
                  key={tab.id}
                  onClick={() => hasData && setActiveTab(tab.id)}
                  disabled={!hasData}
                  className={`p-4 rounded-xl text-center transition-all ${
                    hasData ? 'bg-emerald-50 border-2 border-emerald-300 cursor-pointer hover:shadow-md hover:border-emerald-400' :
                    status === 'running' ? 'bg-blue-50 border-2 border-blue-300 animate-pulse' :
                    'bg-slate-50 border-2 border-slate-200 opacity-60'
                  }`}
                >
                  <span className="text-3xl block mb-2">{tab.icon}</span>
                  <span className="text-sm font-semibold text-slate-700 block">{tab.label}</span>
                  <p className={`text-xs mt-1 font-medium ${
                    hasData ? 'text-emerald-600' : status === 'running' ? 'text-blue-600' : 'text-slate-400'
                  }`}>
                    {hasData ? '✓ Prêt' : status === 'running' ? '⏳ En cours' : '⏸ Attente'}
                  </p>
                </button>
              );
            })}
          </div>
        </Section>

        {/* Résumé des indices si BLOC1 est disponible */}
        {blocsData.BLOC1 && (
          <Section icon="📈" title="Indices PESTEL+ (Bloc 1)">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {Object.entries(blocsData.BLOC1.indices || {}).slice(0, 10).map(([key, val]: [string, any]) => (
                <ScoreCard 
                  key={key} 
                  label={key.replace(/_/g, ' ')} 
                  value={typeof val === 'object' ? val.score : val}
                  color={['blue', 'green', 'amber', 'purple', 'orange'][Math.floor(Math.random() * 5)]}
                />
              ))}
            </div>
          </Section>
        )}
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // ROUTING
  // ═══════════════════════════════════════════════════════════════════════════

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'bloc1': return renderBloc1(blocsData.BLOC1);
      case 'bloc2': return renderBloc2(blocsData.BLOC2);
      case 'bloc3': return renderBloc3(blocsData.BLOC3);
      case 'bloc4': return renderBloc4(blocsData.BLOC4);
      case 'bloc5': return renderBloc5(blocsData.BLOC5);
      case 'bloc6': return renderBloc6(blocsData.BLOC6);
      case 'bloc7': return renderBloc7(blocsData.BLOC7);
      default: return null;
    }
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // LOADING
  // ═══════════════════════════════════════════════════════════════════════════

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
          <p className="text-slate-600">Chargement du dashboard...</p>
        </div>
      </div>
    );
  }

  if (Object.keys(blocsData).length === 0 && Object.keys(blocsStatus).length === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="bg-white rounded-xl border p-12 max-w-lg text-center shadow-lg">
          <span className="text-6xl block mb-4">📊</span>
          <h2 className="text-2xl font-bold mb-3 text-slate-900">Aucune analyse disponible</h2>
          <p className="text-slate-500 mb-6">Remplissez le questionnaire pour générer une analyse stratégique complète.</p>
          <a href="/" className="px-6 py-3 bg-blue-900 text-white rounded-lg font-medium hover:bg-blue-800 inline-block transition-colors">
            🚀 Démarrer une analyse
          </a>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // MAIN RENDER
  // ═══════════════════════════════════════════════════════════════════════════

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Africa Strategy Dashboard</h1>
            <p className="text-sm text-slate-500">
              {allCompleted ? '✅ Analyse complète' : `⏳ Analyse en cours... ${globalProgress}%`}
            </p>
          </div>
          <div className="flex gap-3">
            <a href="/" className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-700 font-medium transition-colors">
              Nouvelle analyse
            </a>
            <button 
              onClick={() => setChatOpen(true)} 
              className="px-4 py-2 bg-blue-900 text-white rounded-lg hover:bg-blue-800 font-medium transition-colors flex items-center gap-2"
            >
              💬 Assistant IA
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b sticky top-[73px] z-20 overflow-x-auto shadow-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;
              const hasData = !!blocsData[tab.blocId] || tab.id === 'overview';
              return (
                <button
                  key={tab.id}
                  onClick={() => (hasData || tab.id === 'overview') && setActiveTab(tab.id)}
                  disabled={!hasData && tab.id !== 'overview'}
                  className={`px-4 py-3 text-sm font-medium flex items-center gap-2 border-b-2 whitespace-nowrap transition-all ${
                    isActive ? 'border-blue-900 text-blue-900 bg-blue-50' :
                    hasData || tab.id === 'overview' ? 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-50' :
                    'border-transparent text-slate-400 cursor-not-allowed'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {renderContent()}
      </main>

      {/* Bouton flottant Chatbot */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 rounded-full shadow-lg flex items-center justify-center text-white transition-all hover:scale-105 z-40"
          title="Assistant IA"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Chatbot Modal */}
      <Chatbot isOpen={chatOpen} onClose={() => setChatOpen(false)} analysisData={blocsData} />
    </div>
  );
}
