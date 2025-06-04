// UPDATE: frontend/src/services/job-posting-service.ts
import { 
  JobPostingCreateRequest,
  JobPostingResponse,
  JobPostingListResponse,
  JobPostingAnalysisResponse,
  JobPostingGenerationRequest,
  JobPostingGenerationResponse
} from '@/types/job-postings';

export const JobPostingService = {
  /**
   * Generate a new job posting using Claude AI
   */
  generateJobPosting: async (data: JobPostingGenerationRequest): Promise<JobPostingGenerationResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/generate`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Generation failed' }));
      throw new Error(error.detail || 'Failed to generate job posting');
    }
    
    return response.json();
  },

  /**
   * Analyze job posting quality using Claude AI
   */
  analyzeJobPosting: async (content: string): Promise<JobPostingAnalysisResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/analyze`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(error.detail || 'Failed to analyze job posting');
    }
    
    return response.json();
  },

  /**
   * Apply suggestions to improve job posting
   */
  applySuggestions: async (
    originalContent: string, 
    suggestions: string[], 
    comment?: string
  ): Promise<{ improved_content: string; credits_used: number }> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/apply-suggestions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          original_content: originalContent,
          suggestions,
          comment
        })
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Suggestion application failed' }));
      throw new Error(error.detail || 'Failed to apply suggestions');
    }
    
    return response.json();
  },

  /**
   * Save a job posting to database
   */
  saveJobPosting: async (data: JobPostingCreateRequest & { 
    generated_content?: string;
    use_ai_generation?: boolean;
  }): Promise<JobPostingResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Save failed' }));
      throw new Error(error.detail || 'Failed to save job posting');
    }
    
    return response.json();
  },

  /**
   * Get list of job postings for current tenant
   */
  listJobPostings: async (params?: { skip?: number; limit?: number }): Promise<JobPostingListResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const queryParams = new URLSearchParams();
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings?${queryParams}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Fetch failed' }));
      throw new Error(error.detail || 'Failed to fetch job postings');
    }
    
    return response.json();
  },

  /**
   * Get a specific job posting by ID
   */
  getJobPosting: async (jobPostingId: string): Promise<JobPostingResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/${jobPostingId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Fetch failed' }));
      throw new Error(error.detail || 'Failed to fetch job posting');
    }
    
    return response.json();
  },

  /**
   * Update a job posting
   */
  updateJobPosting: async (jobPostingId: string, data: Partial<JobPostingCreateRequest>): Promise<JobPostingResponse> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/${jobPostingId}`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Update failed' }));
      throw new Error(error.detail || 'Failed to update job posting');
    }
    
    return response.json();
  },

  /**
   * Delete a job posting
   */
  deleteJobPosting: async (jobPostingId: string): Promise<{ message: string }> => {
    const token = localStorage.getItem('access_token');
    const tenantId = localStorage.getItem('tenant_id');
    
    if (!tenantId) {
      throw new Error('No tenant context available');
    }
    
    const response = await fetch(
      `${import.meta.env.VITE_API_URL}/api/v1/tenants/${tenantId}/job-postings/${jobPostingId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Delete failed' }));
      throw new Error(error.detail || 'Failed to delete job posting');
    }
    
    return response.json();
  }
};