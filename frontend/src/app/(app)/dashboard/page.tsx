import { DashboardView } from "@/components/dashboard";
import { PageHeader } from "@/components/page-header";
export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="早上好，继续向 Offer 出发"
        description="基于 Demo 数据呈现，招聘状态不代表实时开放情况。"
      />
      <DashboardView />
    </>
  );
}
