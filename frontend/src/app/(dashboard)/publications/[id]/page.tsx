"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  Building,
  Calendar,
  Quote,
  Layers,
  ExternalLink,
  Edit,
  Trash2,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  X,
  BrainCircuit,
  Target,
  Cpu,
  Award,
  AlertTriangle,
  Compass,
} from "lucide-react";
import { api } from "@/lib/api";
import { Publication, PublicationUpdate, PaperAnalysisResponse } from "@/types/publication";
import { ResearchDomain } from "@/types/profile";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function PublicationDetailPage() {
  const router = useRouter();
  const params = useParams();
  const pubId = params?.id;

  const [publication, setPublication] = useState<Publication | null>(null);
  const [domains, setDomains] = useState<ResearchDomain[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  // AI Paper Analysis State
  const [analysis, setAnalysis] = useState<PaperAnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  // Edit Modal State
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [modalFeedback, setModalFeedback] = useState<{ success?: string; error?: string }>({});

  // Edit Form Fields
  const [title, setTitle] = useState("");
  const [authors, setAuthors] = useState("");
  const [abstract, setAbstract] = useState("");
  const [venue, setVenue] = useState("");
  const [doi, setDoi] = useState("");
  const [citationCount, setCitationCount] = useState(0);
  const [primaryDomain, setPrimaryDomain] = useState("");
  const [keywordsInput, setKeywordsInput] = useState("");

  const loadPublication = async () => {
    if (!pubId) return;
    setIsLoading(true);
    try {
      const [pubRes, domainsRes] = await Promise.all([
        api.get(`/publications/${pubId}`),
        api.get("/profile/domains"),
      ]);

      if (pubRes.data?.success) {
        const p: Publication = pubRes.data.data;
        setPublication(p);
        setTitle(p.title);
        setAuthors(p.authors);
        setAbstract(p.abstract || "");
        setVenue(p.venue || "");
        setDoi(p.doi || "");
        setCitationCount(p.citation_count);
        setPrimaryDomain(p.primary_domain || "");
        setKeywordsInput(p.keywords?.map((k) => k.keyword).join(", ") || "");
      }
      if (domainsRes.data?.success) {
        setDomains(domainsRes.data.data);
      }

      // Quietly load existing analysis if available
      try {
        const analysisRes = await api.get(`/publications/${pubId}/analyze`);
        if (analysisRes.data?.success) {
          setAnalysis(analysisRes.data.data);
        }
      } catch {
        // Not analyzed yet; user can trigger manually
      }
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error?.message || "Failed to load publication.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadPublication();
  }, [pubId]);

  const handleAnalyze = async () => {
    if (!pubId) return;
    setIsAnalyzing(true);
    setAnalysisError("");
    try {
      const res = await api.post(`/publications/${pubId}/analyze`);
      if (res.data?.success) {
        setAnalysis(res.data.data);
      }
    } catch (err: any) {
      setAnalysisError(
        err.response?.data?.error?.message ||
        "Failed to generate AI paper analysis. Please ensure publication has an adequate abstract."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pubId) return;
    setIsUpdating(true);
    setModalFeedback({});

    const keywords = keywordsInput
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    const payload: PublicationUpdate = {
      title: title.trim(),
      authors: authors.trim(),
      abstract: abstract.trim() || undefined,
      venue: venue.trim() || undefined,
      doi: doi.trim() || undefined,
      citation_count: citationCount,
      primary_domain: primaryDomain || undefined,
      keywords,
    };

    try {
      const res = await api.put(`/publications/${pubId}`, payload);
      if (res.data?.success) {
        setPublication(res.data.data);
        setModalFeedback({ success: "Publication updated successfully!" });
        setTimeout(() => {
          setIsEditOpen(false);
          setModalFeedback({});
        }, 1200);
      }
    } catch (err: any) {
      setModalFeedback({
        error: err.response?.data?.error?.message || "Failed to update publication.",
      });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!pubId || !confirm("Are you sure you want to remove this publication from your profile?")) {
      return;
    }
    setIsDeleting(true);
    try {
      await api.delete(`/publications/${pubId}`);
      router.push("/publications");
    } catch (err: any) {
      alert(err.response?.data?.error?.message || "Failed to delete publication.");
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-400 text-sm">
        <Sparkles className="w-5 h-5 text-blue-400 animate-spin mr-2" />
        Loading publication details...
      </div>
    );
  }

  if (errorMessage || !publication) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-rose-500 mx-auto" />
        <h2 className="text-lg font-bold text-white">Publication Not Found</h2>
        <p className="text-xs text-slate-400">{errorMessage || "The requested publication does not exist."}</p>
        <Link href="/publications">
          <Button size="sm" variant="outline">
            <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Publications
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/publications"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Publications
        </Link>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setIsEditOpen(true)}
            className="flex items-center gap-1.5"
          >
            <Edit className="w-3.5 h-3.5" />
            Edit
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleDelete}
            isLoading={isDeleting}
            className="flex items-center gap-1.5 text-rose-400 border-rose-500/20 hover:bg-rose-500/10"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Remove
          </Button>
        </div>
      </div>

      {/* Main Publication Card */}
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 space-y-6">
        {/* Domain & Metrics */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
          <div className="flex flex-wrap items-center gap-2">
            {publication.primary_domain && (
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
                <Layers className="w-3.5 h-3.5" />
                {publication.primary_domain}
              </span>
            )}
            <Badge variant="secondary" className="capitalize">
              Source: {publication.source}
            </Badge>
          </div>

          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold text-emerald-400">
            <Quote className="w-4 h-4" />
            <span>{publication.citation_count} Citations</span>
          </div>
        </div>

        {/* Title & Authors */}
        <div className="space-y-3">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight">
            {publication.title}
          </h1>
          <p className="text-sm font-medium text-slate-300">
            {publication.authors}
          </p>
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
          {publication.venue && (
            <div className="space-y-1">
              <span className="text-slate-500 block uppercase tracking-wider text-[10px] font-semibold">
                Journal / Venue
              </span>
              <span className="text-slate-200 font-medium flex items-center gap-1.5">
                <Building className="w-3.5 h-3.5 text-blue-400" />
                {publication.venue}
              </span>
            </div>
          )}

          {publication.publication_date && (
            <div className="space-y-1">
              <span className="text-slate-500 block uppercase tracking-wider text-[10px] font-semibold">
                Publication Date
              </span>
              <span className="text-slate-200 font-medium flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-blue-400" />
                {new Date(publication.publication_date).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </span>
            </div>
          )}

          {publication.doi && (
            <div className="space-y-1">
              <span className="text-slate-500 block uppercase tracking-wider text-[10px] font-semibold">
                Digital Object Identifier (DOI)
              </span>
              <a
                href={`https://doi.org/${publication.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 font-mono flex items-center gap-1"
              >
                {publication.doi}
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          )}
        </div>

        {/* Abstract */}
        {publication.abstract && (
          <div className="space-y-2">
            <h2 className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Abstract
            </h2>
            <div className="p-5 rounded-xl bg-slate-900/40 border border-slate-800/60 text-xs leading-relaxed text-slate-300">
              {publication.abstract}
            </div>
          </div>
        )}

        {/* Keywords */}
        {publication.keywords && publication.keywords.length > 0 && (
          <div className="space-y-2">
            <h2 className="text-xs uppercase tracking-wider font-bold text-slate-400">
              Indexed Scientific Keywords
            </h2>
            <div className="flex flex-wrap gap-2">
              {publication.keywords.map((k) => (
                <span
                  key={k.id}
                  className="px-3 py-1 rounded-lg bg-slate-900 text-slate-300 text-xs font-medium border border-slate-800"
                >
                  #{k.keyword}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* AI Paper Analysis Section */}
      <div className="glass-panel p-8 rounded-2xl border border-slate-800 space-y-6">
        {/* Section Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-5">
          <div className="space-y-1">
            <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5">
              <BrainCircuit className="w-6 h-6 text-blue-400" />
              AI Paper Analysis
            </h2>
            <p className="text-xs text-slate-400">
              Rigorous scientific deconstruction across five key analytical facets grounded in verified publication content.
            </p>
          </div>

          <Button
            size="sm"
            onClick={handleAnalyze}
            isLoading={isAnalyzing}
            disabled={isAnalyzing}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20"
          >
            <Sparkles className="w-4 h-4" />
            {analysis ? "Re-analyze Paper" : "Analyze Paper"}
          </Button>
        </div>

        {/* Error Feedback */}
        {analysisError && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-rose-300">Analysis Incomplete</p>
              <p className="mt-0.5 text-slate-300">{analysisError}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isAnalyzing && (
          <div className="py-12 px-6 rounded-xl bg-slate-900/60 border border-blue-500/20 text-center space-y-3 animate-pulse">
            <Sparkles className="w-8 h-8 text-blue-400 animate-spin mx-auto" />
            <h3 className="text-sm font-bold text-white">Synthesizing Paper Facets...</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Extracting Problem Statement, Methodology, Findings, Limitations, and Future Horizons from scientific text.
            </p>
          </div>
        )}

        {/* Empty State (Not yet analyzed) */}
        {!analysis && !isAnalyzing && !analysisError && (
          <div className="py-10 px-6 rounded-xl bg-slate-900/40 border border-dashed border-slate-800 text-center space-y-3">
            <BrainCircuit className="w-10 h-10 text-slate-600 mx-auto" />
            <div className="space-y-1">
              <h3 className="text-sm font-semibold text-slate-300">Ready for Scientific Deconstruction</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                Click &quot;Analyze Paper&quot; above to run automated semantic evaluation and extract the 5 core research facets.
              </p>
            </div>
          </div>
        )}

        {/* Populated Analysis Results */}
        {analysis && !isAnalyzing && (
          <div className="space-y-6">
            {/* Metadata Badges & Confidence */}
            <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {Math.round(analysis.confidence_score * 100)}% Confidence
                </span>
                <Badge variant="secondary" className="capitalize text-slate-300 border-slate-700">
                  Source: {analysis.analysis_source.replace(/_/g, " ")}
                </Badge>
                <Badge variant="secondary" className="text-slate-300">
                  Engine: {analysis.provider}
                </Badge>
              </div>

              <span className="text-[11px] text-slate-400">
                Analyzed on {new Date(analysis.analyzed_at).toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>

            {/* Key Insights Pills (if present) */}
            {analysis.key_insights && analysis.key_insights.length > 0 && (
              <div className="space-y-2">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                  Key Scientific Takeaways
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {analysis.key_insights.map((insight, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 text-xs text-slate-300 flex items-start gap-2"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-blue-400 flex-shrink-0 mt-0.5" />
                      <span>{insight}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* The 5 Mentor Facets Grid */}
            <div className="space-y-4 pt-2">
              {/* 1. Problem Statement */}
              <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-sky-500/30 transition-colors space-y-2.5">
                <div className="flex items-center gap-2 text-sky-400 font-bold text-xs uppercase tracking-wider">
                  <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-500/20">
                    <Target className="w-4 h-4" />
                  </div>
                  <span>1. Problem Statement & Motivation</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-200 pl-8">
                  {analysis.problem_statement}
                </p>
              </div>

              {/* 2. Methodology */}
              <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-purple-500/30 transition-colors space-y-2.5">
                <div className="flex items-center gap-2 text-purple-400 font-bold text-xs uppercase tracking-wider">
                  <div className="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20">
                    <Cpu className="w-4 h-4" />
                  </div>
                  <span>2. Methodology & Experimental Framework</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-200 pl-8">
                  {analysis.methodology}
                </p>
              </div>

              {/* 3. Findings / Contributions */}
              <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-emerald-500/30 transition-colors space-y-2.5">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                  <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <Award className="w-4 h-4" />
                  </div>
                  <span>3. Findings & Contributions</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-200 pl-8">
                  {analysis.findings_contributions}
                </p>
              </div>

              {/* 4. Limitations */}
              <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-amber-500/30 transition-colors space-y-2.5">
                <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
                  <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <span>4. Limitations & Scope Constraints</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-200 pl-8">
                  {analysis.limitations}
                </p>
              </div>

              {/* 5. Future Research Directions */}
              <div className="p-5 rounded-xl bg-slate-900/50 border border-slate-800 hover:border-blue-500/30 transition-colors space-y-2.5">
                <div className="flex items-center gap-2 text-blue-400 font-bold text-xs uppercase tracking-wider">
                  <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20">
                    <Compass className="w-4 h-4" />
                  </div>
                  <span>5. Future Research Directions</span>
                </div>
                <p className="text-xs leading-relaxed text-slate-200 pl-8">
                  {analysis.future_research_directions}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {isEditOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto glass-panel p-6 rounded-2xl border border-slate-700 bg-slate-950 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Edit className="w-5 h-5 text-blue-400" />
                Edit Publication
              </h2>
              <button
                onClick={() => setIsEditOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {modalFeedback.success && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>{modalFeedback.success}</span>
              </div>
            )}
            {modalFeedback.error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span>{modalFeedback.error}</span>
              </div>
            )}

            <form onSubmit={handleUpdate} className="space-y-4">
              <Input
                label="Publication Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />

              <Input
                label="Authors"
                value={authors}
                onChange={(e) => setAuthors(e.target.value)}
                required
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Journal / Venue"
                  value={venue}
                  onChange={(e) => setVenue(e.target.value)}
                />
                <Input
                  label="DOI Identifier"
                  value={doi}
                  onChange={(e) => setDoi(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  type="number"
                  label="Citations Count"
                  min="0"
                  value={citationCount.toString()}
                  onChange={(e) => setCitationCount(parseInt(e.target.value) || 0)}
                />
                <div className="space-y-1.5">
                  <label className="block text-xs font-medium text-slate-300">
                    Primary Domain
                  </label>
                  <select
                    value={primaryDomain}
                    onChange={(e) => setPrimaryDomain(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
                  >
                    <option value="">Select Domain</option>
                    {domains.map((d) => (
                      <option key={d.id} value={d.name}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="block text-xs font-medium text-slate-300">
                  Abstract
                </label>
                <textarea
                  rows={4}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  value={abstract}
                  onChange={(e) => setAbstract(e.target.value)}
                />
              </div>

              <Input
                label="Keywords (comma separated)"
                value={keywordsInput}
                onChange={(e) => setKeywordsInput(e.target.value)}
              />

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" isLoading={isUpdating}>
                  Save Changes
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
