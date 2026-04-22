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

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  withCredentials: true,
});

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

let isRefreshing = false;

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry && !isRefreshing) {
      original._retry = true;
      isRefreshing = true;
      try {
        const { data } = await axios.post(
          "/api/v1/auth/refresh",
          {},
          { withCredentials: true }
        );
        setAccessToken(data.access_token);
        original.headers.Authorization = `Bearer ${data.access_token}`;
        isRefreshing = false;
        return apiClient(original);
      } catch {
        clearAccessToken();
        isRefreshing = false;
        window.dispatchEvent(new Event("session-expired"));
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
