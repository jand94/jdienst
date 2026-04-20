import RequireAccess from "@/components/auth/RequireAccess";

export default function SettingsCrmPage() {
  return (
    <RequireAccess permissions={["settings.view"]}>
      <section className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Einstellungen: CRM</h1>
        <p className="text-muted-foreground">Hier werden kuenftig CRM-Module und Integrationen konfiguriert.</p>
      </section>
    </RequireAccess>
  );
}
