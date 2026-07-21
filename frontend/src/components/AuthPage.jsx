import { useState } from "react";

import {
  loginUser,
  registerUser,
} from "../services/api";

import "./AuthPage.css";

function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState("login");

  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] = useState("");

  const isRegisterMode =
    mode === "register";

  const updateField = (event) => {
    const { name, value } = event.target;

    setFormData((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));

    setError("");
  };

  const switchMode = () => {
    setMode((currentMode) =>
      currentMode === "login"
        ? "register"
        : "login"
    );

    setError("");

    setFormData({
      fullName: "",
      email: "",
      password: "",
      confirmPassword: "",
    });
  };

  const validateForm = () => {
    if (
      isRegisterMode &&
      formData.fullName.trim().length < 2
    ) {
      return "Please enter your full name.";
    }

    if (!formData.email.trim()) {
      return "Please enter your email address.";
    }

    if (!formData.email.includes("@")) {
      return "Please enter a valid email address.";
    }

    if (!formData.password) {
      return "Please enter your password.";
    }

    if (
      isRegisterMode &&
      formData.password.length < 8
    ) {
      return "Password must contain at least 8 characters.";
    }

    if (
      isRegisterMode &&
      !/[A-Z]/.test(formData.password)
    ) {
      return "Password must contain an uppercase letter.";
    }

    if (
      isRegisterMode &&
      !/[a-z]/.test(formData.password)
    ) {
      return "Password must contain a lowercase letter.";
    }

    if (
      isRegisterMode &&
      !/\d/.test(formData.password)
    ) {
      return "Password must contain a number.";
    }

    if (
      isRegisterMode &&
      formData.password !==
        formData.confirmPassword
    ) {
      return "Passwords do not match.";
    }

    return "";
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const validationError =
      validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      const result = isRegisterMode
        ? await registerUser({
            fullName: formData.fullName,
            email: formData.email,
            password: formData.password,
          })
        : await loginUser({
            email: formData.email,
            password: formData.password,
          });

      onAuthenticated(result.user);
    } catch (submitError) {
      setError(
        submitError.message ||
          "Authentication failed."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">
            AI
          </div>

          <p className="auth-eyebrow">
            Enterprise RAG Platform
          </p>

          <h1>
            Enterprise AI Assistant
          </h1>

          <p className="auth-brand-description">
            Securely analyze enterprise PDFs,
            retrieve grounded answers with
            Gemini and ChromaDB, and generate
            professional fraud-analysis reports.
          </p>

          <div className="auth-feature-list">
            <div>
              <span>01</span>

              <p>
                Secure JWT-based user
                authentication
              </p>
            </div>

            <div>
              <span>02</span>

              <p>
                Gemini-powered document
                retrieval and reasoning
              </p>
            </div>

            <div>
              <span>03</span>

              <p>
                ChromaDB vector search with
                grounded sources
              </p>
            </div>

            <div>
              <span>04</span>

              <p>
                Enterprise PDF fraud reports
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="auth-form-panel">
        <div className="auth-form-card">
          <div className="auth-form-header">
            <p>
              {isRegisterMode
                ? "Create account"
                : "Welcome back"}
            </p>

            <h2>
              {isRegisterMode
                ? "Register for access"
                : "Sign in to your workspace"}
            </h2>

            <span>
              {isRegisterMode
                ? "Create your secure Enterprise AI account."
                : "Enter your credentials to continue."}
            </span>
          </div>

          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >
            {isRegisterMode && (
              <label>
                Full name

                <input
                  type="text"
                  name="fullName"
                  autoComplete="name"
                  value={formData.fullName}
                  placeholder="Prasanth Sibbala"
                  disabled={submitting}
                  onChange={updateField}
                />
              </label>
            )}

            <label>
              Email address

              <input
                type="email"
                name="email"
                autoComplete="email"
                value={formData.email}
                placeholder="name@company.com"
                disabled={submitting}
                onChange={updateField}
              />
            </label>

            <label>
              Password

              <input
                type="password"
                name="password"
                autoComplete={
                  isRegisterMode
                    ? "new-password"
                    : "current-password"
                }
                value={formData.password}
                placeholder="Enter password"
                disabled={submitting}
                onChange={updateField}
              />
            </label>

            {isRegisterMode && (
              <label>
                Confirm password

                <input
                  type="password"
                  name="confirmPassword"
                  autoComplete="new-password"
                  value={
                    formData.confirmPassword
                  }
                  placeholder="Confirm password"
                  disabled={submitting}
                  onChange={updateField}
                />
              </label>
            )}

            {error && (
              <div
                className="auth-error"
                role="alert"
              >
                {error}
              </div>
            )}

            <button
              className="auth-submit-button"
              type="submit"
              disabled={submitting}
            >
              {submitting
                ? isRegisterMode
                  ? "Creating account..."
                  : "Signing in..."
                : isRegisterMode
                  ? "Create account"
                  : "Sign in"}
            </button>
          </form>

          <div className="auth-switch">
            <span>
              {isRegisterMode
                ? "Already have an account?"
                : "Do not have an account?"}
            </span>

            <button
              type="button"
              disabled={submitting}
              onClick={switchMode}
            >
              {isRegisterMode
                ? "Sign in"
                : "Create account"}
            </button>
          </div>

          <p className="auth-security-note">
            Protected with secure password hashing
            and JWT access tokens.
          </p>
        </div>
      </section>
    </main>
  );
}

export default AuthPage;