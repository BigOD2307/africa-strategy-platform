'use client';

import { useState, useMemo } from 'react';
import { createPortal } from 'react-dom';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

type ChatbotProps = {
  analysisData: any;
  mode?: 'panel' | 'modal';
  open?: boolean;
  onClose?: () => void;
};

const getTimestamp = () =>
  new Intl.DateTimeFormat('fr-FR', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date());

const systemPrompt =
  'Posez une question sur vos analyses (PESTEL, ESG, marché, risques, synthèse). Le copilote répond à partir des données générées par l’IA.';

export default function Chatbot({
  analysisData,
  mode = 'panel',
  open = true,
  onClose,
}: ChatbotProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Bonjour 👋 Je suis votre copilote IA. Que souhaitez-vous explorer dans ces analyses ?',
      timestamp: getTimestamp(),
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const disabled = loading || !input.trim();

  const suggestions = useMemo(
    () => [
      'Quels sont les risques critiques ?',
      'Résume-moi l’analyse du marché',
      'Quelles priorités ESG ressortent ?',
    ],
    []
  );

  const handleSend = async (value?: string) => {
    const question = (value ?? input).trim();
    if (!question) return;

    const userMessage: Message = {
      role: 'user',
      content: question,
      timestamp: getTimestamp(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          analysis_data: analysisData,
        }),
      });

      if (!response.ok) {
        throw new Error('Le service de chat ne répond pas');
      }

      const data = await response.json();
      const answer =
        data.answer ||
        data.message ||
        'Je n’ai pas pu trouver de réponse précise dans les analyses. Réessayez avec une autre question.';

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: answer,
          timestamp: getTimestamp(),
        },
      ]);
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la réponse');
    } finally {
      setLoading(false);
    }
  };

  if (!analysisData) {
    return null;
  }

  const renderMessages = () => (
    <div className="flex-1 overflow-y-auto rounded-2xl border border-slate-100 bg-slate-50 p-4">
      <div className="space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={`${msg.timestamp}-${idx}`}
            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse text-right' : 'flex-row text-left'}`}
          >
            <div
              className={`flex h-9 w-9 items-center justify-center rounded-2xl ${
                msg.role === 'user' ? 'bg-indigo-500 text-white' : 'bg-slate-200 text-slate-600'
              }`}
            >
              {msg.role === 'user' ? 'Vous' : 'IA'}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user' ? 'bg-indigo-500 text-white shadow-md' : 'bg-white text-slate-800 shadow'
              }`}
            >
              <p>{msg.content}</p>
              <span
                className={`mt-2 block text-[10px] ${
                  msg.role === 'user' ? 'text-white/70' : 'text-slate-400'
                }`}
              >
                {msg.timestamp}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderComposer = () => (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => handleSend(suggestion)}
            className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-indigo-200 hover:bg-indigo-50"
            disabled={loading}
          >
            {suggestion}
          </button>
        ))}
      </div>
      <div className="flex items-end gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm focus-within:border-indigo-300">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Posez votre question..."
          className="h-24 flex-1 resize-none border-0 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none"
        />
        <button
          onClick={() => handleSend()}
          disabled={disabled}
          className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? '…' : '➤'}
        </button>
      </div>
      {error && <p className="text-xs text-rose-500">{error}</p>}
    </div>
  );

  const baseContainerClasses =
    mode === 'panel'
      ? 'flex h-full w-full flex-col gap-5 rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_25px_80px_rgba(15,23,42,0.08)]'
      : 'flex h-full w-full flex-col gap-5 rounded-[28px] border border-slate-200 bg-white p-5 shadow-[0_25px_80px_rgba(15,23,42,0.12)]';

  const content = (
    <div className={baseContainerClasses}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-500/10 text-2xl text-indigo-600">
            🤝
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.4em] text-slate-400">Copilote IA</p>
            <h3 className="text-lg font-semibold text-slate-900">Assistant stratégique</h3>
            <p className="text-sm text-slate-500">{systemPrompt}</p>
          </div>
        </div>
      </div>

      {renderMessages()}

      {renderComposer()}
    </div>
  );

  if (mode === 'modal') {
    if (!open || typeof document === 'undefined') return null;

    return createPortal(
      <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/70 px-4 py-8 sm:items-center">
        <div className="w-full max-w-lg">
          <div className="mb-3 flex justify-end">
            <button
              onClick={onClose}
              className="inline-flex items-center rounded-full border border-white/30 px-3 py-1 text-xs font-semibold text-white/80"
            >
              Fermer ✕
            </button>
          </div>
          <div className="max-h-[80vh] overflow-hidden">{content}</div>
        </div>
      </div>,
      document.body
    );
  }

  return content;
}
