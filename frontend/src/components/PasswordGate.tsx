import { FormEvent, useState } from "react";

type Props = {
  onUnlock: (password: string) => Promise<boolean>;
};

export function PasswordGate({ onUnlock }: Props) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const ok = await onUnlock(password);
    if (!ok) {
      setError("Incorrect password.");
    }
    setSubmitting(false);
  }

  return (
    <main className="gate-shell">
      <form className="panel gate-card form-panel" onSubmit={handleSubmit}>
        <p className="eyebrow">Protected app</p>
        <h1>Enter password</h1>
        <p className="muted">
          This shared smart calendar is public on the web, but access is currently protected with a simple password lock.
        </p>
        <label className="form-field">
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Shared password"
            required
          />
        </label>
        {error ? <p className="error-text">{error}</p> : null}
        <button type="submit" className="primary-button" disabled={submitting}>
          {submitting ? "Unlocking..." : "Unlock app"}
        </button>
      </form>
    </main>
  );
}
