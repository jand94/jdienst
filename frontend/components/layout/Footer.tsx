import { responsiveTokens } from "@/lib/responsive-tokens";

export default function Footer() {
  return (
    <footer className="border-t bg-card">
      <div className={`${responsiveTokens.container} flex h-14 items-center justify-between text-sm text-muted-foreground`}>
        <p>© 2026 jdienst</p>
        <p>Built with Next.js</p>
      </div>
    </footer>
  );
}
