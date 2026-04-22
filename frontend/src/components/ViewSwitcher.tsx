import type { ViewMode } from "../lib/calendar";

type Props = {
  value: ViewMode;
  onChange: (value: ViewMode) => void;
};

export function ViewSwitcher({ value, onChange }: Props) {
  const options: ViewMode[] = ["month", "week", "agenda"];
  return (
    <div className="segment-control">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className={value === option ? "segment-button active" : "segment-button"}
          onClick={() => onChange(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
}

