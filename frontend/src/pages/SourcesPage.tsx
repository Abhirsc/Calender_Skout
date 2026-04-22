import { FormEvent, useEffect, useState } from "react";

import { deleteSource, fetchSources, uploadIcsSource, upsertSource } from "../lib/api";
import type { CalendarSource } from "../lib/types";

const emptyForm = {
  name: "",
  type: "ics",
  url: "",
  enabled: true,
  category: "public",
  calendar_type: "public",
  scan_frequency: "weekly",
  preferred_weight: 0.5,
  config: {},
};

export function SourcesPage() {
  const [sources, setSources] = useState<CalendarSource[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [uploadName, setUploadName] = useState("");
  const [uploadCategory, setUploadCategory] = useState("public");
  const [uploadCalendarType, setUploadCalendarType] = useState("public");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState("");

  useEffect(() => {
    void fetchSources().then(setSources);
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await upsertSource(null, form);
    setSources(await fetchSources());
    setForm(emptyForm);
  }

  async function handleUpload(event: FormEvent) {
    event.preventDefault();
    if (!uploadFile) {
      setUploadError("Choose an .ics file first.");
      return;
    }
    setUploadError("");
    await uploadIcsSource({
      name: uploadName || uploadFile.name,
      calendar_type: uploadCalendarType,
      category: uploadCategory,
      scan_frequency: "weekly",
      preferred_weight: 0.5,
      file: uploadFile,
    });
    setSources(await fetchSources());
    setUploadName("");
    setUploadCategory("public");
    setUploadCalendarType("public");
    setUploadFile(null);
  }

  async function handleDeleteSource(source: CalendarSource) {
    const confirmed = window.confirm(`Delete source "${source.name}"?`);
    if (!confirmed) {
      return;
    }

    await deleteSource(source.id);
    setSources(await fetchSources());
  }

  return (
    <div className="page-stack two-column">
      <section className="panel">
        <p className="eyebrow">Sources</p>
        <h2>Feed management</h2>
        <p className="muted">Editable seed sources are ready for ICS, manual, and future Outlook-backed imports.</p>
        <div className="source-list">
          {sources.map((source) => (
            <article key={source.id} className="source-item">
              <div>
                <strong>{source.name}</strong>
                <p className="muted">
                  {source.type.toUpperCase()} · {source.calendar_type} · {source.enabled ? "Enabled" : "Disabled"}
                </p>
              </div>
              <div className="source-actions">
                <span className="status-pill">{source.scan_frequency}</span>
                <button type="button" className="danger-button" onClick={() => void handleDeleteSource(source)}>
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      </section>

      <div className="page-stack">
      <form className="panel form-panel" onSubmit={handleSubmit}>
        <p className="eyebrow">Add source</p>
        <h2>New calendar feed</h2>
        <label className="form-field">
          Name
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
        </label>
        <label className="form-field">
          Type
          <select value={form.type} onChange={(event) => setForm({ ...form, type: event.target.value })}>
            <option value="ics">ICS</option>
            <option value="manual">Manual</option>
            <option value="rss">RSS</option>
            <option value="outlook">Outlook</option>
          </select>
        </label>
        <label className="form-field">
          URL
          <input value={form.url} onChange={(event) => setForm({ ...form, url: event.target.value })} />
        </label>
        <label className="form-field">
          Category
          <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>
            <option value="public">Public</option>
            <option value="conferences">Conferences</option>
            <option value="personal">Personal</option>
            <option value="work">Work</option>
          </select>
        </label>
        <button type="submit" className="primary-button">
          Save source
        </button>
      </form>
      <form className="panel form-panel" onSubmit={handleUpload}>
        <p className="eyebrow">Upload ICS</p>
        <h2>Import calendar file</h2>
        <label className="form-field">
          Name
          <input value={uploadName} onChange={(event) => setUploadName(event.target.value)} placeholder="Conference file, personal export, team calendar" />
        </label>
        <div className="form-grid">
          <label className="form-field">
            Calendar layer
            <select value={uploadCalendarType} onChange={(event) => { setUploadCalendarType(event.target.value); setUploadCategory(event.target.value); }}>
              <option value="public">Public</option>
              <option value="conferences">Conferences</option>
              <option value="personal">Personal</option>
              <option value="work">Work</option>
            </select>
          </label>
          <label className="form-field">
            ICS file
            <input type="file" accept=".ics,text/calendar" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} />
          </label>
        </div>
        {uploadError ? <p className="error-text">{uploadError}</p> : null}
        <button type="submit" className="primary-button">
          Upload .ics source
        </button>
      </form>
      </div>
    </div>
  );
}
