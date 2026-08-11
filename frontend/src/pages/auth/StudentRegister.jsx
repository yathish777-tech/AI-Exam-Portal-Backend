import React from 'react';
import RegisterForm from '../../components/forms/RegisterForm';

export default function StudentRegister() {
  return (
    <div className="min-h-screen py-12 px-4 flex items-center justify-center bg-[#F5F5F5]">
      <RegisterForm role="student" />
    </div>
  );
}

