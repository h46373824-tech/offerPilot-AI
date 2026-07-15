import { Offers } from "@/components/feature-pages";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="Offer 管理"
        description="记录 Offer 条件、截止日期与最终选择。"
        action={<button className="btn-primary">+ 记录 Offer</button>}
      />
      <Offers />
    </>
  );
}
