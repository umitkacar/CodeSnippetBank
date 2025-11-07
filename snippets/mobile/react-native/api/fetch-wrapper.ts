import AsyncStorage from '@react-native-async-storage/async-storage';

interface FetchOptions extends RequestInit {
  isAuthRequired?: boolean;
}

class FetchWrapper {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async getHeaders(customHeaders?: HeadersInit): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...customHeaders,
    };

    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      (headers as any).Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    }

    return response.text() as any;
  }

  async get<T>(endpoint: string, options?: FetchOptions): Promise<T> {
    const headers = await this.getHeaders(options?.headers);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(endpoint: string, data?: any, options?: FetchOptions): Promise<T> {
    const headers = await this.getHeaders(options?.headers);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async put<T>(endpoint: string, data?: any, options?: FetchOptions): Promise<T> {
    const headers = await this.getHeaders(options?.headers);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(data),
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(endpoint: string, options?: FetchOptions): Promise<T> {
    const headers = await this.getHeaders(options?.headers);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers,
      ...options,
    });

    return this.handleResponse<T>(response);
  }

  async upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const token = await AsyncStorage.getItem('auth_token');
    const headers: HeadersInit = {};

    if (token) {
      (headers as any).Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    return this.handleResponse<T>(response);
  }
}

export const fetchWrapper = new FetchWrapper('https://api.example.com');
