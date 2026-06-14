import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Dashboard', icon: '⊞', end: true },
  { to: '/repositories', label: 'Repositories', icon: '◫' },
  { to: '/pull-requests', label: 'Pull Requests', icon: '⌥' },
  { to: '/analyses', label: 'Analyses', icon: '◈' },
  { to: '/intelligence', label: 'Intelligence', icon: '✦' },
];

export function Sidebar() {
  return (
    <aside className="app-sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon">🛩</div>
        <div>
          <div className="sidebar-logo-text">PRPilot</div>
          <div className="sidebar-logo-sub">AI · PR Intelligence</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Navigation</div>
        {navItems.map(({ to, label, icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'active' : ''}`
            }
          >
            <span className="nav-item-icon">{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div style={{ marginBottom: 2, fontWeight: 600 }}>PRPilot v0.1.0</div>
        <div style={{ opacity: 0.6 }}>Microsoft AI Hackathon</div>
      </div>
    </aside>
  );
}
