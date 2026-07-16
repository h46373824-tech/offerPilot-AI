import { JobTable } from "@/components/catalog";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="岗位库"
        description="无需登录即可浏览已核验的 2027 届招聘项目与岗位，并跳转企业官方渠道投递。"
      />
      <JobTable />
    </>
  );
}
