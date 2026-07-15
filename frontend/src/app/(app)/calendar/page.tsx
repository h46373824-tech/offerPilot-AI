import { Calendar } from "@/components/feature-pages";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="校招日历"
        description="关注 Demo 岗位的示例开放与截止节点。"
      />
      <Calendar />
    </>
  );
}
