import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  BookOpen,
  GraduationCap,
  ShieldCheck,
  TrendingUp,
  Activity,
  Layers,
  ArrowRight
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { api } from '../../services/api';
import { useTheme } from '../../contexts/ThemeContext';
import toast from 'react-hot-toast';

export const AdminDashboard: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { isDark } = useTheme();

  useEffect(() => {
    api.getAdminOverview()
      .then((data) => setOverview(data))
      .catch((err) => toast.error(err.message || 'Failed to load administrator overview'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const PIE_COLORS = ['#4F46E5', '#0EA5E9', '#F59E0B'];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-800/80 mb-2">
            <ShieldCheck className="w-3.5 h-3.5" />
            Platform Governance &amp; Administration
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Dean &amp; System Oversight
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Global telemetry, academic curriculum audits, and role-based access management.
          </p>
        </div>

        <Link
          to="/admin/users"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-md shadow-indigo-600/20"
        >
          <Users className="w-4 h-4" />
          Manage Users Directory
        </Link>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Registered Users</span>
            <Users className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {overview?.total_users ?? 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            {overview?.total_students ?? 0} Students • {overview?.total_teachers ?? 0} Teachers
          </span>
        </div>

        <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Courses</span>
            <BookOpen className="w-4 h-4 text-sky-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {overview?.total_courses ?? 0}
          </div>
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-1 font-semibold block">
            {overview?.published_courses ?? 0} Published Live
          </span>
        </div>

        <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Enrollments</span>
            <GraduationCap className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {overview?.total_enrollments ?? 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Active curriculum seats</span>
        </div>

        <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Quiz Submissions</span>
            <TrendingUp className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white mt-2">
            {overview?.total_quiz_submissions ?? 0}
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">Completed assessments</span>
        </div>
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* User Distribution Pie/Bar */}
        <div className="lg:col-span-5 p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">User Role Breakdown</h3>
            <p className="text-xs text-slate-500">Proportion of students, faculty, and administrators</p>
          </div>
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={overview?.user_distribution || []}
                  dataKey="count"
                  nameKey="role"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                >
                  {overview?.user_distribution?.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0F172A' : '#FFFFFF',
                    borderColor: isDark ? '#334155' : '#E2E8F0',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: isDark ? '#F8FAFC' : '#0F172A',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-2 pt-2 text-center text-xs">
            {overview?.user_distribution?.map((item: any, i: number) => (
              <div key={i} className="p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-100 dark:border-slate-800">
                <span className="w-2.5 h-2.5 rounded-full inline-block mr-1" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                <span className="font-bold text-slate-800 dark:text-slate-200 block">{item.count}</span>
                <span className="text-[10px] text-slate-500">{item.role}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Course Enrollment Breakdown */}
        <div className="lg:col-span-7 p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Course Enrollment Velocity</h3>
            <p className="text-xs text-slate-500">Student uptake by curriculum</p>
          </div>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={overview?.enrollment_trends || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={isDark ? '#334155' : '#E2E8F0'} vertical={false} />
                <XAxis dataKey="course" stroke={isDark ? '#94A3B8' : '#64748B'} fontSize={11} tickLine={false} />
                <YAxis stroke={isDark ? '#94A3B8' : '#64748B'} fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0F172A' : '#FFFFFF',
                    borderColor: isDark ? '#334155' : '#E2E8F0',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: isDark ? '#F8FAFC' : '#0F172A',
                  }}
                />
                <Bar dataKey="enrollments" fill="#4F46E5" radius={[6, 6, 0, 0]} name="Enrollments" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Platform Activity */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-500" />
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white">Recent Platform Activity Stream</h3>
            <p className="text-xs text-slate-500">Live feed of student assessments, submissions, and course events</p>
          </div>
        </div>

        <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
          {overview?.recent_activity?.map((act: any, idx: number) => (
            <div key={idx} className="py-3 flex items-center justify-between">
              <div>
                <p className="font-semibold text-slate-800 dark:text-slate-200">{act.description}</p>
                <span className="text-[10px] text-slate-400">{act.timestamp}</span>
              </div>
              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${act.status === 'Passed' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300'}`}>
                {act.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
