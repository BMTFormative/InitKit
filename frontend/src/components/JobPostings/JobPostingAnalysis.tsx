// frontend/src/components/JobPostings/JobPostingAnalysis.tsx
import { useState } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  Badge,
  Progress,
  Alert,
  Textarea,
  Checkbox,
} from '@chakra-ui/react';
import {
  TrendingUp,
  CheckCircleIcon,
  AlertCircleIcon,
  LightbulbIcon,
  SparklesIcon,
  TrendingUpIcon,
} from 'lucide-react';


import { JobPostingAnalysisResponse } from '@/types/job-postings';
import { toaster } from "@/components/ui/toaster"

interface JobPostingAnalysisProps {
  analysisData: JobPostingAnalysisResponse | null;
  originalContent: string;
  onApplySuggestions: (suggestions: string[], comment?: string) => void;
}

const JobPostingAnalysis = ({
  analysisData,
  originalContent,
  onApplySuggestions
}: JobPostingAnalysisProps) => {
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([]);
  const [suggestionComment, setSuggestionComment] = useState('');
  

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  const handleSuggestionToggle = (suggestion: string) => {
    setSelectedSuggestions(prev => 
      prev.includes(suggestion) 
        ? prev.filter(s => s !== suggestion)
        : [...prev, suggestion]
    );
  };

  const handleApplySuggestions = () => {
    if (selectedSuggestions.length === 0) {
      toaster.create({
        title: 'No suggestions selected',
        description: 'Please select at least one suggestion to apply.',
        type: 'warning'
      });
      return;
    }
    
    onApplySuggestions(selectedSuggestions, suggestionComment);
  };

  if (!analysisData) {
    return (
      <Card.Root>
        <Card.Body>
          <VStack py={12} align="center" gap={4}>
            <Box p={4} bg="bg.muted" borderRadius="full">
              <TrendingUp size={32} />
            </Box>
            <VStack gap={2} textAlign="center">
              <Heading size="md" color="fg.muted">
                No analysis available
              </Heading>
              <Text color="fg.muted">
                Generate and analyze a job posting to see quality insights here.
              </Text>
            </VStack>
          </VStack>
        </Card.Body>
      </Card.Root>
    );
  }

  const { score, suggestions, success } = analysisData;

  if (!success) {
    return (
      <Alert.Root status="error">
        <AlertCircleIcon size={16} />
        <Box>
          <Text fontWeight="medium">Analysis Failed</Text>
          <Text fontSize="sm">
            Unable to analyze the job posting. Please try again later.
          </Text>
        </Box>
      </Alert.Root>
    );
  }

  return (
    <VStack align="stretch" gap={6}>
      {/* Quality Score */}
      <Card.Root>
        <Card.Header>
          <HStack>
            <TrendingUp size={20} />
            <Heading size="md">Quality Analysis</Heading>
          </HStack>
        </Card.Header>
        
        <Card.Body>
          <VStack gap={6}>
            {/* Score Display */}
            <VStack gap={4} w="full">
              <HStack justify="space-between" w="full">
                <VStack align="start" gap={1}>
                  <Text fontSize="3xl" fontWeight="bold" color={`${getScoreColor(score)}.500`}>
                    {score}/100
                  </Text>
                  <Badge 
                    variant="subtle" 
                    colorPalette={getScoreColor(score)}
                    size="lg"
                  >
                    {getScoreLabel(score)}
                  </Badge>
                </VStack>
                
                <Box flex="1" ml={8}>
                  <Text fontSize="sm" color="fg.muted" mb={2}>
                    Quality Score
                  </Text>
                  <Progress.Root 
                    value={score} 
                    max={100}
                    colorPalette={getScoreColor(score)}
                    size="lg"
                  />
                </Box>
              </HStack>

              {/* Score Breakdown */}
              <HStack gap={6} w="full" justify="center">
                <VStack gap={1} align="center">
                  <Text fontSize="sm" fontWeight="medium">Content</Text>
                  <Text fontSize="xs" color="fg.muted">Structure & clarity</Text>
                </VStack>
                <VStack gap={1} align="center">
                  <Text fontSize="sm" fontWeight="medium">Appeal</Text>
                  <Text fontSize="xs" color="fg.muted">Attractiveness</Text>
                </VStack>
                <VStack gap={1} align="center">
                  <Text fontSize="sm" fontWeight="medium">Completeness</Text>
                  <Text fontSize="xs" color="fg.muted">Required information</Text>
                </VStack>
              </HStack>
            </VStack>

            {/* Quick Insights */}
            <Alert.Root 
              status={score >= 80 ? "success" : score >= 60 ? "warning" : "error"} 
              variant="subtle"
            >
              {score >= 80 ? <CheckCircleIcon size={16} /> : <AlertCircleIcon size={16} />}
              <Box>
                <Text fontWeight="medium">
                  {score >= 80 
                    ? "Great job posting!" 
                    : score >= 60 
                    ? "Good foundation, some improvements possible" 
                    : "Several areas need attention"
                  }
                </Text>
                <Text fontSize="sm">
                  {score >= 80 
                    ? "Your job posting follows best practices and should attract quality candidates."
                    : score >= 60
                    ? "Your posting is on the right track but could benefit from some enhancements."
                    : "Consider applying the suggestions below to significantly improve your posting."
                  }
                </Text>
              </Box>
            </Alert.Root>
          </VStack>
        </Card.Body>
      </Card.Root>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <Card.Root>
          <Card.Header>
            <HStack justify="space-between">
              <HStack>
                <LightbulbIcon size={20} />
                <Heading size="md">Improvement Suggestions</Heading>
                <Badge variant="outline">
                  {suggestions.length} suggestion{suggestions.length > 1 ? 's' : ''}
                </Badge>
              </HStack>
              
              {selectedSuggestions.length > 0 && (
                <Badge colorPalette="blue">
                  {selectedSuggestions.length} selected
                </Badge>
              )}
            </HStack>
          </Card.Header>
          
          <Card.Body>
            <VStack align="stretch" gap={4}>
              <Text fontSize="sm" color="fg.muted">
                Select suggestions you'd like to apply automatically using AI:
              </Text>
              
              <VStack align="stretch" gap={3}>
                {suggestions.map((suggestion, index) => (
                  <Card.Root 
                    key={index}
                    variant="subtle"
                    cursor="pointer"
                    onClick={() => handleSuggestionToggle(suggestion)}
                    _hover={{ bg: 'bg.muted' }}
                  >
                    <Card.Body py={3}>
                      <HStack align="start" gap={3}>
                        <Checkbox.Root
                          checked={selectedSuggestions.includes(suggestion)}
                          onCheckedChange={() => handleSuggestionToggle(suggestion)}
                        />
                        <VStack align="start" gap={1} flex="1">
                          <Text fontSize="sm" fontWeight="medium">
                            Suggestion {index + 1}
                          </Text>
                          <Text fontSize="sm" color="fg.muted">
                            {suggestion}
                          </Text>
                        </VStack>
                      </HStack>
                    </Card.Body>
                  </Card.Root>
                ))}
              </VStack>

              {/* Additional Comments */}
              <Box>
                <Text fontSize="sm" fontWeight="medium" mb={2}>
                  Additional Instructions (Optional)
                </Text>
                <Textarea
                  value={suggestionComment}
                  onChange={(e) => setSuggestionComment(e.target.value)}
                  placeholder="Add any specific instructions for how to apply these suggestions..."
                  rows={3}
                  fontSize="sm"
                />
              </Box>

              {/* Apply Button */}
              <HStack justify="end">
                <Button
                  colorPalette="blue"
                  onClick={handleApplySuggestions}
                  disabled={selectedSuggestions.length === 0}
                >
                  <SparklesIcon size={16} />
                  Apply {selectedSuggestions.length} Suggestion{selectedSuggestions.length > 1 ? 's' : ''}
                </Button>
              </HStack>
            </VStack>
          </Card.Body>
        </Card.Root>
      )}

      {/* Analysis Insights */}
      <Card.Root variant="subtle">
        <Card.Body>
          <VStack align="start" gap={3}>
            <HStack>
              <TrendingUpIcon size={16} />
              <Text fontWeight="medium" fontSize="sm">Analysis Insights</Text>
            </HStack>
            <VStack align="start" gap={1} fontSize="sm" color="fg.muted">
              <Text>• Analysis powered by Claude AI using job posting best practices</Text>
              <Text>• Score considers content quality, structure, and appeal to candidates</Text>
              <Text>• Higher scores correlate with better application rates and candidate quality</Text>
              <Text>• Apply suggestions to automatically improve your posting with AI</Text>
            </VStack>
          </VStack>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
};

export default JobPostingAnalysis;