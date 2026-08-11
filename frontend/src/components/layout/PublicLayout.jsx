import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from '../common/Navbar';
import Footer from '../common/Footer';

export default function PublicLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#020617] text-slate-100 font-sans">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
