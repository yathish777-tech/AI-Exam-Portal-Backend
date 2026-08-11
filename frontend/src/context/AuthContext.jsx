import React, { createContext, useContext, useState, useEffect } from 'react';
import { storage, initializeStorage } from '../utils/storage';
import { DEMO_USERS } from '../utils/mockData';
import { authService } from '../services/api';

const AuthContext = createContext(null);

const backendToFrontendRole = (role) => {
  const normalized = String(role || '').toUpperCase();
  if (normalized === 'CANDIDATE') return 'student';
  if (normalized === 'INTERVIEWER') return 'interviewer';
  if (normalized === 'ADMIN') return 'admin';
  return 'student';
};

const toFrontendUser = (backendUser) => ({
  id: backendUser.id,
  email: backendUser.email,
  name: backendUser.email?.split('@')[0] || 'User',
  role: backendToFrontendRole(backendUser.role),
  isActive: backendUser.is_active,
  lastLoginAt: backendUser.last_login_at,
  avatar: DEMO_USERS[backendToFrontendRole(backendUser.role)]?.avatar,
});

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

  const login = async (emailOrUsername, password, role) => {
    const response = await authService.login(
      { email: emailOrUsername, password },
      role
    );
    const loggedInUser = toFrontendUser(response.user);

    if (role && loggedInUser.role !== role) {
      await authService.logout().catch(() => {});
      storage.removeUser();
      throw new Error(`This account belongs to the ${loggedInUser.role} portal.`);
    }

    setUser(loggedInUser);
    storage.setUser(loggedInUser, response.data?.access_token);
    return loggedInUser;
  };

  const register = async (data, role) => {
    if (role !== 'student') {
      throw new Error('Only student self-registration is available. Interviewer accounts must be created by an admin.');
    }

    await authService.register(data, role);
    const response = await authService.login(
      { email: data.email, password: data.password },
      role
    );
    const newUser = {
      ...toFrontendUser(response.user),
      name: data.name,
      domain: data.domain || 'Computer Science',
    };

    setUser(newUser);
    storage.setUser(newUser, response.data?.access_token);
    return newUser;
  };

  const switchRoleDemo = (roleKey) => {
    if (DEMO_USERS[roleKey]) {
      const demoUser = DEMO_USERS[roleKey];
      setUser(demoUser);
      storage.setUser(demoUser);
      return demoUser;
    }
  };

  const logout = async () => {
    await authService.logout().catch(() => {});
    setUser(null);
    storage.removeUser();
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
        role: user?.role || 'student',
        loading,
        login,
        register,
        logout,
        switchRoleDemo,
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
