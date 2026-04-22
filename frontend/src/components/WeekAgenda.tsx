import { format, parseISO } from "date-fns";

import { buildWeekRange, eventsForDay } from "../lib/calendar";
import type { ExternalEvent } from "../lib/types";

type Props = {
  anchorDate: Date;
  events: ExternalEvent[];
  onSelectEvent: (event: ExternalEvent) => void;
  onSelectDate: (date: Date) => void;
};

export function WeekAgenda({ anchorDate, events, onSelectEvent, onSelectDate }: Props) {
  const days = buildWeekRange(anchorDate);

  return (
    <section className="panel week-list">
      {days.map((day) => {
        const items = eventsForDay(events, day);
        return (
          <div key={day.toISOString()} className="week-day">
            <div className="week-label">
              <div>
                <span>{format(day, "EEE")}</span>
                <strong>{format(day, "d MMM")}</strong>
              </div>
              <button type="button" className="day-add-button" onClick={() => onSelectDate(day)}>
                +
              </button>
            </div>
            <div className="week-events">
              {items.length === 0 ? <p className="muted">No events</p> : null}
              {items.map((event) => (
                <button
                  key={event.id}
                  type="button"
                  className={`event-card ${event.calendar_type}`}
                  onClick={() => onSelectEvent(event)}
                >
                  <span>{event.title}</span>
                  <small>{format(parseISO(event.start_datetime), "h:mm a")}</small>
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </section>
  );
}
