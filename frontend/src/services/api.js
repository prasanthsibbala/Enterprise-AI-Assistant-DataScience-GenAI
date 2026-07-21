import axios from "axios";

const ACCESS_TOKEN_KEY =
  "enterprise_ai_access_token";

const USER_KEY =
  "enterprise_ai_user";

const api = axios.create({
  baseURL:
    "http://127.0.0.1:8000/api/v1",
  timeout: 120000,
});

export function getAccessToken() {
  return localStorage.getItem(
    ACCESS_TOKEN_KEY
  );
}

export function getStoredUser() {
  const storedUser =
    localStorage.getItem(USER_KEY);

  if (!storedUser) {
    return null;
  }

  try {
    return JSON.parse(storedUser);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function saveAuthentication(
  authResponse
) {
  localStorage.setItem(
    ACCESS_TOKEN_KEY,
    authResponse.access_token
  );

  localStorage.setItem(
    USER_KEY,
    JSON.stringify(authResponse.user)
  );
}

export function clearAuthentication() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY
  );

  localStorage.removeItem(USER_KEY);
}

api.interceptors.request.use(
  (config) => {
    const accessToken =
      getAccessToken();

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthentication();

      window.dispatchEvent(
        new Event(
          "authentication-expired"
        )
      );
    }

    return Promise.reject(error);
  }
);

async function extractBlobError(
  error,
  fallbackMessage
) {
  const responseData =
    error.response?.data;

  if (responseData instanceof Blob) {
    try {
      const text =
        await responseData.text();

      const parsedData =
        JSON.parse(text);

      return (
        parsedData.detail ||
        parsedData.message ||
        fallbackMessage
      );
    } catch {
      return fallbackMessage;
    }
  }

  return (
    responseData?.detail ||
    responseData?.message ||
    error.message ||
    fallbackMessage
  );
}

function getErrorMessage(
  error,
  fallbackMessage
) {
  const detail =
    error.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => item.msg)
      .join(" ");
  }

  return (
    detail ||
    error.response?.data?.message ||
    error.message ||
    fallbackMessage
  );
}

export async function registerUser({
  fullName,
  email,
  password,
}) {
  try {
    const response = await api.post(
      "/auth/register",
      {
        full_name: fullName.trim(),
        email: email
          .trim()
          .toLowerCase(),
        password,
      }
    );

    saveAuthentication(response.data);

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to create the account."
      )
    );
  }
}

export async function loginUser({
  email,
  password,
}) {
  try {
    const response = await api.post(
      "/auth/login",
      {
        email: email
          .trim()
          .toLowerCase(),
        password,
      }
    );

    saveAuthentication(response.data);

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Invalid email or password."
      )
    );
  }
}

export async function getCurrentUser() {
  try {
    const response =
      await api.get("/auth/me");

    localStorage.setItem(
      USER_KEY,
      JSON.stringify(response.data)
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to restore your session."
      )
    );
  }
}
export async function uploadDocument(file) {
  if (!file) {
    throw new Error(
      "PDF file is required."
    );
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await api.post(
      "/documents/upload",
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Document upload failed."
      )
    );
  }
}

export async function getIndexedDocuments() {
  try {
    const response =
      await api.get("/documents");

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to load indexed documents."
      )
    );
  }
}

export async function deleteIndexedDocument(
  documentId
) {
  if (!documentId) {
    throw new Error(
      "Document ID is required."
    );
  }

  try {
    const response = await api.delete(
      `/documents/${documentId}`
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to delete the document."
      )
    );
  }
}

export async function askDocumentQuestion(
  question,
  documentId
) {
  if (!question?.trim()) {
    throw new Error(
      "Question is required."
    );
  }

  if (!documentId) {
    throw new Error(
      "Please select an indexed document."
    );
  }

  try {
    const response = await api.post(
      "/chat/document",
      {
        question: question.trim(),
        document_id: documentId,
      }
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to answer the question."
      )
    );
  }
}

function extractFilename(
  contentDisposition
) {
  if (!contentDisposition) {
    return "healthcare_fraud_report.pdf";
  }

  const encodedMatch =
    contentDisposition.match(
      /filename\*=UTF-8''([^;]+)/
    );

  if (encodedMatch?.[1]) {
    return decodeURIComponent(
      encodedMatch[1]
    );
  }

  const normalMatch =
    contentDisposition.match(
      /filename="?([^";]+)"?/
    );

  return (
    normalMatch?.[1] ||
    "healthcare_fraud_report.pdf"
  );
}

export async function downloadFraudReport(
  reportData
) {
  try {
    const response = await api.post(
      "/reports/fraud/pdf",
      reportData,
      {
        responseType: "blob",
      }
    );

    const filename = extractFilename(
      response.headers[
        "content-disposition"
      ]
    );

    const pdfBlob = new Blob(
      [response.data],
      {
        type: "application/pdf",
      }
    );

    const downloadUrl =
      window.URL.createObjectURL(
        pdfBlob
      );

    const link =
      window.document.createElement(
        "a"
      );

    link.href = downloadUrl;
    link.download = filename;

    window.document.body.appendChild(
      link
    );

    link.click();
    link.remove();

    window.URL.revokeObjectURL(
      downloadUrl
    );
  } catch (error) {
    const message =
      await extractBlobError(
        error,
        "Unable to download the PDF report."
      );

    throw new Error(message);
  }
}
export async function predictFraud(
  payload
) {
  try {
    const response = await api.post(
      "/fraud/predict",
      payload
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to calculate fraud risk."
      )
    );
  }
}

export async function getFraudModelMetrics() {
  try {
    const response = await api.get(
      "/fraud/model/metrics"
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to load model metrics."
      )
    );
  }
}

export async function trainFraudModel() {
  try {
    const response = await api.post(
      "/fraud/model/train"
    );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Unable to train the fraud model."
      )
    );
  }
}

export default api;