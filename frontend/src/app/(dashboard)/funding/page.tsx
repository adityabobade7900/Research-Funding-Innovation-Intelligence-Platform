'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  FundingOpportunity,
  FundingOpportunityListResponse,
  FundingOpportunityCreatePayload,
  EligibilityEvaluationResult,
  FundingRecommendationItem,
  FundingRecommendationResponse
} from '@/types/funding';

export default function FundingPage() {
  const [activeView, setActiveView] = useState<'explore' | 'recommendations'>('explore');

  // Opportunities List State
  const [opportunities, setOpportunities] = useState<FundingOpportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgency, setSelectedAgency] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  // Recommendations State
  const [recommendations, setRecommendations] = useState<FundingRecommendationItem[]>([]);
  const [recTotal, setRecTotal] = useState(0);
  const [recProfileSummary, setRecProfileSummary] = useState<any>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [recMinScore, setRecMinScore] = useState<number>(0);
  const [recDomain, setRecDomain] = useState('');
  const [recType, setRecType] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Eligibility Evaluation State
  const [selectedOppForEligibility, setSelectedOppForEligibility] = useState<FundingOpportunity | null>(null);
  const [eligibilityResult, setEligibilityResult] = useState<EligibilityEvaluationResult | null>(null);
  const [eligibilityLoading, setEligibilityLoading] = useState(false);
  const [eligibilityError, setEligibilityError] = useState<string | null>(null);

  // Form state
  const [createForm, setCreateForm] = useState<FundingOpportunityCreatePayload>({
    title: '',
    funding_agency: '',
    funding_program: '',
    description: '',
    funding_amount: undefined,
    currency: 'USD',
    application_deadline: '',
    opportunity_type: 'Grant',
    eligibility_summary: '',
    eligible_institutions: '',
    geographic_restrictions: '',
    status: 'open',
    source: 'manual',
    url: '',
    domain_names: [],
    keywords: []
  });

  const [keywordInput, setKeywordInput] = useState('');

  const fetchOpportunities = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const params: Record<string, string | number> = { limit: 50, offset: 0 };
      if (searchQuery) params.q = searchQuery;
      if (selectedAgency) params.agency = selectedAgency;
      if (selectedDomain) params.domain = selectedDomain;
      if (selectedType) params.opportunity_type = selectedType;
      if (selectedStatus) params.status = selectedStatus;

      const res = await api.get<{ data: FundingOpportunityListResponse }>('/api/v1/funding', { params });
      setOpportunities(res.data.data.items || []);
      setTotal(res.data.data.total || 0);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to load funding opportunities');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedAgency, selectedDomain, selectedType, selectedStatus]);

  const fetchRecommendations = useCallback(async () => {
    setRecLoading(true);
    setErrorMsg(null);
    try {
      const params: Record<string, string | number> = {
        limit: 25,
        minimum_score: recMinScore,
        status: 'open'
      };
      if (recDomain) params.domain = recDomain;
      if (recType) params.opportunity_type = recType;

      const res = await api.get<{ data: FundingRecommendationResponse }>('/api/v1/funding/recommendations', { params });
      setRecommendations(res.data.data.items || []);
      setRecTotal(res.data.data.total_recommended || 0);
      setRecProfileSummary(res.data.data.profile_summary || null);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to generate recommendations');
    } finally {
      setRecLoading(false);
    }
  }, [recMinScore, recDomain, recType]);

  useEffect(() => {
    if (activeView === 'explore') {
      const timer = setTimeout(() => {
        fetchOpportunities();
      }, 250);
      return () => clearTimeout(timer);
    } else {
      fetchRecommendations();
    }
  }, [activeView, fetchOpportunities, fetchRecommendations]);

  const handleCheckEligibility = async (opp: FundingOpportunity) => {
    setSelectedOppForEligibility(opp);
    setEligibilityResult(null);
    setEligibilityLoading(true);
    setEligibilityError(null);
    try {
      const res = await api.get<{ data: EligibilityEvaluationResult }>(`/api/v1/funding/${opp.id}/eligibility`);
      setEligibilityResult(res.data.data);
    } catch (err: any) {
      setEligibilityError(err.response?.data?.detail?.message || 'Failed to evaluate eligibility');
    } finally {
      setEligibilityLoading(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setModalLoading(true);
    setErrorMsg(null);
    try {
      const payload = {
        ...createForm,
        funding_amount: createForm.funding_amount ? Number(createForm.funding_amount) : undefined,
        application_deadline: createForm.application_deadline ? new Date(createForm.application_deadline).toISOString() : undefined,
      };
      await api.post('/api/v1/funding', payload);
      setSuccessMsg('Funding opportunity indexed successfully!');
      setShowCreateModal(false);
      setCreateForm({
        title: '',
        funding_agency: '',
        funding_program: '',
        description: '',
        funding_amount: undefined,
        currency: 'USD',
        application_deadline: '',
        opportunity_type: 'Grant',
        eligibility_summary: '',
        eligible_institutions: '',
        geographic_restrictions: '',
        status: 'open',
        source: 'manual',
        url: '',
        domain_names: [],
        keywords: []
      });
      fetchOpportunities();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to create funding opportunity');
    } finally {
      setModalLoading(false);
    }
  };

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !createForm.keywords?.includes(keywordInput.trim())) {
      setCreateForm({
        ...createForm,
        keywords: [...(createForm.keywords || []), keywordInput.trim()]
      });
      setKeywordInput('');
    }
  };

  const handleRemoveKeyword = (kw: string) => {
    setCreateForm({
      ...createForm,
      keywords: (createForm.keywords || []).filter(k => k !== kw)
    });
  };

  const formatCurrency = (amount: number | null, currency: string) => {
    if (!amount) return 'Undisclosed';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDeadline = (dateStr: string | null) => {
    if (!dateStr) return 'Rolling / Open';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ELIGIBLE':
        return <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-bold uppercase tracking-wider">Eligible Match</span>;
      case 'INELIGIBLE':
        return <span className="px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg text-xs font-bold uppercase tracking-wider">Ineligible</span>;
      case 'INSUFFICIENT_DATA':
        return <span className="px-3 py-1 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg text-xs font-bold uppercase tracking-wider">Insufficient Profile Info</span>;
      default:
        return <span className="px-3 py-1 bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded-lg text-xs font-bold uppercase tracking-wider">Conditional Match</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Deterministic Matching &amp; Recommendations
            </span>
            <span className="text-xs text-slate-400">Total Open RFPs: {total}</span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Research Funding &amp; Intelligence</h1>
          <p className="text-sm text-slate-400 mt-0.5">
            Discover grants, fellowships, and contracts across federal and international agencies with explainable recommendations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => { setShowCreateModal(true); setErrorMsg(null); setSuccessMsg(null); }}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition shadow-lg shadow-indigo-900/20 flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
            </svg>
            Index Opportunity
          </button>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveView('explore')}
          className={`px-4 py-2 text-sm font-medium rounded-xl transition flex items-center gap-2 ${
            activeView === 'explore'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
          Explore All Opportunities ({total})
        </button>

        <button
          onClick={() => setActiveView('recommendations')}
          className={`px-4 py-2 text-sm font-medium rounded-xl transition flex items-center gap-2 ${
            activeView === 'recommendations'
              ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-900/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Personalized Recommendations {recTotal > 0 && `(${recTotal})`}
        </button>
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

      {/* =========================================================================
          VIEW 1: EXPLORE ALL OPPORTUNITIES
          ========================================================================= */}
      {activeView === 'explore' && (
        <div className="space-y-6">
          {/* Filter and Search Bar */}
          <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl space-y-3">
            <div className="relative">
              <input
                type="text"
                placeholder="Search grants by keyword, title, agency, or program..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Multi-Filters */}
            <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-slate-800/60">
              <select
                value={selectedAgency}
                onChange={(e) => setSelectedAgency(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Funding Agencies</option>
                <option value="National Science Foundation">National Science Foundation (NSF)</option>
                <option value="National Institutes of Health">National Institutes of Health (NIH)</option>
                <option value="Department of Energy">Department of Energy (DOE)</option>
                <option value="DARPA">DARPA</option>
                <option value="Horizon Europe">Horizon Europe</option>
              </select>

              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Research Domains</option>
                <option value="Quantum Technologies">Quantum Technologies</option>
                <option value="Biotechnology & Genomic Sciences">Biotechnology</option>
                <option value="Clean Energy & Sustainability">Clean Energy</option>
                <option value="Artificial Intelligence & Machine Learning">Artificial Intelligence</option>
                <option value="Cybersecurity & Cryptography">Cybersecurity</option>
              </select>

              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Opportunity Types</option>
                <option value="Grant">Grant</option>
                <option value="Fellowship">Fellowship</option>
                <option value="Contract">Contract</option>
                <option value="Award">Award</option>
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Statuses</option>
                <option value="open">Open</option>
                <option value="upcoming">Upcoming</option>
                <option value="rolling">Rolling</option>
                <option value="closed">Closed</option>
              </select>

              {(searchQuery || selectedAgency || selectedDomain || selectedType || selectedStatus) && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setSelectedAgency('');
                    setSelectedDomain('');
                    setSelectedType('');
                    setSelectedStatus('');
                  }}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-medium ml-auto"
                >
                  Clear Filters
                </button>
              )}
            </div>
          </div>

          {/* Opportunities List */}
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/60 border border-slate-800 p-5 rounded-2xl h-36" />
              ))}
            </div>
          ) : opportunities.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8">
              <div className="w-12 h-12 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-slate-200">No funding opportunities found</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto mt-1">
                Try adjusting your search query or filter tags, or click &quot;Index Opportunity&quot; to add a new RFP.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {opportunities.map((opp) => (
                <div
                  key={opp.id}
                  className="bg-slate-900/70 border border-slate-800/90 hover:border-indigo-500/50 p-5 rounded-2xl transition duration-200 shadow-sm hover:shadow-md flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {opp.funding_agency}
                      </span>
                      {opp.funding_program && (
                        <span className="text-xs text-slate-400 font-medium">
                          • {opp.funding_program}
                        </span>
                      )}
                      <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded ${
                        opp.status === 'open' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'
                      }`}>
                        {opp.status}
                      </span>
                    </div>

                    <h3 className="text-base font-bold text-white hover:text-indigo-300 transition">
                      {opp.title}
                    </h3>

                    {opp.description && (
                      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                        {opp.description}
                      </p>
                    )}

                    {/* Domains & Keywords */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      {opp.domains.map((d) => (
                        <span key={d.id} className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-800/50">
                          {d.name}
                        </span>
                      ))}
                      {opp.keywords.map((k) => (
                        <span key={k.id} className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-400">
                          #{k.keyword}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Amount & Actions Panel */}
                  <div className="md:text-right border-t md:border-t-0 md:border-l border-slate-800/80 pt-3 md:pt-0 md:pl-6 flex flex-col justify-between items-start md:items-end min-w-[210px] gap-2">
                    <div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Funding Amount</span>
                      <span className="text-lg font-bold text-emerald-400">
                        {formatCurrency(opp.funding_amount, opp.currency)}
                      </span>
                    </div>

                    <div>
                      <span className="text-[10px] text-slate-400 block">Deadline:</span>
                      <span className="text-xs font-semibold text-slate-200">
                        {formatDeadline(opp.application_deadline)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mt-2">
                      <button
                        onClick={() => handleCheckEligibility(opp)}
                        className="px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/40 rounded-xl text-xs font-semibold transition flex items-center gap-1"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Check My Eligibility
                      </button>

                      {opp.url && (
                        <a
                          href={opp.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs transition"
                          title="View Official RFP"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          VIEW 2: PERSONALIZED FUNDING RECOMMENDATIONS (RANKED & EXPLAINABLE)
          ========================================================================= */}
      {activeView === 'recommendations' && (
        <div className="space-y-6">
          {/* Profile Summary Context & Controls Bar */}
          <div className="bg-slate-900/90 border border-indigo-900/40 p-5 rounded-2xl space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
              <div>
                <span className="text-xs font-bold text-indigo-400 tracking-wider uppercase">
                  Targeted Researcher Profile Context
                </span>
                <div className="flex flex-wrap items-center gap-2 mt-1">
                  <span className="text-sm font-semibold text-white">
                    {recProfileSummary?.institution || 'Academic Researcher'}
                  </span>
                  {recProfileSummary?.domains?.map((dom: string, i: number) => (
                    <span key={i} className="px-2 py-0.5 bg-indigo-950 text-indigo-300 border border-indigo-800/60 rounded-md text-xs">
                      {dom}
                    </span>
                  ))}
                  <span className="text-xs text-slate-400">
                    • {recProfileSummary?.keyword_count || 0} active keywords
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Min Match Score:</span>
                <select
                  value={recMinScore}
                  onChange={(e) => setRecMinScore(Number(e.target.value))}
                  className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
                >
                  <option value={0}>All Matches (≥ 0%)</option>
                  <option value={50}>Moderate (≥ 50%)</option>
                  <option value={70}>Strong (≥ 70%)</option>
                  <option value={85}>High Confidence (≥ 85%)</option>
                </select>

                <button
                  onClick={fetchRecommendations}
                  className="px-3 py-1.5 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 rounded-lg text-xs font-semibold transition"
                >
                  Refresh
                </button>
              </div>
            </div>

            {/* Recommendation Explanatory Note */}
            <div className="flex items-start gap-2.5 text-xs text-slate-400 bg-slate-950/60 p-3 rounded-xl border border-slate-800/60">
              <span className="text-indigo-400 text-base">ℹ</span>
              <p>
                Recommendations are generated deterministically using your research domain taxonomy, keyword density, institutional eligibility, and proposal preparation deadlines. Strictly ineligible opportunities are automatically excluded.
              </p>
            </div>
          </div>

          {/* Recommendations List */}
          {recLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-48" />
              ))}
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/40 border border-slate-800/80 rounded-2xl p-8">
              <div className="w-12 h-12 rounded-full bg-indigo-950/60 text-indigo-400 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-base font-semibold text-slate-200">No matching recommendations found</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                Try lowering the minimum match score threshold, or update your Research Profile with additional domains and keywords to unlock more opportunities.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec, index) => {
                const opp = rec.opportunity;
                const isTop = index === 0;

                return (
                  <div
                    key={opp.id}
                    className={`p-6 rounded-2xl border transition duration-200 shadow-md ${
                      isTop
                        ? 'bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border-indigo-500/60 ring-1 ring-indigo-500/20'
                        : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
                      {/* Left Details */}
                      <div className="space-y-3 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className={`px-2.5 py-0.5 rounded-lg text-xs font-extrabold tracking-wider uppercase ${
                            index === 0
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                              : index < 3
                              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                              : 'bg-slate-800 text-slate-400'
                          }`}>
                            #{index + 1} Recommended
                          </span>

                          <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                            {opp.funding_agency}
                          </span>

                          {opp.funding_program && (
                            <span className="text-xs text-slate-400">
                              • {opp.funding_program}
                            </span>
                          )}

                          {getStatusBadge(rec.eligibility_status)}
                        </div>

                        <h3 className="text-lg font-bold text-white hover:text-indigo-300 transition">
                          {opp.title}
                        </h3>

                        {opp.description && (
                          <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                            {opp.description}
                          </p>
                        )}

                        {/* Matched Signals */}
                        <div className="flex flex-wrap items-center gap-2 pt-1">
                          {rec.matched_domains.map((dom, idx) => (
                            <span key={idx} className="text-xs px-2.5 py-0.5 rounded-md bg-indigo-950 text-indigo-300 border border-indigo-800/60 font-medium">
                              🎯 Domain: {dom}
                            </span>
                          ))}
                          {rec.matched_keywords.map((kw, idx) => (
                            <span key={idx} className="text-xs px-2.5 py-0.5 rounded-md bg-cyan-950/60 text-cyan-300 border border-cyan-800/40">
                              ✦ {kw}
                            </span>
                          ))}
                        </div>

                        {/* Recommendation Rationale Box */}
                        <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80 space-y-1.5">
                          <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider block">
                            Recommendation Rationale:
                          </span>
                          {rec.reasons.map((reason, idx) => (
                            <div key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                              <span className="text-indigo-400 font-bold">✓</span>
                              <span>{reason}</span>
                            </div>
                          ))}

                          {rec.warnings.length > 0 && (
                            <div className="pt-1.5 border-t border-slate-800/60 space-y-1">
                              {rec.warnings.map((w, idx) => (
                                <div key={idx} className="text-xs text-amber-300/90 flex items-start gap-1.5">
                                  <span>⚠</span>
                                  <span>{w}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Right Metrics & Action Box */}
                      <div className="lg:text-right border-t lg:border-t-0 lg:border-l border-slate-800/80 pt-4 lg:pt-0 lg:pl-6 flex flex-col justify-between items-start lg:items-end min-w-[220px] gap-3">
                        {/* Score Circular / Numerical Gauge */}
                        <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl w-full text-center lg:text-right">
                          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">
                            Compatibility Score
                          </span>
                          <span className="text-3xl font-black text-indigo-400">
                            {rec.recommendation_score}%
                          </span>
                          <span className="text-[10px] text-slate-500 block mt-0.5">Deterministic Match</span>
                        </div>

                        <div>
                          <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Funding Amount</span>
                          <span className="text-base font-bold text-emerald-400">
                            {formatCurrency(opp.funding_amount, opp.currency)}
                          </span>
                        </div>

                        <div>
                          <span className="text-[10px] text-slate-400 block">Deadline:</span>
                          <span className="text-xs font-semibold text-slate-200">
                            {formatDeadline(opp.application_deadline)}
                          </span>
                        </div>

                        <div className="flex items-center gap-2 w-full lg:w-auto pt-1">
                          <button
                            onClick={() => handleCheckEligibility(opp)}
                            className="flex-1 lg:flex-none px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition shadow-md shadow-indigo-900/30 flex items-center justify-center gap-1.5"
                          >
                            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Deep Eligibility Audit
                          </button>

                          {opp.url && (
                            <a
                              href={opp.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs transition"
                              title="Open RFP Portal"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Eligibility Evaluation Modal */}
      {selectedOppForEligibility && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-3 border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs text-indigo-400 font-semibold tracking-wider uppercase">
                  Deterministic Eligibility Evaluation
                </span>
                <h2 className="text-lg font-bold text-white mt-0.5 line-clamp-1">
                  {selectedOppForEligibility.title}
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  {selectedOppForEligibility.funding_agency} {selectedOppForEligibility.funding_program ? `• ${selectedOppForEligibility.funding_program}` : ''}
                </p>
              </div>
              <button
                onClick={() => setSelectedOppForEligibility(null)}
                className="text-slate-400 hover:text-slate-200 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            {eligibilityLoading ? (
              <div className="py-12 text-center space-y-3">
                <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs text-slate-400">Evaluating profile domains, research interests, geography, and institution criteria...</p>
              </div>
            ) : eligibilityError ? (
              <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-xs">
                {eligibilityError}
              </div>
            ) : eligibilityResult ? (
              <div className="space-y-4">
                {/* Status & Score Header Card */}
                <div className="flex items-center justify-between p-4 bg-slate-950 border border-slate-800 rounded-xl">
                  <div>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Evaluation Outcome</span>
                    {getStatusBadge(eligibilityResult.eligibility_status)}
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Compatibility Score</span>
                    <span className="text-2xl font-black text-indigo-400">
                      {eligibilityResult.compatibility_score}%
                    </span>
                  </div>
                </div>

                {/* Explanation / Primary Reasons */}
                {eligibilityResult.reasons.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-slate-300 block">Evaluation Explanation</span>
                    <div className="space-y-1 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                      {eligibilityResult.reasons.map((reason, idx) => (
                        <p key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-indigo-400 font-bold">•</span>
                          <span>{reason}</span>
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {/* Matched Criteria */}
                {eligibilityResult.matched_criteria.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                      </svg>
                      Matched Criteria ({eligibilityResult.matched_criteria.length})
                    </span>
                    <div className="space-y-1 bg-emerald-950/10 p-3 rounded-xl border border-emerald-500/20">
                      {eligibilityResult.matched_criteria.map((item, idx) => (
                        <div key={idx} className="text-xs text-emerald-300 flex items-start gap-2">
                          <span>✓</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Failed Criteria */}
                {eligibilityResult.failed_criteria.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-rose-400 flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Failed Criteria ({eligibilityResult.failed_criteria.length})
                    </span>
                    <div className="space-y-1 bg-rose-950/10 p-3 rounded-xl border border-rose-500/20">
                      {eligibilityResult.failed_criteria.map((item, idx) => (
                        <div key={idx} className="text-xs text-rose-300 flex items-start gap-2">
                          <span>✗</span>
                          <span>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Warnings & Missing Profile Data */}
                {(eligibilityResult.warnings.length > 0 || eligibilityResult.missing_information.length > 0) && (
                  <div className="space-y-1.5">
                    <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      Warnings & Missing Profile Information
                    </span>
                    <div className="space-y-1 bg-amber-950/10 p-3 rounded-xl border border-amber-500/20">
                      {eligibilityResult.warnings.map((w, idx) => (
                        <div key={`w-${idx}`} className="text-xs text-amber-300 flex items-start gap-2">
                          <span>⚠</span>
                          <span>{w}</span>
                        </div>
                      ))}
                      {eligibilityResult.missing_information.map((m, idx) => (
                        <div key={`m-${idx}`} className="text-xs text-amber-200/80 flex items-start gap-2">
                          <span>ℹ</span>
                          <span>Missing data: {m}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : null}

            <div className="pt-3 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedOppForEligibility(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-xl transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-white">Index Funding Opportunity</h2>

            <form onSubmit={handleCreateSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Opportunity Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Scalable Quantum Information Science Program"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Funding Agency *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. National Science Foundation"
                    value={createForm.funding_agency}
                    onChange={(e) => setCreateForm({ ...createForm, funding_agency: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Program Name</label>
                  <input
                    type="text"
                    placeholder="e.g. QISE Track-1"
                    value={createForm.funding_program || ''}
                    onChange={(e) => setCreateForm({ ...createForm, funding_program: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Funding Amount ($)</label>
                  <input
                    type="number"
                    placeholder="e.g. 750000"
                    value={createForm.funding_amount || ''}
                    onChange={(e) => setCreateForm({ ...createForm, funding_amount: e.target.value ? Number(e.target.value) : undefined })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Application Deadline</label>
                  <input
                    type="date"
                    value={createForm.application_deadline || ''}
                    onChange={(e) => setCreateForm({ ...createForm, application_deadline: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Opportunity Type</label>
                <select
                  value={createForm.opportunity_type}
                  onChange={(e) => setCreateForm({ ...createForm, opportunity_type: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="Grant">Grant</option>
                  <option value="Fellowship">Fellowship</option>
                  <option value="Contract">Contract</option>
                  <option value="Award">Award</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description / Summary</label>
                <textarea
                  rows={3}
                  placeholder="Scope, objectives, and research focus..."
                  value={createForm.description || ''}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">URL / Application Link</label>
                <input
                  type="url"
                  placeholder="https://grants.gov/search-results-detail/..."
                  value={createForm.url || ''}
                  onChange={(e) => setCreateForm({ ...createForm, url: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Keywords */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Keywords</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    placeholder="e.g. Quantum, Nanotechnology"
                    value={keywordInput}
                    onChange={(e) => setKeywordInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddKeyword(); } }}
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={handleAddKeyword}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs"
                  >
                    Add
                  </button>
                </div>
                <div className="flex flex-wrap gap-1">
                  {createForm.keywords?.map((kw) => (
                    <span key={kw} className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-lg flex items-center gap-1">
                      #{kw}
                      <button type="button" onClick={() => handleRemoveKeyword(kw)} className="text-slate-400 hover:text-rose-400">×</button>
                    </span>
                  ))}
                </div>
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
                  {modalLoading ? 'Saving...' : 'Save Opportunity'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
