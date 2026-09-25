"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  BookOpen,
  Search,
  Plus,
  Filter,
  ExternalLink,
  Sparkles,
  Quote,
  Layers,
  Calendar,
  X,
  CheckCircle2,
  AlertCircle,
  Building,
} from "lucide-react";
import { api } from "@/lib/api";
import { Publication, PublicationCreate } from "@/types/publication";
import { ResearchDomain } from "@/types/profile";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function PublicationsPage() {
  const [publications, setPublications] = useState<Publication[]>([]);
  const [domains, setDomains] = useState<ResearchDomain[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [activeView, setActiveView] = useState<"all" | "my">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedDomain, setSelectedDomain] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState("");
  const [feedbackError, setFeedbackError] = useState("");

  // New Publication Form
  const [title, setTitle] = useState("");
  const [authors, setAuthors] = useState("");
  const [abstract, setAbstract] = useState("");
  const [venue, setVenue] = useState("");
  const [doi, setDoi] = useState("");
  const [pubDate, setPubDate] = useState("");
  const [citationCount, setCitationCount] = useState<number>(0);
  const [primaryDomain, setPrimaryDomain] = useState("");
  const [keywordsInput, setKeywordsInput] = useState("");
  const [isPrimaryAuthor, setIsPrimaryAuthor] = useState(true);

  const fetchPublications = async () => {
    setIsLoading(true);
    try {
      const endpoint = activeView === "my" ? "/publications/my" : "/publications";
      const params: any = { limit: 50 };
      if (searchQuery.trim()) params.q = searchQuery.trim();
      if (selectedDomain) params.domain = selectedDomain;

      const res = await api.get(endpoint, { params });
      if (res.data?.success) {
        setPublications(res.data.data.items);
        setTotalCount(res.data.data.total);
      }
    } catch (err) {
      console.error("Failed to load publications:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Load taxonomy domains
    api.get("/profile/domains").then((res) => {
      if (res.data?.success) setDomains(res.data.data);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    fetchPublications();
  }, [activeView, selectedDomain]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPublications();
  };

  const handleCreatePublication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !authors.trim()) {
      setFeedbackError("Title and authors are required.");
      return;
    }

    setIsSubmitting(true);
    setFeedbackError("");
    setFeedbackSuccess("");

    const keywords = keywordsInput
      .split(",")
      .map((k) => k.trim())
      .filter((k) => k.length > 0);

    const payload: PublicationCreate = {
      title: title.trim(),
      authors: authors.trim(),
      abstract: abstract.trim() || undefined,
      venue: venue.trim() || undefined,
      doi: doi.trim() || undefined,
      publication_date: pubDate ? new Date(pubDate).toISOString() : undefined,
      citation_count: citationCount || 0,
      primary_domain: primaryDomain || undefined,
      keywords,
      is_primary_author: isPrimaryAuthor,
    };

    try {
      const res = await api.post("/publications", payload);
      if (res.data?.success) {
        setFeedbackSuccess("Publication successfully added to platform!");
        // Reset form
        setTitle("");
        setAuthors("");
        setAbstract("");
        setVenue("");
        setDoi("");
        setPubDate("");
        setCitationCount(0);
        setPrimaryDomain("");
        setKeywordsInput("");
        setTimeout(() => {
          setIsModalOpen(false);
          setFeedbackSuccess("");
          fetchPublications();
        }, 1200);
      }
    } catch (err: any) {
      setFeedbackError(err.response?.data?.error?.message || "Failed to create publication.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-blue-400">
              Research Corpus
            </span>
            <Badge variant="primary">{totalCount} Indexed</Badge>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Scientific Publications</h1>
          <p className="text-xs text-slate-400">
            Explore indexed academic papers, citation metrics, and peer-reviewed discoveries.
          </p>
        </div>

        <Button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-5"
        >
          <Plus className="w-4 h-4" />
          Add Publication
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          {/* Tabs */}
          <div className="flex bg-slate-900/80 p-1 rounded-xl border border-slate-800 self-start">
            <button
              onClick={() => setActiveView("all")}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeView === "all"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              All Research
            </button>
            <button
              onClick={() => setActiveView("my")}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeView === "my"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              My Publications
            </button>
          </div>

          {/* Search Input */}
          <form onSubmit={handleSearch} className="flex-1 flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by paper title, abstract, authors, or journal..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-900/80 border border-slate-700 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <Button type="submit" size="sm">Search</Button>
          </form>

          {/* Domain Dropdown */}
          <select
            value={selectedDomain}
            onChange={(e) => setSelectedDomain(e.target.value)}
            className="rounded-xl border border-slate-700 bg-slate-900/80 px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Domains</option>
            {domains.map((d) => (
              <option key={d.id} value={d.name}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Publications List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24 text-slate-400 text-sm">
          <Sparkles className="w-5 h-5 text-blue-400 animate-spin mr-2" />
          Loading publications...
        </div>
      ) : publications.length === 0 ? (
        <div className="glass-panel p-12 text-center rounded-2xl border border-slate-800 space-y-3">
          <BookOpen className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-200">No Publications Found</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            {activeView === "my"
              ? "You haven't linked any publications to your research profile yet."
              : "No publications match your active filter criteria."}
          </p>
          <Button size="sm" onClick={() => setIsModalOpen(true)} className="mt-2">
            <Plus className="w-3.5 h-3.5 mr-1" />
            Add First Paper
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {publications.map((pub) => (
            <Link
              key={pub.id}
              href={`/publications/${pub.id}`}
              className="block glass-panel p-5 rounded-2xl border border-slate-800/80 hover:border-blue-500/40 hover:bg-slate-900/70 transition-all group"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    {pub.primary_domain && (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded-full border border-blue-500/20">
                        <Layers className="w-3 h-3" />
                        {pub.primary_domain}
                      </span>
                    )}
                    {pub.venue && (
                      <span className="text-[11px] text-slate-400 flex items-center gap-1">
                        <Building className="w-3 h-3 text-slate-500" />
                        {pub.venue}
                      </span>
                    )}
                    {pub.publication_date && (
                      <span className="text-[11px] text-slate-500 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(pub.publication_date).getFullYear()}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors line-clamp-2">
                    {pub.title}
                  </h3>

                  <p className="text-xs text-slate-300 font-medium">
                    {pub.authors}
                  </p>

                  {pub.abstract && (
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                      {pub.abstract}
                    </p>
                  )}

                  {pub.keywords && pub.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {pub.keywords.slice(0, 5).map((k) => (
                        <span
                          key={k.id}
                          className="text-[10px] text-slate-400 bg-slate-950 px-2 py-0.5 rounded-md border border-slate-800"
                        >
                          #{k.keyword}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex md:flex-col items-center md:items-end justify-between gap-3 flex-shrink-0">
                  <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-emerald-400">
                    <Quote className="w-3.5 h-3.5" />
                    <span>{pub.citation_count} citations</span>
                  </div>

                  {pub.doi && (
                    <span className="text-[11px] text-blue-400/80 hover:text-blue-400 flex items-center gap-1 font-mono">
                      DOI: {pub.doi}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Add Publication Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto glass-panel p-6 rounded-2xl border border-slate-700 bg-slate-950 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-400" />
                Add Research Publication
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {feedbackSuccess && (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                <span>{feedbackSuccess}</span>
              </div>
            )}
            {feedbackError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span>{feedbackError}</span>
              </div>
            )}

            <form onSubmit={handleCreatePublication} className="space-y-4">
              <Input
                label="Publication Title *"
                placeholder="e.g. Scalable Fault-Tolerant Quantum Computation"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />

              <Input
                label="Authors *"
                placeholder="e.g. Dr. Vance Adams, Dr. Sarah Connor"
                value={authors}
                onChange={(e) => setAuthors(e.target.value)}
                required
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Input
                  label="Journal / Venue"
                  placeholder="e.g. Nature Physics, IEEE QCE"
                  value={venue}
                  onChange={(e) => setVenue(e.target.value)}
                />
                <Input
                  label="DOI Identifier"
                  placeholder="e.g. 10.1038/s41567-024-0001"
                  value={doi}
                  onChange={(e) => setDoi(e.target.value)}
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Input
                  type="date"
                  label="Publication Date"
                  value={pubDate}
                  onChange={(e) => setPubDate(e.target.value)}
                />
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
                  Abstract / Executive Summary
                </label>
                <textarea
                  rows={3}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  placeholder="Summary of hypotheses, experimental methodology, and key quantitative findings..."
                  value={abstract}
                  onChange={(e) => setAbstract(e.target.value)}
                />
              </div>

              <Input
                label="Keywords (comma separated)"
                placeholder="Quantum Computing, Neutral Atoms, Surface Codes"
                value={keywordsInput}
                onChange={(e) => setKeywordsInput(e.target.value)}
              />

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="primaryAuth"
                  checked={isPrimaryAuthor}
                  onChange={(e) => setIsPrimaryAuthor(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-blue-600 focus:ring-blue-500/20"
                />
                <label htmlFor="primaryAuth" className="text-xs text-slate-300 cursor-pointer">
                  I am a primary or corresponding author on this publication
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" isLoading={isSubmitting}>
                  Save Publication
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
