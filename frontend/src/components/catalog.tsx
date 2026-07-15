"use client";

import { useMemo, useState, useSyncExternalStore } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bookmark, ExternalLink, Search, X } from "lucide-react";
import {
  Badge,
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/status";
import { companies, jobs } from "@/data/demo";
import { apiFetch } from "@/lib/api";
import { useHasToken } from "@/lib/auth";
import type { ApiPage, Company, Favorite, Job } from "@/lib/types";

type CompanyRow = readonly [
  name: string,
  industry: string,
  companyType: string,
  workCities: string,
  education: string,
];

type CompanyApiItem = {
  id: number;
  name: string;
  industry: string;
  company_type: string;
  work_cities: string;
  education_requirement: string;
  is_demo: boolean;
};

function subscribeToAuth(onStoreChange: () => void) {
  window.addEventListener("storage", onStoreChange);
  return () => window.removeEventListener("storage", onStoreChange);
}

function getAuthSnapshot() {
  return Boolean(window.localStorage.getItem("access_token"));
}

function getServerAuthSnapshot() {
  return false;
}

export function CompanyTable() {
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState("");
  const [education, setEducation] = useState("");
  const authenticated = useSyncExternalStore(
    subscribeToAuth,
    getAuthSnapshot,
    getServerAuthSnapshot,
  );
  const companiesQuery = useQuery({
    enabled: authenticated,
    queryFn: () =>
      apiFetch<ApiPage<CompanyApiItem>>(
        "/companies?page_size=100&is_demo=true&sort_by=name&order=asc",
      ),
    queryKey: ["companies", "demo"],
  });
  const sourceRows = useMemo<readonly CompanyRow[]>(() => {
    if (!companiesQuery.data) return companies;

    return companiesQuery.data.items.map((company) => [
      company.name,
      company.industry,
      company.company_type,
      company.work_cities,
      company.education_requirement,
    ]);
  }, [companiesQuery.data]);
  const industries = useMemo(
    () => Array.from(new Set(sourceRows.map((company) => company[1]))),
    [sourceRows],
  );
  const educations = useMemo(
    () => Array.from(new Set(sourceRows.map((company) => company[4]))),
    [sourceRows],
  );
  const rows = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return sourceRows.filter(
      (company) =>
        (!keyword || company.join(" ").toLowerCase().includes(keyword)) &&
        (!industry || company[1] === industry) &&
        (!education || company[4] === education),
    );
  }, [education, industry, query, sourceRows]);
  const hasFilters = Boolean(query || industry || education);

  if (authenticated && companiesQuery.isPending) {
    return <LoadingState text="正在从服务端加载企业数据…" />;
  }

  return (
    <>
      {!authenticated && (
        <p className="mb-4 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-300">
          当前未登录，企业库展示 Demo 示例数据。
        </p>
      )}
      {companiesQuery.isError && (
        <div className="mb-4">
          <ErrorState
            action={
              <button
                className="btn-primary"
                onClick={() => void companiesQuery.refetch()}
                type="button"
              >
                重新同步
              </button>
            }
            text="实时企业数据暂不可用，已自动切换为 Demo 数据。"
          />
        </div>
      )}
      <Filters
        category={industry}
        categoryLabel="行业"
        categoryOptions={industries}
        education={education}
        educationOptions={educations}
        onCategoryChange={setIndustry}
        onEducationChange={setEducation}
        onQueryChange={setQuery}
        onReset={() => {
          setQuery("");
          setIndustry("");
          setEducation("");
        }}
        query={query}
      />
      {rows.length > 0 ? (
        <div className="card table-wrap">
          <table aria-label="企业列表">
            <thead>
              <tr>
                <th scope="col">企业名称</th>
                <th scope="col">行业</th>
                <th scope="col">性质</th>
                <th scope="col">工作城市</th>
                <th scope="col">学历要求</th>
                <th scope="col">状态</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row[0]}>
                  {row.map((value, index) => (
                    <td key={`${row[0]}-${index}`}>{value}</td>
                  ))}
                  <td>
                    <Badge tone="slate">Demo · 待核验</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          action={
            hasFilters ? (
              <button
                className="btn-primary"
                onClick={() => {
                  setQuery("");
                  setIndustry("");
                  setEducation("");
                }}
                type="button"
              >
                清除筛选
              </button>
            ) : undefined
          }
          text={
            companiesQuery.data?.total === 0
              ? "服务端暂无企业数据"
              : "没有匹配的企业"
          }
        />
      )}
    </>
  );
}

