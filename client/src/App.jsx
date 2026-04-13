import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  const isAuthenticated = !!localStorage.getItem('user_id');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard/*" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
