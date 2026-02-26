import { SearchRequest, SearchResponse, SearchFeedback, SuggestionsResponse, ProfileSummary, ScorecardResponse } from '../types';

const API_URL = process.env.EXPO_PUBLIC_API_URL || '';

function generateRequestId(): string {
  return Math.random().toString(36).substring(2, 10);
}

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const requestId = generateRequestId();
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Request-Id': requestId,
      ...(options?.headers || {}),
    },
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

export async function getScorecard(): Promise<ScorecardResponse> {
  return fetchJSON<ScorecardResponse>(`${API_URL}/v1/quality/scorecard`);
}
