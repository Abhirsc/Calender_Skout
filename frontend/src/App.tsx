import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { PasswordGate } from "./components/PasswordGate";
import { fetchAuthStatus, loginWithPassword, logoutFromApp } from "./lib/api";
import { CalendarPage } from "./pages/CalendarPage";
import { SavedPage } from "./pages/SavedPage";
import { SettingsPage } from "./pages/SettingsPage";
import { SourcesPage } from "./pages/SourcesPage";

function App() {
  const [authEnabled, setAuthEnabled] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    void fetchAuthStatus()
      .then((status) => {
        setAuthEnabled(status.enabled);
        setAuthenticated(status.authenticated);
      })
      .finally(() => setLoading(false));
  }, []);

  async function handleUnlock(password: string) {
    try {
      const status = await loginWithPassword(password);
      setAuthEnabled(status.enabled);
      setAuthenticated(status.authenticated);
      return status.authenticated;
    } catch {
      setAuthenticated(false);
      return false;
    }
  }

  async function handleLogout() {
    const status = await logoutFromApp();
    setAuthEnabled(status.enabled);
    setAuthenticated(status.authenticated);
  }

  if (loading) {
    return <main className="gate-shell"><section className="panel gate-card"><p className="muted">Loading…</p></section></main>;
  }

  if (authEnabled && !authenticated) {
    return <PasswordGate onUnlock={handleUnlock} />;
  }

  return (
    <Routes>
      <Route path="/" element={<AppShell onLogout={authEnabled ? handleLogout : undefined} />}>
        <Route index element={<CalendarPage />} />
        <Route path="saved" element={<SavedPage />} />
        <Route path="sources" element={<SourcesPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
