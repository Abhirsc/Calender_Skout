import type { CalendarType } from "../lib/types";

const legend: Array<{ type: CalendarType; label: string }> = [
  { type: "work", label: "Work" },
  { type: "personal", label: "Personal" },
  { type: "public", label: "Public" },
  { type: "conferences", label: "Conferences" },
];

type Props = {
  toggles: Record<CalendarType, boolean>;
  onToggle: (type: CalendarType) => void;
};

export function CalendarLegend({ toggles, onToggle }: Props) {
  return (
    <div className="legend-row">
      {legend.map((item) => (
        <button
          key={item.type}
          type="button"
          className={`legend-chip ${item.type} ${toggles[item.type] ? "active" : "inactive"}`}
          onClick={() => onToggle(item.type)}
        >
          <span className="legend-dot" />
          {item.label}
        </button>
      ))}
    </div>
  );
}

