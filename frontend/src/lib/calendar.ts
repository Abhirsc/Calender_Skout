import {
  addDays,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  parseISO,
  startOfMonth,
  startOfWeek,
} from "date-fns";

import type { ExternalEvent } from "./types";

export type ViewMode = "month" | "week" | "agenda";

export function buildMonthGrid(currentMonth: Date): Date[] {
  return eachDayOfInterval({
    start: startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 0 }),
    end: endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 0 }),
  });
}

export function buildWeekRange(anchorDate: Date): Date[] {
  return Array.from({ length: 7 }, (_, index) => addDays(startOfWeek(anchorDate, { weekStartsOn: 0 }), index));
}

export function formatEventTime(event: ExternalEvent): string {
  return `${format(parseISO(event.start_datetime), "EEE d MMM, h:mm a")} - ${format(parseISO(event.end_datetime), "h:mm a")}`;
}

export function eventsForDay(events: ExternalEvent[], day: Date): ExternalEvent[] {
  return events.filter((event) => isSameDay(parseISO(event.start_datetime), day));
}

export function isCurrentMonth(day: Date, currentMonth: Date): boolean {
  return isSameMonth(day, currentMonth);
}

