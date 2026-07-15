import { JobTable } from "@/components/catalog";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="岗位库"
        description="按城市、学历与岗位类别筛选示例校招岗位。"
        action={<button className="btn-primary">+ 新增岗位</button>}
      />
      <JobTable />
    </>
  );
}
