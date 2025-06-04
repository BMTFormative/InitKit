// frontend/src/components/JobPostings/JobPostingGenerator.tsx
import { useState } from 'react';
import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Alert,
  Spinner,
  Tabs,
   
} from '@chakra-ui/react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { BotIcon, SparklesIcon, EyeIcon, SaveIcon, TrendingUp } from 'lucide-react';

import { JobPostingService } from '@/services/job-posting-service';
import useCustomToast from "../../hooks/useCustomToast"
import {
  JobPostingFormData,
  JobPostingGenerationResponse,
  JobPostingAnalysisResponse,
  PLATFORM_OPTIONS,
  EXPERIENCE_LEVELS,
  EMPLOYMENT_TYPES,
  GENERATION_STYLES,
  JOB_LENGTHS
} from '@/types/job-postings';

import JobPostingForm from '../JobPostings/JobPostingForm';
import JobPostingPreview from '../JobPostings/JobPostingPreview';
import JobPostingAnalysis from '../JobPostings/JobPostingAnalysis';
import { toaster } from "@/components/ui/toaster"
const JobPostingGenerator = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [analysisData, setAnalysisData] = useState<JobPostingAnalysisResponse | null>(null);
  const [creditsUsed, setCreditsUsed] = useState<number>(0);
  
  //const { isOpen: isPreviewOpen, onOpen: onPreviewOpen, onClose: onPreviewClose } = useDisclosure();
  //const showToast = useCustomToast();
  
  const form = useForm<JobPostingFormData>({
    defaultValues: {
      job_title: '',
      location: '',
      experience_level: 'mid',
      employment_type: 'full-time',
      job_overview: '',
      responsibilities: [''],
      team_intro: '',
      required_skills: '',
      education_requirements: '',
      certifications: '',
      include_salary: false,
      salary_range: '',
      benefits: [''],
      perks: '',
      platform: 'linkedin',
      length: 'standard',
      keywords: '',
      use_ai_generation: true,
      generation_style: 'professional',
      target_audience: ''
    }
  });

  // Generate job posting mutation
  const generateMutation = useMutation({
    mutationFn: async (data: JobPostingFormData) => {
      return await JobPostingService.generateJobPosting(data);
    },
    onSuccess: (data: JobPostingGenerationResponse) => {
      setGeneratedContent(data.generated_content);
      setCreditsUsed(prev => prev + data.credits_used);
      setActiveTab(1); // Switch to preview tab
      toaster.create({
        title: 'Job posting generated successfully!',
        description: `Used ${data.credits_used} credits. Generated with ${data.model_used}.`,
        type: 'success'
      });
    },
    onError: (error: Error) => {
      toaster.create({
        title: 'Generation failed',
        description: error.message,
        type: 'error'
      });
    }
  });

  // Analyze job posting mutation
  const analyzeMutation = useMutation({
    mutationFn: async (content: string) => {
      return await JobPostingService.analyzeJobPosting(content);
    },
    onSuccess: (data: JobPostingAnalysisResponse) => {
      setAnalysisData(data);
      setCreditsUsed(prev => prev + data.credits_used);
      setActiveTab(2); // Switch to analysis tab
      toaster.create({
        title: 'Analysis completed!',
        description: `Quality score: ${data.score}/100. Used ${data.credits_used} credits.`,
        type: 'success'
      });
    },
    onError: (error: Error) => {
      toaster.create({
        title: 'Analysis failed',
        description: error.message,
        type: 'error'
      });
    }
  });

  // Save job posting mutation
  const saveMutation = useMutation({
    mutationFn: async (data: JobPostingFormData & { generated_content: string }) => {
      return await JobPostingService.saveJobPosting(data);
    },
    onSuccess: () => {
      toaster.create({
        title: 'Job posting saved!',
        description: 'Your job posting has been saved successfully.',
        type: 'success'
      });
    },
    onError: (error: Error) => {
      toaster.create({
        title: 'Save failed',
        description: error.message,
        type: 'error'
      });
    }
  });

  const handleGenerate = async (data: JobPostingFormData) => {
    if (!data.job_title.trim()) {
      toaster.create({
        title: 'Job title required',
        description: 'Please enter a job title before generating.',
        type: 'warning'
      });
      return;
    }
    
    generateMutation.mutate(data);
  };

  const handleAnalyze = () => {
    if (!generatedContent.trim()) {
      toaster.create({
        title: 'No content to analyze',
        description: 'Please generate a job posting first.',
        type: 'warning'
      });
      return;
    }
    
    analyzeMutation.mutate(generatedContent);
  };

  const handleSave = () => {
    const formData = form.getValues();
    if (!generatedContent.trim()) {
      toaster.create({
        title: 'No content to save',
        description: 'Please generate a job posting first.',
        type: 'warning'
      });
      return;
    }
    
    saveMutation.mutate({
      ...formData,
      generated_content: generatedContent,
      use_ai_generation: true
    });
  };

  const tabsData = [
    {
      label: 'Create',
      icon: BotIcon,
      content: (
        <JobPostingForm
          form={form}
          onSubmit={handleGenerate}
          isLoading={generateMutation.isPending}
          platformOptions={PLATFORM_OPTIONS}
          experienceLevels={EXPERIENCE_LEVELS}
          employmentTypes={EMPLOYMENT_TYPES}
          generationStyles={GENERATION_STYLES}
          jobLengths={JOB_LENGTHS}
        />
      )
    },
    {
      label: 'Preview',
      icon: EyeIcon,
      content: (
        <JobPostingPreview
          content={generatedContent}
          platform={form.watch('platform')}
          onAnalyze={handleAnalyze}
          onSave={handleSave}
          isAnalyzing={analyzeMutation.isPending}
          isSaving={saveMutation.isPending}
        />
      )
    },
    {
      label: 'Analysis',
      icon: TrendingUp,
      content: (
        <JobPostingAnalysis
          analysisData={analysisData}
          originalContent={generatedContent}
          onApplySuggestions={(suggestions, comment) => {
            // TODO: Implement suggestions application
            toaster.create({
              title: 'Feature coming soon',
              description: 'Suggestion application will be available soon.',
              type: 'info'
            });
          }}
        />
      )
    }
  ];

  return (
    <Box maxW="7xl" mx="auto" p={6}>
      {/* Header */}
      <VStack align="stretch" gap={6}>
        <Box>
          <HStack justify="space-between" align="start">
            <VStack align="start" gap={2}>
              <Heading size="lg" color="fg">
                AI Job Posting Generator
              </Heading>
              <Text color="fg.muted" maxW="2xl">
                Create compelling job postings using Claude AI with platform-specific optimization 
                and built-in quality analysis.
              </Text>
            </VStack>
            
            {creditsUsed > 0 && (
              <Badge variant="subtle" colorPalette="blue" size="lg">
                Credits Used: {creditsUsed}
              </Badge>
            )}
          </HStack>
        </Box>

        {/* AI Features Alert */}
        <Alert.Root status="info" variant="subtle">
          <SparklesIcon size={16} />
          <Box>
            <Text fontWeight="medium">Powered by Claude AI</Text>
            <Text fontSize="sm" color="fg.muted">
              Uses LinkedIn guidelines and job posting best practices from our knowledge base
            </Text>
          </Box>
        </Alert.Root>

        {/* Main Content */}
        <Card.Root>
          <Tabs.Root value={activeTab.toString()} onValueChange={(e) => setActiveTab(parseInt(e.value))}>
            <Tabs.List>
              {tabsData.map((tab, index) => (
                <Tabs.Trigger key={index} value={index.toString()}>
                  <HStack>
                    <tab.icon size={16} />
                    <Text>{tab.label}</Text>
                  </HStack>
                </Tabs.Trigger>
              ))}
            </Tabs.List>

            {tabsData.map((tab, index) => (
              <Tabs.Content key={index} value={index.toString()}>
                <Card.Body pt={6}>
                  {tab.content}
                </Card.Body>
              </Tabs.Content>
            ))}
          </Tabs.Root>
        </Card.Root>

        {/* Quick Actions */}
        {generatedContent && (
          <Card.Root>
            <Card.Body>
              <HStack justify="space-between" align="center">
                <VStack align="start" gap={1}>
                  <Text fontWeight="medium">Quick Actions</Text>
                  <Text fontSize="sm" color="fg.muted">
                    Your job posting is ready! Choose what to do next.
                  </Text>
                </VStack>
                
                <HStack>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleAnalyze}
                    disabled={analyzeMutation.isPending}
                  >
                    {analyzeMutation.isPending ? (
                      <Spinner size="sm" />
                    ) : (
                      <TrendingUp size={16} />
                    )}
                    Analyze Quality
                  </Button>
                  
                  <Button
                    size="sm"
                    colorPalette="blue"
                    onClick={handleSave}
                    disabled={saveMutation.isPending}
                  >
                    {saveMutation.isPending ? (
                      <Spinner size="sm" />
                    ) : (
                      <SaveIcon size={16} />
                    )}
                    Save Posting
                  </Button>
                </HStack>
              </HStack>
            </Card.Body>
          </Card.Root>
        )}
      </VStack>
    </Box>
  );
};

export default JobPostingGenerator;