import {
  SimpleGrid,
  Card,
  Text,
  VStack,
  Button,
  Badge,
  Heading,
  Box,
  HStack,
  Dialog
} from "@chakra-ui/react";
import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { SubscriptionsService, type ApiError } from "@/client";
import { PaymentService } from "@/services/payment-service";
import { CreditCardForm } from "@/components/Payment/CreditCardForm";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { Skeleton } from "../ui/skeleton";

const SubscriptionPlans = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  
  // State for payment modal
  const [selectedPlan, setSelectedPlan] = useState<any>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);

  // Fix scroll lock issue
  useEffect(() => {
    const handleScrollLock = () => {
      if (showPaymentModal) {
        // Ensure body can still scroll when modal is open if needed
        document.body.style.overflowY = 'hidden';
      } else {
        // Restore scroll when modal closes
        document.body.style.overflowY = 'auto';
      }
    };

    handleScrollLock();

    // Cleanup on unmount
    return () => {
      document.body.style.overflowY = 'auto';
    };
  }, [showPaymentModal]);

  const { data: plans, isLoading } = useQuery({
    queryKey: ["subscription-plans"],
    queryFn: () =>
      SubscriptionsService.listSubscriptionPlans({ activeOnly: true }),
  });

  const { data: currentSubscription } = useQuery({
    queryKey: ["my-subscription"],
    queryFn: () => SubscriptionsService.getMySubscription(),
  });

  // Free plan subscription (no payment required)
  const freeSubscribeMutation = useMutation({
    mutationFn: (planId: string) =>
      PaymentService.subscribeWithPayment(planId), // No payment method ID
    onSuccess: () => {
      showSuccessToast("Successfully subscribed to free plan");
      queryClient.invalidateQueries({ queryKey: ["my-subscription"] });
      setSelectedPlan(null);
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  // Paid plan subscription (with payment)
  const paidSubscribeMutation = useMutation({
    mutationFn: ({ planId, paymentMethodId }: { planId: string; paymentMethodId: string }) =>
      PaymentService.subscribeWithPayment(planId, paymentMethodId),
    onSuccess: () => {
      showSuccessToast("Successfully subscribed to plan");
      queryClient.invalidateQueries({ queryKey: ["my-subscription"] });
      closeModal();
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const handleSubscribeClick = (plan: any) => {
    if (plan.price === 0) {
      // Free plan - subscribe directly
      freeSubscribeMutation.mutate(plan.id);
    } else {
      // Paid plan - show payment modal
      setSelectedPlan(plan);
      setShowPaymentModal(true);
    }
  };

  const closeModal = () => {
    setShowPaymentModal(false);
    setSelectedPlan(null);
    // Force scroll restoration
    setTimeout(() => {
      document.body.style.overflowY = 'auto';
    }, 100);
  };

  const handlePaymentSubmit = (paymentMethodId: string) => {
    if (selectedPlan) {
      paidSubscribeMutation.mutate({
        planId: selectedPlan.id,
        paymentMethodId,
      });
    }
  };

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
    <>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Subscription Plans</Heading>

        <SimpleGrid columns={{ base: 1, md: 3 }} gap={6}>
          {plans?.data.map((plan) => (
            <Card.Root key={plan.id} variant={plan.price === 0 ? "outline" : "elevated"}>
              <Card.Header>
                <VStack align="start" gap={2}>
                  <HStack justify="space-between" width="100%">
                    <Text fontSize="xl" fontWeight="bold">
                      {plan.name}
                    </Text>
                    {plan.price === 0 && (
                      <Badge colorPalette="green" size="sm">
                        FREE
                      </Badge>
                    )}
                  </HStack>
                  
                  <Text fontSize="3xl" fontWeight="bold" color="teal.500">
                    {plan.price === 0 ? (
                      "Free"
                    ) : (
                      <>
                        ${plan.price}
                        <Text as="span" fontSize="sm" color="gray.500">
                          /{plan.duration_days} days
                        </Text>
                      </>
                    )}
                  </Text>
                  
                  {plan.credit_limit && (
                    <Text fontSize="md" color="gray.600">
                      Credits per user: {plan.credit_limit}
                    </Text>
                  )}
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
                    width="100%"
                    onClick={() => handleSubscribeClick(plan)}
                    loading={
                      freeSubscribeMutation.isPending || 
                      (paidSubscribeMutation.isPending && selectedPlan?.id === plan.id)
                    }
                  >
                    {plan.price === 0 ? "Get Started Free" : "Subscribe"}
                  </Button>
                )}
              </Card.Footer>
            </Card.Root>
          ))}
        </SimpleGrid>
      </VStack>

      {/* Payment Modal for Paid Plans */}
      <Dialog.Root 
        open={showPaymentModal} 
        onOpenChange={({ open }) => {
          if (!open) {
            closeModal();
          }
        }}
      >
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content
            maxW="md"
            maxH="90vh"
            css={{
              overflowY: "auto",
            }}
          >
            <Dialog.Header>
              <Dialog.Title>Complete Your Subscription</Dialog.Title>
            </Dialog.Header>
            
            <Dialog.Body>
              {selectedPlan && (
                <VStack gap={4} align="stretch">
                  <Box p={4} borderRadius="md" bg="gray.50">
                    <Text fontWeight="semibold">{selectedPlan.name}</Text>
                    <Text fontSize="lg" color="teal.500">
                      ${selectedPlan.price}/{selectedPlan.duration_days} days
                    </Text>
                  </Box>
                  
                  <CreditCardForm
                    onSubmit={handlePaymentSubmit}
                    loading={paidSubscribeMutation.isPending}
                  />
                </VStack>
              )}
            </Dialog.Body>
            
            <Dialog.Footer>
              <Button
                variant="outline"
                onClick={closeModal}
              >
                Cancel
              </Button>
            </Dialog.Footer>
          </Dialog.Content>
        </Dialog.Positioner>
      </Dialog.Root>
    </>
  );
};

export default SubscriptionPlans;