export type UserRole = 'teacher' | 'student' | 'admin';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Artifact {
  id: number;
  section_id: number;
  artifact_type: 'script' | 'main_video' | 'summary_video' | 'notes_pdf' | 'notes_docx' | 'quiz';
  status: 'pending' | 'processing' | 'completed' | 'failed';
  file_path?: string;
  error_details?: string;
  updated_at: string;
}

export interface Section {
  id: number;
  course_id: number;
  title: string;
  order_num: number;
  content: string;
  objectives: string[];
  summary?: string;
  video_url?: string;
  summary_video_url?: string;
  is_published: boolean;
  artifacts: Artifact[];
  is_completed?: boolean;
  is_unlocked?: boolean;
  created_at: string;
  updated_at: string;
}

export interface Course {
  id: number;
  title: string;
  description?: string;
  subject: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  teacher_id: number;
  teacher_name?: string;
  is_published: boolean;
  passing_threshold: number;
  max_quiz_attempts: number;
  sections_count: number;
  enrolled_count: number;
  created_at: string;
  updated_at: string;
  sections?: Section[];
  is_enrolled?: boolean;
  student_progress?: number;
}

export interface QuizQuestion {
  id: number;
  section_id: number;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'fill_blank' | 'short_answer';
  options: string[];
  correct_answer?: string;
  explanation?: string;
  associated_concept: string;
}

export interface QuizEvaluation {
  question_id: number;
  question_text: string;
  submitted_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
  associated_concept: string;
}

export interface QuizSubmitResult {
  attempt_id: number;
  attempt_num: number;
  attempts_remaining: number;
  score: number;
  total_questions: number;
  correct_count: number;
  passed: boolean;
  passing_threshold: number;
  weak_concepts: string[];
  strong_concepts: string[];
  feedback_plan?: string;
  evaluations: QuizEvaluation[];
}

export interface QuizAttempt {
  id: number;
  student_id: number;
  section_id: number;
  attempt_num: number;
  submitted_answers: Record<string, string>;
  score: number;
  total_questions: number;
  correct_count: number;
  passed: boolean;
  weak_concepts: string[];
  strong_concepts: string[];
  feedback_plan?: string;
  completed_at: string;
}

export interface ChatMessage {
  id: number;
  role: 'user' | 'assistant';
  message_content: string;
  sources_cited?: string;
  timestamp: string;
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  link?: string;
  is_read: boolean;
  created_at: string;
}

export interface CertificateItem {
  id: number;
  certificate_uid: string;
  course_id: number;
  course_title: string;
  student_name: string;
  completion_date: string;
  download_url: string;
}