export function JobTable() {
  const authenticated = useHasToken();
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("");
  const [education, setEducation] = useState("");
  const jobsQuery = useQuery({
    enabled: authenticated,
    queryKey: ["jobs"],
    queryFn: () =>
      apiFetch<ApiPage<Job>>(
        "/jobs?page_size=100&sort_by=created_at&order=desc",
      ),
  });
  const companiesQuery = useQuery({
    enabled: authenticated,
    queryKey: ["companies", "job-map"],
    queryFn: () => apiFetch<ApiPage<Company>>("/companies?page_size=100"),
  });
  const favoritesQuery = useQuery({
    enabled: authenticated,
    queryKey: ["favorites"],
    queryFn: () => apiFetch<ApiPage<Favorite>>("/favorites?page_size=100"),
  });
  const favoriteMutation = useMutation({
    mutationFn: async ({
      jobId,
      active,
    }: {
      jobId: number;
      active: boolean;
    }) => {
      if (active) {
        await apiFetch<void>(`/favorites/${jobId}`, { method: "DELETE" });
      } else {
        await apiFetch<Favorite>("/favorites", {
          method: "POST",
          body: JSON.stringify({ job_id: jobId }),
        });
      }
    },
    onSuccess: () =>
      void queryClient.invalidateQueries({ queryKey: ["favorites"] }),
  });
  const companyNames = useMemo(
    () =>
      new Map(
        companiesQuery.data?.items.map((item) => [item.id, item.name]) ?? [],
      ),
    [companiesQuery.data],
  );
  const sourceRows = useMemo(
    () =>
      jobsQuery.data?.items.map((job) => ({
        id: job.id,
        title: job.title,
        company: companyNames.get(job.company_id) ?? `企业 #${job.company_id}`,
        category: job.category,
        city: job.work_cities,
        education: job.education_requirement,
        deadline: job.deadline?.slice(0, 10) ?? "待核验",
        applicationUrl: job.application_url,
        status: job.recruitment_status,
        isDemo: job.is_demo,
        verified: Boolean(job.last_verified_at),
      })) ??
      jobs.map((job, index) => ({
        id: -(index + 1),
        title: job[0],
        company: job[1],
        category: job[2],
        city: job[3],
        education: job[4],
        deadline: job[5],
        applicationUrl: null,
        status: "unverified",
        isDemo: true,
        verified: false,
      })),
    [companyNames, jobsQuery.data],
  );
  const categories = useMemo(
    () => Array.from(new Set(sourceRows.map((job) => job.category))),
    [sourceRows],
  );
  const educations = useMemo(
    () => Array.from(new Set(sourceRows.map((job) => job.education))),
    [sourceRows],
  );
  const favoriteIds = new Set(
    favoritesQuery.data?.items.map((item) => item.job_id) ?? [],
  );
  const rows = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return sourceRows.filter(
      (job) =>
        (!keyword ||
          Object.values(job).join(" ").toLowerCase().includes(keyword)) &&
        (!category || job.category === category) &&
        (!education || job.education === education),
    );
  }, [category, education, query, sourceRows]);

  if (authenticated && jobsQuery.isPending)
    return <LoadingState text="正在加载岗位数据…" />;

  return (
    <>
      <Filters
        category={category}
        categoryLabel="岗位类别"
        categoryOptions={categories}
        education={education}
        educationOptions={educations}
        onCategoryChange={setCategory}
        onEducationChange={setEducation}
        onQueryChange={setQuery}
        onReset={() => {
          setQuery("");
          setCategory("");
          setEducation("");
        }}
        query={query}
      />
      {rows.length > 0 ? (
        <div className="card table-wrap">
          <table aria-label="岗位列表">
            <thead>
              <tr>
                <th scope="col">岗位名称</th>
                <th scope="col">企业</th>
                <th scope="col">类别</th>
                <th scope="col">城市</th>
                <th scope="col">学历</th>
                <th scope="col">截止时间</th>
                <th scope="col">数据状态</th>
                <th scope="col">官方投递</th>
                <th scope="col">
                  <span className="sr-only">操作</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td>{row.title}</td>
                  <td>{row.company}</td>
                  <td>{row.category}</td>
                  <td>{row.city}</td>
                  <td>{row.education}</td>
                  <td>{row.deadline}</td>
                  <td>
                    <Badge
                      tone={
                        row.isDemo ? "slate" : row.verified ? "teal" : "amber"
                      }
                    >
                      {row.isDemo
                        ? "Demo · 非实时"
                        : row.verified
                          ? "已核验"
                          : "待核验"}
                    </Badge>
                  </td>
                  <td>
                    {row.applicationUrl ? (
                      <a
                        className="inline-flex items-center gap-1 font-semibold whitespace-nowrap text-teal-600 hover:text-teal-700"
                        href={row.applicationUrl}
                        rel="noopener noreferrer"
                        target="_blank"
                      >
                        前往官方投递
                        <ExternalLink aria-hidden="true" size={14} />
                      </a>
                    ) : (
                      <span className="text-xs text-[var(--muted)]">
                        暂无链接
                      </span>
                    )}
                  </td>
                  <td>
                    <button
                      aria-label={`${favoriteIds.has(row.id) ? "取消收藏" : "收藏岗位"}：${row.title}`}
                      className={`rounded-md p-1 ${favoriteIds.has(row.id) ? "text-teal-600" : "text-slate-400 hover:text-teal-600"}`}
                      disabled={
                        !authenticated ||
                        row.id < 0 ||
                        favoriteMutation.isPending
                      }
                      onClick={() =>
                        favoriteMutation.mutate({
                          jobId: row.id,
                          active: favoriteIds.has(row.id),
                        })
                      }
                      type="button"
                    >
                      <Bookmark aria-hidden="true" size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          action={
            <button
              className="btn-primary"
              onClick={() => {
                setQuery("");
                setCategory("");
                setEducation("");
              }}
              type="button"
            >
              清除筛选
            </button>
          }
          text="没有匹配的岗位"
        />
      )}
    </>
  );
}

