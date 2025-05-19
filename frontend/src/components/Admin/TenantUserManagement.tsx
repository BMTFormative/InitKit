// frontend/src/components/Admin/TenantUserManagement.tsx
import { useState } from "react";
import {
  Button,
  VStack,
  Table,
  IconButton,
  HStack,
  Badge,
  Heading,
  Flex,
  Select,
  createListCollection,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FiPlus, FiTrash2 } from "react-icons/fi";
import useAuth from "@/hooks/useAuth";
import { SkeletonText } from "../ui/skeleton";
import InvitationForm from "./InvitationForm";
import { UserActionsMenu } from "../Common/UserActionsMenu";
import { TenantUserService } from "@/services/tenant-user-service";
import { TenantUser, TenantInvitation } from "@/types/tenant";
import useCustomToast from "@/hooks/useCustomToast";
import { UserWithTenant } from "@/types/tenant";

// Define the collection of view mode options
const viewModeOptions = createListCollection({
  items: [
    { label: "Users", value: "users" },
    { label: "Pending Invitations", value: "invitations" },
  ],
});

const TenantUserManagement = () => {
  const [isInvitationOpen, setIsInvitationOpen] = useState(false);
  const [viewMode, setViewMode] = useState("users"); // "users" or "invitations"
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { showSuccessToast, showErrorToast } = useCustomToast();

  // Add type assertion and default to empty string if null/undefined
  const typedUser = user as UserWithTenant | null;
  const tenantId = typedUser?.tenant_id ?? "";

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["tenant-users", tenantId],
    queryFn: () => TenantUserService.listTenantUsers(tenantId),
    enabled: !!tenantId && viewMode === "users",
  });

  const { data: invitations, isLoading: invitationsLoading } = useQuery({
    queryKey: ["tenant-invitations", tenantId],
    queryFn: () => TenantUserService.listInvitations(tenantId),
    enabled: !!tenantId && viewMode === "invitations",
  });

  const deleteInvitationMutation = useMutation({
    mutationFn: ({
      tenantId,
      invitationId,
    }: {
      tenantId: string;
      invitationId: string;
    }) => TenantUserService.deleteInvitation({ tenantId, invitationId }),
    onSuccess: () => {
      showSuccessToast("Invitation deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["tenant-invitations"] });
    },
    onError: (err: any) => {
      showErrorToast("Failed to delete invitation");
      console.error(err);
    },
  });

  const handleDeleteInvitation = (invitationId: string) => {
    if (confirm("Are you sure you want to delete this invitation?")) {
      deleteInvitationMutation.mutate({ tenantId, invitationId });
    }
  };

  if (!tenantId) {
    return <Heading size="md">No tenant associated with your account</Heading>;
  }

  const isLoading = viewMode === "users" ? usersLoading : invitationsLoading;

  if (isLoading) {
    return <SkeletonText noOfLines={10} gap="4" />;
  }

  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading size="md">User Management</Heading>
        <HStack>
          {/* FIXED: Select component with proper collection implementation */}
          <Select.Root 
            collection={viewModeOptions}
            value={[viewMode]} 
            onValueChange={(e) => setViewMode(e.value[0])}
            width="60"
          >
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText />
              </Select.Trigger>
              <Select.IndicatorGroup>
                <Select.Indicator />
              </Select.IndicatorGroup>
            </Select.Control>
            <Select.Positioner>
              <Select.Content>
                {viewModeOptions.items.map((option) => (
                  <Select.Item key={option.value} item={option}>
                    {option.label}
                    <Select.ItemIndicator />
                  </Select.Item>
                ))}
              </Select.Content>
            </Select.Positioner>
          </Select.Root>
          <Button colorPalette="teal" onClick={() => setIsInvitationOpen(true)}>
            <FiPlus />
            Invite User
          </Button>
        </HStack>
      </Flex>

      {viewMode === "users" ? (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Email</Table.ColumnHeader>
              <Table.ColumnHeader>Full Name</Table.ColumnHeader>
              <Table.ColumnHeader>Role</Table.ColumnHeader>
              <Table.ColumnHeader>Status</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {users?.map((user: TenantUser) => (
              <Table.Row key={user.id}>
                <Table.Cell>{user.email}</Table.Cell>
                <Table.Cell>{user.full_name || "N/A"}</Table.Cell>
                <Table.Cell>{user.role}</Table.Cell>
                <Table.Cell>
                  <Badge colorPalette={user.is_active ? "green" : "red"}>
                    {user.is_active ? "Active" : "Inactive"}
                  </Badge>
                </Table.Cell>
                <Table.Cell>
                  <UserActionsMenu
                    user={user as any}
                    disabled={typedUser?.id === user.id}
                  />
                </Table.Cell>
              </Table.Row>
            ))}
            {(!users || users.length === 0) && (
              <Table.Row>
                <Table.Cell colSpan={5} textAlign="center">
                  No users found.
                </Table.Cell>
              </Table.Row>
            )}
          </Table.Body>
        </Table.Root>
      ) : (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeader>Email</Table.ColumnHeader>
              <Table.ColumnHeader>Role</Table.ColumnHeader>
              <Table.ColumnHeader>Expires</Table.ColumnHeader>
              <Table.ColumnHeader>Actions</Table.ColumnHeader>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {invitations?.map((invitation: TenantInvitation) => (
              <Table.Row key={invitation.id}>
                <Table.Cell>{invitation.email}</Table.Cell>
                <Table.Cell>{invitation.role}</Table.Cell>
                <Table.Cell>
                  {new Date(invitation.expires_at).toLocaleString()}
                </Table.Cell>
                <Table.Cell>
                  <IconButton
                    aria-label="Delete invitation"
                    size="sm"
                    colorPalette="red"
                    onClick={() => handleDeleteInvitation(invitation.id)}
                  >
                    <FiTrash2 />
                  </IconButton>
                </Table.Cell>
              </Table.Row>
            ))}
            {(!invitations || invitations.length === 0) && (
              <Table.Row>
                <Table.Cell colSpan={4} textAlign="center">
                  No pending invitations found.
                </Table.Cell>
              </Table.Row>
            )}
          </Table.Body>
        </Table.Root>
      )}

      <InvitationForm
        isOpen={isInvitationOpen}
        onClose={() => setIsInvitationOpen(false)}
        tenantId={tenantId}
      />
    </VStack>
  );
};

export default TenantUserManagement;