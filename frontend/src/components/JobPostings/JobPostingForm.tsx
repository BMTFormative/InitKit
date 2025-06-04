// frontend/src/components/JobPostings/JobPostingForm.tsx
import { UseFormReturn } from 'react-hook-form';
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Text,
  Grid,
  GridItem,
  Card,
  Spinner,
  Fieldset,
  Separator,
} from '@chakra-ui/react';
import { Field } from '@/components/ui/field';
import { Checkbox } from '@/components/ui/checkbox';
import { PlusIcon, MinusIcon, SparklesIcon } from 'lucide-react';

import {
  JobPostingFormData,
  PlatformOption,
  ExperienceLevelOption,
  EmploymentTypeOption
} from '@/types/job-postings';

interface JobPostingFormProps {
  form: UseFormReturn<JobPostingFormData>;
  onSubmit: (data: JobPostingFormData) => void;
  isLoading: boolean;
  platformOptions: PlatformOption[];
  experienceLevels: ExperienceLevelOption[];
  employmentTypes: EmploymentTypeOption[];
  generationStyles: Array<{ value: string; label: string; description: string }>;
  jobLengths: Array<{ value: string; label: string; description: string }>;
}

const JobPostingForm = ({
  form,
  onSubmit,
  isLoading,
  platformOptions,
  experienceLevels,
  employmentTypes,
  generationStyles,
  jobLengths
}: JobPostingFormProps) => {
  const { register, handleSubmit, watch, setValue, formState: { errors } } = form;
  
  const responsibilities = watch('responsibilities') || [''];
  const benefits = watch('benefits') || [''];
  const includeSalary = watch('include_salary');
  const useAiGeneration = watch('use_ai_generation');

  const addResponsibility = () => {
    setValue('responsibilities', [...responsibilities, '']);
  };

  const removeResponsibility = (index: number) => {
    if (responsibilities.length > 1) {
      setValue('responsibilities', responsibilities.filter((_, i) => i !== index));
    }
  };

  const addBenefit = () => {
    setValue('benefits', [...benefits, '']);
  };

  const removeBenefit = (index: number) => {
    if (benefits.length > 1) {
      setValue('benefits', benefits.filter((_, i) => i !== index));
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)}>
      <VStack align="stretch" gap={8}>
        
        {/* AI Generation Toggle */}
        <Card.Root>
          <Card.Body>
            <VStack align="stretch" gap={4}>
              <HStack>
                <SparklesIcon size={20} />
                <Heading size="md">AI Generation Settings</Heading>
              </HStack>
              
              <Checkbox
                {...register('use_ai_generation')}
                checked={useAiGeneration}
                onCheckedChange={(checked) => setValue('use_ai_generation', !!checked.checked)}
              >
                Use AI-powered job posting generation
              </Checkbox>
              
              {useAiGeneration && (
                <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={4}>
                  <Field label="Generation Style" errorText={errors.generation_style?.message}>
                    <select {...register('generation_style')}>
                      {generationStyles.map(style => (
                        <option key={style.value} value={style.value}>
                          {style.label} - {style.description}
                        </option>
                      ))}
                    </select>
                  </Field>
                  
                  <Field label="Content Length" errorText={errors.length?.message}>
                    <select {...register('length')}>
                      {jobLengths.map(length => (
                        <option key={length.value} value={length.value}>
                          {length.label} - {length.description}
                        </option>
                      ))}
                    </select>
                  </Field>
                </Grid>
              )}
            </VStack>
          </Card.Body>
        </Card.Root>

        {/* Basic Information */}
        <Fieldset.Root>
          <Fieldset.Legend>Basic Information</Fieldset.Legend>
          <Fieldset.Content>
            <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
              <Field 
                label="Job Title" 
                required 
                errorText={errors.job_title?.message}
              >
                <input
                  {...register('job_title', { 
                    required: 'Job title is required',
                    minLength: { value: 2, message: 'Job title must be at least 2 characters' }
                  })}
                  placeholder="e.g., Senior Software Engineer"
                />
              </Field>
              
              <Field label="Location" errorText={errors.location?.message}>
                <input
                  {...register('location')}
                  placeholder="e.g., London, UK or Remote"
                />
              </Field>
              
              <Field label="Experience Level" errorText={errors.experience_level?.message}>
                <select {...register('experience_level')}>
                  {experienceLevels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </Field>
              
              <Field label="Employment Type" errorText={errors.employment_type?.message}>
                <select {...register('employment_type')}>
                  {employmentTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </Field>
              
              <Field label="Platform" errorText={errors.platform?.message}>
                <select {...register('platform')}>
                  {platformOptions.map(platform => (
                    <option key={platform.value} value={platform.value}>
                      {platform.label} - {platform.description}
                    </option>
                  ))}
                </select>
              </Field>
            </Grid>
          </Fieldset.Content>
        </Fieldset.Root>

        {/* Job Details */}
        <Fieldset.Root>
          <Fieldset.Legend>Job Details</Fieldset.Legend>
          <Fieldset.Content>
            <VStack align="stretch" gap={4}>
              <Field label="Job Overview" errorText={errors.job_overview?.message}>
                <textarea
                  {...register('job_overview')}
                  placeholder="Brief description of the role and its purpose..."
                  rows={4}
                />
              </Field>
              
              <Field label="Team Introduction" errorText={errors.team_intro?.message}>
                <textarea
                  {...register('team_intro')}
                  placeholder="Tell candidates about the team they'll be joining..."
                  rows={3}
                />
              </Field>
              
              {/* Responsibilities */}
              <Box>
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="medium">Key Responsibilities</Text>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={addResponsibility}
                    type="button"
                  >
                    <PlusIcon size={16} />
                    Add
                  </Button>
                </HStack>
                
                <VStack align="stretch" gap={2}>
                  {responsibilities.map((_, index) => (
                    <HStack key={index}>
                      <Field flex="1">
                        <input
                          {...register(`responsibilities.${index}` as const)}
                          placeholder={`Responsibility ${index + 1}...`}
                        />
                      </Field>
                      {responsibilities.length > 1 && (
                        <Button
                          size="sm"
                          variant="ghost"
                          colorPalette="red"
                          onClick={() => removeResponsibility(index)}
                          type="button"
                        >
                          <MinusIcon size={16} />
                        </Button>
                      )}
                    </HStack>
                  ))}
                </VStack>
              </Box>
              
              <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
                <Field label="Required Skills" errorText={errors.required_skills?.message}>
                  <textarea
                    {...register('required_skills')}
                    placeholder="List the essential skills and technologies..."
                    rows={4}
                  />
                </Field>
                
                <Field label="Education Requirements" errorText={errors.education_requirements?.message}>
                  <textarea
                    {...register('education_requirements')}
                    placeholder="Degree requirements, preferred fields of study..."
                    rows={4}
                  />
                </Field>
              </Grid>
              
              <Field label="Certifications" errorText={errors.certifications?.message}>
                <input
                  {...register('certifications')}
                  placeholder="Any required or preferred certifications..."
                />
              </Field>
            </VStack>
          </Fieldset.Content>
        </Fieldset.Root>

        {/* Compensation & Benefits */}
        <Fieldset.Root>
          <Fieldset.Legend>Compensation & Benefits</Fieldset.Legend>
          <Fieldset.Content>
            <VStack align="stretch" gap={4}>
              <Checkbox
                {...register('include_salary')}
                checked={includeSalary}
                onCheckedChange={(checked) => setValue('include_salary', !!checked.checked)}
              >
                Include salary information
              </Checkbox>
              
              {includeSalary && (
                <Field label="Salary Range" errorText={errors.salary_range?.message}>
                  <input
                    {...register('salary_range')}
                    placeholder="e.g., £60,000 - £80,000 per year"
                  />
                </Field>
              )}
              
              {/* Benefits */}
              <Box>
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="medium">Benefits</Text>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={addBenefit}
                    type="button"
                  >
                    <PlusIcon size={16} />
                    Add
                  </Button>
                </HStack>
                
                <VStack align="stretch" gap={2}>
                  {benefits.map((_, index) => (
                    <HStack key={index}>
                      <Field flex="1">
                        <input
                          {...register(`benefits.${index}` as const)}
                          placeholder={`Benefit ${index + 1}...`}
                        />
                      </Field>
                      {benefits.length > 1 && (
                        <Button
                          size="sm"
                          variant="ghost"
                          colorPalette="red"
                          onClick={() => removeBenefit(index)}
                          type="button"
                        >
                          <MinusIcon size={16} />
                        </Button>
                      )}
                    </HStack>
                  ))}
                </VStack>
              </Box>
              
              <Field label="Additional Perks" errorText={errors.perks?.message}>
                <textarea
                  {...register('perks')}
                  placeholder="Flexible working, training budget, company events..."
                  rows={3}
                />
              </Field>
            </VStack>
          </Fieldset.Content>
        </Fieldset.Root>

        {/* Keywords & SEO */}
        <Fieldset.Root>
          <Fieldset.Legend>Optimization</Fieldset.Legend>
          <Fieldset.Content>
            <Field label="Keywords" errorText={errors.keywords?.message}>
              <input
                {...register('keywords')}
                placeholder="Important keywords for search optimization..."
              />
            </Field>
            <Text fontSize="sm" color="fg.muted">
              Add relevant keywords to help your job posting appear in search results
            </Text>
          </Fieldset.Content>
        </Fieldset.Root>

        <Separator />

        {/* Submit Button */}
        <HStack justify="end">
          <Button
            type="submit"
            colorPalette="blue"
            size="lg"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Spinner size="sm" />
                Generating with AI...
              </>
            ) : (
              <>
                <SparklesIcon size={16} />
                Generate Job Posting
              </>
            )}
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default JobPostingForm;