const API_BASE = '/api';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('eduai_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse<T = any>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = 'An unexpected error occurred';
    try {
      const errData = await res.json();
      errorMsg = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errorMsg = res.statusText || `HTTP ${res.status}`;
    }
    throw new Error(errorMsg);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // --- Info ---
  getInfo: () => fetch(`${API_BASE}/info`).then(handleResponse),

  // --- Auth ---
  login: (data: any) =>
    fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(handleResponse),

  register: (data: any) =>
    fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }).then(handleResponse),

  getMe: () =>
    fetch(`${API_BASE}/auth/me`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  // --- Courses ---
  getCourses: (params?: { search?: string; subject?: string; difficulty?: string; mine_only?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.subject) query.append('subject', params.subject);
    if (params?.difficulty) query.append('difficulty', params.difficulty);
    if (params?.mine_only) query.append('mine_only', 'true');
    return fetch(`${API_BASE}/courses?${query.toString()}`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse);
  },

  getCourse: (courseId: number) =>
    fetch(`${API_BASE}/courses/${courseId}`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  createCourse: (data: any) =>
    fetch(`${API_BASE}/courses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  generateCourse: (data: any) =>
    fetch(`${API_BASE}/courses/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  updateCourse: (courseId: number, data: any) =>
    fetch(`${API_BASE}/courses/${courseId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  deleteCourse: (courseId: number) =>
    fetch(`${API_BASE}/courses/${courseId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  publishCourse: (courseId: number) =>
    fetch(`${API_BASE}/courses/${courseId}/publish`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  // --- Sections & Artifacts ---
  getSection: (sectionId: number) =>
    fetch(`${API_BASE}/sections/${sectionId}`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  updateSection: (sectionId: number, data: any) =>
    fetch(`${API_BASE}/sections/${sectionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  regenerateArtifacts: (sectionId: number, artifactType = 'all') =>
    fetch(`${API_BASE}/sections/${sectionId}/generate?artifact_type=${artifactType}`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getNotesPdfUrl: (sectionId: number) => `${API_BASE}/sections/${sectionId}/notes/pdf`,
  getNotesDocxUrl: (sectionId: number) => `${API_BASE}/sections/${sectionId}/notes/docx`,

  getSectionQuizQuestions: (sectionId: number) =>
    fetch(`${API_BASE}/sections/${sectionId}/quiz`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  updateSectionProgress: (sectionId: number, data: { is_completed?: boolean; video_progress?: number }) =>
    fetch(`${API_BASE}/sections/${sectionId}/progress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  // --- Ask Anything AI Chat ---
  sendSectionChat: (sectionId: number, message: string) =>
    fetch(`${API_BASE}/sections/${sectionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({ message }),
    }).then(handleResponse),

  getSectionChatHistory: (sectionId: number) =>
    fetch(`${API_BASE}/sections/${sectionId}/chat`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  // --- Quizzes ---
  submitQuiz: (sectionId: number, answers: Record<string, string>) =>
    fetch(`${API_BASE}/quizzes/${sectionId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify({ answers }),
    }).then(handleResponse),

  getQuizAttempts: (sectionId: number) =>
    fetch(`${API_BASE}/quizzes/${sectionId}/attempts`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  updateQuizQuestions: (sectionId: number, questions: any[]) =>
    fetch(`${API_BASE}/quizzes/${sectionId}/questions`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(questions),
    }).then(handleResponse),

  // --- Student ---
  enrollInCourse: (courseId: number) =>
    fetch(`${API_BASE}/student/enroll/${courseId}`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getStudentEnrolledCourses: () =>
    fetch(`${API_BASE}/student/courses`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getStudentDashboard: () =>
    fetch(`${API_BASE}/student/dashboard`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  // --- Admin ---
  getAdminOverview: () =>
    fetch(`${API_BASE}/admin/overview`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getAdminUsers: (params?: { search?: string; role?: string; is_active?: boolean }) => {
    const query = new URLSearchParams();
    if (params?.search) query.append('search', params.search);
    if (params?.role) query.append('role', params.role);
    if (params?.is_active !== undefined) query.append('is_active', String(params.is_active));
    return fetch(`${API_BASE}/admin/users?${query.toString()}`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse);
  },

  updateAdminUser: (userId: number, data: any) =>
    fetch(`${API_BASE}/admin/users/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', ...getAuthHeader() },
      body: JSON.stringify(data),
    }).then(handleResponse),

  // --- Analytics ---
  getTeacherAnalytics: () =>
    fetch(`${API_BASE}/analytics/teacher`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getStudentAnalytics: () =>
    fetch(`${API_BASE}/analytics/student`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getExportCsvUrl: () => `${API_BASE}/analytics/export/csv`,

  // --- Notifications ---
  getNotifications: () =>
    fetch(`${API_BASE}/notifications`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  markNotificationRead: (id: number) =>
    fetch(`${API_BASE}/notifications/${id}/read`, {
      method: 'PATCH',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  markAllNotificationsRead: () =>
    fetch(`${API_BASE}/notifications/read-all`, {
      method: 'POST',
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  // --- Certificates ---
  getCertificates: () =>
    fetch(`${API_BASE}/certificates`, {
      headers: { ...getAuthHeader() },
    }).then(handleResponse),

  getCertificateDownloadUrl: (id: number) => `${API_BASE}/certificates/${id}/download`,
};
