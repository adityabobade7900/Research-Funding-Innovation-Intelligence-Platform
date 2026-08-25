'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { authStorage } from '@/lib/auth';
import { User } from '@/types/user';
import {
  AdminUserItem,
  AdminUserListResponse,
  PipelineTelemetryResponse,
  SystemOverviewResponse,
  AuditLogItem,
  UserRole,
} from '@/types/admin';

export default function AdminPage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<'users' | 'telemetry' | 'overview' | 'audit'>('users');
  
  // Data States
  const [usersData, setUsersData] = useState<AdminUserListResponse | null>(null);
  const [telemetryData, setTelemetryData] = useState<PipelineTelemetryResponse | null>(null);
  const [overviewData, setOverviewData] = useState<SystemOverviewResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  
  // Filters & Pagination
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('');
  const [auditCategory, setAuditCategory] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    try {
      const params: Record<string, string | number> = { page: 1, size: 50 };
      if (searchQuery) params.q = searchQuery;
      if (selectedRole) params.role = selectedRole;

      const res = await api.get<{ data: AdminUserListResponse }>('/api/v1/admin/users', { params });
      setUsersData(res.data.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to fetch user list');
    }
  }, [searchQuery, selectedRole]);

  const fetchTelemetry = useCallback(async () => {
    try {
      const res = await api.get<{ data: PipelineTelemetryResponse }>('/api/v1/admin/telemetry/pipelines');
      setTelemetryData(res.data.data);
    } catch (err: any) {
      console.error(err);
    }
  }, []);

  const fetchOverview = useCallback(async () => {
    try {
      const res = await api.get<{ data: SystemOverviewResponse }>('/api/v1/admin/system/overview');
      setOverviewData(res.data.data);
    } catch (err: any) {
      console.error(err);
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    try {
      const params: Record<string, string | number> = { limit: 50, offset: 0 };
      if (auditCategory) params.category = auditCategory;
      const res = await api.get<{ data: { items: AuditLogItem[] } }>('/api/v1/admin/audit-logs', { params });
      setAuditLogs(res.data.data.items);
    } catch (err: any) {
      console.error(err);
    }
  }, [auditCategory]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      await Promise.all([fetchUsers(), fetchTelemetry(), fetchOverview(), fetchAuditLogs()]);
    } finally {
      setLoading(false);
    }
  }, [fetchUsers, fetchTelemetry, fetchOverview, fetchAuditLogs]);

  useEffect(() => {
    setCurrentUser(authStorage.getUser());
    loadData();
  }, [loadData]);

  const handleRoleChange = async (userId: number, newRole: UserRole) => {
    setActionLoadingId(userId);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.put(`/api/v1/admin/users/${userId}/role`, { role: newRole });
      setSuccessMsg(`Successfully updated role to ${newRole}`);
      await fetchUsers();
      await fetchAuditLogs();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to update user role');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleStatusToggle = async (userId: number, currentStatus: boolean) => {
    setActionLoadingId(userId);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await api.put(`/api/v1/admin/users/${userId}/status`, { is_active: !currentStatus });
      setSuccessMsg(`User account ${!currentStatus ? 'activated' : 'deactivated'}`);
      await fetchUsers();
      await fetchAuditLogs();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail?.message || 'Failed to toggle user status');
    } finally {
      setActionLoadingId(null);
    }
  };

  if (currentUser && currentUser.role !== 'administrator' && !currentUser.is_superuser) {
    return (
      <div className="p-8 text-center bg-slate-900 border border-slate-800 rounded-2xl">
        <h2 className="text-xl font-bold text-rose-400">Access Restricted</h2>
        <p className="text-xs text-slate-400 mt-2">
          Enterprise Administration & Governance Console requires Administrator privileges.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              Enterprise Governance
            </span>
            <span className="text-xs text-slate-400">
              M5 Administration, RBAC & Telemetry
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Administration & System Governance</h1>
          <p className="text-xs text-slate-400 max-w-2xl mt-1">
            Manage platform users, role assignments, provider ingestion health, database capacity, and security audit logs.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3.5 py-2 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
            <span className="text-slate-400">Database: </span>
            <strong className="text-emerald-400 font-mono">
              {overviewData?.database_status} ({overviewData?.database_latency_ms}ms)
            </strong>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center justify-between">
          <span>{errorMsg}</span>
          <button onClick={() => setErrorMsg(null)} className="text-rose-400 font-bold">×</button>
        </div>
      )}
      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center justify-between">
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} className="text-emerald-400 font-bold">×</button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 space-x-4">
        {[
          { id: 'users', label: 'User Governance & RBAC' },
          { id: 'telemetry', label: 'Pipeline Telemetry' },
          { id: 'overview', label: 'System Overview' },
          { id: 'audit', label: 'Security Audit Logs' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`pb-3 text-xs font-semibold border-b-2 transition ${
              activeTab === tab.id
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl h-48" />
          ))}
        </div>
      ) : (
        <>
          {/* TAB 1: USERS & RBAC */}
          {activeTab === 'users' && (
            <div className="space-y-4">
              {/* Filter Bar */}
              <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
                  <input
                    type="text"
                    placeholder="Search by name or email..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 w-full sm:w-64"
                  />
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">All Roles</option>
                    <option value="researcher">Researcher</option>
                    <option value="startup_founder">Startup Founder</option>
                    <option value="innovation_manager">Innovation Manager</option>
                    <option value="administrator">Administrator</option>
                  </select>
                </div>

                <div className="text-xs text-slate-400">
                  Total Users: <strong className="text-white">{usersData?.total ?? 0}</strong>
                </div>
              </div>

              {/* Users Table */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
                        <th className="p-3.5 font-medium">User Profile</th>
                        <th className="p-3.5 font-medium">Platform Role</th>
                        <th className="p-3.5 font-medium">Institution</th>
                        <th className="p-3.5 font-medium">Papers / Patents</th>
                        <th className="p-3.5 font-medium">Status</th>
                        <th className="p-3.5 font-medium text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {usersData?.items.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-950/40 transition">
                          <td className="p-3.5">
                            <div className="font-bold text-white">{u.full_name}</div>
                            <div className="text-[11px] text-slate-400 font-mono">{u.email}</div>
                          </td>
                          <td className="p-3.5">
                            <select
                              value={u.role}
                              disabled={actionLoadingId === u.id}
                              onChange={(e) => handleRoleChange(u.id, e.target.value as UserRole)}
                              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-indigo-300 font-medium focus:outline-none focus:border-indigo-500"
                            >
                              <option value="researcher">Researcher</option>
                              <option value="startup_founder">Startup Founder</option>
                              <option value="innovation_manager">Innovation Manager</option>
                              <option value="administrator">Administrator</option>
                            </select>
                          </td>
                          <td className="p-3.5 text-slate-300">
                            {u.institution || '—'}
                          </td>
                          <td className="p-3.5 text-slate-300 font-mono">
                            {u.publications_count} pubs • {u.patents_count} pats
                          </td>
                          <td className="p-3.5">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              u.is_active
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                            }`}>
                              {u.is_active ? 'ACTIVE' : 'DEACTIVATED'}
                            </span>
                          </td>
                          <td className="p-3.5 text-right">
                            <button
                              onClick={() => handleStatusToggle(u.id, u.is_active)}
                              disabled={actionLoadingId === u.id}
                              className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                                u.is_active
                                  ? 'bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                  : 'bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                              }`}
                            >
                              {u.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PIPELINE TELEMETRY */}
          {activeTab === 'telemetry' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Total Ingestion Connectors</span>
                  <div className="text-2xl font-bold text-white mt-1">{telemetryData?.total_pipelines}</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Active Connectors</span>
                  <div className="text-2xl font-bold text-emerald-400 mt-1">{telemetryData?.active_pipelines}</div>
                </div>
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 uppercase font-medium">Degraded Status</span>
                  <div className="text-2xl font-bold text-slate-400 mt-1">{telemetryData?.degraded_pipelines}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {telemetryData?.pipelines.map((p) => (
                  <div key={p.pipeline_name} className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3 shadow-sm">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        p.category === 'publication'
                          ? 'bg-blue-500/10 text-blue-400'
                          : p.category === 'patent'
                          ? 'bg-purple-500/10 text-purple-400'
                          : 'bg-emerald-500/10 text-emerald-400'
                      }`}>
                        {p.category.toUpperCase()}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400">
                        {p.status}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-white">{p.pipeline_name}</h4>
                      <span className="text-[10px] text-slate-500 font-mono">Provider: {p.provider_name}</span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800/80">
                      <div>
                        <span className="text-[10px] text-slate-500 block">Latency</span>
                        <span className="font-mono text-slate-200 font-bold">{p.latency_ms} ms</span>
                      </div>
                      <div>
                        <span className="text-[10px] text-slate-500 block">Records Ingested</span>
                        <span className="font-mono text-indigo-400 font-bold">{p.total_ingested_records}</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
                      <span>Success: {p.success_rate}%</span>
                      <span>Errors: {p.error_rate}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SYSTEM OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Total Publications</span>
                  <div className="text-3xl font-extrabold text-white mt-1">{overviewData?.total_publications}</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Total Patents</span>
                  <div className="text-3xl font-extrabold text-cyan-400 mt-1">{overviewData?.total_patents}</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Funding Solicitations</span>
                  <div className="text-3xl font-extrabold text-indigo-400 mt-1">{overviewData?.total_funding_opportunities}</div>
                </div>
                <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-medium">Tracked Grant Capital</span>
                  <div className="text-3xl font-extrabold text-emerald-400 mt-1">
                    ${((overviewData?.total_grant_capital_usd ?? 0) / 1000000).toFixed(1)}M
                  </div>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
                <h3 className="text-sm font-bold text-white">Platform Governance & Database Health</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">Database Status</span>
                    <span className="text-emerald-400 font-bold font-mono">{overviewData?.database_status}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">Database Latency</span>
                    <span className="text-white font-bold font-mono">{overviewData?.database_latency_ms} ms</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block">Alembic Migration Head</span>
                    <span className="text-indigo-400 font-bold font-mono">{overviewData?.migration_head}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: SECURITY AUDIT LOGS */}
          {activeTab === 'audit' && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-400">Category Filter:</span>
                <select
                  value={auditCategory}
                  onChange={(e) => setAuditCategory(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">All Categories</option>
                  <option value="RBAC">RBAC</option>
                  <option value="USER_MGMT">User Management</option>
                  <option value="INGESTION">Ingestion</option>
                  <option value="SYSTEM">System</option>
                  <option value="AUTH">Authentication</option>
                </select>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-950/60 text-slate-400">
                        <th className="p-3 font-medium">Timestamp</th>
                        <th className="p-3 font-medium">Event ID</th>
                        <th className="p-3 font-medium">Actor</th>
                        <th className="p-3 font-medium">Category</th>
                        <th className="p-3 font-medium">Action Detail</th>
                        <th className="p-3 font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                      {auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-950/40">
                          <td className="p-3 text-slate-400">{new Date(log.timestamp).toLocaleTimeString()}</td>
                          <td className="p-3 text-indigo-300">{log.id}</td>
                          <td className="p-3 text-slate-200">{log.actor_email}</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 rounded bg-slate-950 text-indigo-400 border border-slate-800">
                              {log.action_category}
                            </span>
                          </td>
                          <td className="p-3 text-slate-300 max-w-xs truncate">{log.action_detail}</td>
                          <td className="p-3">
                            <span className="text-emerald-400 font-bold">{log.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
