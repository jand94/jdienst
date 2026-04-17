"use client";

import { FormEvent, Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";

function LoginForm() {
  const auth = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const nextPath = useMemo(() => searchParams.get("next") || "/", [searchParams]);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (auth.status === "authenticated") {
      router.replace(nextPath);
    }
  }, [auth.status, nextPath, router]);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    try {
      await auth.signIn({ username, password });
      router.replace(nextPath);
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Anmeldung fehlgeschlagen.");
    }
  };

  return (
    <section className="mx-auto flex w-full max-w-md flex-col gap-6 rounded-xl border bg-card p-6 shadow-sm">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold">Anmeldung</h1>
        <p className="text-sm text-muted-foreground">Melde dich mit Benutzername oder E-Mail und Passwort an.</p>
      </header>

      <form className="space-y-4" onSubmit={onSubmit}>
        <label className="block space-y-1 text-sm">
          <span className="font-medium">Benutzername oder E-Mail</span>
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2 outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring"
            placeholder="max.mustermann"
            required
          />
        </label>
        <label className="block space-y-1 text-sm">
          <span className="font-medium">Passwort</span>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-md border bg-background px-3 py-2 outline-none ring-offset-background focus-visible:ring-2 focus-visible:ring-ring"
            required
          />
        </label>

        {(formError || auth.errorMessage) && (
          <p className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {formError || auth.errorMessage}
          </p>
        )}

        <Button type="submit" className="w-full" disabled={auth.status === "loading"}>
          {auth.status === "loading" ? "Melde an..." : "Anmelden"}
        </Button>
      </form>
    </section>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<p className="text-sm text-muted-foreground">Login wird geladen...</p>}>
      <LoginForm />
    </Suspense>
  );
}
