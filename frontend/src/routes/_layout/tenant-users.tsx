// frontend/src/routes/_layout/tenant-users.tsx
import {
  Container,
  Heading,
  Button,
  VStack,
  HStack,
  Text,
  Alert,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { FiPlus } from "react-icons/fi";
import useAuth from "@/hooks/useAuth";
import TenantUserManagement from "@/components/Admin/TenantUserManagement";
import { UserWithTenant } from "@/types/tenant";

export const Route = createFileRoute("/_layout/tenant-users")({
  component: TenantUsers,
});

function TenantUsers() {
  const { user } = useAuth();
  const typedUser = user as UserWithTenant | null;
  const tenantId = typedUser?.tenant_id ?? '';
  const isTenantAdmin = typedUser?.role === "tenant_admin";
  const isSuperAdmin = typedUser?.is_superuser;

  if (!tenantId && !isSuperAdmin) {
    return (
      <Container maxW="full">
        <Alert.Root status="warning">
          <VStack align="stretch">
            <Heading size="md">No Tenant Access</Heading>
            <Text>You don't have access to manage any tenant users.</Text>
          </VStack>
        </Alert.Root>
      </Container>
    );
  }

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Tenant User Management
      </Heading>
      
      <TenantUserManagement />
    </Container>
  );
}