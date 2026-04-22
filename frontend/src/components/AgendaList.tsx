import { format, parseISO } from "date-fns";

import type { ExternalEvent } from "../lib/types";

type Props = {
  events: ExternalEvent[];
  onSelectEvent: (event: ExternalEvent) => void;
};

export function AgendaList({ events, onSelectEvent }: Props) {
  return (
    <section className="panel agenda-list">
      {events.map((event) => (
        <button key={event.id} type="button" className={`agenda-row ${event.calendar_type}`} onClick={() => onSelectEvent(event)}>
          <div>
            <p>{event.title}</p>
            <span>{event.source_name}</span>
          </div>
          <div className="agenda-meta">
            <strong>{format(parseISO(event.start_datetime), "EEE d MMM")}</strong>
            <small>{format(parseISO(event.start_datetime), "h:mm a")}</small>
          </div>
        </button>
      ))}
    </section>
  );
}

