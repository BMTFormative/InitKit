import { Card, Text, VStack, Button, Badge, Flex } from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { SubscriptionsService, type ApiError } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { format } from "date-fns";
import { SkeletonText } from "../ui/skeleton";

const CurrentSubscription = () => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  const { data: subscription, isLoading } = useQuery({
    queryKey: ["my-subscription"],
    queryFn: () => SubscriptionsService.getMySubscription(),
  });

  const cancelMutation = useMutation({
    mutationFn: (subscriptionId: string) =>
      SubscriptionsService.updateSubscription({
        subscriptionId,
        requestBody: { status: "cancelled" },
      }),
    onSuccess: () => {
      showSuccessToast("Subscription cancelled successfully");
      queryClient.invalidateQueries({ queryKey: ["my-subscription"] });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  if (isLoading) {
    return (
      <Card.Root>
        <Card.Body>
          <SkeletonText noOfLines={5} />
        </Card.Body>
      </Card.Root>
    );
  }

  if (!subscription) {
    return (
      <Card.Root>
        <Card.Body>
          <Text>You don't have an active subscription.</Text>
        </Card.Body>
      </Card.Root>
    );
  }

  return (
    <Card.Root>
      <Card.Header>
        <Text fontSize="xl" fontWeight="bold">
          Current Subscription
        </Text>
      </Card.Header>

      <Card.Body>
        <VStack align="stretch" gap={4}>
          <Flex justify="space-between" align="center">
            <Text fontWeight="semibold">Plan:</Text>
            <Text>{subscription.plan.name}</Text>
          </Flex>

          <Flex justify="space-between" align="center">
            <Text fontWeight="semibold">Price:</Text>
            <Text>${subscription.plan.price}</Text>
          </Flex>

          <Flex justify="space-between" align="center">
            <Text fontWeight="semibold">Start Date:</Text>
            <Text>
              {format(new Date(subscription.start_date || ""), "PPP")}
            </Text>
          </Flex>

          <Flex justify="space-between" align="center">
            <Text fontWeight="semibold">End Date:</Text>
            <Text>{format(new Date(subscription.end_date), "PPP")}</Text>
          </Flex>

          <Flex justify="space-between" align="center">
            <Text fontWeight="semibold">Status:</Text>
            <Badge
              colorPalette={subscription.status === "active" ? "green" : "red"}
            >
              {subscription.status}
            </Badge>
          </Flex>

          {subscription.status === "active" && (
            <Button
              colorPalette="red"
              variant="outline"
              mt={4}
              onClick={() => cancelMutation.mutate(subscription.id)}
              loading={cancelMutation.isPending}
            >
              Cancel Subscription
            </Button>
          )}
        </VStack>
      </Card.Body>
    </Card.Root>
  );
};

export default CurrentSubscription;
