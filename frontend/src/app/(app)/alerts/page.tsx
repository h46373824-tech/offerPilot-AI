import { PageHeader } from "@/components/page-header";
import { AlertsManager } from "@/components/workflow-tools";
export default function Page() {
  return (
    <>
      <PageHeader
        title="岗位订阅"
        description="按关键词、城市和类别订阅岗位，生成可追踪提醒。"
      />
      <AlertsManager />
    </>
  );
}
