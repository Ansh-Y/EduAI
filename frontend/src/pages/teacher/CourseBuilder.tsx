import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  BookOpen,
  Sparkles,
  Save,
  Plus,
  Trash2,
  FileText,
  FileCode,
  Video,
  CheckCircle2,
  RefreshCw,
  Eye,
  HelpCircle,
  Download,
  Share2,
  ChevronRight,
  AlertTriangle,
  FileDown
} from 'lucide-react';
import { Course, Section, QuizQuestion } from '../../types';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

export const CourseBuilder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSecIndex, setSelectedSecIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<'content' | 'artifacts' | 'quiz' | 'settings'>('content');

  // Active section editor state
  const [secTitle, setSecTitle] = useState('');
  const [secContent, setSecContent] = useState('');
  const [secSummary, setSecSummary] = useState('');
  const [secObjectives, setSecObjectives] = useState<string[]>([]);
  const [newObjInput, setNewObjInput] = useState('');

  // Course settings state
  const [courseTitle, setCourseTitle] = useState('');
  const [courseDesc, setCourseDesc] = useState('');
  const [courseSubject, setCourseSubject] = useState('');
  const [courseDifficulty, setCourseDifficulty] = useState('Beginner');
  const [passingThreshold, setPassingThreshold] = useState(70);
  const [maxAttempts, setMaxAttempts] = useState(3);

  // Quiz editor state
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [savingSec, setSavingSec] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  const loadCourse = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.getCourse(Number(id));
      setCourse(data);

      setCourseTitle(data.title);
      setCourseDesc(data.description || '');
      setCourseSubject(data.subject);
      setCourseDifficulty(data.difficulty);
      setPassingThreshold(data.passing_threshold || 70);
      setMaxAttempts(data.max_quiz_attempts || 3);

      if (data.sections && data.sections.length > 0) {
        const activeSec = data.sections[selectedSecIndex] || data.sections[0];
        setSecTitle(activeSec.title);
        setSecContent(activeSec.content);
        setSecSummary(activeSec.summary || '');
        setSecObjectives(activeSec.objectives || []);
        loadQuizForSection(activeSec.id);
      }
    } catch (err: any) {
      toast.error(err.message || 'Failed to load course details');
    } finally {
      setLoading(false);
    }
  };

  const loadQuizForSection = async (sectionId: number) => {
    try {
      const qs = await api.getSectionQuizQuestions(sectionId);
      setQuizQuestions(qs);
    } catch (e) {
      setQuizQuestions([]);
    }
  };

  useEffect(() => {
    loadCourse();
  }, [id]);

  const handleSelectSection = (index: number) => {
    if (!course?.sections) return;
    setSelectedSecIndex(index);
    const sec = course.sections[index];
    if (sec) {
      setSecTitle(sec.title);
      setSecContent(sec.content);
      setSecSummary(sec.summary || '');
      setSecObjectives(sec.objectives || []);
      loadQuizForSection(sec.id);
    }
  };

  const handleSaveSection = async () => {
    if (!course?.sections || !course.sections[selectedSecIndex]) return;
    const secId = course.sections[selectedSecIndex].id;
    setSavingSec(true);
    try {
      await api.updateSection(secId, {
        title: secTitle,
        content: secContent,
        summary: secSummary,
        objectives: secObjectives,
      });
      toast.success('Section and Smart Notes updated successfully!');
      loadCourse();
    } catch (err: any) {
      toast.error(err.message || 'Failed to save section');
    } finally {
      setSavingSec(false);
    }
  };

  const handleSaveCourseSettings = async () => {
    if (!course) return;
    try {
      await api.updateCourse(course.id, {
        title: courseTitle,
        description: courseDesc,
        subject: courseSubject,
        difficulty: courseDifficulty,
        passing_threshold: Number(passingThreshold),
        max_quiz_attempts: Number(maxAttempts),
      });
      toast.success('Course settings updated!');
      loadCourse();
    } catch (err: any) {
      toast.error(err.message || 'Failed to update course settings');
    }
  };

  const handleTogglePublish = async () => {
    if (!course) return;
    try {
      const res = await api.publishCourse(course.id);
      toast.success(res.message);
      setCourse({ ...course, is_published: res.is_published });
    } catch (err: any) {
      toast.error(err.message || 'Failed to change publication status');
    }
  };

  const handleRegenerateArtifacts = async (artifactType = 'all') => {
    if (!course?.sections || !course.sections[selectedSecIndex]) return;
    const secId = course.sections[selectedSecIndex].id;
    setRegenerating(true);
    try {
      const res = await api.regenerateArtifacts(secId, artifactType);
      toast.success(res.message);
      loadCourse();
      loadQuizForSection(secId);
    } catch (err: any) {
      toast.error(err.message || 'Regeneration failed');
    } finally {
      setRegenerating(false);
    }
  };

  const handleAddObjective = () => {
    if (!newObjInput.trim()) return;
    setSecObjectives([...secObjectives, newObjInput.trim()]);
    setNewObjInput('');
  };

  const handleRemoveObjective = (index: number) => {
    setSecObjectives(secObjectives.filter((_, i) => i !== index));
  };

  if (loading || !course) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-slate-500">Loading course builder...</p>
        </div>
      </div>
    );
  }

  const activeSec = course.sections?.[selectedSecIndex];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-wider">
              {course.subject}
            </span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                course.is_published
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800'
                  : 'bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800'
              }`}
            >
              {course.is_published ? 'Published to Students' : 'Draft Mode'}
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white">
            {course.title}
          </h1>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            to={`/learn/${course.id}`}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-100 transition"
          >
            <Eye className="w-4 h-4" />
            Preview Student View
          </Link>
          <button
            onClick={handleTogglePublish}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold transition shadow-sm ${
              course.is_published
                ? 'bg-amber-500 hover:bg-amber-600 text-white'
                : 'bg-emerald-600 hover:bg-emerald-700 text-white'
            }`}
          >
            <Share2 className="w-4 h-4" />
            {course.is_published ? 'Unpublish Course' : 'Publish to Students'}
          </button>
        </div>
      </div>

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Section Navigator */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-4 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Course Syllabus ({course.sections?.length || 0} Modules)
              </span>
            </div>

            <div className="space-y-1.5">
              {course.sections?.map((sec, idx) => {
                const isSelected = idx === selectedSecIndex;
                return (
                  <button
                    key={sec.id}
                    onClick={() => handleSelectSection(idx)}
                    className={`w-full flex items-center justify-between p-3 rounded-2xl text-xs font-semibold transition text-left ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                        : 'bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200/60 dark:border-slate-700/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${isSelected ? 'bg-white/20 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}>
                        {idx + 1}
                      </span>
                      <span className="truncate">{sec.title}</span>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-slate-400'}`} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Quick Smart Notes Downloads Card */}
          {activeSec && (
            <div className="p-4 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <FileDown className="w-4 h-4 text-indigo-500" />
                Active Section Smart Notes
              </span>
              <p className="text-xs text-slate-500">
                Download generated ReportLab PDF or Word DOCX documents for Module {selectedSecIndex + 1}:
              </p>
              <div className="grid grid-cols-2 gap-2 pt-1">
                <a
                  href={api.getNotesPdfUrl(activeSec.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-bold bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 hover:bg-rose-100 transition"
                >
                  <FileText className="w-3.5 h-3.5" />
                  PDF Notes
                </a>
                <a
                  href={api.getNotesDocxUrl(activeSec.id)}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-bold bg-sky-50 dark:bg-sky-950/40 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800 hover:bg-sky-100 transition"
                >
                  <FileCode className="w-3.5 h-3.5" />
                  DOCX Notes
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Right: Section Editor & Tools */}
        <div className="lg:col-span-8 space-y-4">
          {/* Subtabs Bar */}
          <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm">
            <button
              onClick={() => setActiveTab('content')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition ${
                activeTab === 'content'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Lesson Content &amp; Script
            </button>
            <button
              onClick={() => setActiveTab('artifacts')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition ${
                activeTab === 'artifacts'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              6-Artifact Pipeline
            </button>
            <button
              onClick={() => setActiveTab('quiz')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition ${
                activeTab === 'quiz'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Section Quiz ({quizQuestions.length})
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition ${
                activeTab === 'settings'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Course Settings
            </button>
          </div>

          {/* TAB 1: Content Editor */}
          {activeTab === 'content' && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-5">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Section Title
                </label>
                <input
                  type="text"
                  value={secTitle}
                  onChange={(e) => setSecTitle(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm font-bold text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Learning Objectives
                </label>
                <div className="space-y-1.5 mb-2">
                  {secObjectives.map((obj, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs">
                      <span className="text-slate-700 dark:text-slate-300">• {obj}</span>
                      <button
                        onClick={() => handleRemoveObjective(i)}
                        className="text-slate-400 hover:text-rose-500"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newObjInput}
                    onChange={(e) => setNewObjInput(e.target.value)}
                    placeholder="Add an actionable learning objective..."
                    className="flex-1 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs text-slate-900 dark:text-white"
                  />
                  <button
                    type="button"
                    onClick={handleAddObjective}
                    className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-bold text-slate-700 dark:text-slate-200 hover:bg-slate-200"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Detailed Lesson Content (Markdown, LaTeX Formulas &amp; Code)
                </label>
                <textarea
                  rows={14}
                  value={secContent}
                  onChange={(e) => setSecContent(e.target.value)}
                  className="w-full font-mono text-xs p-4 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                  Revision Summary
                </label>
                <textarea
                  rows={3}
                  value={secSummary}
                  onChange={(e) => setSecSummary(e.target.value)}
                  className="w-full text-xs p-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  disabled={savingSec}
                  onClick={handleSaveSection}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-md shadow-indigo-600/20 disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  {savingSec ? 'Saving...' : 'Save Section & Regenerate Notes'}
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: Six-Artifact Pipeline Inspector */}
          {activeTab === 'artifacts' && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Six-Artifact AI Pipeline Status
                  </h3>
                  <p className="text-xs text-slate-500">
                    Inspecting educational learning artifacts synthesized for "{secTitle}"
                  </p>
                </div>
                <button
                  onClick={() => handleRegenerateArtifacts('all')}
                  disabled={regenerating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin' : ''}`} />
                  Regenerate All Artifacts
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Artifact 1: Structured Lesson Script */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-indigo-500" />
                      Artifact 1: Lesson Script
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      Completed
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Structured pedagogical script with concepts, definitions, formulas, and examples.
                  </p>
                </div>

                {/* Artifact 2: Main Lesson Video */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <Video className="w-4 h-4 text-sky-500" />
                      Artifact 2: Main Lesson Video
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      Sample Stream Ready
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    High-definition lecture stream with speed control and progress persistence.
                  </p>
                </div>

                {/* Artifact 3: Summary Video */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <Video className="w-4 h-4 text-purple-500" />
                      Artifact 3: Summary Video
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      Completed
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Concise micro-lecture summarizing the key formulas and exam takeaways.
                  </p>
                </div>

                {/* Artifact 4: Smart Notes PDF */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <FileDown className="w-4 h-4 text-rose-500" />
                      Artifact 4: Smart Notes PDF
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      ReportLab PDF
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Publication-grade study guide with headers, page numbers, callouts, and exam tips.
                  </p>
                </div>

                {/* Artifact 5: Smart Notes DOCX */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <FileCode className="w-4 h-4 text-blue-500" />
                      Artifact 5: Smart Notes DOCX
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      python-docx Word
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Editable Microsoft Word document formatted according to university standards.
                  </p>
                </div>

                {/* Artifact 6: Section Quiz */}
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <HelpCircle className="w-4 h-4 text-amber-500" />
                      Artifact 6: Section Quiz
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
                      {quizQuestions.length} Questions
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500">
                    Interactive diagnostic assessment with instant grading and concept tracking.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Quiz Questions Inspector */}
          {activeTab === 'quiz' && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Quiz Questions ({quizQuestions.length})
                  </h3>
                  <p className="text-xs text-slate-500">
                    Generated questions evaluated automatically when students submit
                  </p>
                </div>
                <button
                  onClick={() => handleRegenerateArtifacts('quiz')}
                  disabled={regenerating}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-700 hover:bg-slate-100 transition"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin' : ''}`} />
                  Regenerate Question Bank
                </button>
              </div>

              <div className="space-y-3">
                {quizQuestions.length === 0 ? (
                  <div className="p-8 text-center text-slate-400 text-xs">
                    No questions generated yet. Click "Regenerate Question Bank" above.
                  </div>
                ) : (
                  quizQuestions.map((q, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-slate-50/50 dark:bg-slate-800/40 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                          Question {idx + 1} • {q.question_type.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                          Concept: {q.associated_concept}
                        </span>
                      </div>
                      <p className="text-xs font-semibold text-slate-900 dark:text-white">{q.question_text}</p>
                      
                      {q.options && q.options.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 pt-1">
                          {q.options.map((opt, oIdx) => (
                            <div
                              key={oIdx}
                              className={`p-2 rounded-xl text-xs border ${
                                opt === q.correct_answer
                                  ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300 font-bold'
                                  : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300'
                              }`}
                            >
                              {opt} {opt === q.correct_answer && '✓ (Correct)'}
                            </div>
                          ))}
                        </div>
                      )}

                      <div className="pt-1 text-[11px] text-slate-500 bg-slate-100 dark:bg-slate-900/60 p-2 rounded-xl">
                        <strong>Explanation:</strong> {q.explanation}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* TAB 4: Course Settings */}
          {activeTab === 'settings' && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-5">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Course Configuration &amp; Mastery Settings
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                    Course Title
                  </label>
                  <input
                    type="text"
                    value={courseTitle}
                    onChange={(e) => setCourseTitle(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs font-semibold text-slate-900 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                    Course Description
                  </label>
                  <textarea
                    rows={3}
                    value={courseDesc}
                    onChange={(e) => setCourseDesc(e.target.value)}
                    className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs text-slate-900 dark:text-white"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                      Quiz Passing Threshold (%)
                    </label>
                    <input
                      type="number"
                      min={50}
                      max={100}
                      value={passingThreshold}
                      onChange={(e) => setPassingThreshold(Number(e.target.value))}
                      className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs text-slate-900 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
                      Max Quiz Attempts
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={10}
                      value={maxAttempts}
                      onChange={(e) => setMaxAttempts(Number(e.target.value))}
                      className="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs text-slate-900 dark:text-white"
                    />
                  </div>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    onClick={handleSaveCourseSettings}
                    className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm"
                  >
                    Save Course Settings
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
