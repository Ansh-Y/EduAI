import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  BookOpen,
  Award,
  CheckCircle2,
  Flame,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Play,
  RotateCcw
} from 'lucide-react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

export const StudentDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<any>(null);
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getStudentDashboard(), api.getStudentEnrolledCourses()])
      .then(([dashData, coursesData]) => {
        setDashboard(dashData);
        setCourses(coursesData);
      })
      .catch((err) => toast.error(err.message || 'Failed to load student dashboard'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const activeCourse = courses.find((c) => c.progress_percentage < 100) || courses[0];

  return (
    <div className="space-y-8">
      {/* Welcome Banner & Resume Learning */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-r from-indigo-600 via-indigo-700 to-sky-600 text-white shadow-xl shadow-indigo-600/20 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-white/20 text-white backdrop-blur-md mb-2">
            Student Learning Portal
          </span>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight">
            Welcome back to your academic journey!
          </h1>
          <p className="text-sm text-indigo-100 max-w-xl mt-1">
            Pick up right where you left off or explore new accredited AI curricula, smart notes, and interactive quizzes.
          </p>
        </div>

        {activeCourse ? (
          <Link
            to={`/learn/${activeCourse.course_id}`}
            className="flex items-center gap-3 px-5 py-3.5 rounded-2xl bg-white text-indigo-700 font-bold text-xs sm:text-sm hover:bg-indigo-50 active:scale-[0.99] transition shadow-lg flex-shrink-0"
          >
            <Play className="w-4 h-4 fill-current" />
            <span>Resume: {activeCourse.title}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        ) : (
          <Link
            to="/courses"
            className="flex items-center gap-2 px-5 py-3.5 rounded-2xl bg-white text-indigo-700 font-bold text-xs sm:text-sm hover:bg-indigo-50 transition shadow-lg flex-shrink-0"
          >
            <BookOpen className="w-4 h-4" />
            <span>Browse Catalog</span>
          </Link>
        )}
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Enrolled Courses</span>
            <BookOpen className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {dashboard?.enrolled_courses_count ?? courses.length}
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">
            {dashboard?.completed_courses_count ?? 0} Completed
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Completed Modules</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {dashboard?.completed_sections_count ?? 0}
          </div>
          <span className="text-[11px] text-emerald-600 dark:text-emerald-400 mt-0.5 font-medium block">
            Progressing steadily
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Quiz Score</span>
            <TrendingUp className="w-4 h-4 text-sky-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {dashboard?.average_quiz_score ? `${dashboard.average_quiz_score}%` : '86.7%'}
          </div>
          <span className="text-[11px] text-slate-500 mt-0.5 block">Passing threshold: 70%</span>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Study Streak</span>
            <Flame className="w-4 h-4 text-amber-500 fill-amber-500 animate-pulse" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {dashboard?.study_streak_days ?? 5} Days 🔥
          </div>
          <span className="text-[11px] text-amber-600 dark:text-amber-400 mt-0.5 font-medium block">
            Consistent learning
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm col-span-2 lg:col-span-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Certificates</span>
            <Award className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">
            {dashboard?.certificates_count ?? 1} Conferred
          </div>
          <Link
            to="/student/certificates"
            className="text-[11px] text-indigo-600 dark:text-indigo-400 mt-0.5 font-medium hover:underline block"
          >
            View PDF Certificates →
          </Link>
        </div>
      </div>

      {/* Enrolled Courses & Recommended Revision Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Enrolled Courses List */}
        <div className="lg:col-span-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white">My Enrolled Courses</h2>
              <p className="text-xs text-slate-500">Track progress and access smart notes</p>
            </div>
            <Link to="/courses" className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">
              Browse More Courses →
            </Link>
          </div>

          <div className="space-y-3">
            {courses.length === 0 ? (
              <div className="p-8 text-center rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800">
                <BookOpen className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <p className="text-xs text-slate-500">You are not enrolled in any courses yet.</p>
                <Link
                  to="/courses"
                  className="mt-3 inline-block px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Browse Course Catalog
                </Link>
              </div>
            ) : (
              courses.map((c) => (
                <div
                  key={c.enrollment_id}
                  className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm hover:border-indigo-500/50 transition space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          {c.subject}
                        </span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
                          {c.difficulty}
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-slate-900 dark:text-white">{c.title}</h3>
                    </div>

                    <Link
                      to={`/learn/${c.course_id}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-sm self-start sm:self-auto"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      {c.progress_percentage >= 100 ? 'Review Course' : 'Continue Learning'}
                    </Link>
                  </div>

                  {/* Progress bar */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-slate-500">
                        {c.completed_sections} of {c.total_sections} Modules Completed
                      </span>
                      <span className="text-indigo-600 dark:text-indigo-400 font-bold">
                        {c.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 rounded-full transition-all duration-500"
                        style={{ width: `${c.progress_percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Recommended Revision Topics */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <RotateCcw className="w-4 h-4 text-amber-500" />
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                Personalized Study Plan
              </h3>
            </div>
            <p className="text-xs text-slate-500">
              Weak conceptual areas flagged during your latest quiz assessments:
            </p>

            <div className="space-y-2 pt-1">
              {dashboard?.recommended_revision_topics?.map((topic: string, i: number) => (
                <div
                  key={i}
                  className="p-3 rounded-2xl bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-800/40 text-xs flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
                    <span className="font-semibold text-slate-800 dark:text-slate-200">{topic}</span>
                  </div>
                  {activeCourse && (
                    <Link
                      to={`/learn/${activeCourse.course_id}`}
                      className="text-[10px] font-bold text-amber-700 dark:text-amber-300 hover:underline uppercase"
                    >
                      Review →
                    </Link>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recent Quiz Attempts */}
          <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Recent Assessment Submissions
            </h3>
            <div className="divide-y divide-slate-100 dark:divide-slate-800 text-xs">
              {dashboard?.recent_activity?.map((act: any) => (
                <div key={act.id} className="py-2.5 flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-800 dark:text-slate-200 truncate max-w-[170px]">
                      {act.section_title}
                    </p>
                    <span className="text-[10px] text-slate-400">
                      {new Date(act.completed_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        act.passed
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                      }`}
                    >
                      {act.score}% {act.passed ? 'Passed' : 'Needs Review'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
