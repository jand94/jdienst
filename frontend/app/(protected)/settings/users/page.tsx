import RequireAccess from "@/components/auth/RequireAccess";

export default function SettingsUsersPage() {
  return (
    <RequireAccess permissions={["settings.view"]}>
      <section className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight">Einstellungen: Benutzer</h1>
        <p className="text-muted-foreground">Hier werden kuenftig Benutzerverwaltung und Rollenzuweisung gepflegt.</p>
      </section>
    </RequireAccess>
  );
}
