import React, { useState } from 'react';
import { 
  Scale, 
  ShieldCheck, 
  UserPlus, 
  Search, 
  Lock, 
  FileCheck2, 
  ExternalLink,
  BookOpen
} from 'lucide-react';
import LawyerRegistration from './components/LawyerRegistration';
import AdminVerificationPortal from './components/AdminVerificationPortal';
import LawyerDirectory from './components/LawyerDirectory';
import LawyerProfileModal from './components/LawyerProfileModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('directory'); // 'directory', 'register', 'admin'
  const [selectedLawyer, setSelectedLawyer] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleStatusChanged = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-100/70 text-slate-900 font-sans flex flex-col">
      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-slate-900 text-white shadow-lg border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center text-white shadow-md">
              <Scale size={22} className="stroke-[2.2]" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-white flex items-center gap-1.5">
                Law<span className="text-amber-400">Aid</span>
              </span>
              <span className="text-[10px] text-slate-400 block -mt-1 font-medium tracking-wide">
                Judicial Intelligence & Lawyer Verification
              </span>
            </div>
          </div>

          {/* Module Navigation Tabs */}
          <nav className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={() => setActiveTab('directory')}
              className={`px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'directory' 
                  ? 'bg-amber-500 text-slate-950 shadow-md font-bold' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Search size={15} />
              <span className="hidden sm:inline">Lawyer</span> Directory (FR-3)
            </button>

            <button
              onClick={() => setActiveTab('register')}
              className={`px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'register' 
                  ? 'bg-amber-500 text-slate-950 shadow-md font-bold' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <UserPlus size={15} />
              <span className="hidden sm:inline">Lawyer</span> Upload & Register (FR-2)
            </button>

            <button
              onClick={() => setActiveTab('admin')}
              className={`px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition flex items-center gap-1.5 ${
                activeTab === 'admin' 
                  ? 'bg-amber-500 text-slate-950 shadow-md font-bold' 
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <ShieldCheck size={15} />
              Admin <span className="hidden sm:inline">Verification</span> (FR-38, NFR-4)
            </button>
          </nav>
        </div>
      </header>

      {/* Quick SRS Feature Guide Bar */}
      <aside aria-label="SRS Assignment Guide" className="bg-slate-900/95 text-slate-300 border-b border-slate-800 text-[11px] py-2 px-4">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <span className="font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1">
              <BookOpen size={13} />
              SRS Assignment Guide:
            </span>
            <span className="text-slate-300">
              <strong className="text-white">Task 1 (FR-2, NFR-4):</strong> Lawyer NID & Bar Sanad encrypted upload & admin-only view.
            </span>
            <span className="hidden md:inline text-slate-600">|</span>
            <span className="hidden md:inline text-slate-300">
              <strong className="text-white">Task 2 (FR-3):</strong> Verification status, badge logic, and search visibility filter.
            </span>
          </div>

          <span className="inline-flex items-center gap-1 text-slate-400">
            <Lock size={12} className="text-emerald-400" />
            Backend: DRF & AES-128 Encryption | Frontend: React
          </span>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 px-4 sm:px-6 lg:px-8 py-4">
        {activeTab === 'directory' && (
          <LawyerDirectory 
            key={refreshTrigger}
            onSelectLawyer={(lawyer) => setSelectedLawyer(lawyer)}
          />
        )}

        {activeTab === 'register' && (
          <LawyerRegistration 
            onRegistrationSuccess={() => {
              handleStatusChanged();
              // Option to redirect to admin to review
            }}
          />
        )}

        {activeTab === 'admin' && (
          <AdminVerificationPortal 
            onStatusChanged={handleStatusChanged}
          />
        )}
      </main>

      {/* Lawyer Profile Modal */}
      {selectedLawyer && (
        <LawyerProfileModal 
          lawyer={selectedLawyer}
          onClose={() => setSelectedLawyer(null)}
        />
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <p className="font-semibold text-slate-700">LawAid — AI-Powered Legal Assistant & Law Management System</p>
        <p className="mt-1">
          Developed for Software Engineering Lab | Team SysVision
        </p>
      </footer>
    </div>
  );
}
