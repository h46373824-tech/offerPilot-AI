export type ApiPage<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type Company = {
  id: number;
  name: string;
  industry: string;
  company_type: string;
  work_cities: string;
  education_requirement: string;
  is_demo: boolean;
};

export type Job = {
  id: number;
  title: string;
  company_id: number;
  category: string;
  work_cities: string;
  education_requirement: string;
  description: string;
  requirements: string;
  deadline: string | null;
  recruitment_status: string;
  is_demo: boolean;
};

export type Application = {
  id: number;
  user_id: number;
  job_id: number;
  resume_id: number | null;
  status: string;
  applied_at: string | null;
  channel: string | null;
  notes: string | null;
  created_at: string;
};

export type Interview = {
  id: number;
  application_id: number;
  interview_type: string;
  scheduled_at: string;
  status: string;
  location: string | null;
  notes: string | null;
};

export type Offer = {
  id: number;
  application_id: number;
  status: string;
  compensation: string | null;
  location: string | null;
  received_at: string;
  response_deadline: string | null;
  notes: string | null;
};

export type Favorite = { id: number; job_id: number; created_at: string };

export type Resume = {
  id: number;
  name: string;
  version: string | null;
  is_default: boolean;
  original_filename: string;
  content_type: string;
  file_size: number;
  file_url: string;
  created_at: string;
};

export type JobAlert = {
  id: number;
  name: string;
  criteria: Record<string, unknown>;
  frequency: "daily" | "weekly" | "instant";
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
};

export type Notification = {
  id: number;
  title: string;
  content: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
};

export type DashboardStats = {
  open_companies: number;
  college_companies: number;
  bachelor_companies: number;
  new_jobs_today: number;
  applications: number;
  interviews: number;
  offers: number;
  expiring_jobs: number;
  application_trend: Array<{ date: string; count: number }>;
  industry_distribution: Array<{ industry: string; count: number }>;
  recent_applications: Array<{
    id: number;
    job_id: number;
    job_title: string;
    company_name: string;
    status: string;
    applied_at: string | null;
  }>;
};

export type CurrentUser = {
  id: number;
  email: string;
  full_name: string;
  graduation_year: number | null;
  education_level: string | null;
  target_cities: string | null;
  notifications_enabled: boolean;
};
