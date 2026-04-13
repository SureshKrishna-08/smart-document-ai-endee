import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Activity, LayoutDashboard, FileUp, MessageSquare, History, User, LogOut, ChevronLeft, ChevronRight, Zap } from 'lucide-react';
import ParticleBackground from '../components/ParticleBackground';

export default function Dashboard() {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total: 0, sim: 0, docs: 0 });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Fetch stats
    const fetchStats = async () => {
      const uid = localStorage.getItem('user_id');
      try {
        const res = await fetch(`http://localhost:5000/api/history/${uid}`);
        const data = await res.json();
        setHistory(data);
        const sumSim = data.reduce((acc, curr) => acc + curr.similarity_score, 0);
        setStats({
          total: data.length,
          sim: data.length > 0 ? (sumSim / data.length).toFixed(1) : 0,
          docs: data.length * 2
        });
      } catch (e) {
        console.error("Failed to load history");
      }
    };
    fetchStats();
  }, [activeTab]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const navItems = [
    { id: 'dashboard', icon: <LayoutDashboard />, label: 'Dashboard' },
    { id: 'upload', icon: <FileUp />, label: 'Upload & Compare' },
    { id: 'chat', icon: <MessageSquare />, label: 'Chat with Documents' },
    { id: 'history', icon: <History />, label: 'History' }
  ];

  const StatCard = ({ icon, title, value, color }) => (
    <motion.div whileHover={{ scale: 1.05, boxShadow: `0 0 20px rgba(255,255,255,0.1)` }} className="glass-card p-6 rounded-2xl relative overflow-hidden group">
      <div className={`absolute top-0 right-0 w-32 h-32 bg-${color}-500 opacity-10 rounded-full blur-3xl transform translate-x-10 -translate-y-10 group-hover:opacity-20 transition-all`}></div>
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl bg-opacity-10 backdrop-blur-md`}>
          {React.cloneElement(icon, { className: `w-8 h-8 text-${color}` })}
        </div>
        <div>
          <p className="text-sm text-gray-400 font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-white mt-1">{value}</h3>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="flex h-screen bg-dark text-white overflow-hidden relative">
      {/* Background Particles globally accessible behind the dashboard too */}
      <ParticleBackground />

      {/* Sidebar */}
      <motion.aside 
        animate={{ width: collapsed ? 80 : 280 }}
        className="relative z-20 h-full border-r border-slate-800 glass shadow-2xl flex flex-col justify-between"
      >
        <div>
          <div className="p-6 flex items-center justify-between">
            {!collapsed && <motion.h1 initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xl font-bold gradient-text">SmartDoc AI</motion.h1>}
            <button onClick={() => setCollapsed(!collapsed)} className="text-gray-400 hover:text-white p-2 rounded-lg hover:bg-white/5 transition-colors">
              {collapsed ? <ChevronRight /> : <ChevronLeft />}
            </button>
          </div>

          <nav className="mt-6 px-4 space-y-2">
            {navItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all relative overflow-hidden ${activeTab === item.id ? 'text-white' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
              >
                {activeTab === item.id && (
                  <motion.div layoutId="activeTab" className="absolute inset-0 bg-gradient-to-r from-primary/20 to-transparent border-l-4 border-primary z-0" />
                )}
                <span className="relative z-10">{item.icon}</span>
                {!collapsed && <span className="relative z-10 font-medium">{item.label}</span>}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800">
            <div className="flex items-center gap-3 px-4 py-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-secondary flex items-center justify-center p-[2px]">
                <div className="w-full h-full bg-dark rounded-full flex items-center justify-center">
                  <User size={20} />
                </div>
              </div>
              {!collapsed && (
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-medium truncate">{localStorage.getItem('email') || 'User'}</p>
                </div>
              )}
            </div>
            <button onClick={handleLogout} className="mt-2 w-full flex items-center gap-4 px-4 py-3 rounded-xl text-red-400 hover:bg-red-400/10 transition-colors">
                <LogOut size={20} />
                {!collapsed && <span>Logout</span>}
            </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative z-10 p-8 space-y-8">
        
        {activeTab === 'dashboard' && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            <header>
              <h2 className="text-3xl font-bold">Overview</h2>
              <p className="text-gray-400 mt-1">High-level metrics and recent actions.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <StatCard icon={<Activity />} title="Total Comparisons" value={stats.total} color="primary" />
              <StatCard icon={<Zap />} title="Avg Similarity" value={`${stats.sim}%`} color="secondary" />
              <StatCard icon={<FileUp />} title="Documents Processed" value={stats.docs} color="green-400" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-4">
                <h3 className="text-xl font-bold">Activity Feed</h3>
                <div className="glass-card rounded-2xl p-6">
                  {history.length > 0 ? (
                    <div className="space-y-6">
                      {history.slice(0, 5).map((item, idx) => (
                        <div key={idx} className="flex gap-4 relative">
                          {idx !== history.slice(0, 5).length -1 && <div className="absolute left-[11px] top-8 bottom-[-24px] w-0.5 bg-slate-700"></div>}
                          <div className="w-6 h-6 rounded-full bg-primary/20 border border-primary flex-shrink-0 mt-1"></div>
                          <div>
                            <p className="text-sm text-gray-400">{new Date(item.created_at).toLocaleString()}</p>
                            <p className="font-medium mt-1">Compared <span className="text-primary">{item.doc1_name}</span> vs <span className="text-secondary">{item.doc2_name}</span></p>
                            <p className="text-sm mt-1 text-gray-300">Similarity: {item.similarity_score.toFixed(1)}%</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-400 text-center py-8">No activity recorded yet.</p>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                 <h3 className="text-xl font-bold">Quick Actions</h3>
                 <div className="space-y-4">
                    <button onClick={() => setActiveTab('upload')} className="w-full glass-card hover:bg-white/5 transition-all p-4 rounded-xl flex items-center justify-between group">
                      <span className="font-medium">Upload Document</span>
                      <ChevronRight className="text-gray-500 group-hover:text-primary transition-colors" />
                    </button>
                    <button onClick={() => setActiveTab('chat')} className="w-full glass-card hover:bg-white/5 transition-all p-4 rounded-xl flex items-center justify-between group">
                      <span className="font-medium">Start AI Chat</span>
                      <ChevronRight className="text-gray-500 group-hover:text-primary transition-colors" />
                    </button>
                 </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Placeholders for other tabs for the sake of the structural demo */}
        {activeTab === 'upload' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex h-full items-center justify-center">
            <h2 className="text-2xl text-gray-400">Upload & Compare Module (Implemented backend route waiting for UI)</h2>
          </motion.div>
        )}
        {activeTab === 'chat' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex h-full items-center justify-center">
            <h2 className="text-2xl text-gray-400">RAG Chat Module (Implemented backend route waiting for UI)</h2>
          </motion.div>
        )}
        {activeTab === 'history' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex h-full items-center justify-center">
            <h2 className="text-2xl text-gray-400">Detailed History View</h2>
          </motion.div>
        )}

      </main>
    </div>
  );
}
