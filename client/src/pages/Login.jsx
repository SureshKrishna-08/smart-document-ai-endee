import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, BrainCircuit } from 'lucide-react';
import ParticleBackground from '../components/ParticleBackground';

const TypeWriter = ({ text }) => {
  const [displayedText, setDisplayedText] = useState("");
  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + text.charAt(index));
      index++;
      if (index >= text.length) clearInterval(interval);
    }, 70);
    return () => clearInterval(interval);
  }, [text]);
  return <span>{displayedText}</span>;
};

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    const endpoint = isLogin ? '/api/login' : '/api/register';
    try {
      const res = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (res.ok) {
        if (isLogin) {
          localStorage.setItem('user_id', data.user_id);
          localStorage.setItem('email', data.email);
          navigate('/dashboard');
        } else {
          setIsLogin(true);
          setError('Registration successful. Please login.');
        }
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Cannot connect to server.');
    }
    setLoading(false);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-dark">
      <ParticleBackground />
      
      <div className="relative z-10 w-full max-w-md p-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="glass rounded-2xl p-8 backdrop-blur-xl relative overflow-hidden"
        >
          {/* Decorative glowing orb top right */}
          <div className="absolute -top-20 -right-20 w-40 h-40 bg-primary opacity-20 rounded-full blur-3xl mix-blend-screen"></div>
          
          <div className="flex justify-center mb-6">
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 20, repeat: Infinity, ease: "linear" }}>
              <BrainCircuit className="w-12 h-12 text-primary" />
            </motion.div>
          </div>

          <h2 className="text-3xl font-bold text-center mb-2 text-white">
            <TypeWriter text="Welcome to SmartDoc AI" />
            <span className="animate-pulse ml-1 text-primary">|</span>
          </h2>
          <p className="text-center text-sm text-gray-400 mb-8">
            Analyze. Compare. Understand Documents with AI.
          </p>

          {error && <div className="mb-4 text-red-400 text-sm font-medium text-center">{error}</div>}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="relative group">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
              <input
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Email Address"
                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-inner"
              />
            </div>
            
            <div className="relative group">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-primary transition-colors" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full bg-slate-900/50 border border-slate-700 rounded-xl py-3 pl-10 pr-10 text-white focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-inner"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            <motion.button
              whileHover={{ scale: 1.02, boxShadow: '0 0 20px rgba(79, 172, 254, 0.5)' }}
              whileTap={{ scale: 0.98 }}
              disabled={loading}
              className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-primary to-secondary text-white font-bold text-lg shadow-lg hover:shadow-primary/50 transition-all duration-300 relative overflow-hidden"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
                  Processing...
                </span>
              ) : (
                isLogin ? 'Initialize Uplink' : 'Create Access Node'
              )}
            </motion.button>
          </form>

          <div className="mt-6 text-center">
            <button onClick={() => setIsLogin(!isLogin)} className="text-gray-400 text-sm hover:text-white transition-colors">
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Log in"}
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
