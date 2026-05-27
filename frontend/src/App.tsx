import React from "react";
import { AppProvider } from "@/context/AppContext";
import { Dashboard } from "@/components/Dashboard";
import "@/styles/global.css";

export const App: React.FC = () => {
  return (
    <AppProvider>
      <Dashboard />
    </AppProvider>
  );
};
