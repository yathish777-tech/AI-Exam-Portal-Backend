import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ allowedRole }) {
  const { user, role, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600 text-xs font-semibold">
        Verifying Examination Credentials...
      </div>
    );
  }

  if (!user) {
    return <Navigate to={`/${allowedRole || 'student'}/login`} replace />;
  }

  if (allowedRole && role !== allowedRole) {
    return <Navigate to={`/${role}/dashboard`} replace />;
  }

  return <Outlet />;
}
