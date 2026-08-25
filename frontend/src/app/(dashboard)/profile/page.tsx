"use client";

import React, { useEffect, useState } from "react";
import {
  Sparkles,
  Save,
  Plus,
  Trash2,
  Building,
  GraduationCap,
  Briefcase,
  Layers,
  Tag,
  CheckCircle2,
  AlertCircle,
  BookOpen,
} from "lucide-react";
import { api } from "@/lib/api";
import { authStorage } from "@/lib/auth";
import { User } from "@/types/user";
import {
  ExtendedProfile,
  ResearchDomain,
  ResearchInterest,
  AcademicHistory,
  ResearchHistory,
  TechnologyArea,
} from "@/types/profile";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<ExtendedProfile | null>(null);
  const [availableDomains, setAvailableDomains] = useState<ResearchDomain[]>([]);
  const [selectedDomainIds, setSelectedDomainIds] = useState<number[]>([]);
  const [activeTab, setActiveTab] = useState<"general" | "domains" | "interests" | "academic" | "research">("general");

  // Form State
  const [institution, setInstitution] = useState("");
  const [department, setDepartment] = useState("");
  const [designation, setDesignation] = useState("");
  const [country, setCountry] = useState("");
  const [phone, setPhone] = useState("");
  const [bio, setBio] = useState("");
  const [orcidId, setOrcidId] = useState("");
  const [website, setWebsite] = useState("");

  // Normalized child collections
  const [interests, setInterests] = useState<ResearchInterest[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeywordInput, setNewKeywordInput] = useState("");
  const [technologyAreas, setTechnologyAreas] = useState<TechnologyArea[]>([]);
  const [newTechAreaInput, setNewTechAreaInput] = useState("");
  const [academicHistories, setAcademicHistories] = useState<AcademicHistory[]>([]);
  const [researchHistories, setResearchHistories] = useState<ResearchHistory[]>([]);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const currentUser = authStorage.getUser();
    setUser(currentUser);
    if (currentUser?.phone) {
      setPhone(currentUser.phone);
    }

    // Load available taxonomy domains and profile data concurrently
    Promise.all([
      api.get("/profile/domains"),
      api.get("/profile/me")
    ])
      .then(([domainsRes, profileRes]) => {
        if (domainsRes.data?.success) {
          setAvailableDomains(domainsRes.data.data);
        }
        if (profileRes.data?.success) {
          const prof: ExtendedProfile = profileRes.data.data;
          setProfile(prof);
          setInstitution(prof.institution || "");
          setDepartment(prof.department || "");
          setDesignation(prof.designation || "");
          setCountry(prof.country || "");
          setBio(prof.bio || "");
          setOrcidId(prof.orcid_id || "");
          setWebsite(prof.website || "");
          setSelectedDomainIds(prof.domains.map((d) => d.id));
          setInterests(prof.interests || []);
          setKeywords(prof.keywords.map((k) => k.keyword) || []);
          setTechnologyAreas(prof.technology_areas || []);
          setAcademicHistories(prof.academic_histories || []);
          setResearchHistories(prof.research_histories || []);
        }
      })
      .catch((err) => {
        console.error("Failed to load profile:", err);
        setErrorMessage("Failed to load research profile.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const toggleDomain = (domainId: number) => {
    setSelectedDomainIds((prev) =>
      prev.includes(domainId) ? prev.filter((id) => id !== domainId) : [...prev, domainId]
    );
  };

  const handleAddKeyword = () => {
    if (newKeywordInput.trim() && !keywords.includes(newKeywordInput.trim())) {
      setKeywords([...keywords, newKeywordInput.trim()]);
      setNewKeywordInput("");
    }
  };

  const handleRemoveKeyword = (kw: string) => {
    setKeywords(keywords.filter((k) => k !== kw));
  };

  const handleAddTechArea = () => {
    if (newTechAreaInput.trim()) {
      setTechnologyAreas([...technologyAreas, { name: newTechAreaInput.trim() }]);
      setNewTechAreaInput("");
    }
  };

  const handleRemoveTechArea = (index: number) => {
    setTechnologyAreas(technologyAreas.filter((_, i) => i !== index));
  };

  const handleAddInterest = () => {
    setInterests([
      ...interests,
      { title: "", description: "", importance_level: "primary" }
    ]);
  };

  const handleUpdateInterest = (index: number, field: keyof ResearchInterest, value: string) => {
    const updated = [...interests];
    updated[index] = { ...updated[index], [field]: value };
    setInterests(updated);
  };

  const handleRemoveInterest = (index: number) => {
    setInterests(interests.filter((_, i) => i !== index));
  };

  const handleAddAcademic = () => {
    setAcademicHistories([
      ...academicHistories,
      { degree: "", field_of_study: "", institution: "", start_year: undefined, end_year: undefined }
    ]);
  };

  const handleUpdateAcademic = (index: number, field: keyof AcademicHistory, value: any) => {
    const updated = [...academicHistories];
    updated[index] = { ...updated[index], [field]: value };
    setAcademicHistories(updated);
  };

  const handleRemoveAcademic = (index: number) => {
    setAcademicHistories(academicHistories.filter((_, i) => i !== index));
  };

  const handleAddResearch = () => {
    setResearchHistories([
      ...researchHistories,
      { project_title: "", role: "", organization: "", description: "" }
    ]);
  };

  const handleUpdateResearch = (index: number, field: keyof ResearchHistory, value: any) => {
    const updated = [...researchHistories];
    updated[index] = { ...updated[index], [field]: value };
    setResearchHistories(updated);
  };

  const handleRemoveResearch = (index: number) => {
    setResearchHistories(researchHistories.filter((_, i) => i !== index));
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSuccessMessage("");
    setErrorMessage("");

    const payload = {
      institution,
      department,
      designation,
      country,
      bio,
      orcid_id: orcidId,
      website,
      domain_ids: selectedDomainIds,
      interests: interests.filter((i) => i.title.trim().length > 0),
      keywords,
      technology_areas: technologyAreas.filter((t) => t.name.trim().length > 0),
      academic_histories: academicHistories.filter((a) => a.degree.trim() && a.institution.trim()),
      research_histories: researchHistories.filter((r) => r.project_title.trim() && r.organization.trim())
    };

    try {
      const [res, userRes] = await Promise.all([
        api.put("/profile/me", payload),
        api.put("/auth/me", { phone })
      ]);
      if (res.data?.success) {
        setProfile(res.data.data);
        if (userRes.data?.success) {
          const updatedUser = userRes.data.data;
          setUser(updatedUser);
          authStorage.setUser(updatedUser);
        }
        setSuccessMessage("Research profile updated successfully!");
        setTimeout(() => setSuccessMessage(""), 4000);
      }
    } catch (err: any) {
      setErrorMessage(err.response?.data?.error?.message || "Failed to save profile changes.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24 text-slate-400 text-sm">
        <Sparkles className="w-5 h-5 text-blue-400 animate-spin mr-2" />
        Loading research profile...
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-panel p-6 rounded-2xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-blue-400">
              Researcher Identity
            </span>
            <Badge variant="primary" className="capitalize">
              {user?.role || "Researcher"}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">{user?.full_name}</h1>
          <p className="text-xs text-slate-400">{user?.email}</p>
        </div>

        <Button
          onClick={handleSaveProfile}
          isLoading={isSaving}
          className="flex items-center gap-2 px-6"
        >
          <Save className="w-4 h-4" />
          Save Changes
        </Button>
      </div>

      {/* Notifications */}
      {successMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}
      {errorMessage && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "general", label: "General & Academic", icon: Building },
          { id: "domains", label: "Research Domains", icon: Layers },
          { id: "interests", label: "Interests & Keywords", icon: Tag },
          { id: "academic", label: "Degrees & Education", icon: GraduationCap },
          { id: "research", label: "Research History", icon: Briefcase },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                  : "glass-panel text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: General & Academic */}
      {activeTab === "general" && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
            Institutional Affiliation & Identity
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Primary Institution / University"
              placeholder="e.g. MIT, Stanford, Harvard"
              value={institution}
              onChange={(e) => setInstitution(e.target.value)}
            />
            <Input
              label="Department / Faculty"
              placeholder="e.g. Department of Quantum Physics"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
            />
            <Input
              label="Designation / Role Title"
              placeholder="e.g. Associate Professor, Principal Investigator"
              value={designation}
              onChange={(e) => setDesignation(e.target.value)}
            />
            <Input
              label="Country / Region"
              placeholder="e.g. United States, Germany, Japan"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
            />
            <Input
              label="Contact Phone Number"
              type="tel"
              placeholder="e.g. +1 (555) 000-0000"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <Input
              label="ORCID Identifier"
              placeholder="e.g. 0000-0002-1825-0097"
              value={orcidId}
              onChange={(e) => setOrcidId(e.target.value)}
            />
            <div className="md:col-span-2">
              <Input
                label="Academic / Lab Website"
                placeholder="https://lab.university.edu"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
              />
            </div>
          </div>
          <div className="space-y-1.5 pt-2">
            <label className="block text-xs font-medium text-slate-300">
              Research Biography / Executive Summary
            </label>
            <textarea
              rows={4}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
              placeholder="Describe your active research trajectory, major discoveries, and technological vision..."
              value={bio}
              onChange={(e) => setBio(e.target.value)}
            />
          </div>
        </div>
      )}

      {/* Tab 2: Research Domains */}
      {activeTab === "domains" && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Scientific Domains Taxonomy
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Select primary scientific disciplines for downstream grant matchmaking and publication discovery.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            {availableDomains.map((dom) => {
              const isSelected = selectedDomainIds.includes(dom.id);
              return (
                <button
                  type="button"
                  key={dom.id}
                  onClick={() => toggleDomain(dom.id)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    isSelected
                      ? "bg-blue-600/10 border-blue-500/50 shadow-sm"
                      : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className={`text-xs font-semibold ${isSelected ? "text-blue-400" : "text-slate-200"}`}>
                      {dom.name}
                    </span>
                    {isSelected && <CheckCircle2 className="w-4 h-4 text-blue-400" />}
                  </div>
                  {dom.description && (
                    <p className="text-[11px] text-slate-400 mt-1">{dom.description}</p>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 3: Interests & Keywords */}
      {activeTab === "interests" && (
        <div className="space-y-6">
          {/* Keywords & Tech Areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Keywords */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Research Keywords
              </h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Quantum Optics"
                  value={newKeywordInput}
                  onChange={(e) => setNewKeywordInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddKeyword())}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-100"
                />
                <Button size="sm" onClick={handleAddKeyword}>Add</Button>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                {keywords.map((kw) => (
                  <span
                    key={kw}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20"
                  >
                    {kw}
                    <button
                      type="button"
                      onClick={() => handleRemoveKeyword(kw)}
                      className="hover:text-rose-400"
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Technology Areas */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Technology Areas
              </h2>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Silicon Nitride Waveguides"
                  value={newTechAreaInput}
                  onChange={(e) => setNewTechAreaInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTechArea())}
                  className="flex-1 rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-1.5 text-xs text-slate-100"
                />
                <Button size="sm" onClick={handleAddTechArea}>Add</Button>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                {technologyAreas.map((tech, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20"
                  >
                    {tech.name}
                    <button
                      type="button"
                      onClick={() => handleRemoveTechArea(idx)}
                      className="hover:text-rose-400"
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Granular Research Interests */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Granular Research Interests
                </h2>
                <p className="text-xs text-slate-400">Detailed research topics with priority rankings.</p>
              </div>
              <Button size="sm" variant="outline" onClick={handleAddInterest} className="flex items-center gap-1.5">
                <Plus className="w-3.5 h-3.5" />
                Add Topic
              </Button>
            </div>

            <div className="space-y-3">
              {interests.map((interest, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                  <div className="flex items-center gap-3">
                    <input
                      type="text"
                      placeholder="Topic Title (e.g. Surface Code Quantum Memory)"
                      value={interest.title}
                      onChange={(e) => handleUpdateInterest(idx, "title", e.target.value)}
                      className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                    />
                    <select
                      value={interest.importance_level}
                      onChange={(e) => handleUpdateInterest(idx, "importance_level", e.target.value)}
                      className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-300"
                    >
                      <option value="primary">Primary</option>
                      <option value="secondary">Secondary</option>
                      <option value="exploratory">Exploratory</option>
                    </select>
                    <button
                      type="button"
                      onClick={() => handleRemoveInterest(idx)}
                      className="p-1.5 text-slate-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <input
                    type="text"
                    placeholder="Brief description of research focus or experimental approach..."
                    value={interest.description || ""}
                    onChange={(e) => handleUpdateInterest(idx, "description", e.target.value)}
                    className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-300"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Academic History */}
      {activeTab === "academic" && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Degrees & Educational Background
              </h2>
              <p className="text-xs text-slate-400">Academic credentials and graduate training.</p>
            </div>
            <Button size="sm" variant="outline" onClick={handleAddAcademic} className="flex items-center gap-1.5">
              <Plus className="w-3.5 h-3.5" />
              Add Degree
            </Button>
          </div>

          <div className="space-y-3">
            {academicHistories.map((acad, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 grid grid-cols-1 sm:grid-cols-4 gap-3 items-center">
                <input
                  type="text"
                  placeholder="Degree (e.g. Ph.D.)"
                  value={acad.degree}
                  onChange={(e) => handleUpdateAcademic(idx, "degree", e.target.value)}
                  className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                />
                <input
                  type="text"
                  placeholder="Field (e.g. Applied Physics)"
                  value={acad.field_of_study}
                  onChange={(e) => handleUpdateAcademic(idx, "field_of_study", e.target.value)}
                  className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                />
                <input
                  type="text"
                  placeholder="Institution (e.g. Harvard)"
                  value={acad.institution}
                  onChange={(e) => handleUpdateAcademic(idx, "institution", e.target.value)}
                  className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                />
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    placeholder="Grad Year"
                    value={acad.end_year || ""}
                    onChange={(e) => handleUpdateAcademic(idx, "end_year", e.target.value ? parseInt(e.target.value) : undefined)}
                    className="w-24 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveAcademic(idx)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 ml-auto"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 5: Research History */}
      {activeTab === "research" && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                Research Projects & Grants
              </h2>
              <p className="text-xs text-slate-400">Past scientific projects, leadership roles, and funded awards.</p>
            </div>
            <Button size="sm" variant="outline" onClick={handleAddResearch} className="flex items-center gap-1.5">
              <Plus className="w-3.5 h-3.5" />
              Add Project
            </Button>
          </div>

          <div className="space-y-3">
            {researchHistories.map((res, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <input
                    type="text"
                    placeholder="Project / Grant Title"
                    value={res.project_title}
                    onChange={(e) => handleUpdateResearch(idx, "project_title", e.target.value)}
                    className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                  />
                  <input
                    type="text"
                    placeholder="Role (e.g. Lead Investigator)"
                    value={res.role}
                    onChange={(e) => handleUpdateResearch(idx, "role", e.target.value)}
                    className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                  />
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Sponsor / Organization"
                      value={res.organization}
                      onChange={(e) => handleUpdateResearch(idx, "organization", e.target.value)}
                      className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-100"
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveResearch(idx)}
                      className="p-1.5 text-slate-500 hover:text-rose-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <input
                  type="text"
                  placeholder="Project scope, objectives, or grant funding amount..."
                  value={res.description || ""}
                  onChange={(e) => handleUpdateResearch(idx, "description", e.target.value)}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-1.5 text-xs text-slate-300"
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
