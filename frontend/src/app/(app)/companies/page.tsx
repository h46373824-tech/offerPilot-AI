import { CompanyTable } from "@/components/catalog";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="企业库"
        description="发现适合 2027 届毕业生的示例企业，所有数据均为 Demo。"
        action={<button className="btn-primary">+ 新增企业</button>}
      />
      <CompanyTable />
    </>
  );
}
