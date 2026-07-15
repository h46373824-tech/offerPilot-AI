import { SettingsForm } from "@/components/settings-form";
import { PageHeader } from "@/components/page-header";
export default function Page() {
  return (
    <>
      <PageHeader
        title="设置"
        description="管理个人资料、求职偏好与通知方式。"
      />
      <SettingsForm />
    </>
  );
}
