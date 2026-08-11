import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../common/Sidebar';
import Header from '../common/Header';

export default function AdminLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#F5F5F5] flex text-slate-800 font-sans">
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />
      <div className="flex-1 lg:pl-64 flex flex-col min-w-0">
        <Header title="Admin Control Center" subtitle="System-wide performance monitoring, user governance & exam analytics" setMobileOpen={setMobileOpen} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

