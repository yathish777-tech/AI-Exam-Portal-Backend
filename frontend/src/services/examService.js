import api from './api';

/**
 * AI Proctoring & Exam Session Service
 */
export const examService = {
  /**
   * Fetch Exam Details and Questions
   * BACKEND REQUIRED: GET /exams/:examId
   */
  getExamById: async (examId) => {
    try {
      // const response = await api.get(`/exams/${examId}`);
      // return response.data;
      return null;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Log Proctoring Event / Suspicious Activity Flag
   * BACKEND REQUIRED: POST /proctoring/log
   * AI TEAM REQUIRED: Signal event types: 'FACE_NOT_FOUND', 'MULTIPLE_FACES', 'LOOKING_AWAY', 'VOICE_DETECTED', 'TAB_SWITCH', 'FULLSCREEN_EXIT'
   * DATABASE REQUIRED: table 'proctoring_violations' (exam_id, student_id, violation_type, timestamp, snapshot_url)
   */
  logViolation: async ({ examId, studentId, violationType, details, timestamp }) => {
    try {
      // const response = await api.post('/proctoring/log', {
      //   examId,
      //   studentId,
      //   violationType,
      //   details,
      //   timestamp: timestamp || new Date().toISOString(),
      // });
      // return response.data;
      console.warn(`[Proctoring Violation Logged] ${violationType} in Exam ${examId}: ${details}`);
      return { success: true, logged: true };
    } catch (error) {
      console.error('Failed to log proctoring violation to backend:', error);
      return { success: false };
    }
  },
};

export default examService;
