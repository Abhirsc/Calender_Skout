import { format, isToday } from "date-fns";

import { buildMonthGrid, eventsForDay, isCurrentMonth } from "../lib/calendar";
import type { ExternalEvent } from "../lib/types";

type Props = {
  currentMonth: Date;
  events: ExternalEvent[];
  onSelectEvent: (event: ExternalEvent) => void;
  onSelectDate: (date: Date) => void;
};

export function MonthCalendar({ currentMonth, events, onSelectEvent, onSelectDate }: Props) {
  const days = buildMonthGrid(currentMonth);

  return (
    <section className="panel">
      <div className="calendar-grid weekday-header">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
          <div key={day} className="weekday-cell">
            {day}
          </div>
        ))}
      </div>
      <div className="calendar-grid">
        {days.map((day) => {
          const items = eventsForDay(events, day);
          return (
            <article
              key={day.toISOString()}
              className={`day-cell ${isCurrentMonth(day, currentMonth) ? "" : "outside"} ${isToday(day) ? "today" : ""}`}
            >
              <header className="day-cell-header">
                <span>{format(day, "d")}</span>
                <button type="button" className="day-add-button" onClick={() => onSelectDate(day)}>
                  +
                </button>
              </header>
              <div className="day-events">
                {items.slice(0, 3).map((event) => (
                  <button
                    key={event.id}
                    type="button"
                    className={`event-pill ${event.calendar_type}`}
                    onClick={(clickEvent) => {
                      clickEvent.stopPropagation();
                      onSelectEvent(event);
                    }}
                  >
                    {event.title}
                  </button>
                ))}
                {items.length > 3 ? <span className="more-label">+{items.length - 3} more</span> : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
