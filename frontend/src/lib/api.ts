import type {
  AuthStatus,
  CalendarSource,
  ExternalEvent,
  SavedEventRecord,
  ScanCriteria,
  ScanSchedule,
  ScanRun,
  SlackSettings,
} from "./types";

type JsonValue = Record<string, unknown>;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...init,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      // Keep the fallback message when the response body is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function fetchEvents(): Promise<ExternalEvent[]> {
  return request<ExternalEvent[]>("/api/events");
}

export function fetchSavedEvents(): Promise<SavedEventRecord[]> {
  return request<SavedEventRecord[]>("/api/events/saved");
}

export function deleteSavedEvent(savedEventId: number): Promise<JsonValue> {
  return request<JsonValue>(`/api/events/saved/${savedEventId}`, {
    method: "DELETE",
  });
}

export function saveEvent(eventId: number, payload: JsonValue): Promise<JsonValue> {
  return request<JsonValue>(`/api/events/${eventId}/save`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createEvent(payload: JsonValue): Promise<ExternalEvent> {
  return request<ExternalEvent>("/api/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteEvent(eventId: number): Promise<JsonValue> {
  return request<JsonValue>(`/api/events/${eventId}`, {
    method: "DELETE",
  });
}

export function addScannedEventToCalendar(eventId: number, payload: JsonValue): Promise<ExternalEvent> {
  return request<ExternalEvent>(`/api/events/${eventId}/add-to-calendar`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateSavedNotes(savedEventId: number, payload: JsonValue): Promise<JsonValue> {
  return request<JsonValue>(`/api/events/saved/${savedEventId}/notes`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchSources(): Promise<CalendarSource[]> {
  return request<CalendarSource[]>("/api/settings/sources");
}

export function upsertSource(sourceId: number | null, payload: JsonValue): Promise<CalendarSource> {
  return request<CalendarSource>(sourceId ? `/api/settings/sources/${sourceId}` : "/api/settings/sources", {
    method: sourceId ? "PUT" : "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteSource(sourceId: number): Promise<JsonValue> {
  return request<JsonValue>(`/api/settings/sources/${sourceId}`, {
    method: "DELETE",
  });
}

export async function uploadIcsSource(payload: {
  name: string;
  calendar_type: string;
  category: string;
  scan_frequency: string;
  preferred_weight: number;
  file: File;
}): Promise<CalendarSource> {
  const formData = new FormData();
  formData.append("name", payload.name);
  formData.append("calendar_type", payload.calendar_type);
  formData.append("category", payload.category);
  formData.append("scan_frequency", payload.scan_frequency);
  formData.append("preferred_weight", String(payload.preferred_weight));
  formData.append("file", payload.file);

  const response = await fetch("/api/settings/sources/upload", {
    method: "POST",
    body: formData,
    credentials: "include",
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // keep default
    }
    throw new Error(message);
  }

  return (await response.json()) as CalendarSource;
}

export function fetchCriteria(): Promise<ScanCriteria> {
  return request<ScanCriteria>("/api/settings/scan-criteria");
}

export function updateCriteria(payload: JsonValue): Promise<ScanCriteria> {
  return request<ScanCriteria>("/api/settings/scan-criteria", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchSlackSettings(): Promise<SlackSettings> {
  return request<SlackSettings>("/api/settings/slack");
}

export function updateSlackSettings(payload: JsonValue): Promise<SlackSettings> {
  return request<SlackSettings>("/api/settings/slack", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function fetchScanRuns(): Promise<ScanRun[]> {
  return request<ScanRun[]>("/api/settings/scan-runs");
}

export function triggerScan(): Promise<ScanRun> {
  return request<ScanRun>("/api/settings/run-scan", { method: "POST" });
}

export function fetchScanSchedule(): Promise<ScanSchedule> {
  return request<ScanSchedule>("/api/settings/scan-schedule");
}

export function eventCalendarDownloadUrl(eventId: number): string {
  return `/api/events/${eventId}/calendar.ics`;
}

export function fetchAuthStatus(): Promise<AuthStatus> {
  return request<AuthStatus>("/api/auth/status");
}

export function loginWithPassword(password: string): Promise<AuthStatus> {
  return request<AuthStatus>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ password }),
  });
}

export function logoutFromApp(): Promise<AuthStatus> {
  return request<AuthStatus>("/api/auth/logout", {
    method: "POST",
    body: JSON.stringify({}),
  });
}
