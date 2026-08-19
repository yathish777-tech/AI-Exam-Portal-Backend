import api from './api';

/**
 * Real-time Notifications Service
 */
export const notificationService = {
  /**
   * Fetch User Notifications
   * BACKEND REQUIRED: GET /notifications
   */
  getNotifications: async () => {
    try {
      // const response = await api.get('/notifications');
      // return response.data;
      return [
        { id: 1, title: 'AI Proctor Active', desc: 'Secure lockdown browser checks passed.', time: 'Just now', read: false },
        { id: 2, title: 'Exam Scheduled', desc: 'Data Structures test assigned.', time: '1 hr ago', read: false },
      ];
    } catch (error) {
      throw error;
    }
  },

  /**
   * Mark Notification as Read
   * BACKEND REQUIRED: PATCH /notifications/:id/read
   */
  markAsRead: async (id) => {
    try {
      // const response = await api.patch(`/notifications/${id}/read`);
      // return response.data;
      return { success: true };
    } catch (error) {
      throw error;
    }
  },
};

export default notificationService;
