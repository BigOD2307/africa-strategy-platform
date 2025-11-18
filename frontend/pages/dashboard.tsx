'use client';

import { useState, useEffect, ReactNode } from 'react';
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
import { Radar, Bar, Doughnut, Line } from 'react-chartjs-2';
import clsx from 'clsx';
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

ChartJS.defaults.font.family = 'Inter, system-ui, -apple-system, BlinkMacSystemFont, Helvetica Neue, sans-serif';
ChartJS.defaults.color = '#475569';
ChartJS.defaults.plugins.legend.labels.usePointStyle = true;
ChartJS.defaults.plugins.legend.labels.pointStyleWidth = 8;
ChartJS.defaults.plugins.tooltip.backgroundColor = 'rgba(15,23,42,0.95)';
ChartJS.defaults.plugins.tooltip.borderColor = 'rgba(59,130,246,0.4)';
ChartJS.defaults.plugins.tooltip.borderWidth = 1;

const chartPalette = ['#2563eb', '#38bdf8', '#22c55e', '#f97316', '#a855f7', '#f43f5e'];

type TabType = 'overview' | 'pestel' | 'esg' | 'market' | 'risk' | 'synthesis';

const glassPanelClass = 'rounded-[28px] border border-white/20 bg-white/90 shadow-[0_25px_80px_rgba(15,23,42,0.12)] backdrop-blur-xl';
const frostedCardClass = 'rounded-2xl border border-white/20 bg-white/80 shadow-[0_20px_45px_rgba(15,23,42,0.08)] backdrop-blur';
const subtleCardClass = 'rounded-2xl border border-white/10 bg-slate-900/5';

const sectionEyebrowClass = 'text-[11px] font-semibold uppercase tracking-[0.4em] text-slate-500';
const metricValueClass = 'text-4xl font-semibold text-slate-900';

type PanelProps = {
  title?: string;
  eyebrow?: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
  children: ReactNode;
  contentClassName?: string;
};

const Panel = ({ title, eyebrow, description, actions, className, children, contentClassName }: PanelProps) => (
  <div className={clsx(glassPanelClass, 'p-6 lg:p-8', className)}>
    {(eyebrow || title || description || actions) && (
      <div className="mb-6 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div>
          {eyebrow && <p className={sectionEyebrowClass}>{eyebrow}</p>}
          {title && <h3 className="text-xl font-semibold text-slate-900">{title}</h3>}
          {description && <p className="text-sm text-slate-500">{description}</p>}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
    )}
    <div className={clsx('space-y-4', contentClassName)}>
      {children}
    </div>
  </div>
);

const ChartPanel = ({ title, eyebrow, description, height = 320, children, className }: PanelProps & { height?: number }) => (
  <Panel title={title} eyebrow={eyebrow} description={description} className={clsx('p-0', className)} contentClassName="p-6 lg:p-8">
    <div style={{ height }} className="relative">
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white via-slate-50 to-white opacity-90" />
      <div className="relative h-full">{children}</div>
    </div>
  </Panel>
);

const getSectionData = (analyses: any, keys: string[]) => {
  if (!analyses) return {};
  for (const key of keys) {
    if (analyses[key]) {
      return analyses[key];
    }
  }
  return {};
};

const capitalizeLabel = (label: string) => {
  if (!label) return '';
  return label
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
};

const toArray = (value: any): any[] => {
  if (!value) return [];
  return Array.isArray(value) ? value : [value];
};

const uniqueStrings = (items: any[]): string[] => {
  const flattened = items.flat().filter(Boolean).map((item) => (typeof item === 'string' ? item : JSON.stringify(item)));
  return Array.from(new Set(flattened));
};

const extractNumber = (value: any): number => {
  if (typeof value === 'number') return value;
  if (typeof value !== 'string') return 0;
  const cleaned = value.replace(/[^\d,.-]/g, '').replace(',', '.');
  const parsed = parseFloat(cleaned);
  return Number.isFinite(parsed) ? parsed : 0;
};

