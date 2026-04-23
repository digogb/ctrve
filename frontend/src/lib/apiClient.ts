import axios from "axios";

let accessToken: string | null = null;

export function setAccessToken(token: string): void {
  accessToken = token;
}

export function clearAccessToken(): void {
  accessToken = null;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export const { isAxiosError } = axios;

const baseURL = import.meta.env.VITE_API_URL ?? "/api";

const apiClient = axios.create({
  baseURL,
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

type QueueEntry = { resolve: (token: string) => void; reject: (err: unknown) => void };
let isRefreshing = false;
let failedQueue: QueueEntry[] = [];

function flushQueue(token: string | null, error: unknown): void {
  failedQueue.forEach((entry) => {
    if (token) entry.resolve(token);
    else entry.reject(error);
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          original.headers.Authorization = `Bearer ${token}`;
          return apiClient(original);
        })
        .catch(() => Promise.reject(error));
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const { data } = await axios.post(
        `${baseURL}/v1/auth/refresh`,
        {},
        { withCredentials: true }
      );
      setAccessToken(data.access_token);
      original.headers.Authorization = `Bearer ${data.access_token}`;
      flushQueue(data.access_token, null);
      isRefreshing = false;
      return apiClient(original);
    } catch (refreshError) {
      flushQueue(null, refreshError);
      clearAccessToken();
      isRefreshing = false;
      window.dispatchEvent(new Event("session-expired"));
      return Promise.reject(error);
    }
  }
);

export default apiClient;
