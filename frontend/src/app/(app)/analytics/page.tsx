import { Analytics } from "@/components/analytics";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="数据分析"
        description="复盘投递结构、流程转化和求职节奏。"
      />
      <Analytics />
    </>
  );
}
