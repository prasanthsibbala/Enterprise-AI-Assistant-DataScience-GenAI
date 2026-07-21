import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  askDocumentQuestion,
  clearAuthentication,
  deleteIndexedDocument,
  downloadFraudReport,
  getIndexedDocuments,
  uploadDocument,
} from "../services/api";

import "../App.css";
import FraudAnalytics from "./FraudAnalytics";

function createMessageId() {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random()}`;
}

function Dashboard({
  user,
  onLogout,
}) {
  const [selectedFile, setSelectedFile] =
    useState(null);

  const [activeDocument, setActiveDocument] =
    useState(null);

  const [
    indexedDocuments,
    setIndexedDocuments,
  ] = useState([]);

  const [question, setQuestion] =
    useState("");

  const [messages, setMessages] =
    useState([]);

  const [uploading, setUploading] =
    useState(false);

  const [
    loadingDocuments,
    setLoadingDocuments,
  ] = useState(false);

  const [
    deletingDocumentId,
    setDeletingDocumentId,
  ] = useState(null);

  const [asking, setAsking] =
    useState(false);

  const [
    downloadingReport,
    setDownloadingReport,
  ] = useState(false);

  const [error, setError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const fileInputRef = useRef(null);
  const chatWindowRef = useRef(null);

  const clearMessages = () => {
    setMessages([]);
    setQuestion("");
  };

  const loadIndexedDocuments = async () => {
    setLoadingDocuments(true);
    setError("");

    try {
      const result =
        await getIndexedDocuments();

      const documents =
        result.documents || [];

      setIndexedDocuments(documents);

      setActiveDocument(
        (currentDocument) => {
          if (!currentDocument) {
            return null;
          }

          const stillExists =
            documents.some(
              (item) =>
                item.document_id ===
                currentDocument.document_id
            );

          return stillExists
            ? currentDocument
            : null;
        }
      );
    } catch (loadError) {
      setError(
        loadError.message ||
          "Unable to load indexed documents."
      );
    } finally {
      setLoadingDocuments(false);
    }
  };

  useEffect(() => {
    loadIndexedDocuments();
  }, []);

  useEffect(() => {
    if (!chatWindowRef.current) {
      return;
    }

    chatWindowRef.current.scrollTop =
      chatWindowRef.current.scrollHeight;
  }, [messages, asking]);

  const handleLogout = () => {
    clearAuthentication();
    onLogout();
  };

  const handleFileChange = (event) => {
    const file =
      event.target.files?.[0] || null;

    setSelectedFile(file);
    setError("");
    setSuccessMessage("");
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError(
        "Please select a PDF file."
      );
      return;
    }

    const isPdf =
      selectedFile.type ===
        "application/pdf" ||
      selectedFile.name
        .toLowerCase()
        .endsWith(".pdf");

    if (!isPdf) {
      setError(
        "Only PDF files are supported."
      );
      return;
    }

    setUploading(true);
    setError("");
    setSuccessMessage("");

    try {
      const result =
        await uploadDocument(selectedFile);

      setActiveDocument({
        document_id: result.document_id,
        filename: result.filename,
        pages: result.pages,
        chunks: result.chunks_created,
      });

      clearMessages();

      setSuccessMessage(
        `${result.filename} uploaded and indexed successfully.`
      );

      setSelectedFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      await loadIndexedDocuments();
    } catch (uploadError) {
      setError(
        uploadError.message ||
          "Document upload failed."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleSelectDocument = (item) => {
    setActiveDocument({
      document_id: item.document_id,
      filename: item.filename,
      chunks: item.chunks,
    });

    clearMessages();
    setError("");

    setSuccessMessage(
      `${item.filename} selected.`
    );
  };

  const handleDeleteDocument = async (
    item
  ) => {
    const confirmed =
      window.confirm(
        `Delete "${item.filename}" from the vector database?`
      );

    if (!confirmed) {
      return;
    }

    setDeletingDocumentId(
      item.document_id
    );

    setError("");
    setSuccessMessage("");

    try {
      await deleteIndexedDocument(
        item.document_id
      );

      if (
        activeDocument?.document_id ===
        item.document_id
      ) {
        setActiveDocument(null);
        clearMessages();
      }

      setSuccessMessage(
        `${item.filename} deleted successfully.`
      );

      await loadIndexedDocuments();
    } catch (deleteError) {
      setError(
        deleteError.message ||
          "Unable to delete the document."
      );
    } finally {
      setDeletingDocumentId(null);
    }
  };

  const handleAskQuestion = async () => {
    const trimmedQuestion =
      question.trim();

    if (!activeDocument?.document_id) {
      setError(
        "Please upload or select a document first."
      );
      return;
    }

    if (!trimmedQuestion) {
      setError(
        "Please enter a question."
      );
      return;
    }

    const userMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmedQuestion,
      sources: [],
    };

    setMessages(
      (currentMessages) => [
        ...currentMessages,
        userMessage,
      ]
    );

    setQuestion("");
    setAsking(true);
    setError("");
    setSuccessMessage("");

    try {
      const result =
        await askDocumentQuestion(
          trimmedQuestion,
          activeDocument.document_id
        );

      const assistantMessage = {
        id: createMessageId(),
        role: "assistant",
        content:
          result.answer ||
          "No answer was returned.",
        sources:
          result.sources || [],
        model: result.model,
      };

      setMessages(
        (currentMessages) => [
          ...currentMessages,
          assistantMessage,
        ]
      );
    } catch (questionError) {
      const errorMessage = {
        id: createMessageId(),
        role: "assistant",
        content:
          questionError.message ||
          "Unable to answer this question.",
        sources: [],
        isError: true,
      };

      setMessages(
        (currentMessages) => [
          ...currentMessages,
          errorMessage,
        ]
      );

      setError(
        questionError.message ||
          "Unable to answer the question."
      );
    } finally {
      setAsking(false);
    }
  };

  const handleQuestionKeyDown = (
    event
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      if (
        !asking &&
        question.trim() &&
        activeDocument?.document_id
      ) {
        handleAskQuestion();
      }
    }
  };

  const handleClearChat = () => {
    clearMessages();
    setError("");

    setSuccessMessage(
      "Conversation cleared."
    );
  };

  const handleDownloadReport =
    async () => {
      setDownloadingReport(true);
      setError("");
      setSuccessMessage("");

      try {
        await downloadFraudReport({
          prediction: "Not Fraud",
          fraud_probability: 2.9,
          risk_level: "Low",
          top_features: [
            "TotalClaimAmount",
            "IPClaimCount",
            "TotalClaimCount",
          ],
          ai_explanation:
            "This provider currently appears to have a low fraud risk. " +
            "The combined values did not indicate a strong fraud pattern.",
          recommendation:
            "Continue routine monitoring. " +
            "No immediate audit is required.",
        });

        setSuccessMessage(
          "Fraud analysis report downloaded successfully."
        );
      } catch (downloadError) {
        setError(
          downloadError.message ||
            "Unable to download the PDF report."
        );
      } finally {
        setDownloadingReport(false);
      }
    };

  return (
    <main className="app-shell">
      <header className="application-header">
        <div>
          <strong>
            Enterprise AI Assistant
          </strong>

          <span>
            Secure RAG Workspace
          </span>
        </div>

        <div className="user-menu">
          <div className="user-avatar">
            {user?.full_name
              ?.charAt(0)
              ?.toUpperCase() || "U"}
          </div>

          <div className="user-summary">
            <strong>
              {user?.full_name ||
                "Enterprise User"}
            </strong>

            <span>
              {user?.email ||
                "Authenticated user"}
            </span>
          </div>

          <button
            type="button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </header>

      <section className="hero">
        <div className="hero-badge">
          Enterprise RAG Platform
        </div>

        <h1>
          Enterprise AI Assistant
        </h1>

        <p>
          Upload PDF documents, index them
          in ChromaDB, ask grounded
          questions using Gemini, and
          generate fraud analysis reports.
        </p>
      </section>

      {error && (
        <section
          className="status-box error-box"
          role="alert"
        >
          {error}
        </section>
      )}

      {successMessage && (
        <section
          className="status-box success-message"
          role="status"
        >
          {successMessage}
        </section>
      )}

      <FraudAnalytics user={user} />

      <section className="dashboard-grid">
        <div className="dashboard-column">
          <section className="card">
            <div className="card-header">
              <div>
                <span className="step-number">
                  1
                </span>

                <h2>Upload PDF</h2>
              </div>
            </div>

            <p className="card-description">
              Select a PDF document and
              index its content in ChromaDB.
            </p>

            <label
              className="file-upload-box"
              htmlFor="pdf-file"
            >
              <span className="file-icon">
                PDF
              </span>

              <span className="file-upload-title">
                {selectedFile
                  ? selectedFile.name
                  : "Choose a PDF file"}
              </span>

              <span className="file-upload-description">
                Click here to browse files
              </span>
            </label>

            <input
              ref={fileInputRef}
              id="pdf-file"
              className="hidden-file-input"
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileChange}
            />

            <button
              className="primary-button full-width"
              type="button"
              onClick={handleUpload}
              disabled={
                uploading ||
                !selectedFile
              }
            >
              {uploading
                ? "Uploading and indexing..."
                : "Upload Document"}
            </button>

            {activeDocument && (
              <div className="active-document-box">
                <span className="active-label">
                  Active document
                </span>

                <strong>
                  {activeDocument.filename}
                </strong>

                <span>
                  {activeDocument.pages
                    ? `${activeDocument.pages} page(s) · `
                    : ""}

                  {activeDocument.chunks ||
                    activeDocument.chunks_created ||
                    0}{" "}
                  chunk(s)
                </span>
              </div>
            )}
          </section>

          <section className="card">
            <div className="card-header">
              <div>
                <span className="step-number">
                  2
                </span>

                <h2>
                  Indexed Documents
                </h2>
              </div>

              <button
                className="text-button"
                type="button"
                onClick={
                  loadIndexedDocuments
                }
                disabled={
                  loadingDocuments
                }
              >
                {loadingDocuments
                  ? "Refreshing..."
                  : "Refresh"}
              </button>
            </div>

            <p className="card-description">
              Select a document for chat or
              delete documents that are no
              longer required.
            </p>

            {loadingDocuments && (
              <div className="loading-box">
                Loading indexed
                documents...
              </div>
            )}

            {!loadingDocuments &&
              indexedDocuments.length ===
                0 && (
                <div className="empty-state">
                  <h3>
                    No indexed documents
                  </h3>

                  <p>
                    Upload a PDF to start
                    using the AI assistant.
                  </p>
                </div>
              )}

            {!loadingDocuments &&
              indexedDocuments.length >
                0 && (
                <div className="document-list">
                  {indexedDocuments.map(
                    (item) => {
                      const isSelected =
                        activeDocument?.document_id ===
                        item.document_id;

                      const isDeleting =
                        deletingDocumentId ===
                        item.document_id;

                      return (
                        <article
                          className={`document-item ${
                            isSelected
                              ? "document-item-selected"
                              : ""
                          }`}
                          key={
                            item.document_id
                          }
                        >
                          <div className="document-info">
                            <strong>
                              {item.filename}
                            </strong>

                            <span>
                              {item.chunks}{" "}
                              indexed chunk(s)
                            </span>

                            {isSelected && (
                              <span className="selected-tag">
                                Currently
                                selected
                              </span>
                            )}
                          </div>

                          <div className="document-actions">
                            <button
                              className="secondary-button"
                              type="button"
                              disabled={
                                isSelected ||
                                isDeleting
                              }
                              onClick={() =>
                                handleSelectDocument(
                                  item
                                )
                              }
                            >
                              {isSelected
                                ? "Selected"
                                : "Select"}
                            </button>

                            <button
                              className="danger-button"
                              type="button"
                              disabled={
                                isDeleting
                              }
                              onClick={() =>
                                handleDeleteDocument(
                                  item
                                )
                              }
                            >
                              {isDeleting
                                ? "Deleting..."
                                : "Delete"}
                            </button>
                          </div>
                        </article>
                      );
                    }
                  )}
                </div>
              )}
          </section>

          <section className="card">
            <div className="card-header">
              <div>
                <span className="step-number">
                  4
                </span>

                <h2>
                  Fraud Analysis Report
                </h2>
              </div>
            </div>

            <p className="card-description">
              Generate a professional PDF
              containing prediction,
              probability, risk level,
              explanation, and
              recommendation.
            </p>

            <div className="report-summary">
              <div>
                <span>Prediction</span>
                <strong>
                  Not Fraud
                </strong>
              </div>

              <div>
                <span>
                  Fraud Probability
                </span>

                <strong>2.9%</strong>
              </div>

              <div>
                <span>Risk Level</span>
                <strong>Low</strong>
              </div>
            </div>

            <button
              className="primary-button full-width"
              type="button"
              onClick={
                handleDownloadReport
              }
              disabled={
                downloadingReport
              }
            >
              {downloadingReport
                ? "Generating PDF..."
                : "Download PDF Report"}
            </button>
          </section>
        </div>

        <section className="card chat-card">
          <div className="chat-header">
            <div>
              <div className="card-title-row">
                <span className="step-number">
                  3
                </span>

                <h2>
                  Ask the Document
                </h2>
              </div>

              <p>
                {activeDocument
                  ? `Chatting with ${activeDocument.filename}`
                  : "Upload or select a document to begin."}
              </p>
            </div>

            <button
              className="text-button"
              type="button"
              onClick={handleClearChat}
              disabled={
                messages.length === 0
              }
            >
              Clear chat
            </button>
          </div>

          <div
            className="chat-window"
            ref={chatWindowRef}
          >
            {messages.length === 0 &&
              !asking && (
                <div className="chat-empty-state">
                  <div className="chat-empty-icon">
                    AI
                  </div>

                  <h3>
                    Start a grounded
                    conversation
                  </h3>

                  <p>
                    Ask questions about the
                    selected PDF. Answers
                    will be based only on
                    retrieved document
                    context.
                  </p>

                  <div className="example-questions">
                    <button
                      type="button"
                      disabled={
                        !activeDocument
                      }
                      onClick={() =>
                        setQuestion(
                          "What is the fraud probability?"
                        )
                      }
                    >
                      What is the fraud
                      probability?
                    </button>

                    <button
                      type="button"
                      disabled={
                        !activeDocument
                      }
                      onClick={() =>
                        setQuestion(
                          "What is the risk level and recommendation?"
                        )
                      }
                    >
                      What is the risk level?
                    </button>

                    <button
                      type="button"
                      disabled={
                        !activeDocument
                      }
                      onClick={() =>
                        setQuestion(
                          "Summarize the document."
                        )
                      }
                    >
                      Summarize the document
                    </button>
                  </div>
                </div>
              )}

            {messages.map(
              (message) => (
                <article
                  className={`chat-message ${message.role}`}
                  key={message.id}
                >
                  <div className="message-label">
                    {message.role ===
                    "user"
                      ? "You"
                      : "AI Assistant"}
                  </div>

                  <div
                    className={`message-bubble ${
                      message.isError
                        ? "message-error"
                        : ""
                    }`}
                  >
                    <p>
                      {message.content}
                    </p>
                  </div>

                  {message.model && (
                    <span className="model-label">
                      Model:{" "}
                      {message.model}
                    </span>
                  )}

                  {message.sources
                    ?.length > 0 && (
                    <div className="message-sources">
                      <h4>
                        Retrieved Sources
                      </h4>

                      {message.sources.map(
                        (
                          source,
                          index
                        ) => (
                          <article
                            className="source-item"
                            key={`${source.document_id}-${source.chunk_index}-${index}`}
                          >
                            <div className="source-header">
                              <strong>
                                {
                                  source.filename
                                }
                              </strong>

                              <span>
                                {source.page
                                  ? `Page ${source.page} · `
                                  : ""}

                                Chunk{" "}
                                {
                                  source.chunk_index
                                }
                              </span>
                            </div>

                            {source.relevance_score !==
                              undefined && (
                              <span className="relevance-label">
                                Relevance:{" "}
                                {Math.round(
                                  source.relevance_score *
                                    100
                                )}
                                %
                              </span>
                            )}

                            <p>
                              {source.preview ||
                                source.content?.slice(
                                  0,
                                  300
                                ) ||
                                "No source preview available."}
                            </p>
                          </article>
                        )
                      )}
                    </div>
                  )}
                </article>
              )
            )}

            {asking && (
              <article className="chat-message assistant">
                <div className="message-label">
                  AI Assistant
                </div>

                <div className="message-bubble typing-bubble">
                  <span />
                  <span />
                  <span />
                </div>
              </article>
            )}
          </div>

          <div className="chat-input-area">
            <textarea
              value={question}
              rows={3}
              placeholder={
                activeDocument
                  ? "Ask a question about the selected document..."
                  : "Select a document first..."
              }
              disabled={
                asking ||
                !activeDocument
              }
              onChange={(event) => {
                setQuestion(
                  event.target.value
                );

                setError("");
              }}
              onKeyDown={
                handleQuestionKeyDown
              }
            />

            <div className="chat-input-footer">
              <span>
                Enter to send · Shift +
                Enter for new line
              </span>

              <button
                className="primary-button send-button"
                type="button"
                onClick={
                  handleAskQuestion
                }
                disabled={
                  asking ||
                  !question.trim() ||
                  !activeDocument
                }
              >
                {asking
                  ? "Analyzing..."
                  : "Send Question"}
              </button>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

export default Dashboard;