import api from './api';

/**
 * University Administrator Service
 */
export const adminService = {
  /**
   * Fetch University Dashboard Analytics & Counts
   * BACKEND REQUIRED: GET /admin/analytics/overview
   */
  getDashboardStats: async () => {
    try {
      // const response = await api.get('/admin/analytics/overview');
      // return response.data;
      return null;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch Students List
   * BACKEND REQUIRED: GET /admin/students
   */
  getStudents: async () => {
    try {
      // const response = await api.get('/admin/students');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch Interviewers List
   * BACKEND REQUIRED: GET /admin/interviewers
   */
  getInterviewers: async () => {
    try {
      // const response = await api.get('/admin/interviewers');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create Interviewer Account and Dispatch Invitation / OTP
   * Note: Admin does NOT assign a password. The backend generates a secure invitation token/OTP.
   * BACKEND REQUIRED: POST /admin/interviewers/invite { name, email, domain, organization }
   * DATABASE REQUIRED: insert into 'users' table with role='interviewer', status='pending_activation', invitation_token, invitation_otp
   */
  createInterviewerInvitation: async ({ name, email, domain, organization }) => {
    try {
      // const response = await api.post('/admin/interviewers/invite', { name, email, domain, organization });
      // return response.data;
      const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
      return {
        success: true,
        message: `Invitation successfully dispatched to ${email}`,
        invitationToken: `inv_${Date.now()}`,
        otp: generatedOtp, // Included for local workflow testing
      };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update Interviewer Status (Active, On Hold, Inactive)
   * BACKEND REQUIRED: PATCH /admin/interviewers/:id/status
   */
  updateInterviewerStatus: async (id, status) => {
    try {
      // const response = await api.patch(`/admin/interviewers/${id}/status`, { status });
      // return response.data;
      return { success: true };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete Interviewer Account
   * BACKEND REQUIRED: DELETE /admin/interviewers/:id
   */
  deleteInterviewer: async (id) => {
    try {
      // const response = await api.delete(`/admin/interviewers/${id}`);
      // return response.data;
      return { success: true };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch System Warning Logs
   * BACKEND REQUIRED: GET /admin/warnings/logs
   * DATABASE REQUIRED: query from 'proctoring_logs' table
   */
  getWarningLogs: async () => {
    try {
      // const response = await api.get('/admin/warnings/logs');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch University System Audit Logs
   * BACKEND REQUIRED: GET /admin/audit-logs
   */
  getActivityLogs: async () => {
    try {
      // const response = await api.get('/admin/audit-logs');
      // return response.data;
      return [];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Fetch and Update University Proctoring Settings
   * BACKEND REQUIRED: GET /admin/settings, PUT /admin/settings
   * DATABASE REQUIRED: table 'system_settings' (strictness, maxWarnings, examDuration, fullscreenLock)
   */
  getSettings: async () => {
    try {
      // const response = await api.get('/admin/settings');
      // return response.data;
      return null;
    } catch (error) {
      throw error;
    }
  },

  updateSettings: async (settingsData) => {
    try {
      // const response = await api.put('/admin/settings', settingsData);
      // return response.data;
      return { success: true };
    } catch (error) {
      throw error;
    }
  },
};

export default adminService;
