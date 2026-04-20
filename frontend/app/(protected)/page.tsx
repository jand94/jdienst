import { responsiveTokens } from "@/lib/responsive-tokens";
import RequireAccess from "@/components/auth/RequireAccess";

export default function DashboardPage() {
  return (
    <RequireAccess permissions={["dashboard.view"]}>
      <section className={responsiveTokens.sectionSpacing}>
        <header className={responsiveTokens.headerSpacing}>
          <h1 className="text-3xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Willkommen im neuen App-Layout mit responsiver Navigation.</p>
        </header>

        <div className={responsiveTokens.cardGrid}>
          <article className="rounded-xl border bg-card p-5 shadow-sm">
            <h2 className="mb-1 text-base font-semibold">Aktive Projekte</h2>
            <p className="text-2xl font-bold">12</p>
            <p className="text-sm text-muted-foreground">+2 seit letzter Woche</p>
          </article>
          <article className="rounded-xl border bg-card p-5 shadow-sm">
            <h2 className="mb-1 text-base font-semibold">Offene Tasks</h2>
            <p className="text-2xl font-bold">31</p>
            <p className="text-sm text-muted-foreground">6 mit hoher Prioritaet</p>
          </article>
          <article className="rounded-xl border bg-card p-5 shadow-sm">
            <h2 className="mb-1 text-base font-semibold">Systemstatus</h2>
            <p className="text-2xl font-bold text-emerald-600">Stabil</p>
            <p className="text-sm text-muted-foreground">Keine Stoerungen Test</p>
          </article>
        </div>
      </section>
    </RequireAccess>
  );
}
