// frontend/src/types/job-postings.ts

export interface JobPostingCreateRequest {
  job_title: string;
  location?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview?: string;
  responsibilities?: string;
  required_skills?: string;
  education_requirements?: string;
  certifications?: string;
  team_intro?: string;
  include_salary?: boolean;
  salary_range?: string;
  benefits?: string[];
  perks?: string;
  platform: string;
  length: string;
  application_deadline?: number;
  application_deadline_date?: string;
  keywords?: string;
}

export interface JobPostingResponse {
  id: string;
  tenant_id: string;
  created_by: string;
  job_title: string;
  location?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview?: string;
  responsibilities?: string[];
  required_skills?: string;
  education_requirements?: string;
  certifications?: string;
  team_intro?: string;
  include_salary: boolean;
  salary_range?: string;
  benefits?: string[];
  perks?: string;
  platform: string;
  length: string;
  application_deadline_days?: number;
  application_deadline_date?: string;
  keywords?: string;
  generated_content?: string;
  quality_score?: number;
  ai_suggestions?: string[];
  status: string;
  credits_used: number;
  generation_model?: string;
  created_at: string;
  updated_at: string;
}

export interface JobPostingListResponse {
  data: JobPostingResponse[];
  count: number;
}

export interface JobPostingAnalysisResponse {
  quality_score: number;
  suggestions: string[];
  strengths: string[];
  areas_for_improvement: string[];
}

export interface JobPostingTemplate {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  job_title_template?: string;
  location_template?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview_template?: string;
  responsibilities_template?: string;
  required_skills_template?: string;
  benefits_template?: string;
  platform_default: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobPostingTemplateCreateRequest {
  name: string;
  description?: string;
  job_title_template?: string;
  location_template?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview_template?: string;
  responsibilities_template?: string;
  required_skills_template?: string;
  benefits_template?: string;
  platform_default?: string;
}