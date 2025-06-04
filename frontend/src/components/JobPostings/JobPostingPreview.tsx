// frontend/src/components/JobPostings/JobPostingPreview.tsx
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
  Spinner,
  IconButton,
  Clipboard ,
  Alert,
} from '@chakra-ui/react';
import {
  CopyIcon,
  CheckIcon,
  DownloadIcon,
  TrendingUp,
  SaveIcon,
  EyeIcon,
  LinkedinIcon,
} from 'lucide-react';

//import useCustomToast from "../../hooks/useCustomToast"
import { toaster } from "@/components/ui/toaster"
interface JobPostingPreviewProps {
  content: string;
  platform: string;
  onAnalyze: () => void;
  onSave: () => void;
  isAnalyzing: boolean;
  isSaving: boolean;
}

const JobPostingPreview = ({
  content,
  platform,
  onAnalyze,
  onSave,
  isAnalyzing,
  isSaving
}: JobPostingPreviewProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  //const showToast = useCustomToast();

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `job-posting-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toaster.create({
      title: 'Downloaded successfully',
      description: 'Job posting has been saved to your downloads.',
      type: 'success'
    });
  };

  const getPlatformIcon = () => {
    switch (platform.toLowerCase()) {
      case 'linkedin':
        return <LinkedinIcon size={16} />;
      default:
        return <EyeIcon size={16} />;
    }
  };

  const getPlatformColor = () => {
    switch (platform.toLowerCase()) {
      case 'linkedin':
        return 'blue';
      case 'indeed':
        return 'green';
      case 'glassdoor':
        return 'teal';
      default:
        return 'gray';
    }
  };

  const formatContentForDisplay = (text: string) => {
    // Convert line breaks to HTML for better display
    return text.split('\n').map((line, index) => (
      <Text key={index} mb={line.trim() === '' ? 4 : 1}>
        {line || '\u00A0'} {/* Non-breaking space for empty lines */}
      </Text>
    ));
  };

  const previewContent = isExpanded ? content : content.slice(0, 500) + (content.length > 500 ? '...' : '');

  if (!content.trim()) {
    return (
      <Card.Root>
        <Card.Body>
          <VStack py={12} align="center" gap={4}>
            <Box p={4} bg="bg.muted" borderRadius="full">
              <EyeIcon size={32} />
            </Box>
            <VStack gap={2} textAlign="center">
              <Heading size="md" color="fg.muted">
                No content to preview
              </Heading>
              <Text color="fg.muted">
                Generate a job posting first to see the preview here.
              </Text>
            </VStack>
          </VStack>
        </Card.Body>
      </Card.Root>
    );
  }

  return (
    <VStack align="stretch" gap={6}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <HStack>
          <Heading size="md">Job Posting Preview</Heading>
          <Badge variant="subtle" colorPalette={getPlatformColor()}>
            <HStack>
              {getPlatformIcon()}
              <Text>{platform.charAt(0).toUpperCase() + platform.slice(1)}</Text>
            </HStack>
          </Badge>
        </HStack>
        
        <HStack>
          <IconButton
            size="sm"
            variant="ghost"
            aria-label="Copy to clipboard"
          >
            <Clipboard.Indicator copied="Copied!" />
            Copy Content
          </IconButton>
          
          <IconButton
            size="sm"
            variant="ghost"
            onClick={handleDownload}
            aria-label="Download as text file"
          >
            <DownloadIcon size={16} />
          </IconButton>
        </HStack>
      </HStack>

      {/* Platform-specific info */}
      {platform.toLowerCase() === 'linkedin' && (
        <Alert.Root status="info" variant="subtle">
          <Box>
            <Text fontWeight="medium">LinkedIn Optimized</Text>
            <Text fontSize="sm">
              This content is formatted for LinkedIn with emojis, short paragraphs, and social media optimization.
            </Text>
          </Box>
        </Alert.Root>
      )}

      {/* Content Preview */}
      <Card.Root>
        <Card.Header>
          <HStack justify="space-between">
            <Text fontWeight="medium">Generated Content</Text>
            <Text fontSize="sm" color="fg.muted">
              {content.length} characters
            </Text>
          </HStack>
        </Card.Header>
        
        <Card.Body>
          <Box
            p={4}
            bg="bg.subtle"
            borderRadius="md"
            border="1px solid"
            borderColor="border.muted"
            maxH={isExpanded ? "none" : "400px"}
            overflow="auto"
            fontFamily="mono"
            fontSize="sm"
            lineHeight="tall"
            whiteSpace="pre-wrap"
          >
            {formatContentForDisplay(previewContent)}
          </Box>
          
          {content.length > 500 && (
            <HStack justify="center" mt={4}>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsExpanded(!isExpanded)}
              >
                {isExpanded ? 'Show Less' : 'Show More'}
              </Button>
            </HStack>
          )}
        </Card.Body>
      </Card.Root>

      {/* Actions */}
      <Card.Root>
        <Card.Body>
          <VStack gap={4}>
            <HStack justify="space-between" w="full">
              <VStack align="start" gap={1}>
                <Text fontWeight="medium">What's Next?</Text>
                <Text fontSize="sm" color="fg.muted">
                  Analyze the quality or save your job posting.
                </Text>
              </VStack>
              
              <HStack>
                <Button
                  variant="outline"
                  onClick={onAnalyze}
                  disabled={isAnalyzing}
                >
                  {isAnalyzing ? (
                    <>
                      <Spinner size="sm" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <TrendingUp size={16} />
                      Analyze Quality
                    </>
                  )}
                </Button>
                
                <Button
                  colorPalette="blue"
                  onClick={onSave}
                  disabled={isSaving}
                >
                  {isSaving ? (
                    <>
                      <Spinner size="sm" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <SaveIcon size={16} />
                      Save Posting
                    </>
                  )}
                </Button>
              </HStack>
            </HStack>

            {/* Copy Success Message */}
            {/* {hasCopied && (
              <Alert.Root status="success" variant="subtle" size="sm">
                <Text fontSize="sm">Content copied to clipboard!</Text>
              </Alert.Root>
            )} */}
          </VStack>
        </Card.Body>
      </Card.Root>

      {/* Usage Tips */}
      <Card.Root variant="subtle">
        <Card.Body>
          <VStack align="start" gap={3}>
            <Text fontWeight="medium" fontSize="sm">💡 Usage Tips</Text>
            <VStack align="start" gap={1} fontSize="sm" color="fg.muted">
              <Text>• Copy the content and paste it directly into {platform}</Text>
              <Text>• Use the analysis feature to get quality feedback and suggestions</Text>
              <Text>• Save successful postings as templates for future use</Text>
              {platform.toLowerCase() === 'linkedin' && (
                <Text>• LinkedIn formatting includes emojis and optimized spacing</Text>
              )}
            </VStack>
          </VStack>
        </Card.Body>
      </Card.Root>
    </VStack>
  );
};

export default JobPostingPreview;