import { useEffect, useState } from "react";

import { deleteEvent, deleteSavedEvent, fetchSavedEvents, updateSavedNotes } from "../lib/api";
import type { SavedEventRecord } from "../lib/types";

export function SavedPage() {
  const [items, setItems] = useState<SavedEventRecord[]>([]);

  useEffect(() => {
    void fetchSavedEvents().then(setItems);
  }, []);

  async function handleQuickSave(item: SavedEventRecord, personalNotes: string) {
    await updateSavedNotes(item.saved_event.id, {
      personal_notes: personalNotes,
      follow_up_action: item.saved_event.follow_up_action,
      thoughts: item.note?.thoughts ?? [],
      why_it_matters: item.note?.why_it_matters,
      links: item.note?.links ?? [],
    });
    setItems(await fetchSavedEvents());
  }

  async function handleDelete(item: SavedEventRecord) {
    const confirmed = window.confirm(`Delete "${item.event.title}" from the calendar?`);
    if (!confirmed) {
      return;
    }

    await deleteEvent(item.event.id);
    setItems(await fetchSavedEvents());
  }

  async function handleRemoveSaved(item: SavedEventRecord) {
    const confirmed = window.confirm(`Remove "${item.event.title}" from Saved?`);
    if (!confirmed) {
      return;
    }

    await deleteSavedEvent(item.saved_event.id);
    setItems(await fetchSavedEvents());
  }

  return (
    <div className="page-stack">
      <section className="panel">
        <p className="eyebrow">Saved opportunities</p>
        <h2>Pinned events and notes</h2>
        <p className="muted">Keep rationale, follow-up actions, and useful links attached to event decisions.</p>
      </section>
      <section className="saved-grid">
        {items.map((item) => (
          <article key={item.saved_event.id} className={`panel saved-card ${item.event.calendar_type}`}>
            <div className="saved-card-header">
              <div>
                <p className="eyebrow">{item.event.source_name}</p>
                <h3>{item.event.title}</h3>
              </div>
              {item.saved_event.pinned ? <span className="status-pill">Pinned</span> : null}
            </div>
            <p className="muted">{item.event.location || "Location TBA"}</p>
            <label className="form-field">
              Notes
              <textarea
                defaultValue={item.saved_event.personal_notes ?? ""}
                onBlur={(event) => void handleQuickSave(item, event.target.value)}
              />
            </label>
            <div className="tag-row">
              {(item.note?.thoughts ?? []).map((thought) => (
                <span key={thought} className="tag-chip">
                  {thought}
                </span>
              ))}
            </div>
            <div className="saved-card-actions">
              <button type="button" className="secondary-button" onClick={() => void handleRemoveSaved(item)}>
                Remove from saved
              </button>
              <button type="button" className="danger-button" onClick={() => void handleDelete(item)}>
                Delete event
              </button>
            </div>
          </article>
        ))}
        {items.length === 0 ? <section className="panel"><p className="muted">No saved events yet.</p></section> : null}
      </section>
    </div>
  );
}
