import {
  DEMO_USERS,
  MOCK_UPCOMING_INTERVIEWS,
  MOCK_COMPLETED_INTERVIEWS,
  MOCK_ADMIN_STUDENTS,
  MOCK_ADMIN_INTERVIEWERS,
  MOCK_ADMIN_FEEDBACK,
} from './mockData';

const KEYS = {
  USER: 'exam_portal_user',
  TOKEN: 'exam_portal_token',
  UPCOMING: 'exam_portal_upcoming',
  COMPLETED: 'exam_portal_completed',
  STUDENTS: 'exam_portal_students',
  INTERVIEWERS: 'exam_portal_interviewers',
  FEEDBACK: 'exam_portal_feedback',
};

export const initializeStorage = () => {
  if (!localStorage.getItem(KEYS.UPCOMING)) {
    localStorage.setItem(KEYS.UPCOMING, JSON.stringify(MOCK_UPCOMING_INTERVIEWS));
  }
  if (!localStorage.getItem(KEYS.COMPLETED)) {
    localStorage.setItem(KEYS.COMPLETED, JSON.stringify(MOCK_COMPLETED_INTERVIEWS));
  }
  if (!localStorage.getItem(KEYS.STUDENTS)) {
    localStorage.setItem(KEYS.STUDENTS, JSON.stringify(MOCK_ADMIN_STUDENTS));
  }
  if (!localStorage.getItem(KEYS.INTERVIEWERS)) {
    localStorage.setItem(KEYS.INTERVIEWERS, JSON.stringify(MOCK_ADMIN_INTERVIEWERS));
  }
  if (!localStorage.getItem(KEYS.FEEDBACK)) {
    localStorage.setItem(KEYS.FEEDBACK, JSON.stringify(MOCK_ADMIN_FEEDBACK));
  }
};

export const storage = {
  getUser: () => {
    const data = localStorage.getItem(KEYS.USER);
    return data ? JSON.parse(data) : null;
  },

  setUser: (user) => {
    localStorage.setItem(KEYS.USER, JSON.stringify(user));
    localStorage.setItem(KEYS.TOKEN, `token_mock_${user.id}_${Date.now()}`);
  },

  removeUser: () => {
    localStorage.removeItem(KEYS.USER);
    localStorage.removeItem(KEYS.TOKEN);
  },

  getUpcomingInterviews: () => {
    const data = localStorage.getItem(KEYS.UPCOMING);
    return data ? JSON.parse(data) : MOCK_UPCOMING_INTERVIEWS;
  },

  getCompletedInterviews: () => {
    const data = localStorage.getItem(KEYS.COMPLETED);
    return data ? JSON.parse(data) : MOCK_COMPLETED_INTERVIEWS;
  },

  addCompletedInterview: (interviewResult) => {
    const completed = storage.getCompletedInterviews();
    const updated = [interviewResult, ...completed];
    localStorage.setItem(KEYS.COMPLETED, JSON.stringify(updated));

    // Also update upcoming interviews by removing the completed one
    const upcoming = storage.getUpcomingInterviews();
    const filteredUpcoming = upcoming.filter((item) => item.id !== interviewResult.id && item.code !== interviewResult.code);
    localStorage.setItem(KEYS.UPCOMING, JSON.stringify(filteredUpcoming));
    return updated;
  },

  getStudents: () => {
    const data = localStorage.getItem(KEYS.STUDENTS);
    return data ? JSON.parse(data) : MOCK_ADMIN_STUDENTS;
  },

  saveStudents: (students) => {
    localStorage.setItem(KEYS.STUDENTS, JSON.stringify(students));
  },

  getInterviewers: () => {
    const data = localStorage.getItem(KEYS.INTERVIEWERS);
    return data ? JSON.parse(data) : MOCK_ADMIN_INTERVIEWERS;
  },

  saveInterviewers: (interviewers) => {
    localStorage.setItem(KEYS.INTERVIEWERS, JSON.stringify(interviewers));
  },

  getFeedbacks: () => {
    const data = localStorage.getItem(KEYS.FEEDBACK);
    return data ? JSON.parse(data) : MOCK_ADMIN_FEEDBACK;
  },

  addFeedback: (newFeedback) => {
    const feedbacks = storage.getFeedbacks();
    const updated = [newFeedback, ...feedbacks];
    localStorage.setItem(KEYS.FEEDBACK, JSON.stringify(updated));
    return updated;
  },
};
