import { useState, useCallback } from 'react';
import { ingestDatabase, queryIntelligence } from '../services/api';
import { useLazyApi } from '../hooks/useApi';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import type { GroundedQueryResponse, IngestResponse } from '../types/api';

const SUGGESTED_QUERIES = [
  'Which pull requests are currently high risk?',
  'What are the most common findings across all analyses?',
  'Which repositories have the most pull requests?',
  'Are there any incomplete or failed analysis runs?',
  'Summarise the current state of all tracked repositories.',
];

function IngestPanel() {
  const { execute, loading, error, data } = useLazyApi<[], IngestResponse>(ingestDatabase);

  return (
    <div className="intel-ingest-card">
      <div className="section-header mb-16">
        <div>
          <div className="section-title" style={{ fontSize: 16 }}>Knowledge Ingestion</div>
          <div className="text-muted text-sm mt-4">
            Snapshot the current database state into the Foundry IQ grounding context.
            Run this before querying to ensure responses reflect the latest data.
          </div>
        </div>
      </div>

      <div className="flex-row">
        <button
          id="ingest-btn"
          className="btn btn-primary"
          onClick={() => execute()}
          disabled={loading}
        >
          {loading ? (
            <>
              <LoadingSpinner size="sm" />
              Ingesting…
            </>
          ) : (
            <>
              ⬆ Ingest Database
            </>
          )}
        </button>

        {!loading && !data && !error && (
          <span className="text-muted text-sm">
            Click to snapshot current database state
          </span>
        )}
      </div>

      {error && (
        <div className="error-banner" style={{ marginTop: 12 }}>
          <span>⚠</span>
          {error}
        </div>
      )}

      {data && (
        <>
          <div className="success-banner">
            <span>✓</span>
            Knowledge snapshot saved — {data.status}
          </div>
          <div className="ingest-result">
            {[
              { label: 'Repos', value: data.repositories },
              { label: 'PRs', value: data.pull_requests },
              { label: 'Analyses', value: data.analyses },
            ].map(({ label, value }) => (
              <div key={label} className="ingest-stat">
                <span className="ingest-stat-value">{value}</span>
                <span className="ingest-stat-label">{label}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function QueryPanel() {
  const [inputValue, setInputValue] = useState('');
  const { execute, loading, error, data } = useLazyApi<
    [string],
    GroundedQueryResponse
  >(queryIntelligence);

  const handleSubmit = useCallback(async () => {
    const q = inputValue.trim();
    if (!q) return;
    await execute(q);
  }, [inputValue, execute]);

  const handleSuggestion = useCallback(
    async (q: string) => {
      setInputValue(q);
      await execute(q);
    },
    [execute],
  );

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="intel-query-card">
      <div style={{ marginBottom: 20 }}>
        <div className="section-title" style={{ fontSize: 16, marginBottom: 4 }}>
          ✦ Foundry IQ — Natural Language Query
        </div>
        <div className="text-muted text-sm">
          Ask any question about your repositories, pull requests, or analysis results.
          Responses are grounded with citations from ingested data.
        </div>
      </div>

      {/* Suggested queries */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
          Suggested Queries
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {SUGGESTED_QUERIES.map((q) => (
            <button
              key={q}
              className="btn btn-secondary btn-sm"
              onClick={() => handleSuggestion(q)}
              disabled={loading}
              style={{ textAlign: 'left', whiteSpace: 'normal', height: 'auto', lineHeight: 1.4, maxWidth: 280 }}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Input row */}
      <div className="intel-query-input-row">
        <input
          id="intelligence-query-input"
          type="text"
          className="input"
          placeholder="Ask a question about your PR data…"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          id="intelligence-query-btn"
          className="btn btn-primary"
          onClick={handleSubmit}
          disabled={loading || !inputValue.trim()}
        >
          {loading ? <LoadingSpinner size="sm" /> : '→ Ask'}
        </button>
      </div>

      {error && (
        <div className="error-banner" style={{ marginTop: 16 }}>
          <span>⚠</span>
          {error}
        </div>
      )}

      {/* Answer box */}
      {data && (
        <div className="intel-answer-box">
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
            Answer
          </div>
          <div className="intel-answer-text">{data.answer}</div>

          {data.citations.length > 0 && (
            <div className="intel-citations">
              <div className="intel-citations-title">
                Citations ({data.citations.length})
              </div>
              {data.citations.map((cite) => (
                <div key={cite.id} className="citation-chip">
                  <div className="citation-chip-title">{cite.title}</div>
                  {cite.reference && (
                    <div className="citation-chip-ref">{cite.reference}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function IntelligencePage() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Intelligence</h1>
        <p className="page-subtitle">
          Microsoft Foundry IQ — Grounded natural language queries over PRPilot data
        </p>
      </div>

      {/* Workflow guide */}
      <div
        className="card mb-24"
        style={{
          borderColor: 'var(--border-accent)',
          background: 'rgba(99, 102, 241, 0.04)',
        }}
      >
        <div className="section-title" style={{ marginBottom: 12 }}>Demo Workflow</div>
        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
          {[
            { step: '1', label: 'Sync Repos', desc: 'Configure GitHub webhooks to push PR events.' },
            { step: '2', label: 'Run Analysis', desc: 'Trigger POST /analyses/run/{pr_id} for each PR.' },
            { step: '3', label: 'Ingest Data', desc: 'Click "Ingest Database" to snapshot the DB.' },
            { step: '4', label: 'Ask Questions', desc: 'Query Foundry IQ with natural language.' },
          ].map(({ step, label, desc }) => (
            <div key={step} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', flex: '1 1 180px' }}>
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: '50%',
                  background: 'var(--accent-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: 13,
                  flexShrink: 0,
                  color: '#fff',
                }}
              >
                {step}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: 13, color: 'var(--text-primary)', marginBottom: 2 }}>{label}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="intel-panel">
        <IngestPanel />
        <QueryPanel />
      </div>
    </div>
  );
}
