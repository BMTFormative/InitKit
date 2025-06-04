// frontend/src/types/job-postings.ts

export interface JobPostingCreateRequest {
  job_title: string;
  location?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview?: string;
  responsibilities?: string[];
  team_intro?: string;
  required_skills?: string;
  education_requirements?: string;
  certifications?: string;
  include_salary?: boolean;
  salary_range?: string;
  benefits?: string[];
  perks?: string;
  platform?: string;
  length?: string;
  application_deadline_days?: number;
  application_deadline_date?: string;
  keywords?: string;
}

export interface JobPostingGenerationRequest extends JobPostingCreateRequest {
  // Additional fields specific to AI generation
  use_ai_generation?: boolean;
  generation_style?: 'professional' | 'creative' | 'concise';
  target_audience?: string;
  company_description?: string;
}

export interface JobPostingGenerationResponse {
  generated_content: string;
  model_used: string;
  knowledge_sources: string[];
  credits_used: number;
  success: boolean;
}

export interface JobPostingAnalysisResponse {
  score: number;
  suggestions: string[];
  credits_used: number;
  success: boolean;
}

export interface JobPostingResponse {
  id: string;
  job_title: string;
  platform: string;
  status: string;
  credits_used: number;
  generation_model?: string;
  created_at: string;
  ai_generated: boolean;
  generated_content?: string;
  // Include all other fields from JobPostingCreateRequest
  location?: string;
  experience_level?: string;
  employment_type?: string;
  job_overview?: string;
  responsibilities?: string[];
  team_intro?: string;
  required_skills?: string;
  education_requirements?: string;
  certifications?: string;
  include_salary?: boolean;
  salary_range?: string;
  benefits?: string[];
  perks?: string;
  length?: string;
  application_deadline_days?: number;
  application_deadline_date?: string;
  keywords?: string;
}

export interface JobPostingListResponse {
  data: JobPostingResponse[];
  count: number;
}

export interface JobPostingFormData {
  // Basic Information
  job_title: string;
  company_name?: string;
  location: string;
  experience_level: string;
  employment_type: string;
  
  // Job Details
  job_overview: string;
  responsibilities: string[];
  team_intro: string;
  required_skills: string;
  education_requirements: string;
  certifications: string;
  
  // Compensation & Benefits
  include_salary: boolean;
  salary_range: string;
  benefits: string[];
  perks: string;
  
  // Generation Settings
  platform: string;
  length: string;
  keywords: string;
  
  // AI Generation Options
  use_ai_generation: boolean;
  generation_style?: "professional" | "creative" | "concise";
  target_audience: string;
  
}

export interface PlatformOption {
  value: string;
  label: string;
  description: string;
}

export interface ExperienceLevelOption {
  value: string;
  label: string;
}

export interface EmploymentTypeOption {
  value: string;
  label: string;
}

export const PLATFORM_OPTIONS: PlatformOption[] = [
  {
    value: 'linkedin',
    label: 'LinkedIn',
    description: 'Professional network with emoji support and social formatting'
  },
  {
    value: 'indeed',
    label: 'Indeed',
    description: 'Job board with structured, keyword-optimized format'
  },
  {
    value: 'glassdoor',
    label: 'Glassdoor',
    description: 'Company review site with transparency focus'
  },
  {
    value: 'general',
    label: 'General/Multiple',
    description: 'Professional format suitable for multiple platforms'
  }
];

export const EXPERIENCE_LEVELS: ExperienceLevelOption[] = [
  { value: 'entry', label: 'Entry Level (0-2 years)' },
  { value: 'mid', label: 'Mid Level (3-5 years)' },
  { value: 'senior', label: 'Senior (5-8 years)' },
  { value: 'lead', label: 'Lead (8+ years)' },
  { value: 'director', label: 'Director/Executive (10+ years)' }
];

export const EMPLOYMENT_TYPES: EmploymentTypeOption[] = [
  { value: 'full-time', label: 'Full-time' },
  { value: 'part-time', label: 'Part-time' },
  { value: 'contract', label: 'Contract' },
  { value: 'freelance', label: 'Freelance' },
  { value: 'temporary', label: 'Temporary' },
  { value: 'remote', label: 'Remote' },
  { value: 'hybrid', label: 'Hybrid' }
];

export const GENERATION_STYLES = [
  { value: 'professional', label: 'Professional', description: 'Formal, structured, corporate tone' },
  { value: 'creative', label: 'Creative', description: 'Engaging, dynamic, innovative tone' },
  { value: 'concise', label: 'Concise', description: 'Brief, direct, to-the-point' }
];

export const JOB_LENGTHS = [
  { value: 'short', label: 'Short', description: 'Brief overview, key points only' },
  { value: 'standard', label: 'Standard', description: 'Comprehensive but concise' },
  { value: 'detailed', label: 'Detailed', description: 'Thorough with extensive information' }
];