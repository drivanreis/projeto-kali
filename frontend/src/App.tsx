import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AppProvider } from "@/context/AppContext";
import { Dashboard } from "@/components/Dashboard";
import { PaginaAuditoriaPublica } from "@/components/PaginaAuditoriaPublica";
import "@/styles/global.css";

export const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/audit/:clienteSlug" element={<PaginaAuditoriaPublica />} />
        <Route
          path="*"
          element={
            <AppProvider>
              <Dashboard />
            </AppProvider>
          }
        />
      </Routes>
    </Router>
  );
};
