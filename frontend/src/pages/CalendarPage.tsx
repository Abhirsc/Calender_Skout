import { addMonths, format, subMonths } from "date-fns";
import { useEffect, useMemo, useRef, useState } from "react";

import { AgendaList } from "../components/AgendaList";
import { CalendarLegend } from "../components/CalendarLegend";
import { CreateEventForm } from "../components/CreateEventForm";
import { DiscoverPanel } from "../components/DiscoverPanel";
import { EventDrawer } from "../components/EventDrawer";
import { MonthCalendar } from "../components/MonthCalendar";
import { StatusCard } from "../components/StatusCard";
import { ViewSwitcher } from "../components/ViewSwitcher";
import { WeekAgenda } from "../components/WeekAgenda";
import type { ViewMode } from "../lib/calendar";
import { createEvent, deleteEvent, fetchEvents, fetchScanRuns, fetchSources, saveEvent, triggerScan } from "../lib/api";
import type { CalendarSource, CalendarType, ExternalEvent, ScanRun } from "../lib/types";

const initialToggles: Record<CalendarType, boolean> = {
  work: true,
  personal: true,
  public: true,
  conferences: true,
};

export function CalendarPage() {
  const [events, setEvents] = useState<ExternalEvent[]>([]);
  const [viewMode, setViewMode] = useState<ViewMode>("month");
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<ExternalEvent | null>(null);
  const [selectedCreateDate, setSelectedCreateDate] = useState<Date | null>(null);
  const [toggles, setToggles] = useState(initialToggles);
  const [scanRuns, setScanRuns] = useState<ScanRun[]>([]);
  const [sources, setSources] = useState<CalendarSource[]>([]);
  const [sourceCount, setSourceCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanProgressLabel, setScanProgressLabel] = useState("Ready to scan public feeds");
  const [scanProgressDetail, setScanProgressDetail] = useState("Waiting to scan public and conference sources.");
  const scanIntervalRef = useRef<number | null>(null);
  const scanTimeoutsRef = useRef<number[]>([]);

  useEffect(() => {
    void Promise.all([fetchEvents(), fetchScanRuns(), fetchSources()]).then(([eventItems, runs, sources]) => {
      setEvents(eventItems);
      setScanRuns(runs);
      setSources(sources);
      setSourceCount(sources.length);
    });
  }, []);

  const filteredEvents = useMemo(
    () => events.filter((event) => toggles[event.calendar_type]),
    [events, toggles],
  );
  const discoveredEvents = useMemo(
    () =>
      events
        .filter((event) => ["public", "conferences"].includes(event.calendar_type))
        .sort((left, right) => {
          if (right.relevance_score !== left.relevance_score) {
            return right.relevance_score - left.relevance_score;
          }
          return right.created_at.localeCompare(left.created_at);
        })
        .slice(0, 8),
    [events],
  );

  const lastScanAt = scanRuns[0]?.finished_at ?? scanRuns[0]?.started_at ?? null;
  const latestNewEvents = scanRuns[0]?.new_events_found;

  useEffect(() => {
    return () => {
      if (scanIntervalRef.current) {
        window.clearInterval(scanIntervalRef.current);
      }
      scanTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
    };
  }, []);

  function handleToggle(type: CalendarType) {
    setToggles((current) => ({ ...current, [type]: !current[type] }));
  }

  async function handleSave(payload: Record<string, unknown>) {
    if (!selectedEvent) {
      return;
    }
    await saveEvent(selectedEvent.id, payload);
    const nextEvents = await fetchEvents();
    setEvents(nextEvents);
    setSelectedEvent(nextEvents.find((item) => item.id === selectedEvent.id) ?? null);
  }

  async function handleRunScan() {
    const publicSources = sources.filter(
      (source) => source.enabled && (source.calendar_type === "public" || source.calendar_type === "conferences"),
    );

    const scanStartedAt = Date.now();
    setBusy(true);
    setScanProgress(8);
    setScanProgressLabel("Connecting to public sources");
    setScanProgressDetail(
      publicSources.length > 0
        ? `Preparing ${publicSources.length} sources: ${publicSources.map((source) => source.name).join(", ")}`
        : "No enabled public or conference sources are configured.",
    );

    if (scanIntervalRef.current) {
      window.clearInterval(scanIntervalRef.current);
    }
    scanTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
    scanTimeoutsRef.current = [];
    scanIntervalRef.current = window.setInterval(() => {
      setScanProgress((current) => {
        if (current >= 88) {
          return current;
        }
        return current + 9;
      });
    }, 350);

    try {
      const queueTimeout = (delay: number, action: () => void) => {
        const timeoutId = window.setTimeout(action, delay);
        scanTimeoutsRef.current.push(timeoutId);
      };

      publicSources.forEach((source, index) => {
        queueTimeout(index * 700 + 250, () => {
          setScanProgressLabel(`Scanning ${source.calendar_type} layer`);
          setScanProgressDetail(`Checking source ${index + 1} of ${publicSources.length}: ${source.name}`);
        });
      });

      queueTimeout(Math.max(publicSources.length * 700, 700), () => {
        setScanProgressLabel("Scoring relevance");
        setScanProgressDetail("Comparing keywords, event types, preferred organisations, and timing.");
      });
      queueTimeout(Math.max(publicSources.length * 700, 700) + 500, () => {
        setScanProgressLabel("Refreshing discovered events");
        setScanProgressDetail("Updating the review panel with the latest public opportunities.");
      });

      await triggerScan();
      const [nextEvents, nextRuns] = await Promise.all([fetchEvents(), fetchScanRuns()]);
      setEvents(nextEvents);
      setScanRuns(nextRuns);
      setScanProgress(100);
      setScanProgressLabel(`Scan complete${nextRuns[0] ? `, ${nextRuns[0].new_events_found} new events found` : ""}`);
      setScanProgressDetail(
        publicSources.length > 0
          ? `Finished scanning ${publicSources.length} sources: ${publicSources.map((source) => source.name).join(", ")}`
          : "Scan completed with no enabled public sources.",
      );
    } finally {
      if (scanIntervalRef.current) {
        window.clearInterval(scanIntervalRef.current);
        scanIntervalRef.current = null;
      }
      scanTimeoutsRef.current.forEach((timeoutId) => window.clearTimeout(timeoutId));
      scanTimeoutsRef.current = [];
      const elapsed = Date.now() - scanStartedAt;
      const minimumVisibleDuration = 2400;
      const settleDelay = Math.max(minimumVisibleDuration - elapsed, 900);
      window.setTimeout(() => {
        setBusy(false);
        setScanProgress(0);
        setScanProgressLabel("Ready to scan public feeds");
        setScanProgressDetail("Waiting to scan public and conference sources.");
      }, settleDelay);
    }
  }

  async function handleCreateEvent(payload: Record<string, unknown>) {
    await createEvent(payload);
    setEvents(await fetchEvents());
  }

  async function handleDeleteEvent(eventId: number) {
    await deleteEvent(eventId);
    const nextEvents = await fetchEvents();
    setEvents(nextEvents);
    setSelectedEvent(null);
  }

  return (
    <div className="page-stack">
      <section className="hero panel">
        <div>
          <p className="eyebrow">Unified calendar</p>
          <h2>{format(currentMonth, "MMMM yyyy")}</h2>
          <p className="muted">Dark, clean, responsive calendar for work, personal, public, and conference events.</p>
        </div>
        <div className="hero-actions">
          <button type="button" className="icon-button" onClick={() => setCurrentMonth((value) => subMonths(value, 1))}>
            ←
          </button>
          <button type="button" className="icon-button" onClick={() => setCurrentMonth(new Date())}>
            Today
          </button>
          <button type="button" className="icon-button" onClick={() => setCurrentMonth((value) => addMonths(value, 1))}>
            →
          </button>
        </div>
      </section>

      <CalendarLegend toggles={toggles} onToggle={handleToggle} />
      <div className="calendar-toolbar">
        <ViewSwitcher value={viewMode} onChange={setViewMode} />
      </div>

      {viewMode === "month" ? (
        <MonthCalendar currentMonth={currentMonth} events={filteredEvents} onSelectEvent={setSelectedEvent} onSelectDate={setSelectedCreateDate} />
      ) : null}
      {viewMode === "week" ? (
        <WeekAgenda anchorDate={currentMonth} events={filteredEvents} onSelectEvent={setSelectedEvent} onSelectDate={setSelectedCreateDate} />
      ) : null}
      {viewMode === "agenda" ? <AgendaList events={filteredEvents} onSelectEvent={setSelectedEvent} /> : null}

      <StatusCard
        lastScanAt={lastScanAt}
        sourceCount={sourceCount}
        onScan={handleRunScan}
        busy={busy}
        progress={scanProgress}
        progressLabel={scanProgressLabel}
        progressDetail={scanProgressDetail}
        latestNewEvents={latestNewEvents}
      />
      <DiscoverPanel
        events={discoveredEvents}
        onSelectEvent={setSelectedEvent}
        onAdded={async () => {
          setEvents(await fetchEvents());
        }}
      />
      <CreateEventForm
        isOpen={selectedCreateDate !== null}
        selectedDate={selectedCreateDate}
        onClose={() => setSelectedCreateDate(null)}
        onCreate={handleCreateEvent}
      />

      <EventDrawer event={selectedEvent} onClose={() => setSelectedEvent(null)} onSave={handleSave} onDelete={handleDeleteEvent} />
    </div>
  );
}
