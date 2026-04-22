import { format, parseISO } from "date-fns";
import { useState } from "react";

import { addScannedEventToCalendar, deleteEvent, eventCalendarDownloadUrl } from "../lib/api";
import type { ExternalEvent } from "../lib/types";

type Props = {
  events: ExternalEvent[];
  onSelectEvent: (event: ExternalEvent) => void;
  onAdded?: () => Promise<void>;
};

export function DiscoverPanel({ events, onSelectEvent, onAdded }: Props) {
  const [addingId, setAddingId] = useState<number | null>(null);
  const [dismissingId, setDismissingId] = useState<number | null>(null);

  async function handleAdd(event: ExternalEvent) {
    setAddingId(event.id);
    try {
      await addScannedEventToCalendar(event.id, { calendar_type: "personal", source_name: "Added from scan" });
      if (onAdded) {
        await onAdded();
      }
    } finally {
      setAddingId(null);
    }
  }

  async function handleDismiss(event: ExternalEvent) {
    const confirmed = window.confirm(`Remove "${event.title}" from scanned suggestions?`);
    if (!confirmed) {
      return;
    }

    setDismissingId(event.id);
    try {
      await deleteEvent(event.id);
      if (onAdded) {
        await onAdded();
      }
    } finally {
      setDismissingId(null);
    }
  }

  return (
    <section className="panel">
      <div className="panel-header discover-header">
        <div>
          <p className="eyebrow">Scanned opportunities</p>
          <h2>Review before adding to your calendar</h2>
          <p className="muted">
            Public and conference results appear here after a scan so you can inspect them first, then save or add them.
          </p>
        </div>
        <span className="status-pill">{events.length} visible</span>
      </div>
      <div className="discover-list">
        {events.map((event) => (
          <article key={event.id} className={`discover-card ${event.calendar_type}`}>
            <div className="discover-main">
              <div>
                <div className="discover-title-row">
                  <h3>{event.title}</h3>
                  <span className="score-badge">Score {event.relevance_score.toFixed(2)}</span>
                </div>
                <p className="muted">
                  {event.source_name} · {format(parseISO(event.start_datetime), "EEE d MMM, h:mm a")}
                </p>
                <p className="muted">{event.location || "Location TBA"}</p>
              </div>
              <div className="discover-actions">
                <button type="button" className="secondary-button" onClick={() => onSelectEvent(event)}>
                  Review
                </button>
                <button type="button" className="primary-button" onClick={() => void handleAdd(event)} disabled={addingId === event.id}>
                  {addingId === event.id ? "Adding..." : "Add to my calendar"}
                </button>
                <button
                  type="button"
                  className="danger-button"
                  onClick={() => void handleDismiss(event)}
                  disabled={dismissingId === event.id}
                >
                  {dismissingId === event.id ? "Removing..." : "Not interested"}
                </button>
                <a className="secondary-button link-button" href={eventCalendarDownloadUrl(event.id)}>
                  Download ICS
                </a>
              </div>
            </div>
          </article>
        ))}
        {events.length === 0 ? <p className="muted">No scanned public opportunities are visible yet. Run the weekly scan or broaden the criteria.</p> : null}
      </div>
    </section>
  );
}
