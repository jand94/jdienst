import RequireAccess from "@/components/auth/RequireAccess";

export default function ReportsPage() {
  return (
    <RequireAccess permissions={["reports.view"]}>
      <section className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Reports</h1>
        <p className="text-muted-foreground">Dieser Bereich wird schrittweise ausgebaut.</p>
      </section>
    </RequireAccess>
  );
}
