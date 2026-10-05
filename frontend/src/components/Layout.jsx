import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

export default function Layout({ children }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="app-layout">
      {/* Sidebar for desktop & mobile overlay */}
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

      {/* Main App Area */}
      <div className="main-wrapper">
        <Navbar onMobileMenuToggle={() => setCollapsed(prev => !prev)} />
        <main className="content-container animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
