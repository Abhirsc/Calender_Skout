import { formatDistanceToNow, parseISO } from "date-fns";

type Props = {
  lastScanAt?: string | null;
  sourceCount: number;
  onScan: () => void;
  busy: boolean;
  progress: number;
  progressLabel: string;
  progressDetail: string;
  latestNewEvents?: number;
};

export function StatusCard({ lastScanAt, sourceCount, onScan, busy, progress, progressLabel, progressDetail, latestNewEvents }: Props) {
  return (
    <section className="panel status-card">
      <div>
        <p className="eyebrow">Weekly scan</p>
        <h2>Public source monitor</h2>
        <p className="muted">
          Tracking {sourceCount} configured sources across public feeds and conference discovery.
        </p>
      </div>
      <div className="status-meta">
        <span className="status-pill">
          {lastScanAt ? `Last scan ${formatDistanceToNow(parseISO(lastScanAt), { addSuffix: true })}` : "No scan yet"}
        </span>
        {typeof latestNewEvents === "number" ? <span className="status-pill">{latestNewEvents} new events last run</span> : null}
        <button type="button" className="primary-button" onClick={onScan} disabled={busy}>
          {busy ? "Scanning..." : "Run scan now"}
        </button>
      </div>
      <div className="scan-progress">
        <div className="scan-progress-bar" aria-hidden="true">
          <div className="scan-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <div className="scan-progress-meta">
          <span>{progressLabel}</span>
          <strong>{Math.round(progress)}%</strong>
        </div>
        <p className="scan-progress-detail">{progressDetail}</p>
      </div>
    </section>
  );
}