export default function Dashboard() {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [enrichedData, setEnrichedData] = useState<any>(null);
  const [questionnaireData, setQuestionnaireData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [chatOpen, setChatOpen] = useState(false);
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const enrichedAnalyses = enrichedData?.enriched_analyses || {};
  const enrichedSynthesis = enrichedData?.enriched_synthesis || {};

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = sessionStorage.getItem('analysisResult');
      if (stored) {
        try {
          const data = JSON.parse(stored);
          console.log('Données complètes de l\'IA:', data);
          console.log('Taille totale:', JSON.stringify(data).length, 'caractères');
          setAnalysisData(data);
          
          // Enrichir automatiquement les analyses avec OpenRouter
          enrichAnalyses(data);
        } catch (err) {
          console.error('Erreur parsing:', err);
        }
      }
      const storedForm = sessionStorage.getItem('questionnaireData');
      if (storedForm) {
        try {
          setQuestionnaireData(JSON.parse(storedForm));
        } catch (err) {
          console.error('Erreur parsing questionnaire:', err);
        }
      }
      setLoading(false);
    }
  }, []);

  const enrichAnalyses = async (data: any) => {
    setEnriching(true);
    try {
      console.log('🚀 Enrichissement des analyses avec OpenRouter...');
      const response = await fetch(`${API_BASE_URL}/api/enrich`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analyses: data.analyses || data
        }),
      });

      if (response.ok) {
        const enriched = await response.json();
        console.log('✅ Analyses enrichies:', enriched);
        setEnrichedData(enriched);
      } else {
        console.error('❌ Erreur lors de l\'enrichissement');
      }
    } catch (error) {
      console.error('❌ Erreur lors de l\'enrichissement:', error);
    } finally {
      setEnriching(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 text-center text-white">
        <div className="flex flex-col items-center gap-4">
          <div className="h-16 w-16 animate-spin rounded-full border-4 border-white/10 border-t-blue-400" />
          <p className="text-lg text-slate-200">Chargement des résultats...</p>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4">
        <div className={clsx(glassPanelClass, 'max-w-md text-center text-slate-900')}>
          <h2 className="text-2xl font-semibold text-slate-900">Aucune analyse disponible</h2>
          <p className="mt-2 text-slate-500">Veuillez compléter le formulaire d'abord.</p>
          <button
            onClick={() => window.location.href = '/'}
            className="mt-6 inline-flex items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition hover:translate-y-0.5 hover:shadow-xl"
          >
            Retour au formulaire
          </button>
        </div>
      </div>
    );
  }

  // Extraire TOUTES les données de l'IA avec correspondances multiples
  const questionnaire = questionnaireData || analysisData.form_inputs || analysisData.input_form || {};
  const analyses = analysisData.analyses || analysisData || {};
  const pestel = getSectionData(analyses, ['pestel']) || {};
  const esg = getSectionData(analyses, ['esg']) || {};
  const market = getSectionData(analyses, ['market', 'marche', 'marche_competition', 'analyse_marche', 'marché']) || {};
  const valueChain = getSectionData(analyses, ['value_chain', 'chaine_valeur', 'chaineValue', 'chaine', 'valuechain']) || {};
  const impact = getSectionData(analyses, ['impact_durable', 'impact', 'impact_durabilite', 'impact_durable_global']) || {};
  const synthesis = getSectionData(analyses, ['synthesis', 'synthese', 'synthese_globale']) || {};
  const risk = getSectionData(analyses, ['risk', 'risques', 'risk_analysis']) || {};
  const pipeline = analysisData.pipeline_analytique || {};
  const metadata = analysisData.metadata || {};
  const company = metadata.entreprise || {};
  const sources = metadata.sources_utilisees || {};
  const pipelineIndicators = pipeline.indicateurs || [];
  const themeIndices = pipeline.indices_thematiques || {};
  const globalIndices = pipeline.indices_globaux || {};
  const credibilite = pipeline.indices_credibilite || {};
  const roadmap = analysisData.roadmap_strategique || {};
  const pestelDetails = pestel.analyse_detaillee || pestel.details || {};
  const esgDetails = esg.analyse_detaillee || esg.details || {};
  const esgOdd = esg.contribution_odd || esg.contribution || {};
  const marketSize = market.taille_marche || {};
  const marketProjections = marketSize.projections || {};
  const competitors = toArray(market.concurrents);
  const marketOpportunities = toArray(market.opportunites || market.opportunities);
  const marketThreats = toArray(market.menaces || market.threats);
  const marketTrendNarrative = market.tendances || market.tendances_2025 || '';
  const valueChainPrimary = valueChain.activites_primaires || {};
  const valueChainSupport = valueChain.activites_support || {};
  const impactPrep = impact.preparation_imm || impact.preparation || {};
  const impactOdd = impact.contribution_odd || impact.contribution || {};
  const pestelRecommendationsGlobal = toArray(pestel.recommandations_prioritaires || pestel.recommendations);
  const esgRecommendationsGlobal = toArray(esg.recommendations);
  const riskRecommendationsGlobal = toArray(risk.recommendations || risk.recommandations || []);
  const synthesisRecommendationsGlobal = Array.isArray(synthesis.recommendations) ? synthesis.recommendations : [];
  const companyProfile = {
    name: (company.nom || questionnaire.nomEntreprise || questionnaire.raisonSociale || 'Organisation analysée').trim(),
    sector: company.secteur || questionnaire.secteur || 'Secteur non précisé',
    zone: company.zone_geographique || questionnaire.zoneGeographique || 'Zone non précisée',
    country: company.pays || questionnaire.paysInstallation || 'Pays non précisé',
    profile: questionnaire.profilOrganisation || 'Profil non précisé',
    vision: questionnaire.visionOrganisation || '',
    mission: questionnaire.missionOrganisation || '',
    positioning: questionnaire.positionnementStrategique || '',
    projects: questionnaire.projetsSignificatifs || ''
  };
  const computedSources = {
    ...sources,
    formulaire_utilisateur: true,
    objectifs_dd: questionnaire.objectifsDD || [],
    documents_rag_consultes: sources.documents_rag_consultes || [],
    sites_web_consultes: sources.sites_web_consultes || [],
  };
  const sourceStatus = [
    { label: 'Connaissances internes', value: computedSources.connaissances_internes },
    { label: 'Base RAG', value: computedSources.base_donnees_rag || computedSources['base_données_rag'] },
    { label: 'Recherche internet', value: computedSources.recherche_internet },
    { label: 'Formules appliquées', value: metadata?.traçabilite?.formules_appliquees },
    { label: 'Sources citées', value: metadata?.traçabilite?.sources_citees }
  ];
  const objectivesList = questionnaire.objectifsDD || computedSources.objectifs_dd || [];
  const credibilityInterpretation = credibilite.interpretation || '';
  const pestelRiskList = Object.values(pestelDetails).flatMap((section: any) => toArray((section as any)?.risques || (section as any)?.risks));
  const valueChainRiskPrimary = Object.values(valueChainPrimary).flatMap((activity: any) => toArray(activity?.risques || activity?.alertes));
  const valueChainRiskSupport = Object.values(valueChainSupport).flatMap((activity: any) => toArray(activity?.risques || activity?.alertes));
  const impactRiskList = Object.values(impactPrep).map((value: any) => (typeof value === 'string' ? value : JSON.stringify(value)));
  const allRisks = uniqueStrings([
    pestelRiskList,
    marketThreats,
    valueChainRiskPrimary,
    valueChainRiskSupport,
    impactRiskList
  ]);
  const pestelOpportunities = Object.values(pestelDetails).flatMap((section: any) => toArray((section as any)?.opportunites || (section as any)?.['opportunités']));
  const valueChainOpportunities = [
    ...Object.values(valueChainPrimary).flatMap((activity: any) => toArray(activity?.optimisations)),
    ...Object.values(valueChainSupport).flatMap((activity: any) => toArray(activity?.optimisations))
  ];
  const aggregatedOpportunities = uniqueStrings([
    pestelOpportunities,
    marketOpportunities,
    valueChainOpportunities
  ]).slice(0, 8);
  const aggregatedRecommendations = uniqueStrings([
    pestelRecommendationsGlobal,
    esgRecommendationsGlobal,
    riskRecommendationsGlobal,
    synthesisRecommendationsGlobal
  ]).slice(0, 8);

  // Scores PESTEL avec toutes les variantes possibles
  const pestelScores = pestel.scores || {};
  const pestelData = {
    labels: ['Politique', 'Économique', 'Social', 'Technologique', 'Environnemental', 'Légal'],
    datasets: [{
      label: 'Score PESTEL',
      data: [
        pestelScores.political || pestelScores.politique || pestelScores.P || 0,
        pestelScores.economic || pestelScores.economique || pestelScores.E || 0,
        pestelScores.social || pestelScores.S || 0,
        pestelScores.technological || pestelScores.technologique || pestelScores.T || 0,
        pestelScores.environmental || pestelScores.environnemental || pestelScores.Env || 0,
        pestelScores.legal || pestelScores.legal || pestelScores.L || 0,
      ],
      backgroundColor: 'rgba(37,99,235,0.18)',
      borderColor: '#2563eb',
      borderWidth: 2,
      pointBackgroundColor: '#2563eb',
      pointBorderWidth: 2,
      pointHoverRadius: 5,
      fill: true
    }]
  };

  // Graphique PESTEL par dimension (Bar)
  const pestelBarData = {
    labels: ['Politique', 'Économique', 'Social', 'Technologique', 'Environnemental', 'Légal'],
    datasets: [{
      label: 'Scores PESTEL',
      data: [
        pestelScores.political || pestelScores.politique || pestelScores.P || 0,
        pestelScores.economic || pestelScores.economique || pestelScores.E || 0,
        pestelScores.social || pestelScores.S || 0,
        pestelScores.technological || pestelScores.technologique || pestelScores.T || 0,
        pestelScores.environmental || pestelScores.environnemental || pestelScores.Env || 0,
        pestelScores.legal || pestelScores.legal || pestelScores.L || 0,
      ],
      backgroundColor: chartPalette.map((color) => `${color}33`),
      borderColor: chartPalette,
      borderWidth: 1.5,
      borderRadius: 14,
      borderSkipped: false
    }]
  };

  // Scores ESG
  const esgScores = esg.scores || {};
  const esgData = {
    labels: ['Environnemental', 'Social', 'Gouvernance'],
    datasets: [{
      label: 'Score ESG',
      data: [
        esgScores.environmental || esgScores.environnemental || 0,
        esgScores.social || 0,
        esgScores.governance || esgScores.gouvernance || 0,
      ],
    backgroundColor: ['#22c55e33', '#2563eb33', '#a855f733'],
    borderColor: ['#22c55e', '#2563eb', '#a855f7'],
    borderWidth: 1.5,
    borderRadius: 16,
    borderSkipped: false
    }]
  };

  // Graphique ESG Doughnut
  const esgDoughnutData = {
    labels: ['Environnemental', 'Social', 'Gouvernance'],
    datasets: [{
      data: [
        esgScores.environmental || esgScores.environnemental || 0,
        esgScores.social || 0,
        esgScores.governance || esgScores.gouvernance || 0,
      ],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(168, 85, 247, 0.8)',
      ],
      borderWidth: 0,
    }]
  };

  // Risque
  const computedRiskScore = risk.overall_score || risk.score || credibilite.IB7R || credibilite.niveau_maturite || 50;
  const riskScore = Math.round(typeof computedRiskScore === 'number' ? computedRiskScore : 50);
  const riskData = {
    labels: ['Risque', 'Sécurité'],
    datasets: [{
      data: [riskScore, 100 - riskScore],
      backgroundColor: [
      riskScore > 70 ? '#f43f5e' : riskScore > 40 ? '#f97316' : '#22c55e',
      '#e2e8f0',
      ],
    borderWidth: 0,
    hoverOffset: 4
    }]
  };

  // Graphique de risques par catégorie
  const baseRiskCategories = (risk.categories || risk.risques || {}) as Record<string, any>;
  const fallbackRiskCategories = Object.keys(baseRiskCategories).length > 0 ? baseRiskCategories : Object.fromEntries(
    Object.entries(pestelDetails).map(([key, detail]: [string, any]) => {
      const baseScore = Number(detail?.score || 50);
      const normalizedScore = baseScore > 10 ? baseScore : baseScore * 10;
      const severity = Math.max(0, 100 - normalizedScore);
      const riskCount = toArray(detail?.risques || detail?.risks).length * 5;
      return [key, Math.min(100, (severity + riskCount) || 0)];
    })
  );
  const riskCategories = fallbackRiskCategories;
  const riskCategoriesData = {
    labels: Object.keys(riskCategories).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
    datasets: [{
      label: 'Niveau de Risque',
      data: Object.values(riskCategories).map((v: any) => {
        if (typeof v === 'number') return v;
        if (typeof v === 'object' && v.score) return v.score;
        return 50;
      }),
    backgroundColor: '#f43f5e33',
    borderColor: '#f43f5e',
    borderWidth: 1.5,
    borderRadius: 12,
    borderSkipped: false
    }]
  };

  // Graphiques pour le marché (opportunités vs défis)
  const marketOpportunitiesCount = marketOpportunities.length;
  const marketChallengesCount = marketThreats.length || (market.challenges ? market.challenges.length : 0);
  const marketComparisonData = {
    labels: ['Opportunités', 'Défis'],
    datasets: [{
      label: 'Nombre',
      data: [marketOpportunitiesCount, marketChallengesCount],
      backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(239, 68, 68, 0.8)',
      ],
      borderColor: [
        'rgba(34, 197, 94, 1)',
        'rgba(239, 68, 68, 1)',
      ],
      borderWidth: 2,
    }]
  };

  // Graphique de tendance PESTEL (si données historiques disponibles)
  const pestelTrendData = {
    labels: ['Politique', 'Économique', 'Social', 'Technologique', 'Environnemental', 'Légal'],
    datasets: [{
      label: 'Scores Actuels',
      data: [
        pestelScores.political || pestelScores.politique || pestelScores.P || 0,
        pestelScores.economic || pestelScores.economique || pestelScores.E || 0,
        pestelScores.social || pestelScores.S || 0,
        pestelScores.technological || pestelScores.technologique || pestelScores.T || 0,
        pestelScores.environmental || pestelScores.environnemental || pestelScores.Env || 0,
        pestelScores.legal || pestelScores.legal || pestelScores.L || 0,
      ],
      borderColor: 'rgba(37, 99, 235, 1)',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4,
    }]
  };

  const themeRadarData = Object.keys(themeIndices).length > 0 ? {
    labels: Object.keys(themeIndices).map(capitalizeLabel),
    datasets: [{
      label: 'Indices thématiques',
      data: Object.values(themeIndices).map((value: any) => Number(value) || 0),
      backgroundColor: 'rgba(99,102,241,0.15)',
      borderColor: '#4c1d95',
      borderWidth: 2,
      pointBackgroundColor: '#4c1d95',
      pointBorderWidth: 2,
      pointHoverRadius: 4,
      fill: true
    }]
  } : null;

  const topIndicators = pipelineIndicators.slice(0, 6);
  const indicatorBarData = topIndicators.length > 0 ? {
    labels: topIndicators.map((indicator: any) => indicator.label || indicator.id),
    datasets: [{
      label: 'Scores normalisés',
      data: topIndicators.map((indicator: any) => indicator.score_normalise
        ?? indicator['score_normalisé']
        ?? indicator.score_pondere
        ?? indicator['score_pondéré']
        ?? indicator.valeur_brute
        ?? 0),
      backgroundColor: topIndicators.map((_: unknown, idx: number) => `${chartPalette[idx % chartPalette.length]}33`),
      borderColor: topIndicators.map((_: unknown, idx: number) => chartPalette[idx % chartPalette.length]),
      borderWidth: 1.5,
      borderRadius: 14,
      borderSkipped: false
    }]
  } : null;

  const globalIndicesEntries = Object.entries(globalIndices || {});
  const globalIndicesLineData = globalIndicesEntries.length > 0 ? {
    labels: globalIndicesEntries.map(([key]) => capitalizeLabel(key)),
    datasets: [{
      label: 'Indices globaux',
      data: globalIndicesEntries.map(([, value]) => Number(value) || 0),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37, 99, 235, 0.15)',
      tension: 0.45,
      fill: true,
      borderWidth: 3,
      pointRadius: 5,
      pointBackgroundColor: '#1d4ed8'
    }]
  } : null;

  const credibilityEntries = Object.entries(credibilite || {})
    .filter(([, value]) => typeof value === 'number') as [string, number][];

  const oddLabels = Object.keys(esgOdd);
  const oddContributionData = oddLabels.length > 0 ? {
    labels: oddLabels.map(capitalizeLabel),
    datasets: [
      {
        label: 'Contribution actuelle',
        data: oddLabels.map(key => esgOdd[key]?.score || esgOdd[key]?.contribution || 0),
        backgroundColor: '#2563eb33',
        borderColor: '#2563eb',
        borderWidth: 1.5,
        borderRadius: 14,
        borderSkipped: false
      },
      {
        label: 'Potentiel',
        data: oddLabels.map(key => esgOdd[key]?.potentiel || 0),
        backgroundColor: '#a855f733',
        borderColor: '#a855f7',
        borderWidth: 1.5,
        borderRadius: 14,
        borderSkipped: false
      }
    ]
  } : null;

  const buildValueChainDataset = (section: Record<string, any>, label: string, color: string) => {
    const entries = Object.entries(section);
    if (entries.length === 0) return null;
    return {
      labels: entries.map(([key]) => capitalizeLabel(key)),
      datasets: [{
        label,
        data: entries.map(([, value]) => Number(value?.score || 0)),
        backgroundColor: color,
        borderColor: color,
        borderWidth: 1.5,
        borderRadius: 12,
        borderSkipped: false
      }]
    };
  };

  const valueChainPrimaryData = buildValueChainDataset(valueChainPrimary, 'Activités primaires', 'rgba(245, 158, 11, 0.7)');
  const valueChainSupportData = buildValueChainDataset(valueChainSupport, 'Activités support', 'rgba(99, 102, 241, 0.7)');

  const projectionEntries = Object.entries(marketProjections || {});
  const marketProjectionChart = projectionEntries.length > 0 ? {
    labels: projectionEntries.map(([year]) => year),
    datasets: [{
      label: 'Projection marché (index)',
      data: projectionEntries.map(([, value]) => extractNumber(value) || 0),
      borderColor: '#16a34a',
      backgroundColor: 'rgba(22,163,74,0.15)',
      tension: 0.45,
      fill: true,
      borderWidth: 3,
      pointBackgroundColor: '#15803d',
      pointRadius: 4,
    }]
  } : null;

  const tabs = [
    { id: 'overview' as TabType, label: 'Vue d\'ensemble', icon: '📊' },
    { id: 'pestel' as TabType, label: 'PESTEL', icon: '🌍' },
    { id: 'esg' as TabType, label: 'ESG', icon: '🌱' },
    { id: 'market' as TabType, label: 'Marché', icon: '📈' },
    { id: 'risk' as TabType, label: 'Risques', icon: '⚠️' },
    { id: 'synthesis' as TabType, label: 'Synthèse', icon: '📝' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        const executiveSummary = synthesis.resume_executif || synthesis.summary || analysisData.summary || '';
        const overviewKeyPoints = synthesis.conclusions_cles || [];
        const overviewStats = [
          { label: 'Score PESTEL', value: pestelScores.overall || pestelScores.total || 0, description: 'Analyse macro-environnementale', icon: '🌍' },
          { label: 'Score ESG', value: esgScores.overall || esgScores.total || 0, description: 'Responsabilité sociale & gouvernance', icon: '🌱' },
          { label: 'Niveau de risque', value: riskScore ? `${riskScore}%` : '—', description: 'Vulnérabilité globale', icon: '⚠️' },
          { label: 'Opportunités clés', value: marketOpportunitiesCount, description: 'Détectées sur toutes les analyses', icon: '🚀' },
        ];

        return (
          <div className="space-y-8 pb-12">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className={sectionEyebrowClass}>Vue globale</p>
                <h2 className="text-3xl font-semibold text-slate-900">Vue d'ensemble</h2>
                <p className="text-slate-500">Résumé exécutif consolidé de l'intelligence stratégique générée par l'IA.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                <button className="inline-flex items-center rounded-full border border-white/20 bg-white/70 px-5 py-2.5 text-sm font-semibold text-slate-600 shadow-sm shadow-white/30 backdrop-blur transition hover:-translate-y-0.5 hover:text-slate-900">
                  Partager
                </button>
                <button className="inline-flex items-center rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:translate-y-0.5">
                  Télécharger le rapport
                </button>
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
              {overviewStats.map((stat) => (
                <div key={stat.label} className={clsx(glassPanelClass, 'relative overflow-hidden p-6')}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-500">{stat.label}</p>
                      <p className={clsx(metricValueClass, 'mt-2')}>{stat.value ?? '—'}</p>
                    </div>
                    <span className="text-3xl">{stat.icon}</span>
                  </div>
                  <p className="mt-4 text-sm text-slate-500">{stat.description}</p>
                  <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-b from-transparent via-indigo-50/60 to-white/80" />
                </div>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              <div className={clsx(glassPanelClass, 'p-6')}>
                <p className={sectionEyebrowClass}>Opportunités vs risques</p>
                <div className="mt-4 flex items-center gap-6">
                  <div>
                    <p className="text-3xl font-semibold text-indigo-900">{marketOpportunitiesCount}</p>
                    <p className="text-sm text-indigo-600">Opportunités clés</p>
                  </div>
                  <div className="h-12 w-px bg-white/40" />
                  <div>
                    <p className="text-3xl font-semibold text-amber-900">{allRisks.length || marketThreats.length}</p>
                    <p className="text-sm text-amber-600">Risques indexés</p>
                  </div>
                </div>
                <div className="mt-6 h-2 rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-rose-300"
                    style={{ width: `${Math.min(100, (marketOpportunitiesCount / Math.max(1, marketOpportunitiesCount + allRisks.length)) * 100)}%` }}
                  />
                </div>
              </div>

              <div className={clsx(glassPanelClass, 'p-6')}>
                <p className={sectionEyebrowClass}>Objectifs durables couverts</p>
                {objectivesList.length > 0 ? (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {objectivesList.map((objective: string, idx: number) => (
                      <span key={idx} className="rounded-full border border-emerald-100 bg-emerald-50/80 px-3 py-1 text-xs font-semibold text-emerald-700">
                        {objective}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-slate-500">Aucun objectif renseigné</p>
                )}
              </div>

              <div className={clsx(glassPanelClass, 'p-6')}>
                <p className={sectionEyebrowClass}>Crédibilité & maturité</p>
                <p className="mt-4 text-3xl font-semibold text-rose-900">{credibilite.niveau_maturite || '—'}</p>
                <p className="mt-2 text-sm text-rose-600">{credibilityInterpretation || 'Analyse qualitative en cours.'}</p>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.2fr_1fr_1fr]">
              <Panel title="Profil de l'entreprise" contentClassName="space-y-4">
                <dl className="grid gap-4 text-sm text-slate-600">
                  <div>
                    <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Organisation</dt>
                    <dd className="mt-1 text-base font-semibold text-slate-900">{companyProfile.name}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Secteur</dt>
                    <dd className="mt-1">{companyProfile.sector}</dd>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Zone</dt>
                      <dd className="mt-1">{companyProfile.zone}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Pays</dt>
                      <dd className="mt-1">{companyProfile.country}</dd>
                    </div>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Profil</dt>
                    <dd className="mt-1">{companyProfile.profile}</dd>
                  </div>
                  {companyProfile.positioning && (
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Positionnement</dt>
                      <dd className="mt-1 text-slate-700">{companyProfile.positioning}</dd>
                    </div>
                  )}
                  {companyProfile.vision && (
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Vision</dt>
                      <dd className="mt-1 whitespace-pre-line text-slate-700">{companyProfile.vision}</dd>
                    </div>
                  )}
                  {companyProfile.mission && (
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Mission</dt>
                      <dd className="mt-1 whitespace-pre-line text-slate-700">{companyProfile.mission}</dd>
                    </div>
                  )}
                  {companyProfile.projects && (
                    <div>
                      <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Projets clés</dt>
                      <dd className="mt-1 whitespace-pre-line text-slate-700">{companyProfile.projects}</dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-xs uppercase tracking-[0.3em] text-slate-400">Date d'analyse</dt>
                    <dd className="mt-1">{company.date_analyse || metadata.generated_at || '—'}</dd>
                  </div>
                </dl>
              </Panel>

              <Panel title="Sources & traçabilité" contentClassName="space-y-4">
                <div className="space-y-3 text-sm">
                  {sourceStatus.map((source) => (
                    <div key={source.label} className="flex items-center justify-between rounded-2xl border border-slate-100/60 bg-white/60 px-3 py-2 shadow-sm">
                      <span className="text-slate-600">{source.label}</span>
                      <span className={clsx('text-lg font-semibold', source.value ? 'text-emerald-500' : 'text-rose-500')}>
                        {source.value ? '✔' : '✕'}
                      </span>
                    </div>
                  ))}
                </div>
                {(computedSources.documents_rag_consultes || []).length > 0 && (
                  <div className="text-sm">
                    <p className="font-semibold text-slate-600">Documents clés</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-500">
                      {computedSources.documents_rag_consultes.slice(0, 4).map((doc: string, idx: number) => (
                        <li key={idx}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {(computedSources.sites_web_consultes || []).length > 0 && (
                  <div className="text-sm">
                    <p className="font-semibold text-slate-600">Sites consultés</p>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-slate-500">
                      {computedSources.sites_web_consultes.slice(0, 4).map((site: string, idx: number) => (
                        <li key={idx}>{site}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </Panel>

              <Panel title="Alignement stratégique" contentClassName="space-y-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Objectifs prioritaires</p>
                  {objectivesList.length > 0 ? (
                    <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-slate-600">
                      {objectivesList.map((obj: string, idx: number) => (
                        <li key={idx}>{obj}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-3 text-sm text-slate-500">Non renseigné</p>
                  )}
                </div>
                {impactOdd && Object.keys(impactOdd).length > 0 && (
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Contribution ODD</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {Object.keys(impactOdd).map((oddKey) => (
                        <span key={oddKey} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600">
                          {oddKey.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </Panel>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <ChartPanel title="Analyse PESTEL" eyebrow="Radar global" height={360}>
                <Radar data={pestelData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 100,
                      ticks: { stepSize: 20 },
                      grid: { color: 'rgba(148, 163, 184, 0.3)' }
                    }
                  },
                  plugins: { legend: { display: false } }
                }} />
              </ChartPanel>
              <ChartPanel title="Analyse ESG" eyebrow="Scores détaillés" height={360}>
                <Bar data={esgData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      ticks: { stepSize: 20 },
                      grid: { color: 'rgba(226, 232, 240, 0.5)' }
                    },
                    x: {
                      grid: { display: false }
                    }
                  },
                  plugins: { legend: { display: false } }
                }} />
              </ChartPanel>
            </div>

            {themeRadarData && (
              <ChartPanel title="Indices thématiques" eyebrow="Focus insights" height={360}>
                <Radar data={themeRadarData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 100,
                      ticks: { stepSize: 20 },
                      grid: { color: 'rgba(148, 163, 184, 0.3)' }
                    }
                  },
                  plugins: { legend: { display: false } }
                }} />
              </ChartPanel>
            )}

            {indicatorBarData && (
              <ChartPanel title="Top indicateurs suivis" eyebrow="Monitoring" height={360}>
                <Bar data={indicatorBarData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      ticks: { stepSize: 20 },
                      grid: { color: 'rgba(226, 232, 240, 0.5)' }
                    },
                    x: {
                      grid: { display: false }
                    }
                  },
                  plugins: { legend: { display: false } }
                }} />
              </ChartPanel>
            )}

            {globalIndicesLineData && (
              <ChartPanel title="Indice global comparatif" eyebrow="Momentum" height={360}>
                <Line data={globalIndicesLineData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      grid: { color: 'rgba(226, 232, 240, 0.5)' }
                    },
                    x: {
                      grid: { color: 'rgba(226, 232, 240, 0.3)' }
                    }
                  },
                  plugins: { legend: { display: false } }
                }} />
              </ChartPanel>
            )}

            {pipelineIndicators.length > 0 && (
              <Panel title="Pipeline analytique (extrait)" contentClassName="space-y-0">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-100 text-sm">
                    <thead>
                      <tr className="text-left text-xs uppercase tracking-[0.3em] text-slate-400">
                        <th className="px-4 py-3">Indicateur</th>
                        <th className="px-4 py-3">Valeur</th>
                        <th className="px-4 py-3">Score normalisé</th>
                        <th className="px-4 py-3">Source</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-600">
                      {pipelineIndicators.slice(0, 6).map((indicator: any, idx: number) => (
                        <tr key={indicator.id || idx}>
                          <td className="px-4 py-3 font-semibold text-slate-900">{indicator.label}</td>
                          <td className="px-4 py-3">{indicator.valeur_brute ?? '—'}</td>
                          <td className="px-4 py-3">{indicator.score_normalise ?? indicator.score_pondere ?? '—'}</td>
                          <td className="px-4 py-3 text-slate-400">{indicator.source || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Panel>
            )}

            {credibilityEntries.length > 0 && (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {credibilityEntries.map(([key, value]: [string, number]) => (
                  <div key={key} className={clsx(glassPanelClass, 'p-5')}>
                    <p className={sectionEyebrowClass}>{capitalizeLabel(key)}</p>
                    <p className="mt-3 text-3xl font-semibold text-slate-900">{value ?? 0}</p>
                    <div className="mt-4 h-2 rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-blue-500" style={{ width: `${Math.min(100, Number(value) || 0)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {credibilityInterpretation && (
              <Panel title="Interprétation" contentClassName="space-y-3">
                <p className="text-base leading-relaxed text-slate-600">{credibilityInterpretation}</p>
              </Panel>
            )}

            <Panel title="Résumé exécutif complet" contentClassName="space-y-4">
              <p className="text-base leading-relaxed text-slate-700 whitespace-pre-line">
                {executiveSummary || 'Aucun résumé disponible'}
              </p>
              {overviewKeyPoints.length > 0 && (
                <ul className="list-disc space-y-2 pl-5 text-slate-600">
                  {overviewKeyPoints.map((point: string, idx: number) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              )}
            </Panel>

            {(aggregatedOpportunities.length > 0 || aggregatedRecommendations.length > 0) && (
              <div className="grid gap-6 lg:grid-cols-2">
                {aggregatedOpportunities.length > 0 && (
                  <Panel title="Opportunités à saisir">
                    <ul className="list-disc space-y-3 pl-5 text-slate-600">
                      {aggregatedOpportunities.map((item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </Panel>
                )}
                {aggregatedRecommendations.length > 0 && (
                  <Panel title="Actions prioritaires">
                    <ul className="list-disc space-y-3 pl-5 text-slate-600">
                      {aggregatedRecommendations.map((item: string, idx: number) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </Panel>
                )}
              </div>
            )}
          </div>
        );


      case 'pestel':
        const pestelAnalysis = pestel.analysis || pestel.analyse || pestel.description || pestel.resume || '';
        const pestelRecommendations = pestelRecommendationsGlobal;
        const enrichedPestel = enrichedAnalyses?.pestel || {};

        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>Analyse PESTEL</h2>
              <p style={{ color: '#6b7280', fontSize: '16px' }}>Analyse macro-environnementale complète</p>
            </div>

            {/* Graphiques multiples */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Graphique Radar</h3>
                <div style={{ height: '400px' }}>
                  <Radar data={pestelData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    }
                  }} />
                </div>
              </div>

              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Scores par Dimension</h3>
                <div style={{ height: '400px' }}>
                  <Bar data={pestelBarData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    }
                  }} />
                </div>
              </div>

              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Tendance PESTEL</h3>
                <div style={{ height: '400px' }}>
                  <Line data={pestelTrendData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    },
                    plugins: {
                      legend: { display: false }
                    }
                  }} />
                </div>
              </div>
            </div>

            {/* Scores détaillés */}
            <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Scores Détaillés</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {Object.entries({
                  'Politique': pestelScores.political || pestelScores.politique || pestelScores.P || 0,
                  'Économique': pestelScores.economic || pestelScores.economique || pestelScores.E || 0,
                  'Social': pestelScores.social || pestelScores.S || 0,
                  'Technologique': pestelScores.technological || pestelScores.technologique || pestelScores.T || 0,
                  'Environnemental': pestelScores.environmental || pestelScores.environnemental || pestelScores.Env || 0,
                  'Légal': pestelScores.legal || pestelScores.legal || pestelScores.L || 0,
                }).map(([label, score]) => (
                  <div key={label}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>{label}</span>
                      <span style={{ fontSize: '14px', fontWeight: '600', color: '#111827' }}>{score}/100</span>
                    </div>
                    <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '10px' }}>
                      <div
                        style={{
                          backgroundColor: '#2563eb',
                          height: '10px',
                          borderRadius: '9999px',
                          width: `${score}%`,
                          transition: 'width 0.3s'
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Analyse complète - TOUT LE TEXTE */}
            {pestelAnalysis && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Analyse Complète PESTEL</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof pestelAnalysis === 'string' ? pestelAnalysis : JSON.stringify(pestelAnalysis, null, 2)}
                </div>
                {(enrichedPestel.analysis_short || enrichedPestel.key_points) && (
                  <div style={{ marginTop: '24px', backgroundColor: '#f9fafb', borderRadius: '12px', padding: '24px', border: '1px dashed #c7d2fe' }}>
                    {enrichedPestel.analysis_short && (
                      <>
                        <p style={{ fontSize: '14px', color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>Résumé OpenRouter</p>
                        <p style={{ color: '#374151', lineHeight: '1.75' }}>{enrichedPestel.analysis_short}</p>
                      </>
                    )}
                    {Array.isArray(enrichedPestel.key_points) && enrichedPestel.key_points.length > 0 && (
                      <ul style={{ marginTop: '16px', paddingLeft: '20px', color: '#111827' }}>
                        {enrichedPestel.key_points.map((point: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '8px' }}>{point}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Détails textuels - TOUS les détails */}
            {Object.keys(pestelDetails).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Analyse Détaillée par Dimension</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
                  {Object.entries(pestelDetails).map(([key, value]: [string, any]) => {
                    const opportunities = toArray(value?.opportunites || value?.['opportunités']);
                    const risks = toArray(value?.risques || value?.risks);
                    const recommendations = toArray(value?.recommandations);

                    return (
                      <div key={key} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px', backgroundColor: '#fcfcff' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                          <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', textTransform: 'capitalize', margin: 0 }}>{key}</h4>
                          {value?.score && (
                            <span style={{ fontWeight: '600', color: '#6366f1' }}>{value.score}/10</span>
                          )}
                        </div>
                        {value?.justification && (
                          <p style={{ color: '#4b5563', fontSize: '14px', lineHeight: '1.6', marginBottom: '12px' }}>{value.justification}</p>
                        )}
                        {opportunities.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#22c55e', marginBottom: '6px' }}>Opportunités</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {opportunities.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {risks.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#f97316', marginBottom: '6px' }}>Risques</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {risks.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {recommendations.length > 0 && (
                          <div>
                            <p style={{ fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#2563eb', marginBottom: '6px' }}>Recommandations</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {recommendations.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Recommandations */}
            {(pestelRecommendations && pestelRecommendations.length > 0) && (
              <div style={{ backgroundColor: '#eff6ff', borderRadius: '12px', padding: '32px', border: '1px solid #bfdbfe' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recommandations Stratégiques</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingLeft: '0', listStyle: 'none' }}>
                  {pestelRecommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#2563eb', marginRight: '12px', marginTop: '4px', fontSize: '20px' }}>•</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'esg':
        const esgAnalysis = esg.analysis || esg.analyse || esg.description || esg.resume || '';
        const esgRecommendations = esgRecommendationsGlobal;
        const enrichedEsg = enrichedAnalyses?.esg || {};

        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>Analyse ESG</h2>
              <p style={{ color: '#6b7280', fontSize: '16px' }}>Environnement, Social et Gouvernance</p>
            </div>

            {/* Graphiques multiples */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Scores par Dimension</h3>
                <div style={{ height: '400px' }}>
                  <Bar data={esgData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    }
                  }} />
                </div>
              </div>

              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Répartition ESG</h3>
                <div style={{ height: '400px' }}>
                  <Doughnut data={esgDoughnutData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }} />
                </div>
              </div>

              {oddContributionData && (
                <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Contribution ODD</h3>
                  <div style={{ height: '400px' }}>
                    <Bar data={oddContributionData} options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          ticks: { stepSize: 20 }
                        }
                      }
                    }} />
                  </div>
                </div>
              )}
            </div>

            {/* Scores détaillés */}
            <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Détails des Scores</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '500', color: '#374151' }}>Environnemental</span>
                    <span style={{ fontWeight: '600', color: '#22c55e' }}>{esgScores.environmental || esgScores.environnemental || 0}/100</span>
                  </div>
                  <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '12px' }}>
                    <div style={{ backgroundColor: '#22c55e', height: '12px', borderRadius: '9999px', width: `${esgScores.environmental || esgScores.environnemental || 0}%` }} />
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '500', color: '#374151' }}>Social</span>
                    <span style={{ fontWeight: '600', color: '#3b82f6' }}>{esgScores.social || 0}/100</span>
                  </div>
                  <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '12px' }}>
                    <div style={{ backgroundColor: '#3b82f6', height: '12px', borderRadius: '9999px', width: `${esgScores.social || 0}%` }} />
                  </div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '500', color: '#374151' }}>Gouvernance</span>
                    <span style={{ fontWeight: '600', color: '#a855f7' }}>{esgScores.governance || esgScores.gouvernance || 0}/100</span>
                  </div>
                  <div style={{ width: '100%', backgroundColor: '#e5e7eb', borderRadius: '9999px', height: '12px' }}>
                    <div style={{ backgroundColor: '#a855f7', height: '12px', borderRadius: '9999px', width: `${esgScores.governance || esgScores.gouvernance || 0}%` }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Analyse complète - TOUT LE TEXTE */}
            {esgAnalysis && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Analyse Complète ESG</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof esgAnalysis === 'string' ? esgAnalysis : JSON.stringify(esgAnalysis, null, 2)}
                </div>
                {(enrichedEsg.analysis_short || enrichedEsg.key_points) && (
                  <div style={{ marginTop: '24px', backgroundColor: '#ecfdf5', border: '1px dashed #34d399', borderRadius: '12px', padding: '24px' }}>
                    {enrichedEsg.analysis_short && (
                      <>
                        <p style={{ fontSize: '13px', color: '#059669', textTransform: 'uppercase', marginBottom: '8px', letterSpacing: '0.05em' }}>Résumé OpenRouter</p>
                        <p style={{ color: '#064e3b', lineHeight: '1.7' }}>{enrichedEsg.analysis_short}</p>
                      </>
                    )}
                    {Array.isArray(enrichedEsg.key_points) && (
                      <ul style={{ paddingLeft: '20px', marginTop: '12px', color: '#064e3b' }}>
                        {enrichedEsg.key_points.map((point: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{point}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Détails textuels - TOUS les détails */}
            {Object.keys(esgDetails).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Analyse Détaillée par Pilier</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
                  {Object.entries(esgDetails).map(([key, value]: [string, any]) => {
                    const strengths = toArray(value?.points_forts);
                    const weaknesses = toArray(value?.points_faibles);
                    const plans = toArray(value?.plans_amelioration);
                    const benchmarks = value?.benchmarks;

                    return (
                      <div key={key} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px', backgroundColor: '#f8fefc' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                          <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', textTransform: 'capitalize', margin: 0 }}>{key}</h4>
                          {value?.score && (
                            <span style={{ fontWeight: '600', color: '#059669' }}>{value.score}/100</span>
                          )}
                        </div>
                        {strengths.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', color: '#16a34a', fontWeight: 600, marginBottom: '6px' }}>Points forts</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {strengths.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {weaknesses.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', color: '#f97316', fontWeight: 600, marginBottom: '6px' }}>Points faibles</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {weaknesses.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {plans.length > 0 && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', color: '#2563eb', fontWeight: 600, marginBottom: '6px' }}>Plans d'amélioration</p>
                            <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                              {plans.map((item: string, idx: number) => (
                                <li key={idx} style={{ marginBottom: '4px' }}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {benchmarks && (
                          <div>
                            <p style={{ fontSize: '13px', color: '#4b5563', fontWeight: 600, marginBottom: '6px' }}>Benchmarks</p>
                            <div style={{ fontSize: '14px', color: '#4b5563' }}>
                              {Object.entries(benchmarks as Record<string, string | number>).map(([label, val]) => (
                                <div key={label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                                  <span>{label}</span>
                                  <span style={{ fontWeight: 600 }}>{String(val ?? '—')}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Recommandations */}
            {esgRecommendations.length > 0 && (
              <div style={{ backgroundColor: '#f0fdf4', borderRadius: '12px', padding: '32px', border: '1px solid #bbf7d0' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recommandations ESG</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingLeft: '0', listStyle: 'none' }}>
                  {esgRecommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#22c55e', marginRight: '12px', marginTop: '4px', fontSize: '20px' }}>•</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {Object.keys(impactOdd).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginTop: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Alignement Impact Durable / ODD</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                  {Object.entries(impactOdd).map(([oddKey, oddValue]: [string, any]) => (
                    <div key={oddKey} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px' }}>
                      <p style={{ fontSize: '13px', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{oddKey.toUpperCase()}</p>
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>{oddValue?.impact || oddValue?.description || 'Impact à préciser'}</p>
                      <div style={{ marginTop: '12px' }}>
                        <span style={{ fontSize: '13px', color: '#6b7280' }}>Contribution</span>
                        <div style={{ width: '100%', backgroundColor: '#f3f4f6', borderRadius: '999px', height: '8px', marginTop: '4px' }}>
                          <div style={{ width: `${Math.min(100, oddValue?.contribution || oddValue?.score || 0)}%`, backgroundColor: '#10b981', height: '8px', borderRadius: '999px' }} />
                        </div>
                      </div>
                      {oddValue?.actions && (
                        <ul style={{ marginTop: '12px', paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                          {oddValue.actions.map((action: string, idx: number) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>{action}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {globalIndicesLineData && (
              <div style={{ marginTop: '24px', backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Indice global (comparatif)</h3>
                <div style={{ height: '320px' }}>
                  <Line data={globalIndicesLineData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100
                      }
                    },
                    plugins: {
                      legend: { display: false }
                    }
                  }} />
                </div>
              </div>
            )}
          </div>
        );

      case 'market':
        const marketAnalysis = market.analysis || market.description || market.tendances || marketTrendNarrative || '';
        const marketDetails = market.details || market.detail || {};
        const enrichedMarket = enrichedAnalyses?.market || enrichedAnalyses?.marche || enrichedAnalyses?.marche_competition || {};

        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>Analyse de Marché</h2>
              <p style={{ color: '#6b7280', fontSize: '16px' }}>Opportunités et défis du marché</p>
            </div>

            {/* Taille du marché */}
            {Object.keys(marketSize).length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb' }}>
                  <p style={{ color: '#9ca3af', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Taille actuelle</p>
                  <p style={{ fontSize: '28px', fontWeight: '700', color: '#111827', margin: '8px 0' }}>{marketSize.valeur_actuelle || '—'}</p>
                  <p style={{ color: '#6b7280' }}>{marketSize.croissance || 'Croissance à préciser'}</p>
                </div>
                {marketSize.projections && (
                  <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb' }}>
                    <p style={{ color: '#9ca3af', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Projections clés</p>
                    {Object.entries(marketSize.projections).map(([year, value]) => (
                      <div key={year} style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', color: '#374151' }}>
                        <span>{year}</span>
                        <span style={{ fontWeight: 600 }}>{value as string}</span>
                      </div>
                    ))}
                  </div>
                )}
                {marketTrendNarrative && (
                  <div style={{ backgroundColor: '#f8fafc', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb' }}>
                    <p style={{ color: '#9ca3af', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Tendances majeures</p>
                    <p style={{ color: '#111827', marginTop: '8px', lineHeight: '1.7' }}>{marketTrendNarrative}</p>
                  </div>
                )}
              </div>
            )}

            {/* Graphiques pour le marché */}
            {(marketOpportunitiesCount > 0 || marketChallengesCount > 0) && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Opportunités vs Défis</h3>
                  <div style={{ height: '300px' }}>
                    <Bar data={marketComparisonData} options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          ticks: { stepSize: 1 }
                        }
                      },
                      plugins: {
                        legend: { display: false }
                      }
                    }} />
                  </div>
                </div>

                <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Répartition</h3>
                  <div style={{ height: '300px' }}>
                    <Doughnut data={{
                      labels: ['Opportunités', 'Défis'],
                      datasets: [{
                        data: [marketOpportunitiesCount, marketChallengesCount],
                        backgroundColor: [
                          'rgba(34, 197, 94, 0.8)',
                          'rgba(239, 68, 68, 0.8)',
                        ],
                        borderWidth: 0,
                      }]
                    }} options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { position: 'bottom' }
                      }
                    }} />
                  </div>
                </div>

                {marketProjectionChart && (
                  <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Projection de croissance</h3>
                    <div style={{ height: '300px' }}>
                      <Line data={marketProjectionChart} options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                          y: {
                            beginAtZero: true
                          }
                        }
                      }} />
                    </div>
                  </div>
                )}
              </div>
            )}

            {competitors.length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Panorama des concurrents</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                  {competitors.map((competitor: any, idx: number) => (
                    <div key={idx} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px' }}>
                      <p style={{ fontSize: '16px', fontWeight: '600', color: '#111827' }}>{competitor.nom}</p>
                      <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '12px' }}>{competitor.positionnement}</p>
                      <div style={{ marginBottom: '12px' }}>
                        <p style={{ fontSize: '13px', color: '#16a34a', fontWeight: 600, marginBottom: '4px' }}>Forces</p>
                        <ul style={{ paddingLeft: '18px', fontSize: '14px', color: '#374151' }}>
                          {toArray(competitor.forces).map((force: string, forceIdx: number) => (
                            <li key={forceIdx} style={{ marginBottom: '4px' }}>{force}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <p style={{ fontSize: '13px', color: '#dc2626', fontWeight: 600, marginBottom: '4px' }}>Faiblesses</p>
                        <ul style={{ paddingLeft: '18px', fontSize: '14px', color: '#374151' }}>
                          {toArray(competitor.faiblesses).map((weak: string, weakIdx: number) => (
                            <li key={weakIdx} style={{ marginBottom: '4px' }}>{weak}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {marketOpportunities.length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Opportunités</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingLeft: '0', listStyle: 'none' }}>
                  {marketOpportunities.map((opp: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#22c55e', marginRight: '12px', marginTop: '4px', fontSize: '24px' }}>✓</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{opp}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {marketThreats.length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Défis</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingLeft: '0', listStyle: 'none' }}>
                  {marketThreats.map((challenge: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#f97316', marginRight: '12px', marginTop: '4px', fontSize: '24px' }}>⚠</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{challenge}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Analyse complète - TOUT LE TEXTE */}
            {marketAnalysis && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Analyse Complète du Marché</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof marketAnalysis === 'string' ? marketAnalysis : JSON.stringify(marketAnalysis, null, 2)}
                </div>
                {(enrichedMarket.analysis_short || enrichedMarket.key_points) && (
                  <div style={{ marginTop: '24px', backgroundColor: '#fff7ed', borderRadius: '12px', padding: '24px', border: '1px dashed #fdba74' }}>
                    {enrichedMarket.analysis_short && (
                      <p style={{ color: '#9a3412', lineHeight: '1.7' }}>{enrichedMarket.analysis_short}</p>
                    )}
                    {Array.isArray(enrichedMarket.key_points) && (
                      <ul style={{ paddingLeft: '20px', marginTop: '12px', color: '#9a3412' }}>
                        {enrichedMarket.key_points.map((point: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{point}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Détails si disponibles */}
            {Object.keys(marketDetails).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Détails de l'Analyse</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  {Object.entries(marketDetails).map(([key, value]: [string, any]) => (
                    <div key={key} style={{ borderBottom: '1px solid #f3f4f6', paddingBottom: '16px', marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '12px', textTransform: 'capitalize' }}>{key}</h4>
                      <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>
                        {typeof value === 'string' ? (
                          <div style={{ whiteSpace: 'pre-line' }}>{value}</div>
                        ) : Array.isArray(value) ? (
                          <ul style={{ paddingLeft: '20px' }}>
                            {value.map((item: any, idx: number) => (
                              <li key={idx} style={{ marginBottom: '8px' }}>
                                {typeof item === 'string' ? item : JSON.stringify(item)}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div style={{ whiteSpace: 'pre-line' }}>{JSON.stringify(value, null, 2)}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'risk':
        const riskAnalysis = risk.analysis || risk.analyse || risk.description || '';
        const riskDetails = risk.details || risk.detail || {};
        const riskRecommendations = riskRecommendationsGlobal;
        const enrichedRisk = enrichedAnalyses?.risk || {};
        const consolidatedRiskNarrative = riskAnalysis || allRisks.join('\n');

        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>Analyse des Risques</h2>
              <p style={{ color: '#6b7280', fontSize: '16px' }}>Évaluation complète des risques</p>
            </div>

            {/* Graphiques multiples */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Niveau de Risque Global</h3>
                <div style={{ height: '256px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Doughnut data={riskData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }} />
                </div>
                <div style={{ textAlign: 'center', marginTop: '16px' }}>
                  <p style={{ fontSize: '36px', fontWeight: '700', color: '#111827' }}>{riskScore}%</p>
                  <p style={{ fontSize: '14px', color: '#6b7280' }}>Niveau de risque global</p>
                </div>
              </div>

              {Object.keys(riskCategories).length > 0 && (
                <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Risques par Catégorie</h3>
                  <div style={{ height: '256px' }}>
                    <Bar data={riskCategoriesData} options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100,
                          ticks: { stepSize: 20 }
                        }
                      }
                    }} />
                  </div>
                </div>
              )}
            </div>

            {/* Évaluation */}
            <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Évaluation</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Niveau</p>
                  <p style={{ fontSize: '24px', fontWeight: '600', color: '#111827' }}>{risk.overall_level || risk.niveau || 'Moyen'}</p>
                </div>
                {Object.entries(riskCategories).map(([key, value]: [string, any]) => (
                  <div key={key}>
                    <p style={{ fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '4px', textTransform: 'capitalize' }}>{key}</p>
                    <p style={{ color: '#6b7280', fontSize: '16px' }}>{typeof value === 'string' ? value : JSON.stringify(value)}</p>
                  </div>
                ))}
              </div>
            </div>

            {allRisks.length > 0 && (
              <div style={{ backgroundColor: '#fff7ed', borderRadius: '12px', padding: '32px', border: '1px solid #fed7aa', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#9a3412', marginBottom: '16px' }}>Top risques identifiés (agrégés)</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingLeft: '0', listStyle: 'none' }}>
                  {allRisks.map((riskItem: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#f97316', marginRight: '10px', marginTop: '4px' }}>⚠</span>
                      <span style={{ color: '#7c2d12', lineHeight: '1.6' }}>{riskItem}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {(valueChainPrimaryData || valueChainSupportData) && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                {valueChainPrimaryData && (
                  <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Activités primaires</h3>
                    <div style={{ height: '300px' }}>
                      <Bar data={valueChainPrimaryData} options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: { y: { beginAtZero: true, max: 100 } },
                        plugins: { legend: { display: false } }
                      }} />
                    </div>
                  </div>
                )}
                {valueChainSupportData && (
                  <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Activités support</h3>
                    <div style={{ height: '300px' }}>
                      <Bar data={valueChainSupportData} options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: { y: { beginAtZero: true, max: 100 } },
                        plugins: { legend: { display: false } }
                      }} />
                    </div>
                  </div>
                )}
              </div>
            )}

            {Object.keys(valueChainPrimary).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Chaîne de valeur - Activités primaires</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                  {Object.entries(valueChainPrimary).map(([key, data]: [string, any]) => (
                    <div key={key} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <p style={{ fontWeight: 600, color: '#111827', textTransform: 'capitalize' }}>{key}</p>
                        <span style={{ fontWeight: 600, color: '#f97316' }}>{data.score}/100</span>
                      </div>
                      <p style={{ color: '#374151', fontSize: '14px', lineHeight: '1.6', marginBottom: '12px' }}>{data.analyse}</p>
                      {toArray(data.optimisations).length > 0 && (
                        <ul style={{ paddingLeft: '18px', color: '#4b5563', fontSize: '13px' }}>
                          {toArray(data.optimisations).map((opt: string, idx: number) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>{opt}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(valueChainSupport).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Chaîne de valeur - Activités support</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                  {Object.entries(valueChainSupport).map(([key, data]: [string, any]) => (
                    <div key={key} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <p style={{ fontWeight: 600, color: '#111827', textTransform: 'capitalize' }}>{key}</p>
                        <span style={{ fontWeight: 600, color: '#2563eb' }}>{data.score}/100</span>
                      </div>
                      <p style={{ color: '#374151', fontSize: '14px', lineHeight: '1.6', marginBottom: '12px' }}>{data.analyse}</p>
                      {toArray(data.optimisations).length > 0 && (
                        <ul style={{ paddingLeft: '18px', color: '#4b5563', fontSize: '13px' }}>
                          {toArray(data.optimisations).map((opt: string, idx: number) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>{opt}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(impactPrep).length > 0 && (
              <div style={{ backgroundColor: '#f5f3ff', borderRadius: '12px', padding: '32px', border: '1px solid #ddd6fe', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#4c1d95', marginBottom: '16px' }}>Préparation IMM / Conformité</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
                  {Object.entries(impactPrep).map(([key, value]: [string, any]) => (
                    <div key={key} style={{ backgroundColor: 'white', borderRadius: '12px', padding: '20px', border: '1px solid #e0e7ff' }}>
                      <p style={{ fontSize: '13px', color: '#6b21a8', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{capitalizeLabel(key)}</p>
                      <p style={{ color: '#312e81', fontSize: '14px', lineHeight: '1.6', marginTop: '8px' }}>
                        {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Analyse complète - TOUT LE TEXTE */}
            {consolidatedRiskNarrative && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Analyse Complète des Risques</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof consolidatedRiskNarrative === 'string' ? consolidatedRiskNarrative : JSON.stringify(consolidatedRiskNarrative, null, 2)}
                </div>
                {(enrichedRisk.analysis_short || enrichedRisk.key_points) && (
                  <div style={{ marginTop: '24px', backgroundColor: '#fff7ed', border: '1px dashed #f97316', borderRadius: '12px', padding: '24px' }}>
                    {enrichedRisk.analysis_short && (
                      <p style={{ color: '#9a3412', lineHeight: '1.7' }}>{enrichedRisk.analysis_short}</p>
                    )}
                    {Array.isArray(enrichedRisk.key_points) && (
                      <ul style={{ paddingLeft: '20px', marginTop: '12px', color: '#9a3412' }}>
                        {enrichedRisk.key_points.map((point: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{point}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Détails complets des risques */}
            {Object.keys(riskDetails).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Analyse Détaillée des Risques</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  {Object.entries(riskDetails).map(([key, value]: [string, any]) => (
                    <div key={key} style={{ borderBottom: '1px solid #f3f4f6', paddingBottom: '16px', marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '12px', textTransform: 'capitalize' }}>{key}</h4>
                      <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>
                        {typeof value === 'string' ? (
                          <div style={{ whiteSpace: 'pre-line' }}>{value}</div>
                        ) : Array.isArray(value) ? (
                          <ul style={{ paddingLeft: '20px' }}>
                            {value.map((item: any, idx: number) => (
                              <li key={idx} style={{ marginBottom: '8px' }}>
                                {typeof item === 'string' ? item : JSON.stringify(item)}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div style={{ whiteSpace: 'pre-line' }}>{JSON.stringify(value, null, 2)}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommandations */}
            {riskRecommendations.length > 0 && (
              <div style={{ backgroundColor: '#fefce8', borderRadius: '12px', padding: '32px', border: '1px solid #fde047' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recommandations de Mitigation</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingLeft: '0', listStyle: 'none' }}>
                  {riskRecommendations.map((rec: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#eab308', marginRight: '12px', marginTop: '4px', fontSize: '20px' }}>•</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        );

      case 'synthesis':
        const synthesisAnalysis = synthesis.analysis || synthesis.analyse || synthesis.description || synthesis.resume_executif || '';
        const synthesisDetails = synthesis.details || synthesis.detail || {};
        const synthesisSummary = synthesis.resume_executif || synthesis.summary || enrichedSynthesis.executive_summary || '';
        const synthesisKeyPoints = synthesis.conclusions_cles || enrichedSynthesis.key_points || [];
        const prioritizedRecommendations = synthesis.recommandations_strategiques || {};
        const synthesisRecommendations = Array.isArray(synthesis.recommendations)
          ? synthesis.recommendations
          : enrichedSynthesis.strategic_recommendations || [];
        const enrichedStrengths = toArray(enrichedSynthesis.strengths);
        const enrichedWeaknesses = toArray(enrichedSynthesis.weaknesses);
        const enrichedOpportunities = toArray(enrichedSynthesis.opportunities);
        const enrichedThreats = toArray(enrichedSynthesis.threats);
        const enrichedKpis = toArray(enrichedSynthesis.kpis);

        // Graphique de synthèse globale (scores combinés)
        const synthesisScoresData = {
          labels: ['PESTEL', 'ESG', 'Marché', 'Risques'],
          datasets: [{
            label: 'Scores Globaux',
            data: [
              pestelScores.overall || pestelScores.total || 0,
              esgScores.overall || esgScores.total || 0,
              market.score || market.overall_score || 50,
              riskScore
            ],
            backgroundColor: [
              'rgba(37, 99, 235, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(251, 191, 36, 0.8)',
              'rgba(239, 68, 68, 0.8)',
            ],
            borderColor: [
              'rgba(37, 99, 235, 1)',
              'rgba(34, 197, 94, 1)',
              'rgba(251, 191, 36, 1)',
              'rgba(239, 68, 68, 1)',
            ],
            borderWidth: 2,
          }]
        };

        return (
          <div style={{ padding: '24px' }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ fontSize: '30px', fontWeight: '700', color: '#111827', marginBottom: '8px' }}>Synthèse Stratégique</h2>
              <p style={{ color: '#6b7280', fontSize: '16px' }}>Vue d'ensemble et recommandations finales</p>
            </div>

            {/* Graphiques de synthèse */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Scores par Analyse</h3>
                <div style={{ height: '400px' }}>
                  <Bar data={synthesisScoresData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    },
                    plugins: {
                      legend: { display: false }
                    }
                  }} />
                </div>
              </div>

              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '24px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Vue d'Ensemble</h3>
                <div style={{ height: '400px' }}>
                  <Radar data={{
                    labels: ['PESTEL', 'ESG', 'Marché', 'Risques', 'Synthèse'],
                    datasets: [{
                      label: 'Performance Globale',
                      data: [
                        pestelScores.overall || pestelScores.total || 0,
                        esgScores.overall || esgScores.total || 0,
                        market.score || market.overall_score || 50,
                        100 - riskScore, // Inverser pour avoir un score de sécurité
                        ((pestelScores.overall || 0) + (esgScores.overall || 0) + (market.score || 50) + (100 - riskScore)) / 4
                      ],
                      backgroundColor: 'rgba(37, 99, 235, 0.2)',
                      borderColor: 'rgba(37, 99, 235, 1)',
                      borderWidth: 2,
                      pointBackgroundColor: 'rgba(37, 99, 235, 1)',
                    }]
                  }} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 20 }
                      }
                    }
                  }} />
                </div>
              </div>
            </div>

            {synthesisSummary && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Résumé Exécutif</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof synthesisSummary === 'string' ? synthesisSummary : JSON.stringify(synthesisSummary, null, 2)}
                </div>
              </div>
            )}

            {synthesisKeyPoints && synthesisKeyPoints.length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Points Clés</h3>
                <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingLeft: '0', listStyle: 'none' }}>
                  {synthesisKeyPoints.map((finding: string, idx: number) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                      <span style={{ color: '#2563eb', marginRight: '12px', marginTop: '4px', fontSize: '20px' }}>•</span>
                      <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Analyse complète - TOUT LE TEXTE */}
            {synthesisAnalysis && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Analyse Complète de la Synthèse</h3>
                <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px', whiteSpace: 'pre-line' }}>
                  {typeof synthesisAnalysis === 'string' ? synthesisAnalysis : JSON.stringify(synthesisAnalysis, null, 2)}
                </div>
              </div>
            )}

            {/* Détails si disponibles */}
            {Object.keys(synthesisDetails).length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Détails de la Synthèse</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                  {Object.entries(synthesisDetails).map(([key, value]: [string, any]) => (
                    <div key={key} style={{ borderBottom: '1px solid #f3f4f6', paddingBottom: '16px', marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '12px', textTransform: 'capitalize' }}>{key}</h4>
                      <div style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>
                        {typeof value === 'string' ? (
                          <div style={{ whiteSpace: 'pre-line' }}>{value}</div>
                        ) : Array.isArray(value) ? (
                          <ul style={{ paddingLeft: '20px' }}>
                            {value.map((item: any, idx: number) => (
                              <li key={idx} style={{ marginBottom: '8px' }}>
                                {typeof item === 'string' ? item : JSON.stringify(item)}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <div style={{ whiteSpace: 'pre-line' }}>{JSON.stringify(value, null, 2)}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(enrichedStrengths.length > 0 || enrichedWeaknesses.length > 0) && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 10px 25px rgba(15,23,42,0.05)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Forces & Faiblesses (OpenRouter)</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                  {enrichedStrengths.length > 0 && (
                    <div style={{ borderRadius: '12px', padding: '20px', backgroundColor: '#ecfdf5', border: '1px solid #bbf7d0' }}>
                      <p style={{ fontSize: '13px', color: '#059669', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Forces</p>
                      <ul style={{ paddingLeft: '18px', marginTop: '12px', color: '#064e3b', fontSize: '14px' }}>
                        {enrichedStrengths.map((item: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {enrichedWeaknesses.length > 0 && (
                    <div style={{ borderRadius: '12px', padding: '20px', backgroundColor: '#fef2f2', border: '1px solid #fecaca' }}>
                      <p style={{ fontSize: '13px', color: '#dc2626', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Faiblesses</p>
                      <ul style={{ paddingLeft: '18px', marginTop: '12px', color: '#7f1d1d', fontSize: '14px' }}>
                        {enrichedWeaknesses.map((item: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {(enrichedOpportunities.length > 0 || enrichedThreats.length > 0) && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 10px 25px rgba(15,23,42,0.05)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Opportunités & Menaces (OpenRouter)</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
                  {enrichedOpportunities.length > 0 && (
                    <div style={{ borderRadius: '12px', padding: '20px', backgroundColor: '#ecfeff', border: '1px solid #bae6fd' }}>
                      <p style={{ fontSize: '13px', color: '#0284c7', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Opportunités</p>
                      <ul style={{ paddingLeft: '18px', marginTop: '12px', color: '#0c4a6e', fontSize: '14px' }}>
                        {enrichedOpportunities.map((item: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {enrichedThreats.length > 0 && (
                    <div style={{ borderRadius: '12px', padding: '20px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa' }}>
                      <p style={{ fontSize: '13px', color: '#c2410c', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Menaces</p>
                      <ul style={{ paddingLeft: '18px', marginTop: '12px', color: '#7c2d12', fontSize: '14px' }}>
                        {enrichedThreats.map((item: string, idx: number) => (
                          <li key={idx} style={{ marginBottom: '6px' }}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {(enrichedSynthesis.vision_3_5_years || enrichedSynthesis.maturity_level) && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '24px' }}>
                {enrichedSynthesis.vision_3_5_years && (
                  <div style={{ backgroundColor: '#eef2ff', borderRadius: '12px', padding: '24px', border: '1px solid #c7d2fe' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#312e81', marginBottom: '8px' }}>Vision 3-5 ans</h3>
                    <p style={{ color: '#312e81', lineHeight: '1.7' }}>{enrichedSynthesis.vision_3_5_years}</p>
                  </div>
                )}
                {enrichedSynthesis.maturity_level && (
                  <div style={{ backgroundColor: '#ecfccb', borderRadius: '12px', padding: '24px', border: '1px solid #bef264' }}>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#365314', marginBottom: '8px' }}>Niveau de maturité</h3>
                    <p style={{ fontSize: '28px', fontWeight: '700', color: '#3f6212', marginBottom: '8px' }}>{enrichedSynthesis.maturity_level}</p>
                    <p style={{ color: '#3f6212', lineHeight: '1.6' }}>{enrichedSynthesis.maturity_justification}</p>
                  </div>
                )}
              </div>
            )}

            {enrichedKpis.length > 0 && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>KPIs de suivi recommandés</h3>
                <ul style={{ columns: 2, columnGap: '24px', color: '#374151', fontSize: '15px', lineHeight: '1.8' }}>
                  {enrichedKpis.map((kpi: string, idx: number) => (
                    <li key={idx}>{kpi}</li>
                  ))}
                </ul>
              </div>
            )}

            {Array.isArray(roadmap.phases) && (
              <div style={{ backgroundColor: 'white', borderRadius: '12px', padding: '32px', border: '1px solid #e5e7eb', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Feuille de route stratégique</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {roadmap.phases.map((phase: any) => (
                    <div key={phase.numero} style={{ border: '1px solid #f3f4f6', borderRadius: '12px', padding: '20px' }}>
                      <p style={{ color: '#6b7280', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Phase {phase.numero} • {phase.nom}</p>
                      <p style={{ color: '#111827', fontWeight: '600', margin: '8px 0' }}>Durée : {phase.duree_mois} mois</p>
                      {phase.objectifs && (
                        <div style={{ marginBottom: '12px' }}>
                          <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '6px' }}>Objectifs</p>
                          <ul style={{ paddingLeft: '18px', color: '#374151', fontSize: '14px' }}>
                            {phase.objectifs.map((obj: string, idx: number) => (
                              <li key={idx}>{obj}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {phase.actions && (
                        <div>
                          <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '6px' }}>Actions clés</p>
                          {phase.actions.map((action: any, idx: number) => (
                            <div key={idx} style={{ padding: '12px', border: '1px solid #f3f4f6', borderRadius: '8px', marginBottom: '8px' }}>
                              <p style={{ fontWeight: '600', color: '#111827' }}>{action.titre}</p>
                              <p style={{ color: '#374151', fontSize: '14px', margin: '4px 0' }}>{action.description}</p>
                              {action.metriques && (
                                <p style={{ color: '#6b7280', fontSize: '13px' }}>Métriques : {action.metriques.join(', ')}</p>
                              )}
                              {action.investissement && (
                                <p style={{ color: '#6b7280', fontSize: '13px' }}>Investissement : {action.investissement}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(prioritizedRecommendations).length > 0 ? (
              <div style={{ backgroundColor: '#eff6ff', borderRadius: '12px', padding: '32px', border: '1px solid #bfdbfe' }}>
                <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recommandations Stratégiques (par priorité)</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                  {Object.entries(prioritizedRecommendations).map(([priority, items]: [string, any]) => (
                    <div key={priority} style={{ border: '1px solid #dbeafe', borderRadius: '12px', padding: '20px', backgroundColor: 'white' }}>
                      <p style={{ fontSize: '13px', textTransform: 'uppercase', color: '#1d4ed8', letterSpacing: '0.08em', marginBottom: '8px' }}>{priority.replace('_', ' ').toUpperCase()}</p>
                      {Array.isArray(items) ? items.map((item: any, idx: number) => (
                        <div key={idx} style={{ marginBottom: '16px' }}>
                          <p style={{ fontWeight: '600', color: '#111827' }}>{item.titre}</p>
                          <p style={{ color: '#374151', fontSize: '14px', margin: '4px 0' }}>{item.description}</p>
                          <p style={{ color: '#6b7280', fontSize: '13px' }}>Impact : {item.impact}</p>
                          <p style={{ color: '#6b7280', fontSize: '13px' }}>Timeline : {item.timeline} • Budget : {item.investissement}</p>
                        </div>
                      )) : <p>{JSON.stringify(items)}</p>}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              synthesisRecommendations.length > 0 && (
                <div style={{ backgroundColor: '#eff6ff', borderRadius: '12px', padding: '32px', border: '1px solid #bfdbfe' }}>
                  <h3 style={{ fontSize: '20px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recommandations Stratégiques</h3>
                  <ul style={{ display: 'flex', flexDirection: 'column', gap: '12px', paddingLeft: '0', listStyle: 'none' }}>
                    {synthesisRecommendations.map((rec: string, idx: number) => (
                      <li key={idx} style={{ display: 'flex', alignItems: 'flex-start' }}>
                        <span style={{ color: '#2563eb', marginRight: '12px', marginTop: '4px', fontSize: '20px' }}>•</span>
                        <span style={{ color: '#374151', lineHeight: '1.75', fontSize: '16px' }}>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="flex min-h-screen bg-[rgba(248,250,255,1)] text-slate-900">
      <aside className="hidden w-72 flex-col border-r border-slate-100 bg-white p-6 xl:flex">
        <div className="mb-10">
          <p className="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">Africa Strategy</p>
          <h1 className="mt-3 text-2xl font-semibold text-slate-900">Command Center</h1>
        </div>
        <nav className="flex flex-1 flex-col gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition',
                activeTab === tab.id
                  ? 'bg-slate-900 text-white shadow-inner shadow-slate-900/10'
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900'
              )}
            >
              <span className="text-lg">{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
        <button
          onClick={() => window.location.href = '/'}
          className="mt-6 inline-flex items-center justify-center rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-600 transition hover:border-slate-400 hover:text-slate-900"
        >
          ← Nouvelle analyse
        </button>
      </aside>

      <main className="flex flex-1 flex-col">
        <header className="sticky top-0 z-20 border-b border-slate-100 bg-white/90 px-4 py-4 backdrop-blur lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
              <h2 className="text-xl font-semibold text-slate-900">
                {tabs.find(t => t.id === activeTab)?.label || 'Dashboard'}
              </h2>
            </div>
            <div className="flex gap-3">
              <button className="flex h-10 w-10 items-center justify-center rounded-full border border-white/40 bg-white/80 text-slate-500 shadow-sm">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              <button className="flex h-10 w-10 items-center justify-center rounded-full border border-white/40 bg-white/80 text-slate-500 shadow-sm">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 00-2-2H6a2 2 0 00-2 2v.341C3.67 6.165 3 7.388 3 8.849V11a2 2 0 002 2h5v2H6a2 2 0 00-2 2v1.159c0 1.47.67 2.684 1.659 3.508L6 21h10" />
                </svg>
              </button>
              <button className="flex h-10 w-10 items-center justify-center rounded-full border border-white/40 bg-white/80 text-slate-500 shadow-sm">
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto px-4 py-6 lg:px-8">
          {renderContent()}
        </div>
      </main>

      {!loading && analysisData && (
        <>
          <button
            onClick={() => setChatOpen(true)}
            className="fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full bg-slate-900 text-white shadow-xl shadow-slate-900/30 transition hover:-translate-y-0.5"
            aria-label="Ouvrir le copilote IA"
          >
            💬
          </button>
          <Chatbot
            analysisData={analysisData}
            mode="modal"
            open={chatOpen}
            onClose={() => setChatOpen(false)}
          />
        </>
      )}
    </div>
  );
}
