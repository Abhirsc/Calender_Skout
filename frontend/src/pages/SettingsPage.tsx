import { FormEvent, useEffect, useState } from "react";

import { fetchCriteria, fetchScanRuns, fetchScanSchedule, fetchSlackSettings, triggerScan, updateCriteria, updateSlackSettings } from "../lib/api";
import type { ScanCriteria, ScanRun, ScanSchedule, SlackSettings } from "../lib/types";

function listToText(items: string[]) {
  return items.join("\n");
}

function textToList(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

const criteriaPresets = {
  ecology: {
    keywords: ["ecology", "biodiversity", "conservation", "species distribution modelling", "ecological society"],
    preferred_organisations: ["ecological society", "landcare", "atlas of living australia"],
    event_types: ["conference", "workshop", "webinar"],
  },
  gis: {
    keywords: ["gis", "remote sensing", "spatial analysis", "earth observation", "mapping"],
    preferred_organisations: ["esri", "research infrastructure", "spatial community"],
    event_types: ["workshop", "webinar", "conference"],
  },
  dataScience: {
    keywords: ["data science", "machine learning", "python", "modelling", "reproducible research"],
    preferred_organisations: ["data community", "research software", "open science"],
    event_types: ["webinar", "workshop", "conference"],
  },
};

export function SettingsPage() {
  const [criteria, setCriteria] = useState<ScanCriteria | null>(null);
  const [slack, setSlack] = useState<SlackSettings | null>(null);
  const [schedule, setSchedule] = useState<ScanSchedule | null>(null);
  const [runs, setRuns] = useState<ScanRun[]>([]);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    void Promise.all([fetchCriteria(), fetchSlackSettings(), fetchScanSchedule(), fetchScanRuns()]).then(([criteriaValue, slackValue, scheduleValue, runValues]) => {
      setCriteria(criteriaValue);
      setSlack(slackValue);
      setSchedule(scheduleValue);
      setRuns(runValues);
    });
  }, []);

  async function handleCriteriaSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!criteria) {
      return;
    }
    const form = new FormData(event.currentTarget);
    const next = await updateCriteria({
      keywords: textToList(String(form.get("keywords") ?? "")),
      excluded_keywords: textToList(String(form.get("excluded_keywords") ?? "")),
      preferred_organisations: textToList(String(form.get("preferred_organisations") ?? "")),
      preferred_locations: textToList(String(form.get("preferred_locations") ?? "")),
      event_types: textToList(String(form.get("event_types") ?? "")),
      date_horizon_days: Number(form.get("date_horizon_days") ?? 180),
      minimum_relevance_score: Number(form.get("minimum_relevance_score") ?? 0.35),
    });
    setCriteria(next);
  }

  async function handleSlackSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const next = await updateSlackSettings({
      enabled: form.get("enabled") === "on",
      webhook_url: String(form.get("webhook_url") ?? ""),
      channel_label: String(form.get("channel_label") ?? ""),
    });
    setSlack(next);
  }

  async function handleRunScan() {
    setScanning(true);
    await triggerScan();
    setRuns(await fetchScanRuns());
    setScanning(false);
  }

  function applyPreset(presetKey: keyof typeof criteriaPresets) {
    if (!criteria) {
      return;
    }
    const preset = criteriaPresets[presetKey];
    setCriteria({
      ...criteria,
      keywords: preset.keywords,
      preferred_organisations: preset.preferred_organisations,
      event_types: preset.event_types,
    });
  }

  if (!criteria || !slack || !schedule) {
    return <section className="panel"><p className="muted">Loading settings…</p></section>;
  }

  return (
    <div className="page-stack two-column">
      <section className="panel">
        <p className="eyebrow">Weekly public scan</p>
        <h2>Automatic scan schedule</h2>
        <p className="muted">
          Public and conference layers are scanned automatically every {schedule.day_of_week.toUpperCase()} at{" "}
          {String(schedule.hour_utc).padStart(2, "0")}:{String(schedule.minute_utc).padStart(2, "0")} UTC while the backend is running.
        </p>
        <div className="status-meta">
          <span className="status-pill">Targets: {schedule.target_layers.join(", ")}</span>
          <button type="button" className="primary-button" onClick={handleRunScan} disabled={scanning}>
            {scanning ? "Scanning..." : "Run weekly scan now"}
          </button>
        </div>
        <div className="run-list">
          {runs.slice(0, 3).map((run) => (
            <div key={run.id} className="run-item">
              <strong>{run.status}</strong>
              <span className="muted">
                {run.scanned_sources} sources · {run.new_events_found} new events
              </span>
            </div>
          ))}
        </div>
      </section>

      <form className="panel form-panel" onSubmit={handleCriteriaSubmit}>
        <p className="eyebrow">Scanning criteria</p>
        <h2>Discovery rules</h2>
        <p className="muted">
          Think of this like a saved search. Broader keywords find more events; exclusions and minimum score keep the results useful.
        </p>
        <div className="preset-row">
          <button type="button" className="secondary-button" onClick={() => applyPreset("ecology")}>
            Ecology preset
          </button>
          <button type="button" className="secondary-button" onClick={() => applyPreset("gis")}>
            GIS preset
          </button>
          <button type="button" className="secondary-button" onClick={() => applyPreset("dataScience")}>
            Data science preset
          </button>
        </div>
        <label className="form-field">
          Keywords
          <textarea name="keywords" value={listToText(criteria.keywords)} onChange={(event) => setCriteria({ ...criteria, keywords: textToList(event.target.value) })} />
          <span className="helper-text">One phrase per line. These drive first-pass relevance scoring.</span>
        </label>
        <label className="form-field">
          Excluded keywords
          <textarea
            name="excluded_keywords"
            value={listToText(criteria.excluded_keywords)}
            onChange={(event) => setCriteria({ ...criteria, excluded_keywords: textToList(event.target.value) })}
          />
          <span className="helper-text">Use these to hide noisy topics like fundraising, holidays, or unrelated meetups.</span>
        </label>
        <label className="form-field">
          Preferred organisations
          <textarea
            name="preferred_organisations"
            value={listToText(criteria.preferred_organisations)}
            onChange={(event) => setCriteria({ ...criteria, preferred_organisations: textToList(event.target.value) })}
          />
          <span className="helper-text">Matches here increase the score rather than acting as a strict filter.</span>
        </label>
        <label className="form-field">
          Preferred locations
          <textarea
            name="preferred_locations"
            value={listToText(criteria.preferred_locations)}
            onChange={(event) => setCriteria({ ...criteria, preferred_locations: textToList(event.target.value) })}
          />
          <span className="helper-text">Try city names like Sydney, Melbourne, Brisbane, or Online.</span>
        </label>
        <label className="form-field">
          Event types
          <textarea name="event_types" value={listToText(criteria.event_types)} onChange={(event) => setCriteria({ ...criteria, event_types: textToList(event.target.value) })} />
          <span className="helper-text">Examples: conference, webinar, workshop, symposium.</span>
        </label>
        <label className="form-field">
          Date horizon (days)
          <input
            name="date_horizon_days"
            type="number"
            value={criteria.date_horizon_days}
            onChange={(event) => setCriteria({ ...criteria, date_horizon_days: Number(event.target.value) })}
          />
        </label>
        <label className="form-field">
          Minimum relevance score
          <input
            name="minimum_relevance_score"
            type="number"
            min="0"
            max="1"
            step="0.05"
            value={criteria.minimum_relevance_score}
            onChange={(event) => setCriteria({ ...criteria, minimum_relevance_score: Number(event.target.value) })}
          />
          <span className="helper-text">Lower it if you want more discovery. Raise it if too many weak matches appear.</span>
        </label>
        <button type="submit" className="primary-button">
          Save scan criteria
        </button>
      </form>

      <form className="panel form-panel" onSubmit={handleSlackSubmit}>
        <p className="eyebrow">Slack</p>
        <h2>Notification settings</h2>
        <label className="checkbox-row">
          <input name="enabled" type="checkbox" defaultChecked={slack.enabled} />
          Enable Slack webhook posting
        </label>
        <label className="form-field">
          Webhook URL
          <input name="webhook_url" defaultValue={slack.webhook_url ?? ""} />
        </label>
        <label className="form-field">
          Channel label
          <input name="channel_label" defaultValue={slack.channel_label ?? ""} />
        </label>
        <button type="submit" className="primary-button">
          Save Slack settings
        </button>
      </form>
    </div>
  );
}
