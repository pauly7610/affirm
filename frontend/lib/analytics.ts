/**
 * Lightweight analytics event logger.
 * Logs structured events to console in dev; swap transport for production.
 *
 * Key events mapped to KPIs:
 *   search_submitted     → search volume, query distribution
 *   refine_applied       → refine usage rate
 *   offer_selected       → search → plan review conversion
 *   plan_modal_opened    → time-to-first-decision
 *   feedback_submitted   → feedback rate, sentiment
 */

type EventName =
  | 'search_submitted'
  | 'refine_applied'
  | 'offer_selected'
  | 'plan_modal_opened'
  | 'feedback_submitted';

interface AnalyticsEvent {
  event: EventName;
  timestamp: string;
  properties: Record<string, unknown>;
}

const eventLog: AnalyticsEvent[] = [];

export function trackEvent(event: EventName, properties: Record<string, unknown> = {}): void {
  const entry: AnalyticsEvent = {
    event,
    timestamp: new Date().toISOString(),
    properties,
  };
  eventLog.push(entry);

  if (__DEV__) {
    console.log(`[analytics] ${event}`, properties);
  }
}

export function getEventLog(): AnalyticsEvent[] {
  return [...eventLog];
}
