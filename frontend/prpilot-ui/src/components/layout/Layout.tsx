import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

export function Layout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <TopBar />
        <div className="app-content fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
