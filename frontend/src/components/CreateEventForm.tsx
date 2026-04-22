import { addHours, format } from "date-fns";
import { FormEvent, useEffect, useState } from "react";

type Props = {
  isOpen: boolean;
  selectedDate: Date | null;
  onClose: () => void;
  onCreate: (payload: {
    title: string;
    description: string;
    start_datetime: string;
    end_datetime: string;
    timezone: string;
    location: string;
    url: string;
    source_name: string;
    calendar_type: string;
    category: string;
    tags: string[];
  }) => Promise<void>;
};

const initialForm = {
  title: "",
  description: "",
  start_datetime: "",
  end_datetime: "",
  timezone: "Australia/Sydney",
  location: "",
  url: "",
  source_name: "Manual Entry",
  calendar_type: "personal",
  category: "personal",
  tags: "",
};

function buildDatePrefill(selectedDate: Date | null) {
  if (!selectedDate) {
    return {
      start_datetime: "",
      end_datetime: "",
    };
  }

  const start = new Date(selectedDate);
  start.setHours(9, 0, 0, 0);
  const end = addHours(start, 1);
  return {
    start_datetime: format(start, "yyyy-MM-dd'T'HH:mm"),
    end_datetime: format(end, "yyyy-MM-dd'T'HH:mm"),
  };
}

export function CreateEventForm({ isOpen, selectedDate, onClose, onCreate }: Props) {
  const [form, setForm] = useState(initialForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    setError("");
    setForm((current) => ({
      ...current,
      ...buildDatePrefill(selectedDate),
    }));
  }, [isOpen, selectedDate]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await onCreate({
        ...form,
        tags: form.tags.split(",").map((item) => item.trim()).filter(Boolean),
      });
      setForm(initialForm);
      onClose();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Unable to create event.");
    } finally {
      setSubmitting(false);
    }
  }

  if (!isOpen) {
    return null;
  }

  return (
    <aside className="drawer-backdrop" onClick={onClose}>
      <form className="drawer create-event-modal form-panel" onClick={(event) => event.stopPropagation()} onSubmit={handleSubmit}>
        <div className="drawer-header">
          <div>
            <p className="eyebrow">Create event</p>
            <h2>Add event on {selectedDate ? format(selectedDate, "EEE d MMM") : "calendar"}</h2>
          </div>
          <button type="button" className="icon-button" onClick={onClose}>
            ×
          </button>
        </div>
        <label className="form-field">
          Title
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required autoFocus />
        </label>
        <label className="form-field">
          Description
          <textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
        </label>
        <div className="form-grid">
          <label className="form-field">
            Start
            <input
              type="datetime-local"
              value={form.start_datetime}
              onChange={(event) => setForm({ ...form, start_datetime: event.target.value })}
              required
            />
          </label>
          <label className="form-field">
            End
            <input
              type="datetime-local"
              value={form.end_datetime}
              onChange={(event) => setForm({ ...form, end_datetime: event.target.value })}
              required
            />
          </label>
        </div>
        <div className="form-grid">
        <label className="form-field">
          Calendar layer
          <select
            value={form.calendar_type}
            onChange={(event) => setForm({ ...form, calendar_type: event.target.value, category: event.target.value })}
          >
            <option value="work">Work</option>
            <option value="personal">Personal</option>
            <option value="public">Public</option>
            <option value="conferences">Conferences</option>
          </select>
        </label>
        <label className="form-field">
          Source name
          <input value={form.source_name} onChange={(event) => setForm({ ...form, source_name: event.target.value })} />
        </label>
        </div>
        <div className="form-grid">
        <label className="form-field">
          Location
          <input value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} />
        </label>
        <label className="form-field">
          Link
          <input value={form.url} onChange={(event) => setForm({ ...form, url: event.target.value })} />
        </label>
        </div>
        <label className="form-field">
          Tags
          <input value={form.tags} onChange={(event) => setForm({ ...form, tags: event.target.value })} placeholder="conference, gis, planning" />
        </label>
        {error ? <p className="error-text">{error}</p> : null}
        <div className="drawer-actions">
          <button type="button" className="secondary-button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? "Creating..." : "Create event"}
          </button>
        </div>
      </form>
    </aside>
  );
}
