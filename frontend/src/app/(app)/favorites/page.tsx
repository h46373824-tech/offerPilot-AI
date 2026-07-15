import { Favorites } from "@/components/feature-pages";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="我的收藏"
        description="保存感兴趣的企业与岗位，便于后续比较。"
      />
      <Favorites />
    </>
  );
}
