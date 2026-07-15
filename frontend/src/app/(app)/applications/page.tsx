import { Applications } from "@/components/feature-pages";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="投递管理"
        description="集中跟踪网申、笔试、面试与结果。"
        action={<button className="btn-primary">+ 新增投递</button>}
      />
      <Applications />
    </>
  );
}
