import React, { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import {
  VStack,
  Button,
  Input,
  Textarea,
  Select,
  Checkbox,
  Box,
  Heading,
  Alert,
  Field,
  Accordion,
  Flex,
  Text,
  Portal,
  createListCollection,
} from "@chakra-ui/react";

import { useAuth } from "@/hooks/useAuth";
import { JobPostingService } from "@/services/job-posting-service";
import { JobPostingCreateRequest } from "@/types/job-postings";

// Create collections for select options
const experienceLevels = createListCollection({
  items: [
    { label: "Internship", value: "internship" },
    { label: "Entry (0-2 yrs)", value: "entry" },
    { label: "Associate (2-4 yrs)", value: "associate" },
    { label: "Mid (4-6 yrs)", value: "mid" },
    { label: "Senior (6-8 yrs)", value: "senior" },
    { label: "Director (8-10 yrs)", value: "director" },
    { label: "Executive (10+ yrs)", value: "executive" },
  ],
});

const employmentTypes = createListCollection({
  items: [
    { label: "Full-time", value: "full-time" },
    { label: "Part-time", value: "part-time" },
    { label: "Contract", value: "contract" },
    { label: "Internship", value: "internship" },
    { label: "Temporary", value: "temporary" },
  ],
});

const platforms = createListCollection({
  items: [
    { label: "LinkedIn", value: "LinkedIn" },
    { label: "Indeed", value: "Indeed" },
    { label: "Glassdoor", value: "Glassdoor" },
    { label: "Monster", value: "Monster" },
    { label: "ZipRecruiter", value: "ZipRecruiter" },
    { label: "Company Website", value: "Company Website" },
  ],
});

const lengthOptions = createListCollection({
  items: [
    { label: "Short", value: "short" },
    { label: "Standard", value: "standard" },
    { label: "Long", value: "long" },
  ],
});

interface JobPostingForm extends JobPostingCreateRequest {
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
  keywords?: string;
}

interface JobPostingPreviewProps {
  content: string;
  isLoading?: boolean;
}

const JobPostingPreview: React.FC<JobPostingPreviewProps> = ({
  content,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <Box p={6} border="1px solid" borderColor="gray.200" borderRadius="md">
        <Text>Generating job posting...</Text>
      </Box>
    );
  }

  if (!content) {
    return (
      <Box p={6} border="1px solid" borderColor="gray.200" borderRadius="md">
        <Text color="gray.500">Generated content will appear here...</Text>
      </Box>
    );
  }

  return (
    <Box p={6} border="1px solid" borderColor="gray.200" borderRadius="md">
      <Box
        dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, "<br />") }}
        lineHeight="1.6"
      />
    </Box>
  );
};

