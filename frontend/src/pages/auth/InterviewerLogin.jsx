import React from 'react';
import LoginForm from '../../components/forms/LoginForm';

export default function InterviewerLogin() {
  return (
    <div className="min-h-screen py-12 px-4 flex items-center justify-center bg-[#F5F5F5]">
      <LoginForm initialRole="interviewer" />
    </div>
  );
}

