import { PageHeader } from "@/components/page-header";
import { ResumesManager } from "@/components/workflow-tools";
export default function Page() {
  return (
    <>
      <PageHeader
        title="简历版本"
        description="安全管理不同方向的简历附件，并关联到具体投递。"
      />
      <ResumesManager />
    </>
  );
}