type FiltersProps = {
  category: string;
  categoryLabel: string;
  categoryOptions: readonly string[];
  education: string;
  educationOptions: readonly string[];
  onCategoryChange: (value: string) => void;
  onEducationChange: (value: string) => void;
  onQueryChange: (value: string) => void;
  onReset: () => void;
  query: string;
};

function Filters({
  category,
  categoryLabel,
  categoryOptions,
  education,
  educationOptions,
  onCategoryChange,
  onEducationChange,
  onQueryChange,
  onReset,
  query,
}: FiltersProps) {
  const hasFilters = Boolean(query || category || education);

  return (
    <div className="card mb-4 grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_180px_180px_auto]">
      <label className="relative">
        <span className="sr-only">关键词搜索</span>
        <Search
          aria-hidden="true"
          className="absolute top-3 left-3 text-slate-400"
          size={18}
        />
        <input
          className="field pl-10"
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="输入关键词搜索"
          type="search"
          value={query}
        />
      </label>
      <label>
        <span className="sr-only">按{categoryLabel}筛选</span>
        <select
          className="field"
          onChange={(event) => onCategoryChange(event.target.value)}
          value={category}
        >
          <option value="">全部{categoryLabel}</option>
          {categoryOptions.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      </label>
      <label>
        <span className="sr-only">按学历筛选</span>
        <select
          className="field"
          onChange={(event) => onEducationChange(event.target.value)}
          value={education}
        >
          <option value="">全部学历</option>
          {educationOptions.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      </label>
      <button
        aria-label="清除全部筛选条件"
        className="flex min-h-11 items-center justify-center gap-1 rounded-lg px-3 text-sm font-semibold text-[var(--muted)] hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40 dark:hover:bg-slate-800"
        disabled={!hasFilters}
        onClick={onReset}
        type="button"
      >
        <X aria-hidden="true" size={16} />
        清除
      </button>
    </div>
  );
}
