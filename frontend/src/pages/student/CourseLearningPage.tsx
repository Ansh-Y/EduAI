import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  BookOpen,
  Video,
  FileText,
  HelpCircle,
  MessageSquare,
  Lock,
  CheckCircle,
  ChevronRight,
  Download,
  Send,
  AlertCircle,
  Sparkles,
  RotateCcw,
  CheckCircle2,
  FileCode,
  ArrowRight,
  Award
} from 'lucide-react';
import { Course, Section, QuizQuestion, QuizSubmitResult, ChatMessage } from '../../types';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

export const CourseLearningPage: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSecIndex, setSelectedSecIndex] = useState(0);
  const [activeTab, setActiveTab] = useState<'lesson' | 'video' | 'notes' | 'quiz' | 'chat'>('lesson');

  // Video state
  const [videoMode, setVideoMode] = useState<'main' | 'summary'>('main');
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Quiz state
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [quizResult, setQuizResult] = useState<QuizSubmitResult | null>(null);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [sendingChat, setSendingChat] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  const loadCourse = async () => {
    if (!courseId) return;
    try {
      setLoading(true);
      const data = await api.getCourse(Number(courseId));
      setCourse(data);

      if (data.sections && data.sections.length > 0) {
        const activeSec = data.sections[selectedSecIndex] || data.sections[0];
        loadSectionData(activeSec.id);
      }
    } catch (err: any) {
      toast.error(err.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const loadSectionData = async (sectionId: number) => {
    try {
      const [qs, chats] = await Promise.all([
        api.getSectionQuizQuestions(sectionId),
        api.getSectionChatHistory(sectionId).catch(() => []),
      ]);
      setQuizQuestions(qs);
      setChatMessages(chats);
      setQuizAnswers({});
      setQuizResult(null);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadCourse();
  }, [courseId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, activeTab]);

  const handleSelectSection = (index: number) => {
    if (!course?.sections) return;
    const target = course.sections[index];
    if (!target.is_unlocked) {
      toast.error('Complete the previous section quiz to unlock this module!');
      return;
    }
    setSelectedSecIndex(index);
    loadSectionData(target.id);
  };

  const handleMarkComplete = async () => {
    if (!course?.sections) return;
    const sec = course.sections[selectedSecIndex];
    try {
      await api.updateSectionProgress(sec.id, { is_completed: true, video_progress: 100 });
      toast.success('Section marked as complete! Next section unlocked.');
      loadCourse();
    } catch (err: any) {
      toast.error(err.message || 'Failed to update progress');
    }
  };

  const handleQuizAnswer = (qId: number, answer: string) => {
    setQuizAnswers((prev) => ({ ...prev, [String(qId)]: answer }));
  };

  const handleSubmitQuiz = async () => {
    if (!course?.sections) return;
    const sec = course.sections[selectedSecIndex];
    if (Object.keys(quizAnswers).length === 0) {
      toast.error('Please select or write answers before submitting.');
      return;
    }
    setSubmittingQuiz(true);
    try {
      const res = await api.submitQuiz(sec.id, quizAnswers);
      setQuizResult(res);
      if (res.passed) {
        toast.success(`Passed! You scored ${res.score}%`);
        loadCourse();
      } else {
        toast.error(`Score: ${res.score}%. Passing threshold is ${res.passing_threshold}%. Review notes and retry!`);
      }
    } catch (err: any) {
      toast.error(err.message || 'Quiz submission failed');
    } finally {
      setSubmittingQuiz(false);
    }
  };

  const handleSendChat = async (presetPrompt?: string) => {
    const textToSend = presetPrompt || chatInput.trim();
    if (!textToSend || !course?.sections) return;
    const sec = course.sections[selectedSecIndex];

    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      message_content: textToSend,
      timestamp: new Date().toISOString(),
    };
    setChatMessages((prev) => [...prev, tempUserMsg]);
    if (!presetPrompt) setChatInput('');
    setSendingChat(true);

    try {
      const reply = await api.sendSectionChat(sec.id, textToSend);
      setChatMessages((prev) => [...prev, reply]);
    } catch (err: any) {
      toast.error(err.message || 'Assistant failed to respond');
    } finally {
      setSendingChat(false);
    }
  };

  if (loading || !course) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-slate-500">Preparing learning workspace...</p>
        </div>
      </div>
    );
  }

  const activeSec = course.sections?.[selectedSecIndex];
  const progressPct = course.student_progress || 0;

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Progress Banner */}
      <div className="p-5 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link to="/courses" className="hover:underline">Catalog</Link>
            <span>/</span>
            <span className="font-semibold text-slate-700 dark:text-slate-200">{course.title}</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
            {activeSec ? `Module ${selectedSecIndex + 1}: ${activeSec.title}` : course.title}
          </h1>
        </div>

        {/* Course Progress Widget */}
        <div className="flex items-center gap-4 bg-slate-50 dark:bg-slate-900/60 p-3 rounded-2xl border border-slate-200/60 dark:border-slate-800">
          <div className="text-right">
            <span className="text-[10px] font-bold uppercase text-slate-400 tracking-wider block">Course Mastery</span>
            <span className="text-sm font-black text-indigo-600 dark:text-indigo-400">{progressPct}% Complete</span>
          </div>
          <div className="w-24 h-2.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 to-sky-500 rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          {progressPct >= 100 && (
            <Link
              to="/student/certificates"
              className="p-1.5 rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300 font-bold text-xs flex items-center gap-1"
              title="View Earned Certificate"
            >
              <Award className="w-4 h-4" />
            </Link>
          )}
        </div>
      </div>

      {/* Main Grid: Sidebar Navigator + Interactive Tab View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Syllabus Navigator */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-4 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 px-2 block">
              Curriculum Sections
            </span>

            <div className="space-y-1.5">
              {course.sections?.map((sec, idx) => {
                const isSelected = idx === selectedSecIndex;
                const isUnlocked = sec.is_unlocked;
                const isCompleted = sec.is_completed;

                return (
                  <button
                    key={sec.id}
                    onClick={() => handleSelectSection(idx)}
                    disabled={!isUnlocked}
                    className={`w-full flex items-center justify-between p-3 rounded-2xl text-xs font-semibold transition text-left ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
                        : isUnlocked
                        ? 'bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200/60 dark:border-slate-700/60'
                        : 'bg-slate-100/60 dark:bg-slate-800/20 text-slate-400 border border-transparent cursor-not-allowed'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <div className="flex-shrink-0">
                        {isCompleted ? (
                          <CheckCircle2 className={`w-4 h-4 ${isSelected ? 'text-white' : 'text-emerald-500'}`} />
                        ) : !isUnlocked ? (
                          <Lock className="w-4 h-4 text-slate-400" />
                        ) : (
                          <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${isSelected ? 'bg-white/20 text-white' : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'}`}>
                            {idx + 1}
                          </span>
                        )}
                      </div>
                      <span className="truncate">{sec.title}</span>
                    </div>

                    {isCompleted && (
                      <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${isSelected ? 'bg-white/20 text-white' : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'}`}>
                        Done
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Content Viewport & Active Tabs */}
        <div className="lg:col-span-8 space-y-4">
          {/* Main Tab Switcher */}
          <div className="flex items-center gap-1.5 p-1.5 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm overflow-x-auto">
            <button
              onClick={() => setActiveTab('lesson')}
              className={`flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                activeTab === 'lesson'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              Lesson
            </button>
            <button
              onClick={() => setActiveTab('video')}
              className={`flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                activeTab === 'video'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Video className="w-3.5 h-3.5" />
              Video Lecture
            </button>
            <button
              onClick={() => setActiveTab('notes')}
              className={`flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                activeTab === 'notes'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              Smart Notes
            </button>
            <button
              onClick={() => setActiveTab('quiz')}
              className={`flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                activeTab === 'quiz'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <HelpCircle className="w-3.5 h-3.5" />
              Interactive Quiz ({quizQuestions.length})
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center justify-center gap-2 py-2 px-3.5 rounded-xl text-xs font-bold whitespace-nowrap transition ${
                activeTab === 'chat'
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              Ask Tutor AI
            </button>
          </div>

          {/* TAB 1: Lesson Content */}
          {activeTab === 'lesson' && activeSec && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
              {/* Executive Summary */}
              {activeSec.summary && (
                <div className="p-4 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/80">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-700 dark:text-indigo-400 block mb-1">
                    Executive Summary
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">
                    {activeSec.summary}
                  </p>
                </div>
              )}

              {/* Objectives */}
              {activeSec.objectives && activeSec.objectives.length > 0 && (
                <div className="space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Core Learning Objectives
                  </h3>
                  <div className="grid grid-cols-1 gap-1.5">
                    {activeSec.objectives.map((obj, i) => (
                      <div key={i} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                        <CheckCircle className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                        <span>{obj}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <hr className="border-slate-100 dark:border-slate-800" />

              {/* Main Text Content */}
              <div className="prose dark:prose-invert max-w-none text-xs leading-relaxed space-y-4">
                {activeSec.content.split('\n').map((line, idx) => {
                  const s = line.trim();
                  if (!s) return null;
                  if (s.startsWith('# ')) {
                    return <h2 key={idx} className="text-lg font-black text-slate-900 dark:text-white pt-2">{s.slice(2)}</h2>;
                  }
                  if (s.startsWith('## ')) {
                    return <h3 key={idx} className="text-sm font-bold text-indigo-600 dark:text-indigo-400 pt-3">{s.slice(3)}</h3>;
                  }
                  if (s.startsWith('### ')) {
                    return <h4 key={idx} className="text-xs font-bold text-slate-800 dark:text-slate-200 pt-1">{s.slice(4)}</h4>;
                  }
                  if (s.startsWith('- ') || s.startsWith('* ')) {
                    return <li key={idx} className="ml-4 list-disc text-slate-700 dark:text-slate-300">{s.slice(2)}</li>;
                  }
                  if (s.toLowerCase().includes('tip') || s.toLowerCase().includes('exam note:')) {
                    return (
                      <div key={idx} className="p-3 rounded-2xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 font-medium">
                        {s}
                      </div>
                    );
                  }
                  if (s.startsWith('```')) {
                    return null;
                  }
                  return <p key={idx} className="text-slate-700 dark:text-slate-300 leading-relaxed">{s}</p>;
                })}
              </div>

              {/* Lesson Completion Action Button */}
              <div className="pt-6 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400">
                  Ready to test your comprehension?
                </span>
                <button
                  type="button"
                  onClick={handleMarkComplete}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition shadow-md shadow-emerald-600/20"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Mark Lesson Completed &amp; Unlock Next
                </button>
              </div>
            </div>
          )}

          {/* TAB 2: Video Player */}
          {activeTab === 'video' && activeSec && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {videoMode === 'main' ? 'Main Lecture Video' : 'Summary Concept Takeaways'}
                  </h3>
                  <p className="text-xs text-slate-500">HD instructional video stream with interactive rate control</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setVideoMode(videoMode === 'main' ? 'summary' : 'main')}
                    className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200"
                  >
                    Switch to {videoMode === 'main' ? 'Summary Video' : 'Main Lecture'}
                  </button>
                </div>
              </div>

              {/* Video Element */}
              <div className="relative aspect-video rounded-2xl overflow-hidden bg-black shadow-lg">
                <video
                  ref={videoRef}
                  key={`${activeSec.id}-${videoMode}`}
                  controls
                  className="w-full h-full object-cover"
                  src={videoMode === 'main' ? activeSec.video_url : activeSec.summary_video_url}
                >
                  Your browser does not support HTML5 video playback.
                </video>
              </div>

              {/* Playback Speed Controls */}
              <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800">
                <span className="text-xs font-bold text-slate-600 dark:text-slate-300">Playback Speed:</span>
                <div className="flex items-center gap-1.5">
                  {[0.75, 1, 1.25, 1.5].map((speed) => (
                    <button
                      key={speed}
                      onClick={() => {
                        setPlaybackSpeed(speed);
                        if (videoRef.current) videoRef.current.playbackRate = speed;
                      }}
                      className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                        playbackSpeed === speed
                          ? 'bg-indigo-600 text-white'
                          : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                      }`}
                    >
                      {speed}x
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Smart Notes Preview & Downloads */}
          {activeTab === 'notes' && activeSec && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Smart Study Notes &amp; Exam Checklist
                  </h3>
                  <p className="text-xs text-slate-500">
                    Full academic review guide synthesized from {course.title}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <a
                    href={api.getNotesPdfUrl(activeSec.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 transition shadow-sm"
                  >
                    <Download className="w-4 h-4" />
                    Download PDF
                  </a>
                  <a
                    href={api.getNotesDocxUrl(activeSec.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-sky-600 hover:bg-sky-700 transition shadow-sm"
                  >
                    <FileCode className="w-4 h-4" />
                    Download DOCX
                  </a>
                </div>
              </div>

              {/* In-Browser Document Preview */}
              <div className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 font-sans space-y-4">
                <div className="border-b border-slate-200 dark:border-slate-800 pb-3">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400">
                    EduAI Academic Series
                  </span>
                  <h2 className="text-lg font-black text-slate-900 dark:text-white mt-0.5">
                    {course.title}
                  </h2>
                  <p className="text-xs font-bold text-slate-600 dark:text-slate-300">
                    Topic: {activeSec.title}
                  </p>
                </div>

                {activeSec.summary && (
                  <div className="p-3.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-xs">
                    <strong>Executive Summary:</strong> {activeSec.summary}
                  </div>
                )}

                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    1. Verified Objectives
                  </h4>
                  {activeSec.objectives?.map((o, idx) => (
                    <p key={idx} className="text-xs text-slate-600 dark:text-slate-400 pl-3">
                      • {o}
                    </p>
                  ))}
                </div>

                <div className="space-y-2 pt-2">
                  <h4 className="text-xs font-bold uppercase text-slate-700 dark:text-slate-300">
                    2. Technical Content
                  </h4>
                  <div className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed">
                    {activeSec.content.slice(0, 1200)}...
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: Interactive Quiz Player */}
          {activeTab === 'quiz' && activeSec && (
            <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Section Assessment Quiz
                  </h3>
                  <p className="text-xs text-slate-500">
                    Passing Threshold: {course.passing_threshold}% | Max Attempts: {course.max_quiz_attempts}
                  </p>
                </div>
                {quizResult && (
                  <button
                    onClick={() => {
                      setQuizResult(null);
                      setQuizAnswers({});
                    }}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    Retake Quiz
                  </button>
                )}
              </div>

              {/* POST-QUIZ DIAGNOSTIC & PERSONALIZED FEEDBACK */}
              {quizResult && (
                <div className="space-y-4">
                  <div
                    className={`p-6 rounded-3xl border ${
                      quizResult.passed
                        ? 'bg-emerald-50/60 dark:bg-emerald-950/30 border-emerald-300 dark:border-emerald-800'
                        : 'bg-rose-50/60 dark:bg-rose-950/30 border-rose-300 dark:border-rose-800'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div>
                        <span
                          className={`inline-block px-3 py-1 rounded-full text-xs font-bold mb-1.5 ${
                            quizResult.passed
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200'
                              : 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200'
                          }`}
                        >
                          {quizResult.passed ? 'Assessment Passed! ✓' : 'Revision Required ✗'}
                        </span>
                        <h4 className="text-2xl font-black text-slate-900 dark:text-white">
                          Your Score: {quizResult.score}%
                        </h4>
                        <p className="text-xs text-slate-600 dark:text-slate-300 mt-1">
                          {quizResult.correct_count} of {quizResult.total_questions} questions correct.
                          Attempts remaining: {quizResult.attempts_remaining}
                        </p>
                      </div>

                      {quizResult.weak_concepts?.length > 0 && (
                        <button
                          onClick={() => setActiveTab('lesson')}
                          className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-sm self-start"
                        >
                          Review Lesson Concept →
                        </button>
                      )}
                    </div>

                    {/* Feedback Plan */}
                    {quizResult.feedback_plan && (
                      <div className="mt-4 p-3.5 rounded-2xl bg-white/80 dark:bg-slate-900/60 border border-slate-200/60 dark:border-slate-800 text-xs">
                        <strong className="text-slate-800 dark:text-slate-200 block mb-1">
                          Personalized Pedagogical Feedback:
                        </strong>
                        <p className="text-slate-600 dark:text-slate-300">{quizResult.feedback_plan}</p>
                      </div>
                    )}
                  </div>

                  {/* Question-by-Question Evaluation Breakdown */}
                  <div className="space-y-3 pt-2">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      Detailed Answer Breakdown &amp; Explanations
                    </h4>
                    {quizResult.evaluations?.map((ev, idx) => (
                      <div
                        key={idx}
                        className={`p-4 rounded-2xl border text-xs space-y-1.5 ${
                          ev.is_correct
                            ? 'bg-emerald-50/30 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800/60'
                            : 'bg-rose-50/30 dark:bg-rose-950/20 border-rose-200 dark:border-rose-800/60'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-800 dark:text-slate-200">
                            Question {idx + 1}: {ev.question_text}
                          </span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              ev.is_correct
                                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                                : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                            }`}
                          >
                            {ev.is_correct ? 'Correct' : 'Incorrect'}
                          </span>
                        </div>
                        <p className="text-slate-600 dark:text-slate-400">
                          <strong>Your Answer:</strong> {ev.submitted_answer || '(Blank)'}
                        </p>
                        {!ev.is_correct && (
                          <p className="text-emerald-700 dark:text-emerald-400 font-semibold">
                            <strong>Correct Answer:</strong> {ev.correct_answer}
                          </p>
                        )}
                        <p className="text-slate-500 text-[11px] bg-white/60 dark:bg-slate-900/40 p-2 rounded-xl">
                          <strong>Explanation:</strong> {ev.explanation}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* QUIZ FORM */}
              {!quizResult && (
                <div className="space-y-6">
                  {quizQuestions.length === 0 ? (
                    <div className="p-8 text-center text-xs text-slate-400">
                      No questions configured for this section.
                    </div>
                  ) : (
                    quizQuestions.map((q, qIdx) => (
                      <div
                        key={q.id}
                        className="p-5 rounded-2xl bg-slate-50/70 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 uppercase">
                            Question {qIdx + 1}
                          </span>
                          <span className="text-[10px] font-semibold text-slate-400">
                            Concept: {q.associated_concept}
                          </span>
                        </div>

                        <p className="text-xs font-bold text-slate-900 dark:text-white">
                          {q.question_text}
                        </p>

                        {/* Options */}
                        {q.question_type === 'multiple_choice' || q.question_type === 'true_false' ? (
                          <div className="space-y-2 pt-1">
                            {q.options?.map((opt, oIdx) => {
                              const isChecked = quizAnswers[String(q.id)] === opt;
                              return (
                                <label
                                  key={oIdx}
                                  className={`flex items-center gap-3 p-3 rounded-xl border text-xs cursor-pointer transition ${
                                    isChecked
                                      ? 'bg-indigo-50 dark:bg-indigo-950/60 border-indigo-500 text-indigo-900 dark:text-indigo-200 font-semibold'
                                      : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700/80 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                                  }`}
                                >
                                  <input
                                    type="radio"
                                    name={`q_${q.id}`}
                                    value={opt}
                                    checked={isChecked}
                                    onChange={() => handleQuizAnswer(q.id, opt)}
                                    className="accent-indigo-600"
                                  />
                                  <span>{opt}</span>
                                </label>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="pt-1">
                            <input
                              type="text"
                              value={quizAnswers[String(q.id)] || ''}
                              onChange={(e) => handleQuizAnswer(q.id, e.target.value)}
                              placeholder="Type your answer here..."
                              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                            />
                          </div>
                        )}
                      </div>
                    ))
                  )}

                  {quizQuestions.length > 0 && (
                    <div className="pt-4 flex justify-end">
                      <button
                        type="button"
                        disabled={submittingQuiz}
                        onClick={handleSubmitQuiz}
                        className="flex items-center gap-2 px-6 py-3 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition shadow-md shadow-indigo-600/30 disabled:opacity-50"
                      >
                        {submittingQuiz ? 'Grading Assessment...' : 'Submit Assessment for Instant Grading'}
                        <ArrowRight className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Ask Anything AI Assistant */}
          {activeTab === 'chat' && activeSec && (
            <div className="p-6 rounded-3xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm flex flex-col h-[600px]">
              <div className="pb-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-indigo-500" />
                    Ask Anything — Context-Grounded AI Teaching Assistant
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    Answers questions grounded in "{activeSec.title}"
                  </p>
                </div>
              </div>

              {/* Chat history */}
              <div className="flex-1 overflow-y-auto py-4 space-y-3">
                {chatMessages.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400 space-y-2">
                    <Sparkles className="w-8 h-8 text-indigo-500/40 mx-auto" />
                    <p className="font-semibold text-slate-600 dark:text-slate-300">
                      What would you like clarified about {activeSec.title}?
                    </p>
                    <p className="text-[11px] text-slate-400">
                      Click any suggested prompt below or type your own question.
                    </p>
                  </div>
                ) : (
                  chatMessages.map((msg, i) => (
                    <div
                      key={i}
                      className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                    >
                      <div
                        className={`max-w-[85%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                          msg.role === 'user'
                            ? 'bg-indigo-600 text-white rounded-br-none'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-bl-none border border-slate-200 dark:border-slate-700/60'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.message_content}</p>
                        {msg.sources_cited && (
                          <span className="mt-2 block text-[10px] opacity-75 font-medium border-t border-slate-200 dark:border-slate-700 pt-1">
                            Source: {msg.sources_cited}
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {sendingChat && (
                  <div className="flex items-center gap-2 text-xs text-indigo-500 font-medium">
                    <div className="w-3 h-3 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                    <span>Tutor is formulating response from lesson context...</span>
                  </div>
                )}
                <div ref={chatBottomRef} />
              </div>

              {/* Quick Prompt Pills */}
              <div className="pt-2 pb-3 flex items-center gap-1.5 overflow-x-auto">
                {[
                  'Explain this in simple terms',
                  'Give me a practical real-world example',
                  'Summarize key formulas for the exam',
                  'What is the common pitfall here?'
                ].map((pill, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendChat(pill)}
                    className="px-2.5 py-1 rounded-xl text-[10px] font-semibold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 whitespace-nowrap transition"
                  >
                    {pill}
                  </button>
                ))}
              </div>

              {/* Chat Input Bar */}
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                  placeholder="Ask a question about this lesson..."
                  className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                />
                <button
                  type="button"
                  disabled={sendingChat || !chatInput.trim()}
                  onClick={() => handleSendChat()}
                  className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition shadow-sm disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
