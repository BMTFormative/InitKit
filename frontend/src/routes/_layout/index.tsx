import { Box, Button, Container, Flex, Heading, Link, Text, VStack } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"

import useAuth from "@/hooks/useAuth"
import { UserWithTenant } from "@/types/tenant";
import { FiPlus, FiUsers } from "react-icons/fi";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {
  const { user: currentUser } = useAuth();
  const typedUser = currentUser as UserWithTenant | null;
  const isTenantAdmin = typedUser?.role === "tenant_admin";
  const hasTenant = !!typedUser?.tenant_id;

  return (
    <>
      <Container maxW="full">
        <Box pt={12} m={4}>
          <Text fontSize="2xl" truncate maxW="sm">
            Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
          </Text>
          <Text>Welcome back, nice to see you again!</Text>
          
          {/* Quick actions for tenant admins */}
          {isTenantAdmin && hasTenant && (
            <VStack align="start" mt={8} gap={4}>
              <Heading size="md">Quick Actions</Heading>
              <Flex gap={4}>
                <Link href="/tenant-users"></Link>
                <Button 
                  colorPalette="teal" 
                >
                  <FiUsers />Manage Users
                </Button>
                <Button 
                  colorPalette="green" 
                  onClick={() => {
                    // Open invitation modal directly
                    // You can use a global state or context to control this
                    window.dispatchEvent(new CustomEvent("open-invitation-modal"));
                  }}
                >
                  <FiPlus />Invite New User
                </Button>
              </Flex>
            </VStack>
          )}
        </Box>
      </Container>
    </>
  );
}
