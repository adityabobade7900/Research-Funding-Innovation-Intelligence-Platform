'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { Patent, PatentListResponse, PatentCreatePayload, PatentIngestPayload } from '@/types/patent';
import {
  PatentLandscapeSummary,
  CompetitiveLandscapeResponse,
  PatentTrendsResponse,
  PatentClusteringResponse,
  InnovationMapResponse,
  PatentRecommendationsResponse,
} from '@/types/patent_intelligence';

type ActiveTab = 'search' | 'clusters' | 'trends' | 'competitors' | 'innovation_map' | 'my' | 'recommendations';

export default function PatentsPage() {
  const [patents, setPatents] = useState<Patent[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedClassification, setSelectedClassification] = useState('');
  const [selectedTab, setSelectedTab] = useState<ActiveTab>('search');
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<number>>(new Set());

  // Analytics states
  const [landscapeSummary, setLandscapeSummary] = useState<PatentLandscapeSummary | null>(null);
  const [competitiveData, setCompetitiveData] = useState<CompetitiveLandscapeResponse | null>(null);
  const [trendsData, setTrendsData] = useState<PatentTrendsResponse | null>(null);
  const [clusteringData, setClusteringData] = useState<PatentClusteringResponse | null>(null);
  const [innovationMapData, setInnovationMapData] = useState<InnovationMapResponse | null>(null);
  const [recommendationsData, setRecommendationsData] = useState<PatentRecommendationsResponse | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // Modals & Details
  const [selectedPatentDetails, setSelectedPatentDetails] = useState<Patent | null>(null);
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

  // Fetch patents list
  const fetchPatents = useCallback(async () => {
    if (selectedTab !== 'search' && selectedTab !== 'my') return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const endpoint = selectedTab === 'my' ? '/patents/my' : '/patents';
      const params: Record<string, string | number> = { limit: 50, offset: 0 };
      if (searchQuery) params.q = searchQuery;
      if (selectedDomain) params.domain = selectedDomain;
      if (selectedClassification) params.classification = selectedClassification;

      const res = await api.get<{ data: PatentListResponse }>(endpoint, { params });
      const items = res.data.data.items || [];
      setPatents(items);
      setTotal(res.data.data.total || 0);

      // Populate bookmarked ids
      const newBookmarked = new Set<number>();
      items.forEach((p) => {
        if (p.is_bookmarked || selectedTab === 'my') {
          newBookmarked.add(p.id);
        }
      });
      setBookmarkedIds((prev) => new Set([...Array.from(prev), ...Array.from(newBookmarked)]));
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load patents');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedDomain, selectedClassification, selectedTab]);

  // Fetch intelligence data depending on tab
  const fetchAnalyticsData = useCallback(async () => {
    if (selectedTab === 'search' || selectedTab === 'my') return;
    setAnalyticsLoading(true);
    setErrorMsg(null);
    try {
      const params: Record<string, string> = {};
      if (selectedDomain) params.domain = selectedDomain;
      if (selectedClassification) params.classification = selectedClassification;

      if (selectedTab === 'clusters') {
        const res = await api.get<{ data: PatentClusteringResponse }>('/patent-intelligence/clusters', { params });
        setClusteringData(res.data.data);
      } else if (selectedTab === 'trends') {
        const [trendsRes, summaryRes] = await Promise.all([
          api.get<{ data: PatentTrendsResponse }>('/patent-intelligence/trends', { params }),
          api.get<{ data: PatentLandscapeSummary }>('/patent-intelligence/landscape', { params }),
        ]);
        setTrendsData(trendsRes.data.data);
        setLandscapeSummary(summaryRes.data.data);
      } else if (selectedTab === 'competitors') {
        const compRes = await api.get<{ data: CompetitiveLandscapeResponse }>('/patent-intelligence/competitive-landscape', { params });
        setCompetitiveData(compRes.data.data);
      } else if (selectedTab === 'innovation_map') {
        const mapRes = await api.get<{ data: InnovationMapResponse }>('/patent-intelligence/innovation-map', { params });
        setInnovationMapData(mapRes.data.data);
      } else if (selectedTab === 'recommendations') {
        const recRes = await api.get<{ data: PatentRecommendationsResponse }>('/patent-intelligence/recommendations');
        setRecommendationsData(recRes.data.data);
      }
    } catch (err: any) {
      setErrorMsg('Failed to load patent analytics intelligence');
    } finally {
      setAnalyticsLoading(false);
    }
  }, [selectedTab, selectedDomain, selectedClassification]);

  useEffect(() => {
    if (selectedTab === 'search' || selectedTab === 'my') {
      const timer = setTimeout(() => {
        fetchPatents();
      }, 250);
      return () => clearTimeout(timer);
    } else {
      fetchAnalyticsData();
    }
  }, [fetchPatents, fetchAnalyticsData, selectedTab]);

  // Bookmark toggle handler
  const handleToggleBookmark = async (patentId: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const isBookmarked = bookmarkedIds.has(patentId);
    try {
      if (isBookmarked) {
        await api.delete(`/patents/${patentId}/bookmark`);
        setBookmarkedIds((prev) => {
          const next = new Set(prev);
          next.delete(patentId);
          return next;
        });
        setSuccessMsg('Patent removed from your linked bookmarks');
        if (selectedTab === 'my') {
          setPatents((prev) => prev.filter((p) => p.id !== patentId));
        }
      } else {
        await api.post(`/patents/${patentId}/bookmark`);
        setBookmarkedIds((prev) => new Set(prev).add(patentId));
        setSuccessMsg('Patent bookmarked and linked to your research profile');
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to update bookmark');
    }
  };

  // Inspect patent details
  const handleInspectPatent = async (patent: Patent) => {
    try {
      const res = await api.get<{ data: Patent }>(`/patents/${patent.id}`);
      setSelectedPatentDetails(res.data.data);
    } catch {
      setSelectedPatentDetails(patent);
    }
  };

  // Create patent
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
      setSuccessMsg('Patent indexed and linked successfully!');
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

  // Ingest patent
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

  // Edit patent
  const handleOpenEdit = (p: Patent, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
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

  // Delete patent
  const handleDelete = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (!confirm('Are you sure you want to remove this patent?')) return;
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
              Module 5: Patent Landscape Intelligence
            </span>
            <span className="text-xs text-slate-400">Total Indexed: {total}</span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Intellectual Property & Patent Intelligence</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Discover patents, run unsupervised ML clustering, analyze competitor portfolios, and map technology whitespace.
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

      {/* Navigation Tabs Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-3 rounded-2xl space-y-3">
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-950 p-1.5 rounded-xl border border-slate-800/80">
          <button
            onClick={() => setSelectedTab('search')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              selectedTab === 'search' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Patent Search ({total})
          </button>
          <button
            onClick={() => setSelectedTab('my')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              selectedTab === 'my' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            My Bookmarked / Linked
          </button>
          <button
            onClick={() => setSelectedTab('clusters')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center gap-1.5 ${
              selectedTab === 'clusters' ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            ML Clusters
          </button>
          <button
            onClick={() => setSelectedTab('trends')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              selectedTab === 'trends' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Filing Trends
          </button>
          <button
            onClick={() => setSelectedTab('competitors')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              selectedTab === 'competitors' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Competitor Analysis (HHI)
          </button>
          <button
            onClick={() => setSelectedTab('innovation_map')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
              selectedTab === 'innovation_map' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Innovation Mapping
          </button>
          <button
            onClick={() => setSelectedTab('recommendations')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition flex items-center gap-1.5 ${
              selectedTab === 'recommendations' ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Profile Recommendations
          </button>
        </div>

        {/* Global Filters Bar */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800/60">
          {(selectedTab === 'search' || selectedTab === 'my') && (
            <div className="flex-1 min-w-[200px] max-w-sm">
              <input
                type="text"
                placeholder="Search patent #, title, assignee, inventor..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}

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
            placeholder="Classification (e.g. G06N, A61K)..."
            value={selectedClassification}
            onChange={(e) => setSelectedClassification(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 max-w-xs"
          />

          {(searchQuery || selectedDomain || selectedClassification) && (
            <button
              onClick={() => { setSearchQuery(''); setSelectedDomain(''); setSelectedClassification(''); }}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium ml-auto"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* ========================================================= */}
      {/* TAB 1 & 2: Patent Search & My Bookmarked Patents */}
      {/* ========================================================= */}
      {(selectedTab === 'search' || selectedTab === 'my') && (
        <div className="space-y-4">
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
              {patents.map((p) => {
                const isBookmarked = bookmarkedIds.has(p.id) || selectedTab === 'my';
                return (
                  <div
                    key={p.id}
                    onClick={() => handleInspectPatent(p)}
                    className="group bg-slate-900/70 border border-slate-800/90 hover:border-indigo-500/50 p-5 rounded-2xl transition duration-200 flex flex-col justify-between shadow-sm hover:shadow-md cursor-pointer"
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
                          <button
                            onClick={(e) => handleToggleBookmark(p.id, e)}
                            className={`p-1 rounded-md transition ${
                              isBookmarked
                                ? 'text-amber-400 hover:text-amber-300 bg-amber-500/10'
                                : 'text-slate-500 hover:text-amber-400 hover:bg-slate-800'
                            }`}
                            title={isBookmarked ? 'Remove Bookmark' : 'Bookmark to Profile'}
                          >
                            <svg className="w-4 h-4" fill={isBookmarked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                            </svg>
                          </button>
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
                        <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
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
                            onClick={(e) => e.stopPropagation()}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium transition"
                          >
                            Source ↗
                          </a>
                        )}
                        <button
                          onClick={(e) => handleOpenEdit(p, e)}
                          className="p-1 text-slate-500 hover:text-indigo-400 transition"
                          title="Edit patent"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                        <button
                          onClick={(e) => handleDelete(p.id, e)}
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
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 3: Machine Learning Clusters (TF-IDF + K-Means) */}
      {/* ========================================================= */}
      {selectedTab === 'clusters' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                Unsupervised Machine Learning Patent Clustering
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Algorithm: <strong className="text-cyan-400">{clusteringData?.algorithm || 'TF-IDF Vectorization + K-Means'}</strong>. Groups disclosures by technical and semantic centroid proximity.
              </p>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono text-slate-300">
                {clusteringData?.total_clusters ?? 0} Clusters / {clusteringData?.total_patents ?? 0} Patents
              </span>
            </div>
          </div>

          {analyticsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-56" />
              ))}
            </div>
          ) : clusteringData?.clusters.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/40 border border-slate-800 rounded-2xl">
              <p className="text-xs text-slate-400">No clusters formed. Try clearing filters or ingesting patents.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {clusteringData?.clusters.map((cluster) => (
                <div
                  key={cluster.cluster_id}
                  className="bg-slate-900/70 border border-slate-800 hover:border-cyan-500/40 p-5 rounded-2xl space-y-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                        Cluster #{cluster.cluster_id}
                      </span>
                      <h3 className="text-base font-bold text-white mt-1.5">{cluster.cluster_name}</h3>
                      <span className="text-xs text-indigo-400 font-medium">{cluster.technology_domain}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-base font-bold text-white">{cluster.patent_count}</span>
                      <span className="text-[10px] text-slate-400 block">({cluster.share_percentage}%)</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                    {cluster.description}
                  </p>

                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                      Centroid Dominant Keywords
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {cluster.dominant_terms.map((term) => (
                        <span key={term} className="px-2 py-0.5 rounded-md text-xs font-mono bg-slate-800 text-slate-200 border border-slate-700">
                          {term}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                      Representative Patents & Centroid Proximity
                    </span>
                    <div className="space-y-2">
                      {cluster.representative_patents.slice(0, 3).map((rep) => (
                        <div
                          key={rep.patent_id}
                          onClick={() => handleInspectPatent(rep as any)}
                          className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 text-xs cursor-pointer flex items-center justify-between gap-3"
                        >
                          <div className="truncate">
                            <span className="font-mono text-[11px] font-bold text-indigo-400 mr-2">{rep.patent_number}</span>
                            <span className="text-slate-200 truncate">{rep.title}</span>
                          </div>
                          {rep.distance_to_centroid !== null && (
                            <span className="text-[10px] font-mono text-cyan-400 shrink-0">
                              dist: {rep.distance_to_centroid}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 4: Patent Trends Analysis */}
      {/* ========================================================= */}
      {selectedTab === 'trends' && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Total Patents Analyzed</span>
              <span className="text-xl font-bold text-white mt-1 block">{trendsData?.total_patents ?? 0}</span>
              <span className="text-[10px] text-cyan-400">Historical Corpus</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Active Year Span</span>
              <span className="text-xl font-bold text-indigo-400 mt-1 block">
                {trendsData?.year_range.min_year ?? 'N/A'} - {trendsData?.year_range.max_year ?? 'N/A'}
              </span>
              <span className="text-[10px] text-slate-400">Timeline</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Total Assignees</span>
              <span className="text-xl font-bold text-emerald-400 mt-1 block">{landscapeSummary?.total_assignees ?? 0}</span>
              <span className="text-[10px] text-slate-400">Organizations</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Average Citations</span>
              <span className="text-xl font-bold text-amber-400 mt-1 block">{landscapeSummary?.average_citations ?? 0}</span>
              <span className="text-[10px] text-slate-400">Citations / Patent</span>
            </div>
          </div>

          {/* Yearly Filing Table & Growth */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              Year-over-Year (YoY) Patent Filing and Grant Trajectory
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2 font-medium">Year</th>
                    <th className="pb-2 font-medium">Patent Filings</th>
                    <th className="pb-2 font-medium">Grants / Publications</th>
                    <th className="pb-2 font-medium">YoY Filing Growth</th>
                    <th className="pb-2 font-medium">Filing Activity Bar</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {trendsData?.points.map((pt) => {
                    const maxFilings = Math.max(...(trendsData.points.map((p) => p.filings_count) || [1]));
                    const barWidth = Math.max(5, (pt.filings_count / maxFilings) * 100);
                    return (
                      <tr key={pt.year} className="hover:bg-slate-950/40">
                        <td className="py-2.5 font-bold text-white">{pt.year}</td>
                        <td className="py-2.5 text-cyan-400 font-semibold">{pt.filings_count}</td>
                        <td className="py-2.5 text-indigo-300">{pt.grants_count}</td>
                        <td className="py-2.5">
                          {pt.filing_growth_rate !== null ? (
                            <span className={`font-semibold ${pt.filing_growth_rate >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                              {pt.filing_growth_rate >= 0 ? `+${pt.filing_growth_rate}%` : `${pt.filing_growth_rate}%`}
                            </span>
                          ) : (
                            <span className="text-slate-500">Baseline</span>
                          )}
                        </td>
                        <td className="py-2.5 w-1/3">
                          <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                            <div
                              style={{ width: `${barWidth}%` }}
                              className="h-full bg-gradient-to-r from-cyan-500 to-indigo-500 rounded-full"
                            ></div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 5: Competitor Analysis & Composite Competitive Index */}
      {/* ========================================================= */}
      {selectedTab === 'competitors' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Total Competitor Assignees</span>
              <span className="text-xl font-bold text-white mt-1 block">{competitiveData?.total_competitors ?? 0}</span>
              <span className="text-[10px] text-slate-400">Active Applicants</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Assignee Concentration (HHI)</span>
              <span className="text-xl font-bold text-amber-400 mt-1 block">{competitiveData?.assignee_concentration_hhi ?? 0}</span>
              <span className="text-[10px] text-slate-400">Scale: 0-10000 (Market Concentration)</span>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[11px] text-slate-400 font-medium block">Concentration Level</span>
              <span className="text-xl font-bold text-cyan-400 mt-1 block">
                {competitiveData?.concentration_level?.replace('_', ' ') ?? 'DIVERSIFIED'}
              </span>
              <span className="text-[10px] text-slate-400">Market Structure</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Composite Competitive Index Ranking
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Formula considers: Volume (40%), Recent Filing Velocity (30%), Citation Strength (20%), and Domain Breadth (10%).
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2 font-medium">Assignee</th>
                    <th className="pb-2 font-medium">Patents</th>
                    <th className="pb-2 font-medium">Domain Breadth</th>
                    <th className="pb-2 font-medium">Filing Velocity</th>
                    <th className="pb-2 font-medium">Competitive Index</th>
                    <th className="pb-2 font-medium">Classification</th>
                    <th className="pb-2 font-medium">Key Drivers</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {competitiveData?.competitors.map((comp) => (
                    <tr key={comp.assignee} className="hover:bg-slate-950/40">
                      <td className="py-3 font-bold text-white">{comp.assignee}</td>
                      <td className="py-3 text-slate-300">{comp.patent_count}</td>
                      <td className="py-3 text-slate-300">{comp.domain_breadth_count} fields</td>
                      <td className="py-3 text-cyan-400 font-semibold">{comp.recent_filing_velocity_pct}%</td>
                      <td className="py-3">
                        <span className="text-sm font-bold text-emerald-400">{comp.competitive_index} / 100</span>
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          comp.classification === 'DOMINANT_PORTFOLIO'
                            ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/30'
                            : comp.classification === 'HIGH_VELOCITY'
                            ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                            : comp.classification === 'NICHE_SPECIALIST'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                            : 'bg-slate-800 text-slate-300'
                        }`}>
                          {comp.classification.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400 text-[11px]">
                        {comp.key_drivers.join(' • ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 6: Innovation Mapping */}
      {/* ========================================================= */}
      {selectedTab === 'innovation_map' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
              Multi-Dimensional Innovation Map
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Connects Patent → Technology Domain → Classification → Assignee → Whitespace Opportunities.
            </p>
          </div>

          {/* Domain x Assignee Matrix */}
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-white">Domain × Assignee Cross-Tabulation Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="pb-2 font-medium">Technology Domain</th>
                    <th className="pb-2 font-medium">Assignee Organization</th>
                    <th className="pb-2 font-medium">Patents</th>
                    <th className="pb-2 font-medium">Patent Disclosures</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {innovationMapData?.matrix.map((cell, idx) => (
                    <tr key={idx} className="hover:bg-slate-950/40">
                      <td className="py-2.5 font-semibold text-cyan-400">{cell.domain}</td>
                      <td className="py-2.5 text-white">{cell.assignee}</td>
                      <td className="py-2.5 font-bold text-slate-200">{cell.patent_count}</td>
                      <td className="py-2.5 font-mono text-[11px] text-slate-400">{cell.patent_numbers.join(', ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Hotspots & Whitespaces */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Hotspots */}
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Active Innovation Hotspots
              </h3>
              <div className="space-y-3">
                {innovationMapData?.hotspots.map((hs, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{hs.domain} ({hs.classification})</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        {hs.activity_type.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Patents: <strong>{hs.patent_count}</strong></span>
                      <span>Filing Velocity: <strong className="text-cyan-400">{hs.velocity_score}%</strong></span>
                    </div>
                    <div className="text-[10px] text-slate-400 truncate">
                      Leading Applicants: {hs.top_assignees.join(', ') || 'Various'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Whitespaces */}
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-400"></span>
                Potential Technology Whitespace Opportunities
              </h3>
              <div className="space-y-3">
                {innovationMapData?.whitespaces.map((ws, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{ws.domain}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        {ws.opportunity_level} OPPORTUNITY
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed">{ws.description}</p>
                    <span className="text-[10px] text-amber-400 block">{ws.whitespace_reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================= */}
      {/* TAB 7: Profile-Based Recommendations (Module 3 Integration) */}
      {/* ========================================================= */}
      {selectedTab === 'recommendations' && (
        <div className="space-y-6">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
              Profile-Based Patent Recommendations
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Personalized patent intelligence matched against your research domains, keywords, and publication track record.
            </p>
          </div>

          {analyticsLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-44" />
              ))}
            </div>
          ) : recommendationsData?.recommendations.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/40 border border-slate-800 rounded-2xl">
              <p className="text-xs text-slate-400">No patent recommendations found for current profile.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendationsData?.recommendations.map((rec) => {
                const isBookmarked = bookmarkedIds.has(rec.patent_id);
                return (
                  <div
                    key={rec.patent_id}
                    onClick={() => handleInspectPatent(rec as any)}
                    className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-emerald-500/40 space-y-3 cursor-pointer shadow-sm transition"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="font-mono text-xs font-bold text-indigo-400 mr-2">{rec.patent_number}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                          Match: {rec.match_score}%
                        </span>
                      </div>
                      <button
                        onClick={(e) => handleToggleBookmark(rec.patent_id, e)}
                        className={`p-1 rounded-md transition ${
                          isBookmarked ? 'text-amber-400 bg-amber-500/10' : 'text-slate-500 hover:text-amber-400'
                        }`}
                        title={isBookmarked ? 'Remove Bookmark' : 'Bookmark to Profile'}
                      >
                        <svg className="w-4 h-4" fill={isBookmarked ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                        </svg>
                      </button>
                    </div>

                    <h4 className="text-sm font-semibold text-white line-clamp-2">{rec.title}</h4>
                    {rec.assignee && (
                      <span className="text-xs text-slate-400 block">{rec.assignee}</span>
                    )}

                    <p className="text-xs text-slate-300 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 leading-relaxed">
                      {rec.rationale}
                    </p>

                    <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60">
                      <span>Domain: <strong className="text-cyan-400">{rec.technology_domain || 'General'}</strong></span>
                      <span>Citations: <strong className="text-slate-200">{rec.citation_count}</strong></span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ========================================================= */}
      {/* Patent Details Drawer / Inspection Modal */}
      {/* ========================================================= */}
      {selectedPatentDetails && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/30">
                  {selectedPatentDetails.patent_number}
                </span>
                <h2 className="text-lg font-bold text-white mt-1.5 leading-snug">
                  {selectedPatentDetails.title}
                </h2>
              </div>
              <button
                onClick={() => setSelectedPatentDetails(null)}
                className="text-slate-400 hover:text-slate-200 text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Metadata Grid */}
            <div className="grid grid-cols-2 gap-3 text-xs bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              <div>
                <span className="text-slate-500 block">Assignee Organization:</span>
                <span className="font-semibold text-slate-200">{selectedPatentDetails.assignee || 'Not available'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Inventors:</span>
                <span className="font-semibold text-slate-200">{selectedPatentDetails.inventors || 'Not available'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Technology Domain:</span>
                <span className="font-semibold text-cyan-400">{selectedPatentDetails.technology_domain || 'Not classified'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Classification (IPC/CPC):</span>
                <span className="font-semibold text-slate-200">{selectedPatentDetails.patent_classification || 'Not available'}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Citation Count:</span>
                <span className="font-semibold text-amber-400">{selectedPatentDetails.citation_count} citations</span>
              </div>
              <div>
                <span className="text-slate-500 block">Source Provider:</span>
                <span className="font-semibold text-slate-200 uppercase">{selectedPatentDetails.source || 'manual'}</span>
              </div>
            </div>

            {/* Abstract */}
            <div>
              <span className="text-xs font-semibold text-slate-300 block mb-1">Patent Abstract & Disclosures</span>
              <p className="text-xs text-slate-400 leading-relaxed bg-slate-950 p-3 rounded-xl border border-slate-800/80">
                {selectedPatentDetails.abstract || 'Abstract disclosure not available for this record.'}
              </p>
            </div>

            {/* Actions Bar */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-800 text-xs">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleToggleBookmark(selectedPatentDetails.id)}
                  className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 ${
                    bookmarkedIds.has(selectedPatentDetails.id)
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  <svg className="w-3.5 h-3.5" fill={bookmarkedIds.has(selectedPatentDetails.id) ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                  </svg>
                  {bookmarkedIds.has(selectedPatentDetails.id) ? 'Bookmarked' : 'Bookmark Patent'}
                </button>

                {selectedPatentDetails.url && (
                  <a
                    href={selectedPatentDetails.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium transition"
                  >
                    View on Google Patents ↗
                  </a>
                )}
              </div>

              <button
                onClick={() => setSelectedPatentDetails(null)}
                className="px-4 py-1.5 bg-slate-800 text-slate-300 hover:bg-slate-700 rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
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
