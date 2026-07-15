import { AdminConsole } from "@/components/admin-console";
import { PageHeader } from "@/components/page-header";

export default function Page() {
  return (
    <>
      <PageHeader
        title="本地数据治理"
        description="登记授权来源、导入 CSV、审核记录并监控数据质量。"
      />
      <AdminConsole />
    </>
  );
}
