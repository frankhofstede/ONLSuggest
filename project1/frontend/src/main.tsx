import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { App } from './App'
import { AdminDashboard } from './pages/AdminDashboard'
import { AdminGemeentes } from './pages/AdminGemeentes'
import { AdminServices } from './pages/AdminServices'
import { AdminAssociations } from './pages/AdminAssociations'
import { AdminSettings } from './pages/AdminSettings'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/gemeentes" element={<AdminGemeentes />} />
        <Route path="/admin/services" element={<AdminServices />} />
        <Route path="/admin/associations" element={<AdminAssociations />} />
        <Route path="/admin/settings" element={<AdminSettings />} />
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