export const JobPostingGenerator = () => {
  const { user, creditBalance } = useAuth();
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");
  const [qualityScore, setQualityScore] = useState(0);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    control,
  } = useForm<JobPostingForm>({
    defaultValues: {
      platform: "LinkedIn",
      length: "standard",
      include_salary: false,
    },
  });

  const watchIncludeSalary = watch("include_salary");

  const onSubmit = async (data: JobPostingForm) => {
    if (creditBalance < 5) {
      return;
    }

    setIsGenerating(true);
    try {
      const result = await JobPostingService.generateJobPosting(data);
      setGeneratedContent(result.generated_content || "");
      setQualityScore(result.quality_score || 0);
    } catch (error) {
      console.error("Generation error:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
      <VStack align="stretch" gap={6}>
        <Heading size="lg">Job Posting Generator</Heading>

        {/* Credit Balance Alert */}
        {creditBalance < 5 && (
          <Alert.Root status="warning">
            <Alert.Description>
              Insufficient credits. Need 5 credits to generate job posting.
            </Alert.Description>
          </Alert.Root>
        )}

        <Flex gap={6}>
          {/* Form Section */}
          <Box flex="1">
            <form onSubmit={handleSubmit(onSubmit)}>
              <Accordion.Root multiple defaultValue={["essential"]}>
                {/* 1. Essential Information */}
                <Accordion.Item value="essential">
                  <Accordion.ItemTrigger>
                    <Text fontWeight="semibold">1. Essential Information</Text>
                    <Accordion.ItemIndicator />
                  </Accordion.ItemTrigger>
                  <Accordion.ItemContent>
                    <Accordion.ItemBody>
                      <VStack gap={4} align="stretch">
                        <Field.Root invalid={!!errors.job_title} required>
                          <Field.Label>
                            Job Title
                            <Field.RequiredIndicator />
                          </Field.Label>
                          <Input
                            {...register("job_title", {
                              required: "Job title is required",
                            })}
                            placeholder="Enter job title"
                          />
                          {errors.job_title && (
                            <Field.ErrorText>
                              {errors.job_title.message}
                            </Field.ErrorText>
                          )}
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Job Overview</Field.Label>
                          <Textarea
                            {...register("job_overview")}
                            rows={6}
                            placeholder="Brief overview or paste complete job description..."
                          />
                          <Field.HelperText>
                            Provide a brief overview or paste your complete job
                            description
                          </Field.HelperText>
                        </Field.Root>
                      </VStack>
                    </Accordion.ItemBody>
                  </Accordion.ItemContent>
                </Accordion.Item>

                {/* 2. Job Context */}
                <Accordion.Item value="context">
                  <Accordion.ItemTrigger>
                    <Text fontWeight="semibold">2. Job Context</Text>
                    <Accordion.ItemIndicator />
                  </Accordion.ItemTrigger>
                  <Accordion.ItemContent>
                    <Accordion.ItemBody>
                      <VStack gap={4} align="stretch">
                        <Field.Root>
                          <Field.Label>Location</Field.Label>
                          <Input
                            {...register("location")}
                            placeholder="e.g. Remote, New York, London"
                          />
                        </Field.Root>

                        <Flex gap={4}>
                          {/* Experience Level Select */}
                          <Field.Root flex="1">
                            <Field.Label>Experience Level</Field.Label>
                            <Controller
                              name="experience_level"
                              control={control}
                              render={({ field }) => (
                                <Select.Root
                                  collection={experienceLevels}
                                  value={field.value ? [field.value] : []}
                                  onValueChange={(details) => {
                                    field.onChange(details.value[0] || "");
                                  }}
                                >
                                  <Select.HiddenSelect />
                                  <Select.Control>
                                    <Select.Trigger>
                                      <Select.ValueText placeholder="Select experience level" />
                                    </Select.Trigger>
                                    <Select.IndicatorGroup>
                                      <Select.Indicator />
                                    </Select.IndicatorGroup>
                                  </Select.Control>
                                  <Portal>
                                    <Select.Positioner>
                                      <Select.Content>
                                        {experienceLevels.items.map((level) => (
                                          <Select.Item
                                            item={level}
                                            key={level.value}
                                          >
                                            <Select.ItemText>
                                              {level.label}
                                            </Select.ItemText>
                                            <Select.ItemIndicator />
                                          </Select.Item>
                                        ))}
                                      </Select.Content>
                                    </Select.Positioner>
                                  </Portal>
                                </Select.Root>
                              )}
                            />
                          </Field.Root>

                          {/* Employment Type Select */}
                          <Field.Root flex="1">
                            <Field.Label>Employment Type</Field.Label>
                            <Controller
                              name="employment_type"
                              control={control}
                              render={({ field }) => (
                                <Select.Root
                                  collection={employmentTypes}
                                  value={field.value ? [field.value] : []}
                                  onValueChange={(details) => {
                                    field.onChange(details.value[0] || "");
                                  }}
                                >
                                  <Select.HiddenSelect />
                                  <Select.Control>
                                    <Select.Trigger>
                                      <Select.ValueText placeholder="Select employment type" />
                                    </Select.Trigger>
                                    <Select.IndicatorGroup>
                                      <Select.Indicator />
                                    </Select.IndicatorGroup>
                                  </Select.Control>
                                  <Portal>
                                    <Select.Positioner>
                                      <Select.Content>
                                        {employmentTypes.items.map((type) => (
                                          <Select.Item
                                            item={type}
                                            key={type.value}
                                          >
                                            <Select.ItemText>
                                              {type.label}
                                            </Select.ItemText>
                                            <Select.ItemIndicator />
                                          </Select.Item>
                                        ))}
                                      </Select.Content>
                                    </Select.Positioner>
                                  </Portal>
                                </Select.Root>
                              )}
                            />
                          </Field.Root>
                        </Flex>

                        <Field.Root>
                          <Field.Label>Team / Organization</Field.Label>
                          <Textarea
                            {...register("team_intro")}
                            rows={2}
                            placeholder="Brief intro about the team or organization"
                          />
                        </Field.Root>
                      </VStack>
                    </Accordion.ItemBody>
                  </Accordion.ItemContent>
                </Accordion.Item>

                {/* 3. Qualifications & Skills */}
                <Accordion.Item value="qualifications">
                  <Accordion.ItemTrigger>
                    <Text fontWeight="semibold">
                      3. Qualifications & Skills
                    </Text>
                    <Accordion.ItemIndicator />
                  </Accordion.ItemTrigger>
                  <Accordion.ItemContent>
                    <Accordion.ItemBody>
                      <VStack gap={4} align="stretch">
                        <Field.Root>
                          <Field.Label>Key Responsibilities</Field.Label>
                          <Textarea
                            {...register("responsibilities")}
                            rows={4}
                            placeholder="List each responsibility on its own line"
                          />
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Required Skills</Field.Label>
                          <Textarea
                            {...register("required_skills")}
                            rows={3}
                            placeholder="List each required skill on its own line"
                          />
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Education Requirements</Field.Label>
                          <Textarea
                            {...register("education_requirements")}
                            rows={2}
                            placeholder="List education requirements"
                          />
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Certifications</Field.Label>
                          <Textarea
                            {...register("certifications")}
                            rows={2}
                            placeholder="List relevant certifications"
                          />
                        </Field.Root>
                      </VStack>
                    </Accordion.ItemBody>
                  </Accordion.ItemContent>
                </Accordion.Item>

                {/* 4. Compensation & Benefits */}
                <Accordion.Item value="compensation">
                  <Accordion.ItemTrigger>
                    <Text fontWeight="semibold">
                      4. Compensation & Benefits
                    </Text>
                    <Accordion.ItemIndicator />
                  </Accordion.ItemTrigger>
                  <Accordion.ItemContent>
                    <Accordion.ItemBody>
                      <VStack gap={4} align="stretch">
                        <Field.Root>
                          <Checkbox.Root
                            checked={watchIncludeSalary}
                            onCheckedChange={(e) =>
                              setValue("include_salary", !!e.checked)
                            }
                          >
                            <Checkbox.HiddenInput
                              {...register("include_salary")}
                            />
                            <Checkbox.Control />
                            <Checkbox.Label>
                              Include Salary Range
                            </Checkbox.Label>
                          </Checkbox.Root>
                        </Field.Root>

                        {watchIncludeSalary && (
                          <Field.Root>
                            <Field.Label>Salary Range</Field.Label>
                            <Input
                              {...register("salary_range")}
                              placeholder="e.g. $50k-$70k, £40k-£60k"
                            />
                          </Field.Root>
                        )}

                        <Field.Root>
                          <Field.Label>Benefits & Perks</Field.Label>
                          <Textarea
                            {...register("perks")}
                            rows={3}
                            placeholder="List benefits and perks, one per line"
                          />
                        </Field.Root>
                      </VStack>
                    </Accordion.ItemBody>
                  </Accordion.ItemContent>
                </Accordion.Item>

                {/* 5. Publication Settings */}
                <Accordion.Item value="publication">
                  <Accordion.ItemTrigger>
                    <Text fontWeight="semibold">5. Publication Settings</Text>
                    <Accordion.ItemIndicator />
                  </Accordion.ItemTrigger>
                  <Accordion.ItemContent>
                    <Accordion.ItemBody>
                      <VStack gap={4} align="stretch">
                        {/* Platform Select */}
                        <Field.Root>
                          <Field.Label>Platform</Field.Label>
                          <Controller
                            name="platform"
                            control={control}
                            defaultValue="LinkedIn"
                            render={({ field }) => (
                              <Select.Root
                                collection={platforms}
                                value={
                                  field.value ? [field.value] : ["LinkedIn"]
                                }
                                onValueChange={(details) => {
                                  field.onChange(
                                    details.value[0] || "LinkedIn"
                                  );
                                }}
                              >
                                <Select.HiddenSelect />
                                <Select.Control>
                                  <Select.Trigger>
                                    <Select.ValueText placeholder="Select platform" />
                                  </Select.Trigger>
                                  <Select.IndicatorGroup>
                                    <Select.Indicator />
                                  </Select.IndicatorGroup>
                                </Select.Control>
                                <Portal>
                                  <Select.Positioner>
                                    <Select.Content>
                                      {platforms.items.map((platform) => (
                                        <Select.Item
                                          item={platform}
                                          key={platform.value}
                                        >
                                          <Select.ItemText>
                                            {platform.label}
                                          </Select.ItemText>
                                          <Select.ItemIndicator />
                                        </Select.Item>
                                      ))}
                                    </Select.Content>
                                  </Select.Positioner>
                                </Portal>
                              </Select.Root>
                            )}
                          />
                        </Field.Root>

                        {/* Length Select */}
                        <Field.Root>
                          <Field.Label>Length</Field.Label>
                          <Controller
                            name="length"
                            control={control}
                            defaultValue="standard"
                            render={({ field }) => (
                              <Select.Root
                                collection={lengthOptions}
                                value={
                                  field.value ? [field.value] : ["standard"]
                                }
                                onValueChange={(details) => {
                                  field.onChange(
                                    details.value[0] || "standard"
                                  );
                                }}
                              >
                                <Select.HiddenSelect />
                                <Select.Control>
                                  <Select.Trigger>
                                    <Select.ValueText placeholder="Select length" />
                                  </Select.Trigger>
                                  <Select.IndicatorGroup>
                                    <Select.Indicator />
                                  </Select.IndicatorGroup>
                                </Select.Control>
                                <Portal>
                                  <Select.Positioner>
                                    <Select.Content>
                                      {lengthOptions.items.map((length) => (
                                        <Select.Item
                                          item={length}
                                          key={length.value}
                                        >
                                          <Select.ItemText>
                                            {length.label}
                                          </Select.ItemText>
                                          <Select.ItemIndicator />
                                        </Select.Item>
                                      ))}
                                    </Select.Content>
                                  </Select.Positioner>
                                </Portal>
                              </Select.Root>
                            )}
                          />
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Application Deadline (days)</Field.Label>
                          <Input
                            {...register("application_deadline", {
                              valueAsNumber: true,
                            })}
                            type="number"
                            placeholder="30"
                            defaultValue={30}
                          />
                        </Field.Root>

                        <Field.Root>
                          <Field.Label>Additional Keywords</Field.Label>
                          <Textarea
                            {...register("keywords")}
                            rows={2}
                            placeholder="Additional keywords, comma-separated"
                          />
                        </Field.Root>
                      </VStack>
                    </Accordion.ItemBody>
                  </Accordion.ItemContent>
                </Accordion.Item>
              </Accordion.Root>

              <Button
                type="submit"
                size="lg"
                w="full"
                mt={6}
                loading={isGenerating}
                disabled={creditBalance < 5}
              >
                Generate Job Posting (5 credits)
              </Button>
            </form>
          </Box>

          {/* Generated Content Section */}
          <Box flex="1">
            <VStack align="stretch" gap={4}>
              <Flex justify="space-between" align="center">
                <Heading size="md">Generated Job Posting</Heading>
                {qualityScore > 0 && (
                  <Text fontSize="sm" color="gray.600">
                    Quality Score: {qualityScore}%
                  </Text>
                )}
              </Flex>

              <JobPostingPreview
                content={generatedContent}
                isLoading={isGenerating}
              />

              {generatedContent && (
                <Flex gap={2}>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      navigator.clipboard.writeText(generatedContent)
                    }
                  >
                    Copy
                  </Button>
                  <Button size="sm" variant="outline">
                    Download
                  </Button>
                  <Button size="sm" variant="outline">
                    Save Template
                  </Button>
                </Flex>
              )}
            </VStack>
          </Box>
        </Flex>
      </VStack>
  );
};

export default JobPostingGenerator;
