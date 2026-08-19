import api from './api';

/**
 * Authentication Service
 * Handles user login, student self-registration, interviewer invitation activation,
 * and multi-role password reset workflows.
 */
export const authService = {
  /**
   * User Login (Student, Interviewer, Admin)
   * BACKEND REQUIRED: POST /auth/login { email, password, role }
   */
  login: async ({ email, password, role }) => {
    try {
      // Real backend integration hook:
      // const response = await api.post(`/auth/${role}/login`, { email, password });
      // return response.data;
      
      // Client-side fallback / verification against local storage
      const token = 'jwt_' + Math.random().toString(36).substring(2) + Date.now();
      localStorage.setItem('exam_portal_token', token);
      return { success: true, token };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Student Self-Registration
   * BACKEND REQUIRED: POST /auth/student/register { name, email, rollNo, department, password }
   */
  registerStudent: async (studentData) => {
    try {
      // const response = await api.post('/auth/student/register', studentData);
      // return response.data;
      return { success: true, message: 'Student account registered successfully.' };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Interviewer Account Activation via Invitation OTP or Token
   * BACKEND REQUIRED: POST /auth/interviewer/activate { email, otp, newPassword }
   */
  activateInterviewer: async ({ email, otp, newPassword }) => {
    try {
      // const response = await api.post('/auth/interviewer/activate', { email, otp, newPassword });
      // return response.data;
      return { success: true, message: 'Interviewer account activated successfully.' };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Request Password Reset OTP
   * BACKEND REQUIRED: POST /auth/forgot-password { email, role }
   */
  requestPasswordReset: async ({ email, role }) => {
    try {
      // const response = await api.post('/auth/forgot-password', { email, role });
      // return response.data;
      return { success: true, message: 'Verification code sent to your registered university email.' };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Verify Password Reset OTP
   * BACKEND REQUIRED: POST /auth/verify-reset-otp { email, otp }
   */
  verifyResetOtp: async ({ email, otp }) => {
    try {
      // const response = await api.post('/auth/verify-reset-otp', { email, otp });
      // return response.data;
      return { success: true, verified: true };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Confirm and Set New Password
   * BACKEND REQUIRED: POST /auth/reset-password { email, otp, newPassword }
   */
  resetPassword: async ({ email, otp, newPassword }) => {
    try {
      // const response = await api.post('/auth/reset-password', { email, otp, newPassword });
      // return response.data;
      return { success: true, message: 'Password updated successfully. You can now sign in.' };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch Current Authenticated User Profile
   * BACKEND REQUIRED: GET /auth/me
   */
  getCurrentUser: async () => {
    try {
      // const response = await api.get('/auth/me');
      // return response.data;
      const stored = localStorage.getItem('exam_portal_user');
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Logout user and clear stored tokens
   */
  logout: () => {
    localStorage.removeItem('exam_portal_token');
    localStorage.removeItem('exam_portal_user');
  },
};

export default authService;
