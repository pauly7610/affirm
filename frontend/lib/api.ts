import { SearchRequest, SearchResponse, SearchFeedback, SuggestionsResponse, ProfileSummary } from '../types';

const API_URL = process.env.EXPO_PUBLIC_API_URL || '';

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export async function searchQuery(req: SearchRequest): Promise<SearchResponse> {
  return fetchJSON<SearchResponse>(`${API_URL}/v1/search/query`, {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

export async function getSuggestions(userId = 'demo-user'): Promise<SuggestionsResponse> {
  return fetchJSON<SuggestionsResponse>(`${API_URL}/v1/search/suggestions?userId=${userId}`);
}

export async function submitFeedback(feedback: SearchFeedback): Promise<void> {
  await fetchJSON(`${API_URL}/v1/search/feedback`, {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

export async function getProfileSummary(userId = 'demo-user'): Promise<ProfileSummary> {
  return fetchJSON<ProfileSummary>(`${API_URL}/v1/profile/summary?userId=${userId}`);
}

export async function getHealth(): Promise<{ status: string }> {
  return fetchJSON(`${API_URL}/healthz`);
}
