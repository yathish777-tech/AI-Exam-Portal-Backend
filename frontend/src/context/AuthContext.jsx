import React, { createContext, useContext, useState, useEffect } from 'react';
import { storage, initializeStorage } from '../utils/storage';
import { DEMO_USERS } from '../utils/mockData';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    initializeStorage();
    const currentUser = storage.getUser();
    if (currentUser) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  /**
   * Universal Login Handler
   * Validates credentials according to role
   */
  const login = (emailOrUsername, password, role) => {
    const cleanIdentifier = (emailOrUsername || '').trim().toLowerCase();
    let matchedUser = null;

    if (role === 'admin') {
      // Admin verification
      if (cleanIdentifier === 'admin' || cleanIdentifier === 'admin@examportal.edu') {
        matchedUser = {
          id: 'adm_01',
          name: 'Chief Examination Controller',
          username: 'admin',
          email: 'admin@examportal.edu',
          role: 'admin',
          department: 'Central University Board',
          avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=250',
        };
      } else {
        matchedUser = {
          id: 'adm_' + Date.now(),
          name: emailOrUsername || 'Administrator',
          username: emailOrUsername,
          email: emailOrUsername.includes('@') ? emailOrUsername : `${emailOrUsername}@university.edu`,
          role: 'admin',
          department: 'Central Board of Examinations',
          avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=250',
        };
      }
    } else if (role === 'interviewer') {
      // Check stored interviewers in localStorage to verify activation status
      const savedInterviewers = localStorage.getItem('exam_portal_interviewers_v3');
      let interviewerList = [];
      if (savedInterviewers) {
        try { interviewerList = JSON.parse(savedInterviewers); } catch (e) {}
      }

      const existingRecord = interviewerList.find(
        (i) => (i.email || '').toLowerCase() === cleanIdentifier
      );

      if (existingRecord && existingRecord.status === 'Pending Activation') {
        throw new Error('This interviewer account is pending activation. Please use your invitation code/OTP to activate your account.');
      }

      if (existingRecord) {
        matchedUser = {
          id: existingRecord.id,
          name: existingRecord.name,
          email: existingRecord.email,
          role: 'interviewer',
          domain: existingRecord.domain || 'Computer Science & Engineering',
          department: existingRecord.organization || 'Department of CSE',
          experience: existingRecord.experience || '5+ Years',
          avatar: existingRecord.avatar || 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=250',
        };
      } else if (cleanIdentifier === 'interviewer@examportal.edu' || cleanIdentifier === 'harish.k@university.edu') {
        matchedUser = {
          id: 'int_01',
          name: 'Dr. Harish Kumar',
          email: cleanIdentifier,
          role: 'interviewer',
          domain: 'Artificial Intelligence & Data Science',
          department: 'Department of Computer Science',
          experience: '8 Years',
          avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=250',
        };
      } else {
        // Custom signed in interviewer
        const derivedName = cleanIdentifier.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
        matchedUser = {
          id: 'int_' + Date.now(),
          name: derivedName.charAt(0).toUpperCase() + derivedName.slice(1) || 'Faculty Examiner',
          email: cleanIdentifier,
          role: 'interviewer',
          domain: 'Computer Science',
          department: 'University Faculty of Engineering',
          experience: '5 Years',
          avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=250',
        };
      }
    } else {
      // Student role
      if (cleanIdentifier === 'student@examportal.edu' || cleanIdentifier === 'aarav.s@university.edu') {
        matchedUser = {
          id: 'std_01',
          name: 'Aarav Sharma',
          email: cleanIdentifier,
          role: 'student',
          rollNo: '2026-CS-042',
          department: 'Computer Science & Engineering',
          avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=250',
        };
      } else {
        const derivedName = cleanIdentifier.split('@')[0].replace(/[^a-zA-Z]/g, ' ');
        matchedUser = {
          id: 'std_' + Date.now(),
          name: derivedName.charAt(0).toUpperCase() + derivedName.slice(1) || 'Student Candidate',
          email: cleanIdentifier,
          role: 'student',
          rollNo: `2026-CS-${Math.floor(100 + Math.random() * 900)}`,
          department: 'School of Computing Sciences',
          avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=250',
        };
      }
    }

    setUser(matchedUser);
    storage.setUser(matchedUser);
    return matchedUser;
  };

  /**
   * Student Self Registration
   */
  const register = (data) => {
    const newUser = {
      id: `std_${Date.now()}`,
      name: data.name,
      email: (data.email || '').trim().toLowerCase(),
      role: 'student',
      rollNo: data.rollNo || `2026-CS-${Math.floor(100 + Math.random() * 900)}`,
      department: data.department || 'Computer Science & Engineering',
      avatar: 'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=250',
    };

    setUser(newUser);
    storage.setUser(newUser);
    return newUser;
  };

  const logout = () => {
    setUser(null);
    storage.removeUser();
    localStorage.removeItem('exam_portal_token');
  };

  const updateProfile = (updatedFields) => {
    if (!user) return;
    const updated = { ...user, ...updatedFields };
    setUser(updated);
    storage.setUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role: user?.role || null,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
