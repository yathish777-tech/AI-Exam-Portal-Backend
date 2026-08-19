import api from './api';

/**
 * Student Examination Service
 */
export const studentService = {
  /**
   * Fetch Upcoming Scheduled Exams
   * BACKEND REQUIRED: GET /student/exams/upcoming
   */
  getUpcomingExams: async () => {
    try {
      // const response = await api.get('/student/exams/upcoming');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch Completed Exams & Evaluated Submissions
   * BACKEND REQUIRED: GET /student/exams/completed
   */
  getCompletedExams: async () => {
    try {
      // const response = await api.get('/student/exams/completed');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch Specific Exam Evaluation & Detailed Scorecard
   * BACKEND REQUIRED: GET /student/exams/results/:resultId
   */
  getExamResult: async (resultId) => {
    try {
      // const response = await api.get(`/student/exams/results/${resultId}`);
      // return response.data;
      return null;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Submit Final Exam Answers and Proctoring Telemetry
   * BACKEND REQUIRED: POST /student/exams/:examId/submit
   * DATABASE REQUIRED: updates 'submissions' table with answers, final score, violation summary
   */
  submitExam: async (examId, submissionPayload) => {
    try {
      // const response = await api.post(`/student/exams/${examId}/submit`, submissionPayload);
      // return response.data;
      return { success: true, examId, timestamp: new Date().toISOString() };
    } catch (error) {
      throw error;
    }
  },
};

export default studentService;
