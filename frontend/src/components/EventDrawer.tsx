import { useState } from "react";

import { eventCalendarDownloadUrl } from "../lib/api";
import { formatEventTime } from "../lib/calendar";
import type { ExternalEvent } from "../lib/types";

type SavePayload = {
  pinned: boolean;
  personal_notes: string;
  follow_up_action: string;
  thoughts: string[];
  why_it_matters: string;
  links: string[];
  post_to_slack: boolean;
};

type Props = {
  event: ExternalEvent | null;
  onClose: () => void;
  onSave: (payload: SavePayload) => Promise<void>;
  onDelete: (eventId: number) => Promise<void>;
};

export function EventDrawer({ event, onClose, onSave, onDelete }: Props) {
  const [notes, setNotes] = useState("");
  const [followUp, setFollowUp] = useState("");
  const [thoughts, setThoughts] = useState("");
  const [whyItMatters, setWhyItMatters] = useState("");
  const [linkText, setLinkText] = useState("");
  const [postToSlack, setPostToSlack] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  if (!event) {
    return null;
  }

  const activeEvent = event;

  async function handleSave() {
    setSaving(true);
    try {
      await onSave({
        pinned: true,
        personal_notes: notes,
        follow_up_action: followUp,
        thoughts: thoughts.split("\n").map((item) => item.trim()).filter(Boolean),
        why_it_matters: whyItMatters,
        links: linkText.split("\n").map((item) => item.trim()).filter(Boolean),
        post_to_slack: postToSlack,
      });
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    const confirmed = window.confirm(`Delete "${activeEvent.title}" from the calendar?`);
    if (!confirmed) {
      return;
    }

    setDeleting(true);
    try {
      await onDelete(activeEvent.id);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <aside className="drawer-backdrop" onClick={onClose}>
      <div className="drawer" onClick={(event_) => event_.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow">{event.source_name}</p>
            <h2>{activeEvent.title}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="drawer-meta">
          <p>{formatEventTime(activeEvent)}</p>
          <p>{activeEvent.location || "Location TBA"}</p>
          <p>Relevance score {activeEvent.relevance_score}</p>
        </div>
        <label className="form-field">
          Notes
          <textarea value={notes} onChange={(item) => setNotes(item.target.value)} placeholder="Why this event matters..." />
        </label>
        <label className="form-field">
          Follow-up
          <input value={followUp} onChange={(item) => setFollowUp(item.target.value)} placeholder="Next action" />
        </label>
        <label className="form-field">
          Quick thoughts
          <textarea value={thoughts} onChange={(item) => setThoughts(item.target.value)} placeholder="One note per line" />
        </label>
        <label className="form-field">
          Why it matters
          <input value={whyItMatters} onChange={(item) => setWhyItMatters(item.target.value)} placeholder="Connection to your work" />
        </label>
        <label className="form-field">
          Links
          <textarea value={linkText} onChange={(item) => setLinkText(item.target.value)} placeholder="One URL per line" />
        </label>
        <label className="checkbox-row">
          <input type="checkbox" checked={postToSlack} onChange={(item) => setPostToSlack(item.target.checked)} />
          Post to Slack when saved
        </label>
        <div className="drawer-actions">
          <a className="secondary-button link-button" href={eventCalendarDownloadUrl(activeEvent.id)}>
            Add to calendar
          </a>
          <button type="button" className="danger-button" onClick={handleDelete} disabled={deleting || saving}>
            {deleting ? "Deleting..." : "Delete"}
          </button>
          <button type="button" className="secondary-button" onClick={onClose}>
            Close
          </button>
          <button type="button" className="primary-button" onClick={handleSave} disabled={saving || deleting}>
            {saving ? "Saving..." : "Save & pin"}
          </button>
        </div>
      </div>
    </aside>
  );
}
