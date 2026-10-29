import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, Wand2, BookOpen, Layers, Check, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

export const AICourseGenerator: React.FC = () => {
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [prompt, setPrompt] = useState('');
  const [difficulty, setDifficulty] = useState('Beginner');
  const [targetAudience, setTargetAudience] = useState('Undergraduate Students');
  const [sectionCount, setSectionCount] = useState(5);
  const [generating, setGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const navigate = useNavigate();

  const samplePrompts = [
    {
      title: 'Introduction to Machine Learning',
      subject: 'Computer Science & AI',
      prompt: 'Cover supervised learning, unsupervised learning, model evaluation, overfitting and regularization, and practical Python implementations.',
      difficulty: 'Intermediate',
      sections: 5
    },
    {
      title: 'Distributed Cloud Systems & DevOps',
      subject: 'Software Architecture',
      prompt: 'Cover microservices design, containerization with Docker, Kubernetes orchestration, CI/CD pipelines, and high availability consensus.',
      difficulty: 'Advanced',
      sections: 4
    },
    {
      title: 'Modern Full-Stack Web Development',
      subject: 'Web Technologies',
      prompt: 'Cover modern React components, state management, asynchronous REST APIs with FastAPI, database modeling, and token authentication.',
      difficulty: 'Beginner',
      sections: 4
    }
  ];

  const handleApplySample = (s: typeof samplePrompts[0]) => {
    setTitle(s.title);
    setSubject(s.subject);
    setPrompt(s.prompt);
    setDescription(`Comprehensive university-level curriculum covering ${s.title}.`);
    setDifficulty(s.difficulty);
    setSectionCount(s.sections);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !subject.trim()) {
      toast.error('Please specify both Course Title and Subject.');
      return;
    }

    setGenerating(true);
    setCurrentStep(1);

    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 1200);

    try {
      const result = await api.generateCourse({
        title,
        subject,
        description,
        prompt,
        target_audience: targetAudience,
        difficulty,
        section_count: Number(sectionCount),
      });

      clearInterval(stepInterval);
      setCurrentStep(4);
      toast.success('Course generated successfully with 6-artifact pipeline!');
      setTimeout(() => {
        navigate(`/teacher/courses/${result.id}`);
      }, 800);
    } catch (err: any) {
      clearInterval(stepInterval);
      toast.error(err.message || 'Course generation failed');
      setGenerating(false);
      setCurrentStep(0);
    }
  };

  const steps = [
    'Synthesizing curriculum syllabus & learning objectives...',
    'Formulating mathematical explanations & practical code examples...',
    'Compiling ReportLab Smart Notes PDF & Word DOCX documents...',
    'Assembling interactive question bank & diagnostic rubrics...',
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/80 mb-2">
          <Sparkles className="w-3.5 h-3.5" />
          University AI Curriculum Engine
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Generate Accredited Course
        </h1>
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
          Provide a high-level natural language prompt. EduAI will synthesize complete lesson scripts, video lecture outlines, genuine Smart Notes (PDF &amp; DOCX), and interactive graded quizzes.
        </p>
      </div>

      {/* Sample Presets */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#1E293B] border border-slate-200/80 dark:border-slate-800 shadow-sm space-y-2">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Quick Start Demonstration Prompts
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
          {samplePrompts.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplySample(s)}
              className="p-3 text-left rounded-xl border border-slate-200 dark:border-slate-700/80 bg-slate-50 dark:bg-slate-800/40 hover:border-indigo-500/80 dark:hover:border-indigo-500/80 transition group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                  {s.title}
                </span>
                <span className="text-[10px] px-1.5 py-0.2 rounded bg-slate-200 dark:bg-slate-700 font-semibold">
                  {s.sections} Sec
                </span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">{s.prompt}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Main Form */}
      <div className="bg-white dark:bg-[#1E293B] p-6 sm:p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                Course Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Introduction to Machine Learning"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                Academic Subject / Domain *
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g. Computer Science & AI"
                required
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
              Course Overview &amp; Learning Objectives
            </label>
            <textarea
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief summary of course scope, prerequisites, and target competencies..."
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
              Curriculum Guidance Prompt
            </label>
            <textarea
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Specify topics you want included (e.g. 'Cover supervised learning, gradient descent, SVMs, neural networks, cross-validation, and practical python code')..."
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                Target Audience
              </label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="Undergraduate Students"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300 mb-1.5">
                Difficulty Level
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              >
                <option value="Beginner">Beginner (100 Level)</option>
                <option value="Intermediate">Intermediate (200-300 Level)</option>
                <option value="Advanced">Advanced (400+ Graduate Level)</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                  Number of Sections:
                </label>
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                  {sectionCount} Sections
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={sectionCount}
                onChange={(e) => setSectionCount(Number(e.target.value))}
                className="w-full accent-indigo-600 h-2 bg-slate-200 dark:bg-slate-700 rounded-lg cursor-pointer"
              />
            </div>
          </div>

          {/* Live Generation Progress Indicator */}
          {generating && (
            <div className="p-5 rounded-2xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 space-y-3">
              <div className="flex items-center justify-between text-xs font-bold text-indigo-900 dark:text-indigo-200">
                <span className="flex items-center gap-2">
                  <Wand2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400 animate-spin" />
                  Generating University Curriculum Pipeline...
                </span>
                <span>Step {currentStep} of 4</span>
              </div>

              <div className="w-full h-2 rounded-full bg-indigo-200 dark:bg-indigo-900 overflow-hidden">
                <div
                  className="h-full bg-indigo-600 transition-all duration-500 rounded-full"
                  style={{ width: `${(currentStep / 4) * 100}%` }}
                />
              </div>

              <div className="space-y-1.5">
                {steps.map((s, idx) => {
                  const stepNum = idx + 1;
                  const isDone = currentStep > stepNum;
                  const isCurrent = currentStep === stepNum;
                  return (
                    <div key={idx} className="flex items-center gap-2 text-xs">
                      {isDone ? (
                        <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                      ) : isCurrent ? (
                        <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-300 dark:border-slate-600" />
                      )}
                      <span className={isCurrent ? 'font-bold text-indigo-700 dark:text-indigo-300' : isDone ? 'text-slate-700 dark:text-slate-300' : 'text-slate-400'}>
                        {s}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="submit"
              disabled={generating}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-700 hover:to-sky-700 transition shadow-md shadow-indigo-600/30 disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              {generating ? 'Generating Syllabus...' : 'Generate Full Course & Materials'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
