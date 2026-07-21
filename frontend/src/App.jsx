import {
  useEffect,
  useState,
} from "react";

import AuthPage from "./components/AuthPage";
import Dashboard from "./components/Dashboard";

import {
  clearAuthentication,
  getAccessToken,
  getCurrentUser,
  getStoredUser,
} from "./services/api";

import "./App.css";

function App() {
  const [user, setUser] = useState(
    getStoredUser()
  );

  const [
    checkingSession,
    setCheckingSession,
  ] = useState(
    Boolean(getAccessToken())
  );

  useEffect(() => {
    const restoreSession = async () => {
      const accessToken =
        getAccessToken();

      if (!accessToken) {
        setUser(null);
        setCheckingSession(false);
        return;
      }

      try {
        const currentUser =
          await getCurrentUser();

        setUser(currentUser);
      } catch {
        clearAuthentication();
        setUser(null);
      } finally {
        setCheckingSession(false);
      }
    };

    restoreSession();
  }, []);

  useEffect(() => {
    const handleAuthenticationExpired =
      () => {
        clearAuthentication();
        setUser(null);
        setCheckingSession(false);
      };

    window.addEventListener(
      "authentication-expired",
      handleAuthenticationExpired
    );

    return () => {
      window.removeEventListener(
        "authentication-expired",
        handleAuthenticationExpired
      );
    };
  }, []);

  const handleAuthenticated = (
    authenticatedUser
  ) => {
    setUser(authenticatedUser);
  };

  const handleLogout = () => {
    clearAuthentication();
    setUser(null);
  };

  if (checkingSession) {
    return (
      <main className="session-loading-page">
        <div className="session-loader">
          <div className="session-loader-logo">
            AI
          </div>

          <h1>
            Enterprise AI Assistant
          </h1>

          <p>
            Restoring your secure session...
          </p>

          <div className="session-spinner" />
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <AuthPage
        onAuthenticated={
          handleAuthenticated
        }
      />
    );
  }

  return (
    <Dashboard
      user={user}
      onLogout={handleLogout}
    />
  );
}

export default App;