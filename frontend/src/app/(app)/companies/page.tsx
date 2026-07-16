import { CompanyTable } from "@/components/catalog";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="企业库"
        description="公开浏览已核验招聘来源的企业；状态与链接以企业官网最新信息为准。"
      />
      <CompanyTable />
    </>
  );
}
