'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  ReportType,
  ReportFilterRequest,
  ReportPreviewResponse,
  ExecutiveDossierResponse,
  ExecutiveDossierSummary,
} from '@/types/executive_report';
import {
  SUPPORTED_REPORT_TYPES,
  validateReportFilters,
} from '@/lib/reports';

export default function ReportsAndExportPage() {
  const [selectedReportType, setSelectedReportType] = useState<ReportType>('FUNDING');
  const [selectedDomain, setSelectedDomain] = useState('Quantum Computing');
  const [myProfileOnly, setMyProfileOnly] = useState(false);
  const [startYear, setStartYear] = useState<string>('');
  const [endYear, setEndYear] = useState<string>('');
  const [agencyFilter, setAgencyFilter] = useState<string>('');
  const [minAmountFilter, setMinAmountFilter] = useState<string>('');

  const [previewData, setPreviewData] = useState<ReportPreviewResponse | null>(null);
  const [dossierData, setDossierData] = useState<ExecutiveDossierResponse | null>(null);
  const [summaryData, setSummaryData] = useState<ExecutiveDossierSummary | null>(null);

  const [loading, setLoading] = useState(true);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingExcel, setIsExportingExcel] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successToast, setSuccessToast] = useState<string | null>(null);

  const fetchReportPreview = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      // Validate filter inputs
      const sYearNum = startYear ? parseInt(startYear) : undefined;
      const eYearNum = endYear ? parseInt(endYear) : undefined;
      const minAmtNum = minAmountFilter ? parseFloat(minAmountFilter) : undefined;

      const validation = validateReportFilters({
        start_year: sYearNum,
        end_year: eYearNum,
        min_amount: minAmtNum,
      });

      if (!validation.isValid) {
        setErrorMsg(validation.error || 'Invalid filter parameters.');
        setLoading(false);
        return;
      }

      const payload: ReportFilterRequest = {
        report_type: selectedReportType,
        domain: myProfileOnly ? undefined : selectedDomain,
        my_profile_only: myProfileOnly,
        start_year: sYearNum,
        end_year: eYearNum,
        agency: agencyFilter.trim() || undefined,
        assignee: agencyFilter.trim() || undefined,
        min_amount: minAmtNum,
      };

      // 1. Fetch unified Module 11 preview
      const previewRes = await api.post<{ data: ReportPreviewResponse }>(
        '/reports/preview',
        payload
      );
      setPreviewData(previewRes.data.data);

      // 2. If Executive Dossier is active, fetch detailed SWOT + Roadmap
      if (selectedReportType === 'EXECUTIVE_DOSSIER') {
        const params = new URLSearchParams();
        if (myProfileOnly) params.append('my_profile_only', 'true');
        else if (selectedDomain) params.append('domain', selectedDomain);
        const queryStr = params.toString() ? `?${params.toString()}` : '';

        const [dosRes, sumRes] = await Promise.all([
          api.get<{ data: ExecutiveDossierResponse }>(`/reports/dossier${queryStr}`),
          api.get<{ data: ExecutiveDossierSummary }>('/reports/summary'),
        ]);
        setDossierData(dosRes.data.data);
        setSummaryData(sumRes.data.data);
      }
    } catch (err: any) {
      setErrorMsg(
        err.response?.data?.detail?.message ||
          err.response?.data?.detail ||
          'Failed to retrieve report data from backend services.'
      );
    } finally {
      setLoading(false);
    }
  }, [
    selectedReportType,
    selectedDomain,
    myProfileOnly,
    startYear,
    endYear,
    agencyFilter,
    minAmountFilter,
  ]);

  useEffect(() => {
    fetchReportPreview();
  }, [fetchReportPreview]);

  const handleDownloadPdf = async () => {
    try {
      setIsExportingPdf(true);
      setErrorMsg(null);
      const payload: ReportFilterRequest = {
        report_type: selectedReportType,
        domain: myProfileOnly ? undefined : selectedDomain,
        my_profile_only: myProfileOnly,
        start_year: startYear ? parseInt(startYear) : undefined,
        end_year: endYear ? parseInt(endYear) : undefined,
        agency: agencyFilter.trim() || undefined,
        assignee: agencyFilter.trim() || undefined,
        min_amount: minAmountFilter ? parseFloat(minAmountFilter) : undefined,
      };

      const res = await api.post('/reports/export/pdf', payload, {
        responseType: 'blob',
      });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const targetSlug = (myProfileOnly ? 'My_Profile' : selectedDomain).replace(/\s+/g, '_');
      a.download = `${selectedReportType}_Report_${targetSlug}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccessToast(`PDF Report generated and downloaded successfully!`);
      setTimeout(() => setSuccessToast(null), 4000);
    } catch (err: any) {
      setErrorMsg('Failed to generate PDF document. Please review filter parameters.');
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleDownloadExcel = async () => {
    try {
      setIsExportingExcel(true);
      setErrorMsg(null);
      const payload: ReportFilterRequest = {
        report_type: selectedReportType,
        domain: myProfileOnly ? undefined : selectedDomain,
        my_profile_only: myProfileOnly,
        start_year: startYear ? parseInt(startYear) : undefined,
        end_year: endYear ? parseInt(endYear) : undefined,
        agency: agencyFilter.trim() || undefined,
        assignee: agencyFilter.trim() || undefined,
        min_amount: minAmountFilter ? parseFloat(minAmountFilter) : undefined,
      };

      const res = await api.post('/reports/export/excel', payload, {
        responseType: 'blob',
      });
      const blob = new Blob([res.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const targetSlug = (myProfileOnly ? 'My_Profile' : selectedDomain).replace(/\s+/g, '_');
      a.download = `${selectedReportType}_Report_${targetSlug}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccessToast(`Excel workbook (.xlsx) generated and downloaded successfully!`);
      setTimeout(() => setSuccessToast(null), 4000);
    } catch (err: any) {
      setErrorMsg('Failed to generate Excel workbook. Please review filter parameters.');
    } finally {
      setIsExportingExcel(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleResetFilters = () => {
    setStartYear('');
    setEndYear('');
    setAgencyFilter('');
    setMinAmountFilter('');
    setSelectedDomain('Quantum Computing');
    setMyProfileOnly(false);
  };

  const activeMeta = SUPPORTED_REPORT_TYPES.find((r) => r.type === selectedReportType);

  return (
    <div className="space-y-6 pb-12 print:space-y-4 print:pb-0">
      {/* Top Banner & Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl print:border-none print:shadow-none print:p-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Module 11: Reports & Export System
            </span>
            <span className="text-xs text-slate-400">
              Multi-Source Intelligence & Analysis
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1 print:text-black">
            Reports & Export Center
          </h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1 print:hidden">
            Select report category, configure analytical filters, preview structured platform telemetry, and download professional PDF or Excel (.xlsx) exports.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2 print:hidden">
          <button
            onClick={handleDownloadPdf}
            disabled={isExportingPdf || loading}
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow transition flex items-center gap-2 disabled:opacity-50"
          >
            {isExportingPdf ? (
              <>
                <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating PDF...</span>
              </>
            ) : (
              <>
                <span>📄</span>
                <span>Export PDF</span>
              </>
            )}
          </button>

          <button
            onClick={handleDownloadExcel}
            disabled={isExportingExcel || loading}
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-emerald-700 hover:bg-emerald-600 text-white shadow transition flex items-center gap-2 disabled:opacity-50"
          >
            {isExportingExcel ? (
              <>
                <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Generating XLSX...</span>
              </>
            ) : (
              <>
                <span>📊</span>
                <span>Export Excel</span>
              </>
            )}
          </button>

          <button
            onClick={handlePrint}
            className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-200 hover:bg-slate-900 transition flex items-center gap-1.5"
          >
            <span>🖨️</span>
            <span>Print</span>
          </button>
        </div>
      </div>

      {/* Notifications / Feedback Toasts */}
      {successToast && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <span>✅</span>
            <span>{successToast}</span>
          </div>
          <button onClick={() => setSuccessToast(null)} className="text-emerald-400 font-bold hover:text-emerald-200">
            ×
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 font-bold hover:text-rose-200">
            ×
          </button>
        </div>
      )}

      {/* Report Category Selector Tabs */}
      <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-2xl shadow-sm print:hidden">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider px-2 block mb-2">
          Select Report Category
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {SUPPORTED_REPORT_TYPES.map((rep) => {
            const isSelected = selectedReportType === rep.type;
            return (
              <button
                key={rep.type}
                onClick={() => setSelectedReportType(rep.type)}
                className={`p-3 rounded-xl text-left border transition flex flex-col justify-between ${
                  isSelected
                    ? 'bg-indigo-600/20 border-indigo-500 shadow-md ring-1 ring-indigo-500'
                    : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700'
                }`}
              >
                <div>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    isSelected ? 'bg-indigo-500/20 text-indigo-300' : 'bg-slate-900 text-slate-400'
                  }`}>
                    {rep.badge}
                  </span>
                  <h3 className={`text-xs font-bold mt-1.5 ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                    {rep.label}
                  </h3>
                </div>
                <span className="text-[9px] text-slate-400 mt-2 line-clamp-1">
                  {rep.moduleOrigin.split(':')[0]}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Filter & Parameters Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4 print:hidden">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-white">Report Configuration & Filters</span>
            <span className="text-[10px] text-slate-400 font-mono">({activeMeta?.label})</span>
          </div>
          <button
            onClick={handleResetFilters}
            className="text-[11px] text-slate-400 hover:text-slate-200 underline"
          >
            Reset Filters
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* Scope Selector */}
          <div>
            <label className="text-[10px] font-medium text-slate-400 block mb-1">Target Scope</label>
            <button
              onClick={() => setMyProfileOnly(!myProfileOnly)}
              className={`w-full px-3 py-2 rounded-xl text-xs font-semibold border transition flex items-center justify-between ${
                myProfileOnly
                  ? 'bg-indigo-600/20 border-indigo-500 text-indigo-300'
                  : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
              }`}
            >
              <span>{myProfileOnly ? 'My Portfolio' : 'Global Domain'}</span>
              <span className={`w-2 h-2 rounded-full ${myProfileOnly ? 'bg-indigo-400' : 'bg-slate-600'}`} />
            </button>
          </div>

          {/* Domain Dropdown */}
          <div>
            <label className="text-[10px] font-medium text-slate-400 block mb-1">Technology Domain</label>
            <select
              value={selectedDomain}
              disabled={myProfileOnly}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 disabled:opacity-40"
            >
              <option value="Quantum Computing">Quantum Computing</option>
              <option value="Artificial Intelligence">Artificial Intelligence</option>
              <option value="Energy Storage">Energy Storage</option>
              <option value="Biotechnology">Biotechnology</option>
              <option value="Photonics">Photonics</option>
              <option value="Robotics">Robotics</option>
            </select>
          </div>

          {/* Year Range (Start & End) */}
          <div className="flex gap-2">
            <div className="w-1/2">
              <label className="text-[10px] font-medium text-slate-400 block mb-1">Start Year</label>
              <input
                type="number"
                placeholder="YYYY"
                value={startYear}
                onChange={(e) => setStartYear(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>
            <div className="w-1/2">
              <label className="text-[10px] font-medium text-slate-400 block mb-1">End Year</label>
              <input
                type="number"
                placeholder="YYYY"
                value={endYear}
                onChange={(e) => setEndYear(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>
          </div>

          {/* Agency / Assignee / Org */}
          <div>
            <label className="text-[10px] font-medium text-slate-400 block mb-1">Agency / Assignee</label>
            <input
              type="text"
              placeholder="e.g. NSF, IBM, DARPA"
              value={agencyFilter}
              onChange={(e) => setAgencyFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Min Amount / Filter Button */}
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="text-[10px] font-medium text-slate-400 block mb-1">Min Grant ($)</label>
              <input
                type="number"
                placeholder="e.g. 500000"
                value={minAmountFilter}
                onChange={(e) => setMinAmountFilter(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
              />
            </div>
            <button
              onClick={fetchReportPreview}
              disabled={loading}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 h-[38px]"
            >
              <span>🔄</span>
              <span>Apply</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Report Preview Content */}
      {loading ? (
        <div className="space-y-4 animate-pulse">
          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-36" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl h-24" />
            ))}
          </div>
          <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-64" />
        </div>
      ) : previewData ? (
        <div className="space-y-6">
          {/* Report Preview Header Card */}
          <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs font-bold text-indigo-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                  {previewData.report_type}
                </span>
                <div>
                  <h2 className="text-base font-bold text-white">{previewData.title}</h2>
                  <span className="text-[11px] text-slate-400">
                    Generated: {previewData.generated_at} • Filtered Records: {previewData.total_records}
                  </span>
                </div>
              </div>

              {/* Applied Filter Tags */}
              <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
                {Object.entries(previewData.applied_filters).map(([k, v]) => (
                  <span
                    key={k}
                    className="px-2 py-0.5 rounded-full font-mono bg-slate-950 text-indigo-300 border border-slate-800"
                  >
                    {k}: {String(v)}
                  </span>
                ))}
              </div>
            </div>

            {/* Narrative Executive Summary */}
            <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80">
              <span className="text-[10px] text-indigo-400 uppercase tracking-wider font-semibold block mb-1">
                Executive Synthesis & Analytical Summary
              </span>
              <p className="text-xs text-slate-200 leading-relaxed font-normal">
                {previewData.summary_text}
              </p>
            </div>
          </div>

          {/* Top Key Metrics Grid */}
          {previewData.metrics && Object.keys(previewData.metrics).length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(previewData.metrics).map(([mKey, mVal]) => (
                <div
                  key={mKey}
                  className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm flex flex-col justify-between"
                >
                  <span className="text-[10px] text-slate-400 block font-medium truncate">
                    {mKey}
                  </span>
                  <div className="text-xl font-extrabold text-white mt-1.5 truncate">
                    {String(mVal)}
                  </div>
                  <span className="text-[9px] text-indigo-400 mt-1 block">Verified Metric</span>
                </div>
              ))}
            </div>
          )}

          {/* Module 7 Specific: Innovation Intelligence 5-Pillar Score Factors */}
          {selectedReportType === 'INNOVATION_INTELLIGENCE' && previewData.factors && (
            <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <span>💡</span> 5-Pillar Innovation Score Factor Decomposition
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Governed by Module 7 official weighted methodology (Novelty 30%, Patents 20%, Tech 15%, Market 20%, Funding 15%).
                  </p>
                </div>
                <span className="px-2.5 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
                  100% Normalized Weight
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                {previewData.factors.map((f) => (
                  <div
                    key={f.factor_name}
                    className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold text-indigo-300">
                          {f.weight_pct}% Weight
                        </span>
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-mono font-bold ${
                          f.status === 'AVAILABLE'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}>
                          {f.status}
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-white mt-1">{f.factor_name}</h4>
                      <div className="text-lg font-extrabold text-indigo-400 mt-1">
                        {f.score.toFixed(1)}{' '}
                        <span className="text-[10px] text-slate-500 font-normal">/ 100</span>
                      </div>
                      <p className="text-[10px] text-slate-400 leading-tight mt-1.5">
                        {f.description}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 text-[10px] text-slate-400">
                      Weighted Contribution:{' '}
                      <strong className="text-white">
                        {(f.score * (f.weight_pct / 100)).toFixed(2)} pts
                      </strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Module 8 Specific: Commercialization Pathways Grid */}
          {selectedReportType === 'COMMERCIALIZATION' && (
            <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>🚀</span> Four Strategic Commercialization Pathways
                </h3>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  Conservative translational feasibility guidelines derived from empirical IP, grant, and ecosystem signals.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] font-bold text-indigo-400 uppercase">Pathway 1</span>
                  <h4 className="text-xs font-bold text-white">Potential Productization</h4>
                  <p className="text-[11px] text-slate-300">Direct translational deployment and product roadmap development.</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] font-bold text-cyan-400 uppercase">Pathway 2</span>
                  <h4 className="text-xs font-bold text-white">Potential Licensing</h4>
                  <p className="text-[11px] text-slate-300">Out-licensing patent claims to corporate assignees with domain overlap.</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase">Pathway 3</span>
                  <h4 className="text-xs font-bold text-white">Potential Startup Spinout</h4>
                  <p className="text-[11px] text-slate-300">Venture creation backed by non-dilutive translation funding streams.</p>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                  <span className="text-[10px] font-bold text-amber-400 uppercase">Pathway 4</span>
                  <h4 className="text-xs font-bold text-white">Potential Industry Partnership</h4>
                  <p className="text-[11px] text-slate-300">Collaborative co-development and pre-commercial operational testing.</p>
                </div>
              </div>
            </div>
          )}

          {/* Structured Records Data Table */}
          <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">Structured Telemetry Records</h3>
                <span className="text-[11px] text-slate-400">
                  Showing {previewData.table_rows.length} tabular entries for {activeMeta?.label}
                </span>
              </div>
              <span className="text-xs font-mono text-indigo-400 font-bold">
                {previewData.total_records} Total Matches
              </span>
            </div>

            {previewData.table_rows.length === 0 ? (
              <div className="p-12 text-center border border-dashed border-slate-800 rounded-xl space-y-2">
                <span className="text-3xl">🔍</span>
                <h4 className="text-sm font-bold text-white">No Matching Records Found</h4>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  No records match the applied filter criteria. Try broadening your date range, removing keyword constraints, or clearing filters.
                </p>
                <button
                  onClick={handleResetFilters}
                  className="mt-2 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-indigo-600 text-white hover:bg-indigo-500 transition"
                >
                  Clear All Filters
                </button>
              </div>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-slate-800/80">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/90 border-b border-slate-800">
                    <tr>
                      {previewData.table_headers.map((h, idx) => (
                        <th key={idx} className="px-4 py-3 font-semibold text-slate-300">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 bg-slate-900/40">
                    {previewData.table_rows.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-800/30 transition">
                        {row.map((cell, cIdx) => (
                          <td key={cIdx} className="px-4 py-3 text-slate-200">
                            {String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Actionable Strategic Recommendations */}
          {previewData.recommendations && previewData.recommendations.length > 0 && (
            <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📋</span> Strategic Recommendations & Next Actions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {previewData.recommendations.map((rec, idx) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5"
                  >
                    <span className="text-emerald-400 font-bold mt-0.5">✓</span>
                    <span>{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Executive Dossier SWOT + Roadmap Add-on (If Dossier Selected) */}
          {selectedReportType === 'EXECUTIVE_DOSSIER' && dossierData && (
            <div className="space-y-6 pt-2">
              {/* SWOT Matrix */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-white">Strategic Assessment (SWOT Synthesis)</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-5 rounded-2xl bg-slate-900/80 border border-emerald-500/30 space-y-2">
                    <h4 className="text-xs font-bold text-emerald-400">Verified Strengths & Advantages</h4>
                    <ul className="space-y-1.5 pt-1">
                      {dossierData.strategic_assessment.strengths.map((s, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-emerald-400 font-bold">•</span>
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-5 rounded-2xl bg-slate-900/80 border border-rose-500/30 space-y-2">
                    <h4 className="text-xs font-bold text-rose-400">Critical Risks & Bottlenecks</h4>
                    <ul className="space-y-1.5 pt-1">
                      {dossierData.strategic_assessment.risks_and_bottlenecks.map((r, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <span className="text-rose-400 font-bold">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* 3-Phase Roadmap */}
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h3 className="text-sm font-bold text-white">Three-Phase Strategic Execution Roadmap</h3>
                <div className="space-y-3">
                  {dossierData.roadmap.map((phase) => (
                    <div key={phase.phase_name} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-indigo-300">{phase.phase_name}</h4>
                        <span className="text-[10px] font-mono text-slate-400">{phase.timeframe}</span>
                      </div>
                      <p className="text-[11px] text-slate-400">{phase.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Data Limitations & Governance Notice */}
          <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800/80 text-slate-400 text-xs leading-relaxed space-y-1">
            <p className="font-semibold text-slate-300 flex items-center gap-1.5">
              <span>⚖️</span> Data Limitations & Regulatory Governance
            </p>
            <p>
              {previewData.data_limitations ||
                'This report is generated from verified platform data records. All recommendations and metrics represent advisory guidelines and do not constitute legal freedom-to-operate or financial guarantees.'}
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}
