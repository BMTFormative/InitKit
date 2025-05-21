import {
  SimpleGrid,
  Card,
  Text,
  VStack,
  Button,
  Badge,
  Heading,
  Box,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { SubscriptionsService, type ApiError } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { Skeleton } from "../ui/skeleton";

const SubscriptionPlans = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  // Note: This assumes the SubscriptionsService exists after backend implementation
  // For now, you might need to create a mock service or wait for backend
  const { data: plans, isLoading } = useQuery({
    queryKey: ["subscription-plans"],
    queryFn: () =>
      SubscriptionsService.listSubscriptionPlans({ activeOnly: true }),
  });

  const { data: currentSubscription } = useQuery({
    queryKey: ["my-subscription"],
    queryFn: () => SubscriptionsService.getMySubscription(),
  });

  const subscribeMutation = useMutation({
    mutationFn: (planId: string) =>
      SubscriptionsService.subscribeToPlan({
        requestBody: { plan_id: planId },
      }),
    onSuccess: () => {
      showSuccessToast("Successfully subscribed to plan");
      queryClient.invalidateQueries({ queryKey: ["my-subscription"] });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  if (isLoading) {
    return (
      <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
        {[1, 2, 3].map((i) => (
          <Card.Root key={i}>
            <Card.Body>
              <Skeleton height="200px" />
            </Card.Body>
          </Card.Root>
        ))}
      </SimpleGrid>
    );
  }

  return (
    <VStack gap={6} align="stretch">
      <Heading size="lg">Subscription Plans</Heading>

      <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
        {plans?.data.map((plan) => (
          <Card.Root key={plan.id}>
            <Card.Header>
              <VStack align="start" gap={2}>
                <Text fontSize="xl" fontWeight="bold">
                  {plan.name}
                </Text>
                <Text fontSize="3xl" fontWeight="bold" color="teal.500">
                  ${plan.price}
                  <Text as="span" fontSize="sm" color="gray.500">
                    /{plan.duration_days} days
                  </Text>
                </Text>
                <Text fontSize="md" color="gray.600">
                  Credits per user: {plan.credit_limit}
                </Text>
              </VStack>
            </Card.Header>

            <Card.Body>
              <VStack align="stretch" gap={4}>
                <Text>{plan.description}</Text>

                {plan.features && plan.features.length > 0 && (
                  <Box>
                    <Text fontWeight="semibold" mb={2}>
                      Features:
                    </Text>
                    <VStack align="start">
                      {plan.features.map((feature, index) => (
                        <Text key={index}>• {feature}</Text>
                      ))}
                    </VStack>
                  </Box>
                )}
              </VStack>
            </Card.Body>

            <Card.Footer>
              {currentSubscription?.plan_id === plan.id ? (
                <Badge colorPalette="green" size="lg">
                  Current Plan
                </Badge>
              ) : (
                <Button
                  colorPalette="teal"
                  width="full"
                  onClick={() => subscribeMutation.mutate(plan.id)}
                  loading={subscribeMutation.isPending}
                >
                  Subscribe
                </Button>
              )}
            </Card.Footer>
          </Card.Root>
        ))}
      </SimpleGrid>
    </VStack>
  );
};

export default SubscriptionPlans;
