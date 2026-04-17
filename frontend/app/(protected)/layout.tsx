import RequireAuth from "@/components/auth/RequireAuth";

type ProtectedLayoutProps = {
  children: React.ReactNode;
};

export default function ProtectedLayout({ children }: ProtectedLayoutProps) {
  return <RequireAuth>{children}</RequireAuth>;
}
