import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Calendar", end: true },
  { to: "/saved", label: "Saved" },
  { to: "/sources", label: "Sources" },
  { to: "/settings", label: "Settings" },
];

type Props = {
  onLogout?: () => void | Promise<void>;
};

export function AppShell({ onLogout }: Props) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Smart Calendar App</p>
          <h1>Smart Calendar</h1>
          <p className="muted">
            Personal, work, public feeds, and curated conference scanning in one calm interface.
          </p>
        </div>
        <nav className="side-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              {item.label}
            </NavLink>
          ))}
          {onLogout ? (
            <button type="button" className="nav-link logout-link" onClick={() => void onLogout()}>
              Lock
            </button>
          ) : null}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
