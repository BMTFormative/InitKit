import { Container, Heading, Tabs, VStack } from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import SubscriptionPlans from "@/components/Subscriptions/SubscriptionPlans";
import CurrentSubscription from "@/components/Subscriptions/CurrentSubscription";

export const Route = createFileRoute("/_layout/subscriptions")({
  component: Subscriptions,
});

function Subscriptions() {
  return (
    <Container maxW="full">
      <VStack gap={8} align="stretch">
        <Heading size="lg" py={8}>
          Subscriptions
        </Heading>

        <Tabs.Root defaultValue="plans" variant="subtle">
          <Tabs.List>
            <Tabs.Trigger value="plans">Available Plans</Tabs.Trigger>
            <Tabs.Trigger value="current">My Subscription</Tabs.Trigger>
          </Tabs.List>

          <Tabs.Content value="plans">
            <SubscriptionPlans />
          </Tabs.Content>

          <Tabs.Content value="current">
            <CurrentSubscription />
          </Tabs.Content>
        </Tabs.Root>
      </VStack>
    </Container>
  );
}
