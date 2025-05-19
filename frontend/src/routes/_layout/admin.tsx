import { Badge, Container, Flex, Heading, Table, Tabs } from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { z } from "zod";

import { UserPublic, UsersService } from "@/client";
import AddUser from "@/components/Admin/AddUser";
import { UserActionsMenu } from "@/components/Common/UserActionsMenu";
import PendingUsers from "@/components/Pending/PendingUsers";
import {
  PaginationItems,
  PaginationNextTrigger,
  PaginationPrevTrigger,
  PaginationRoot,
} from "@/components/ui/pagination.tsx";
import TenantsManagement from "@/components/Admin/TenantsManagement";
import TenantUserManagement from "@/components/Admin/TenantUserManagement";
import TenantApiKeyManagement from "@/components/Admin/TenantApiKeyManagement";
import CreditTransactions from "@/components/Admin/CreditTransactions";
import SubscriptionPlanManagement from "@/components/Admin/SubscriptionPlanManagement";
import { UserWithTenant } from "@/types/tenant";
import EmailConfiguration from "@/components/Admin/EmailConfiguration";

const tabsConfig = [
  { value: "users", title: "Users", component: UsersTable },
  {
    value: "subscriptions",
    title: "Subscription Plans",
    component: SubscriptionPlanManagement,
  },
];

const usersSearchSchema = z.object({
  page: z.number().catch(1),
});

const PER_PAGE = 5;

function getUsersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      UsersService.readUsers({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["users", { page }],
  };
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  validateSearch: (search) => usersSearchSchema.parse(search),
});

function UsersTable() {
  const queryClient = useQueryClient();
  const currentUser = queryClient.getQueryData<UserPublic>([
    "currentUser",
  ]) as UserWithTenant | null;
  const navigate = useNavigate({ from: Route.fullPath });
  const { page } = Route.useSearch();

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getUsersQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  });

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    });

  const users = data?.data.slice(0, PER_PAGE) ?? [];
  const count = data?.count ?? 0;

  if (isLoading) {
    return <PendingUsers />;
  }

  return (
    <>
      <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader w="sm">Full name</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Email</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Role</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Status</Table.ColumnHeader>
            <Table.ColumnHeader w="sm">Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {users?.map((user) => (
            <Table.Row key={user.id} opacity={isPlaceholderData ? 0.5 : 1}>
              <Table.Cell color={!user.full_name ? "gray" : "inherit"}>
                {user.full_name || "N/A"}
                {currentUser?.id === user.id && (
                  <Badge ml="1" colorScheme="teal">
                    You
                  </Badge>
                )}
              </Table.Cell>
              <Table.Cell truncate maxW="sm">
                {user.email}
              </Table.Cell>
              <Table.Cell>
                {user.is_superuser ? "Superuser" : "User"}
              </Table.Cell>
              <Table.Cell>{user.is_active ? "Active" : "Inactive"}</Table.Cell>
              <Table.Cell>
                <UserActionsMenu
                  user={user}
                  disabled={currentUser?.id === user.id}
                />
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
      <Flex justifyContent="flex-end" mt={4}>
        <PaginationRoot
          count={count}
          pageSize={PER_PAGE}
          onPageChange={({ page }) => setPage(page)}
        >
          <Flex>
            <PaginationPrevTrigger />
            <PaginationItems />
            <PaginationNextTrigger />
          </Flex>
        </PaginationRoot>
      </Flex>
    </>
  );
}

function Admin() {
  const queryClient = useQueryClient();
  const currentUser = queryClient.getQueryData<UserWithTenant>(["currentUser"]);
  const isSuperAdmin = currentUser?.is_superuser;
  const hasTenant = currentUser
    ? "tenant_id" in currentUser && !!currentUser.tenant_id
    : false;
  const isTenantAdmin = currentUser
    ? "role" in currentUser && currentUser.role === "tenant_admin"
    : false;

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Admin Dashboard
      </Heading>

      <Tabs.Root defaultValue="users" variant="subtle" mt={4}>
        <Tabs.List>
          {/* Only SuperAdmin can see Tenants tab */}
          {isSuperAdmin && <Tabs.Trigger value="tenants">Tenants</Tabs.Trigger>}

          {/* Only SuperAdmin can see Subscription Plans tab */}
          {isSuperAdmin && (
            <Tabs.Trigger value="subscription-plans">
              Subscription Plans
            </Tabs.Trigger>
          )}
          {hasTenant && (
            <Tabs.Trigger value="email">Email Settings</Tabs.Trigger>
          )}
          {/* Both SuperAdmin and TenantAdmin can see Users tab */}
          {(isSuperAdmin || (hasTenant && isTenantAdmin)) && (
            <Tabs.Trigger value="users">Users</Tabs.Trigger>
          )}

          {/* Tenant-related tabs visible to both SuperAdmin and TenantAdmin with a tenant */}
          {hasTenant && <Tabs.Trigger value="api-keys">API Keys</Tabs.Trigger>}
          {hasTenant && <Tabs.Trigger value="credits">Credits</Tabs.Trigger>}
        </Tabs.List>

        {/* Tab contents with conditional rendering */}
        {isSuperAdmin && (
          <Tabs.Content value="tenants">
            <TenantsManagement />
          </Tabs.Content>
        )}

        {isSuperAdmin && (
          <Tabs.Content value="subscription-plans">
            <SubscriptionPlanManagement />
          </Tabs.Content>
        )}

        {(isSuperAdmin || (hasTenant && isTenantAdmin)) && (
          <Tabs.Content value="users">
            <TenantUserManagement />
          </Tabs.Content>
        )}

        {hasTenant && (
          <Tabs.Content value="api-keys">
            <TenantApiKeyManagement />
          </Tabs.Content>
        )}

        {hasTenant && (
          <Tabs.Content value="credits">
            <CreditTransactions />
          </Tabs.Content>
        )}
        {hasTenant && (
          <Tabs.Content value="email">
            <EmailConfiguration />
          </Tabs.Content>
        )}
      </Tabs.Root>
    </Container>
  );
}
