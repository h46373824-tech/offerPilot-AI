"use client";

import { useMemo, useState } from "react";
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

type CompanyRow = {
  name: string;
  industry: string;
  companyType: string;
  workCities: string;
  education: string;
  campusWebsite: string | null;
  lastVerifiedAt: string | null;
  isDemo: boolean;
};

export function CompanyTable() {
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState("");
  const [education, setEducation] = useState("");
  const companiesQuery = useQuery({
    queryFn: () =>
      apiFetch<ApiPage<Company>>(
        "/companies?page_size=100&is_demo=false&verified_only=true&verified_within_days=30&recruitment_status=open&sort_by=name&order=asc",
      ),
    queryKey: ["companies", "public-verified"],
  });
  const sourceRows = useMemo<readonly CompanyRow[]>(() => {
    if (!companiesQuery.data)
      return companies.map((company) => ({
        name: company[0],
        industry: company[1],
        companyType: company[2],
        workCities: company[3],
        education: company[4],
        campusWebsite: null,
        lastVerifiedAt: null,
        isDemo: true,
      }));

    return companiesQuery.data.items.map((company) => ({
      name: company.name,
      industry: company.industry,
      companyType: company.company_type,
      workCities: company.work_cities,
      education: company.education_requirement,
      campusWebsite: company.campus_website,
      lastVerifiedAt: company.last_verified_at,
      isDemo: company.is_demo,
    }));
  }, [companiesQuery.data]);
  const industries = useMemo(
    () => Array.from(new Set(sourceRows.map((company) => company.industry))),
    [sourceRows],
  );
  const educations = useMemo(
    () => Array.from(new Set(sourceRows.map((company) => company.education))),
    [sourceRows],
  );
  const rows = useMemo(() => {
    const keyword = query.trim().toLowerCase();

    return sourceRows.filter(
      (company) =>
        (!keyword ||
          Object.values(company).join(" ").toLowerCase().includes(keyword)) &&
        (!industry || company.industry === industry) &&
        (!education || company.education === education),
    );
  }, [education, industry, query, sourceRows]);
  const hasFilters = Boolean(query || industry || education);

  if (companiesQuery.isPending) {
    return <LoadingState text="正在从服务端加载企业数据…" />;
  }

  return (
    <>
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
            text="官方企业数据暂不可用，已自动切换为明确标记的 Demo 数据。"
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
                <th scope="col">官方招聘</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.name}>
                  <td className="font-semibold">{row.name}</td>
                  <td>{row.industry}</td>
                  <td>{row.companyType}</td>
                  <td>{row.workCities}</td>
                  <td>{row.education}</td>
                  <td>
                    <Badge tone={row.isDemo ? "slate" : "teal"}>
                      {row.isDemo
                        ? "Demo · 非实时"
                        : `已核验 ${row.lastVerifiedAt?.slice(5, 10) ?? ""}`}
                    </Badge>
                  </td>
                  <td>
                    {row.campusWebsite ? (
                      <a
                        className="inline-flex items-center gap-1 font-semibold whitespace-nowrap text-teal-600 hover:text-teal-700"
                        href={row.campusWebsite}
                        rel="noopener noreferrer"
                        target="_blank"
                      >
                        招聘官网
                        <ExternalLink aria-hidden="true" size={14} />
                      </a>
                    ) : (
                      <span className="text-xs text-[var(--muted)]">
                        暂无链接
                      </span>
                    )}
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
    queryKey: ["jobs", "public-verified"],
    queryFn: () =>
      apiFetch<ApiPage<Job>>(
        "/jobs?page_size=100&is_demo=false&verified_only=true&verified_within_days=30&recruitment_status=open&sort_by=published_at&order=desc",
      ),
  });
  const companiesQuery = useQuery({
    queryKey: ["companies", "job-map"],
    queryFn: () =>
      apiFetch<ApiPage<Company>>(
        "/companies?page_size=100&is_demo=false&verified_only=true&verified_within_days=30",
      ),
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
        lastVerifiedAt: job.last_verified_at,
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
        lastVerifiedAt: null,
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

  if (jobsQuery.isPending || companiesQuery.isPending)
    return <LoadingState text="正在加载岗位数据…" />;

  return (
    <>
      {jobsQuery.isError && (
        <div className="mb-4">
          <ErrorState
            action={
              <button
                className="btn-primary"
                onClick={() => void jobsQuery.refetch()}
                type="button"
              >
                重新加载
              </button>
            }
            text="官方岗位暂不可用，当前仅展示 Demo 降级数据。"
          />
        </div>
      )}
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
                          ? `已核验 ${row.lastVerifiedAt?.slice(5, 10) ?? ""}`
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
