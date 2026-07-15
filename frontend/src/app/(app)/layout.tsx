import { AppShell } from "@/components/shell";
export default function ProductLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AppShell>{children}</AppShell>;
}
