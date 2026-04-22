export type CalendarType = "work" | "personal" | "public" | "conferences";

export type SavedEventState = {
  id: number;
  external_event_id: number;
  pinned: boolean;
  personal_notes: string | null;
  follow_up_action: string | null;
  slack_posted: boolean;
  saved_at: string;
  updated_at: string;
};

export type EventNote = {
  id: number;
  saved_event_id: number;
  thoughts: string[];
  why_it_matters: string | null;
  links: string[];
  created_at: string;
  updated_at: string;
};

export type ExternalEvent = {
  id: number;
  external_id: string;
  title: string;
  description: string | null;
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  location: string | null;
  url: string | null;
  source_name: string;
  source_type: string;
  calendar_type: CalendarType;
  category: string;
  tags: string[];
  relevance_score: number;
  is_saved: boolean;
  created_at: string;
  updated_at: string;
  saved_event: SavedEventState | null;
  note: EventNote | null;
};

export type CalendarSource = {
  id: number;
  name: string;
  type: string;
  url: string | null;
  enabled: boolean;
  category: string;
  calendar_type: CalendarType;
  scan_frequency: string;
  preferred_weight: number;
  last_scanned_at: string | null;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ScanCriteria = {
  id: number;
  keywords: string[];
  excluded_keywords: string[];
  preferred_organisations: string[];
  preferred_locations: string[];
  date_horizon_days: number;
  event_types: string[];
  minimum_relevance_score: number;
  created_at: string;
  updated_at: string;
};

export type SlackSettings = {
  id: number;
  enabled: boolean;
  webhook_url: string | null;
  channel_label: string | null;
  created_at: string;
  updated_at: string;
};

export type SavedEventRecord = {
  event: Omit<ExternalEvent, "saved_event" | "note">;
  saved_event: SavedEventState;
  note: EventNote | null;
};

export type ScanRun = {
  id: number;
  status: string;
  scanned_sources: number;
  new_events_found: number;
  started_at: string;
  finished_at: string | null;
  notes: Record<string, unknown>;
};

export type ScanSchedule = {
  enabled: boolean;
  target_layers: string[];
  frequency: string;
  day_of_week: string;
  hour_utc: number;
  minute_utc: number;
};

export type AuthStatus = {
  enabled: boolean;
  authenticated: boolean;
};
