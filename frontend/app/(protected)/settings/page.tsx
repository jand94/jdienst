import RequireAccess from "@/components/auth/RequireAccess";

export default function SettingsPage() {
  return (
    <RequireAccess permissions={["settings.view"]}>
      <section className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Einstellungen</h1>
        <p className="text-muted-foreground">Hier werden tenant- und profilbezogene Einstellungen bereitgestellt.</p>
      </section>
    </RequireAccess>
  );
}
