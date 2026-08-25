'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { Patent, PatentListResponse, PatentCreatePayload, PatentIngestPayload } from '@/types/patent';
import {
  PatentLandscapeSummary,
  CompetitiveLandscapeResponse,
  PatentTrendsResponse,
} from '@/types/patent_intelligence';

export default function PatentsPage() {
  const [patents, setPatents] = useState<Patent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedClassification, setSelectedClassification] = useState('');
  const [selectedTab, setSelectedTab] = useState<'all' | 'my' | 'landscape'>('all');

  // Landscape state
  const [landscapeSummary, setLandscapeSummary] = useState<PatentLandscapeSummary | null>(null);
  const [competitiveData, setCompetitiveData] = useState<CompetitiveLandscapeResponse | null>(null);
  const [trendsData, setTrendsData] = useState<PatentTrendsResponse | null>(null);
  const [landscapeLoading, setLandscapeLoading] = useState(false);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingPatentId, setEditingPatentId] = useState<number | null>(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form states
  const [createForm, setCreateForm] = useState<PatentCreatePayload>({
    patent_number: '',
    title: '',
    abstract: '',
    assignee: '',
    inventors: '',
    filing_date: '',
    publication_date: '',
    patent_classification: '',
    technology_domain: '',
    citation_count: 0,
    source: 'manual',
    url: ''
  });

  const [editForm, setEditForm] = useState<Partial<PatentCreatePayload>>({
    title: '',
    abstract: '',
    assignee: '',
    inventors: '',
    patent_classification: '',
    technology_domain: '',
    citation_count: 0,
    url: ''
  });

  const [ingestForm, setIngestForm] = useState<PatentIngestPayload>({
    patent_number: '',
    provider: 'mock'
  });

  const fetchPatents = useCallback(async () => {
    if (selectedTab === 'landscape') return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const endpoint = selectedTab === 'my' ? '/patents/my' : '/patents';
      const params: Record<string, string | number> = { limit: 50, offset: 0 };
      if (searchQuery) params.q = searchQuery;
      if (selectedDomain) params.domain = selectedDomain;
      if (selectedClassification) params.classification = selectedClassification;

      const res = await api.get<{ data: PatentListResponse }>(endpoint, { params });
      setPatents(res.data.data.items || []);
      setTotal(res.data.data.total || 0);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load patents');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedDomain, selectedClassification, selectedTab]);

  const fetchLandscapeData = useCallback(async () => {
    if (selectedTab !== 'landscape') return;
    setLandscapeLoading(true);
    try {
      const [sumRes, compRes, trRes] = await Promise.all([
        api.get<{ data: PatentLandscapeSummary }>('/patent-intelligence/landscape'),
        api.get<{ data: CompetitiveLandscapeResponse }>('/patent-intelligence/competitive-landscape'),
        api.get<{ data: PatentTrendsResponse }>('/patent-intelligence/trends'),
      ]);
      setLandscapeSummary(sumRes.data.data);
      setCompetitiveData(compRes.data.data);
      setTrendsData(trRes.data.data);
    } catch (err: any) {
      setErrorMsg('Failed to load patent landscape intelligence');
    } finally {
      setLandscapeLoading(false);
    }
  }, [selectedTab]);

  useEffect(() => {
    if (selectedTab === 'landscape') {
      fetchLandscapeData();
    } else {
      const timer = setTimeout(() => {
        fetchPatents();
      }, 250);
      return () => clearTimeout(timer);
    }
  }, [fetchPatents, fetchLandscapeData, selectedTab]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalLoading(true);
    setErrorMsg(null);
    try {
      const payload = {
        ...createForm,
        filing_date: createForm.filing_date ? new Date(createForm.filing_date).toISOString() : undefined,
        publication_date: createForm.publication_date ? new Date(createForm.publication_date).toISOString() : undefined,
      };
      await api.post('/patents', payload);
      setSuccessMsg('Patent indexed successfully!');
      setShowCreateModal(false);
      setCreateForm({
        patent_number: '',
        title: '',
        abstract: '',
        assignee: '',
        inventors: '',
        filing_date: '',
        publication_date: '',
        patent_classification: '',
        technology_domain: '',
        citation_count: 0,
        source: 'manual',
        url: ''
      });
      fetchPatents();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to create patent');
    } finally {
      setModalLoading(false);
    }
  };

  const handleIngestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalLoading(true);
    setErrorMsg(null);
    try {
      await api.post('/patents/ingest', ingestForm);
      setSuccessMsg('Patent ingested and linked to your profile successfully!');
      setShowIngestModal(false);
      setIngestForm({ patent_number: '', provider: 'mock' });
      fetchPatents();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to ingest patent');
    } finally {
      setModalLoading(false);
    }
  };

  const handleOpenEdit = (p: Patent) => {
    setEditingPatentId(p.id);
    setEditForm({
      title: p.title,
      abstract: p.abstract || '',
      assignee: p.assignee || '',
      inventors: p.inventors || '',
      patent_classification: p.patent_classification || '',
      technology_domain: p.technology_domain || '',
      citation_count: p.citation_count || 0,
      url: p.url || ''
    });
    setErrorMsg(null);
    setSuccessMsg(null);
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingPatentId) return;
    setModalLoading(true);
    setErrorMsg(null);
    try {
      await api.put(`/patents/${editingPatentId}`, editForm);
      setSuccessMsg('Patent updated successfully!');
      setShowEditModal(false);
      setEditingPatentId(null);
      fetchPatents();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to update patent');
    } finally {
      setModalLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to remove this patent from your profile?')) return;
    try {
      await api.delete(`/patents/${id}`);
      setSuccessMsg('Patent removed successfully');
      fetchPatents();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to delete patent');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Patent Foundation
            </span>
            <span className="text-xs text-slate-400">Total Indexed: {total}</span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Intellectual Property & Patents</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Explore normalized patent disclosures, technology domain classifications, and inventors.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => { setShowIngestModal(true); setErrorMsg(null); setSuccessMsg(null); }}
            className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-cyan-900/20 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            Ingest Patent
          </button>
          <button
            onClick={() => { setShowCreateModal(true); setErrorMsg(null); setSuccessMsg(null); }}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-indigo-900/20 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Patent
          </button>
        </div>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-sm flex items-center justify-between">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 hover:text-rose-300 font-bold">×</button>
        </div>
      )}
      {successMsg && (
        <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 text-sm flex items-center justify-between">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 hover:text-emerald-300 font-bold">×</button>
        </div>
      )}

      {/* Filter and Tab Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl space-y-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setSelectedTab('all')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition ${
                selectedTab === 'all' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All Patents ({total})
            </button>
            <button
              onClick={() => setSelectedTab('my')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition ${
                selectedTab === 'my' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              My Linked Patents
            </button>
            <button
              onClick={() => setSelectedTab('landscape')}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition flex items-center gap-1.5 ${
                selectedTab === 'landscape' ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              Patent Landscape
            </button>
          </div>

          {selectedTab !== 'landscape' && (
            <div className="flex-1 max-w-md w-full relative">
              <input
                type="text"
                placeholder="Search by patent #, title, assignee, or inventor..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}
        </div>

        {/* Taxonomy Filters */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800/60">
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Technology Domains</option>
            <option value="Quantum Technologies">Quantum Technologies</option>
            <option value="Biotechnology & Genomic Sciences">Biotechnology & Genomic Sciences</option>
            <option value="Clean Energy & Sustainability">Clean Energy & Sustainability</option>
            <option value="Artificial Intelligence & Machine Learning">Artificial Intelligence</option>
            <option value="Cybersecurity & Cryptography">Cybersecurity & Cryptography</option>
          </select>

          <input
            type="text"
            placeholder="Filter classification (e.g. G06N, A61K)..."
            value={selectedClassification}
            onChange={(e) => setSelectedClassification(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 max-w-xs"
          />

          {(searchQuery || selectedDomain || selectedClassification) && (
            <button
              onClick={() => { setSearchQuery(''); setSelectedDomain(''); setSelectedClassification(''); }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium ml-auto"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Patent Landscape Section */}
      {selectedTab === 'landscape' && (
        <div className="space-y-6">
          {landscapeLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-32" />
              ))}
            </div>
          ) : (
            <>
              {/* KPI Cards */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium block">Total Patents</span>
                  <span className="text-xl font-bold text-white mt-1 block">
                    {landscapeSummary?.total_patents ?? 0}
                  </span>
                  <span className="text-[10px] text-cyan-400">Indexed Corpus</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium block">Active Assignees</span>
                  <span className="text-xl font-bold text-indigo-400 mt-1 block">
                    {landscapeSummary?.total_assignees ?? 0}
                  </span>
                  <span className="text-[10px] text-slate-400">Organizations / Entities</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium block">Tech Domains</span>
                  <span className="text-xl font-bold text-emerald-400 mt-1 block">
                    {landscapeSummary?.total_domains ?? 0}
                  </span>
                  <span className="text-[10px] text-slate-400">Classified Fields</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span className="text-[11px] text-slate-400 font-medium block">Total Citations</span>
                  <span className="text-xl font-bold text-amber-400 mt-1 block">
                    {landscapeSummary?.total_citations ?? 0}
                  </span>
                  <span className="text-[10px] text-slate-400">Avg {landscapeSummary?.average_citations ?? 0} / patent</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 col-span-2 md:col-span-1">
                  <span className="text-[11px] text-slate-400 font-medium block">Concentration (HHI)</span>
                  <span className="text-xl font-bold text-rose-400 mt-1 block">
                    {landscapeSummary?.top_domains ? Math.round(landscapeSummary.top_domains.reduce((acc, d) => acc + (d.share_percentage ** 2), 0)) : 0}
                  </span>
                  <span className="text-[10px] text-slate-400">HHI Score (0-10000)</span>
                </div>
              </div>

              {/* Technology Domains & Top Assignees */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Domains Leaderboard */}
                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                      Technology Domain Distribution
                    </h3>
                    <span className="text-xs text-slate-400 font-mono">
                      {landscapeSummary?.top_domains?.length ?? 0} Fields
                    </span>
                  </div>

                  <div className="space-y-3">
                    {landscapeSummary?.top_domains?.map((d) => (
                      <div key={d.domain} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-semibold text-slate-200">{d.domain}</span>
                          <span className="font-bold text-cyan-400">{d.patent_count} patents ({d.share_percentage}%)</span>
                        </div>
                        <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                          <div
                            style={{ width: `${Math.min(100, Math.max(5, d.share_percentage))}%` }}
                            className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                          ></div>
                        </div>
                        {d.top_assignees && d.top_assignees.length > 0 && (
                          <div className="flex items-center gap-1 text-[10px] text-slate-400">
                            <span>Top Holders:</span>
                            <span className="text-slate-300 truncate">{d.top_assignees.join(', ')}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Top Assignees Leaderboard */}
                <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                      Top Patent Holders & Assignees
                    </h3>
                    <span className="text-xs text-slate-400 font-mono">
                      {landscapeSummary?.top_assignees?.length ?? 0} Leaders
                    </span>
                  </div>

                  <div className="space-y-3">
                    {landscapeSummary?.top_assignees?.map((a, idx) => (
                      <div key={a.assignee} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2">
                            <span className="w-4 h-4 rounded bg-indigo-500/10 text-indigo-400 text-[10px] font-bold flex items-center justify-center">
                              #{idx + 1}
                            </span>
                            <span className="font-semibold text-white truncate max-w-[200px]">{a.assignee}</span>
                          </div>
                          <span className="font-bold text-indigo-400">{a.patent_count} patents</span>
                        </div>
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <span>Recent: {a.recent_filings_count} filings</span>
                          <span>Jurisdictions: {a.jurisdictions.join(', ') || 'Global'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Competitive Indicators */}
              <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                      Structured Patent Landscape Indicators
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Deterministic portfolio breadth, velocity, and citation index
                    </p>
                  </div>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {competitiveData?.total_competitors ?? 0} Entities
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="pb-2 font-medium">Assignee</th>
                        <th className="pb-2 font-medium">Patents</th>
                        <th className="pb-2 font-medium">Domain Breadth</th>
                        <th className="pb-2 font-medium">Recent Velocity</th>
                        <th className="pb-2 font-medium">Competitive Index</th>
                        <th className="pb-2 font-medium">Classification</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {competitiveData?.competitors?.map((comp) => (
                        <tr key={comp.assignee} className="hover:bg-slate-950/40">
                          <td className="py-2.5 font-semibold text-slate-200">{comp.assignee}</td>
                          <td className="py-2.5 text-slate-300">{comp.patent_count}</td>
                          <td className="py-2.5 text-slate-300">{comp.domain_breadth_count} fields</td>
                          <td className="py-2.5 text-cyan-400 font-medium">{comp.recent_filing_velocity_pct}%</td>
                          <td className="py-2.5">
                            <span className="font-bold text-emerald-400">{comp.competitive_index} / 100</span>
                          </td>
                          <td className="py-2.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              comp.classification === 'DOMINANT_PORTFOLIO'
                                ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                                : comp.classification === 'HIGH_VELOCITY'
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                                : 'bg-slate-800 text-slate-300'
                            }`}>
                              {comp.classification.replace('_', ' ')}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Patent Cards Grid */}
      {selectedTab !== 'landscape' && (
        <>
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-44" />
              ))}
            </div>
          ) : patents.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8">
              <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-slate-200">No patents found</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                Try adjusting your search criteria, or ingest a sample patent like <code className="text-indigo-400">US11234567B2</code>.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {patents.map((p) => (
                <div
                  key={p.id}
                  className="group bg-slate-900/70 border border-slate-800/90 hover:border-indigo-500/50 p-5 rounded-2xl transition duration-200 flex flex-col justify-between shadow-sm hover:shadow-md"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {p.patent_number}
                      </span>
                      <div className="flex items-center gap-2">
                        {p.patent_classification && (
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {p.patent_classification}
                          </span>
                        )}
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider">{p.source}</span>
                      </div>
                    </div>

                    <h3 className="text-base font-semibold text-white mt-2 group-hover:text-indigo-300 transition line-clamp-2">
                      {p.title}
                    </h3>

                    {p.assignee && (
                      <p className="text-xs text-slate-300 mt-1 font-medium flex items-center gap-1.5">
                        <svg className="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                        </svg>
                        {p.assignee}
                      </p>
                    )}

                    {p.abstract && (
                      <p className="text-xs text-slate-400 mt-2 line-clamp-3 leading-relaxed">
                        {p.abstract}
                      </p>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <div className="flex items-center gap-3">
                      {p.technology_domain && (
                        <span className="text-[11px] text-cyan-400">{p.technology_domain}</span>
                      )}
                      <span>Citations: <strong className="text-slate-200">{p.citation_count}</strong></span>
                    </div>

                    <div className="flex items-center gap-2">
                      {p.url && (
                        <a
                          href={p.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium transition"
                        >
                          View Source ↗
                        </a>
                      )}
                      <button
                        onClick={() => handleOpenEdit(p)}
                        className="p-1 text-slate-500 hover:text-indigo-400 transition"
                        title="Edit patent"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                      <button
                        onClick={() => handleDelete(p.id)}
                        className="p-1 text-slate-500 hover:text-rose-400 transition"
                        title="Remove patent"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Ingest Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h2 className="text-lg font-bold text-white">Ingest External Patent</h2>
            <p className="text-xs text-slate-400">
              Fetch normalized patent metadata from patent provider registries and associate it with your research profile.
            </p>

            <form onSubmit={handleIngestSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Patent Number *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. US11234567B2, US10987654B1, EP3456789A1"
                  value={ingestForm.patent_number}
                  onChange={(e) => setIngestForm({ ...ingestForm, patent_number: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Provider</label>
                <select
                  value={ingestForm.provider}
                  onChange={(e) => setIngestForm({ ...ingestForm, provider: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="mock">Mock Patent Registry (Deterministic)</option>
                  <option value="google_patents">Google Patents (URL Shell)</option>
                  <option value="lens">The Lens (Lens.org)</option>
                  <option value="uspto">USPTO Public Data</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowIngestModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 hover:bg-slate-700 rounded-xl text-xs font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalLoading}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-medium transition disabled:opacity-50"
                >
                  {modalLoading ? 'Ingesting...' : 'Ingest & Link'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Patent Modal */}
      {showEditModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-white">Edit Patent</h2>

            <form onSubmit={handleEditSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Patent Title *</label>
                <input
                  type="text"
                  required
                  placeholder="Patent title..."
                  value={editForm.title || ''}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assignee / Organization</label>
                  <input
                    type="text"
                    placeholder="e.g. MIT, IBM"
                    value={editForm.assignee || ''}
                    onChange={(e) => setEditForm({ ...editForm, assignee: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Classification (IPC/CPC)</label>
                  <input
                    type="text"
                    placeholder="e.g. G06N10/00"
                    value={editForm.patent_classification || ''}
                    onChange={(e) => setEditForm({ ...editForm, patent_classification: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Technology Domain</label>
                  <input
                    type="text"
                    placeholder="e.g. Quantum Technologies"
                    value={editForm.technology_domain || ''}
                    onChange={(e) => setEditForm({ ...editForm, technology_domain: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Citations</label>
                  <input
                    type="number"
                    min={0}
                    value={editForm.citation_count ?? 0}
                    onChange={(e) => setEditForm({ ...editForm, citation_count: Number(e.target.value) })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Inventors</label>
                <input
                  type="text"
                  placeholder="e.g. Dr. Jane Smith, Dr. Alan Doe"
                  value={editForm.inventors || ''}
                  onChange={(e) => setEditForm({ ...editForm, inventors: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Abstract / Summary</label>
                <textarea
                  rows={3}
                  placeholder="Detailed description of patent disclosure..."
                  value={editForm.abstract || ''}
                  onChange={(e) => setEditForm({ ...editForm, abstract: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 hover:bg-slate-700 rounded-xl text-xs font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium transition disabled:opacity-50"
                >
                  {modalLoading ? 'Updating...' : 'Update Patent'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-white">Add Patent Disclosure</h2>

            <form onSubmit={handleCreateSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Patent Number / Identifier *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. US12345678B2"
                  value={createForm.patent_number}
                  onChange={(e) => setCreateForm({ ...createForm, patent_number: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Patent Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Quantum Dot Sensor Array"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Assignee / Organization</label>
                  <input
                    type="text"
                    placeholder="e.g. MIT, IBM"
                    value={createForm.assignee || ''}
                    onChange={(e) => setCreateForm({ ...createForm, assignee: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Classification (IPC/CPC)</label>
                  <input
                    type="text"
                    placeholder="e.g. G06N10/00"
                    value={createForm.patent_classification || ''}
                    onChange={(e) => setCreateForm({ ...createForm, patent_classification: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Technology Domain</label>
                <input
                  type="text"
                  placeholder="e.g. Quantum Technologies"
                  value={createForm.technology_domain || ''}
                  onChange={(e) => setCreateForm({ ...createForm, technology_domain: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Abstract / Summary</label>
                <textarea
                  rows={3}
                  placeholder="Detailed description of patent disclosure..."
                  value={createForm.abstract || ''}
                  onChange={(e) => setCreateForm({ ...createForm, abstract: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 hover:bg-slate-700 rounded-xl text-xs font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalLoading}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-medium transition disabled:opacity-50"
                >
                  {modalLoading ? 'Indexing...' : 'Save Patent'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
