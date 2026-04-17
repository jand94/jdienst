import Image from "next/image";
import { responsiveTokens } from "@/lib/responsive-tokens";

export default function Footer() {
  return (
    <footer className="border-t bg-card">
      <div className={`${responsiveTokens.container} flex h-14 items-center justify-between text-sm text-muted-foreground`}>
        <div className="flex items-center gap-2">
          <Image src="/logo.png" alt="jdienst Logo" width={24} height={24} className="h-6 w-6 rounded-sm" />
          <p>© 2026 jdienst</p>
        </div>
        <p>Enhance your customer experience</p>
      </div>
    </footer>
  );
}
