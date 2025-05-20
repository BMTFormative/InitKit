// frontend/src/components/Admin/TenantApiKeyManagement.tsx
import { useState, useEffect } from "react";
import {
  Button,
  Input,
  VStack,
  Table,
  Text,
  IconButton,
  Flex,
  Heading,
  Badge,
  NativeSelectRoot,
  NativeSelectField,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FiPlus, FiTrash2 } from "react-icons/fi";
import { type SubmitHandler, useForm } from "react-hook-form";
import useAuth from "@/hooks/useAuth";
import useCustomToast from "@/hooks/useCustomToast";
import GlobalApiKeyManagement from "./GlobalApiKeyManagement";
import { handleError } from "@/utils";
import {
  DialogRoot,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogFooter,
  DialogActionTrigger,
  DialogCloseTrigger,
} from "@/components/ui/dialog";
import { Field } from "@/components/ui/field";
import { SkeletonText } from "../ui/skeleton";
import { ApiKeyService } from "@/services/api-key-service";
import { TenantService } from "@/services/tenant-service";
import { Tenant } from "@/types/tenant";
import { ApiKey, ApiKeyCreateInput } from "@/types/tenant";
import { UserPublic } from "@/client";
import { UserWithTenant } from "@/types/tenant";

interface ApiKeyForm {
  provider: string;
  api_key: string;
}

const TenantApiKeyManagement = () => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  const { user } = useAuth();

  // Add type assertion and default to empty string if null/undefined
  const typedUser = user as UserWithTenant | null;
  const isSuperAdmin = !!typedUser?.is_superuser;
  // Super-admins use the global API key management interface
  if (isSuperAdmin) {
    return <GlobalApiKeyManagement />;
  }
  // For tenant admins, use their tenant; for super-admins, allow selecting a tenant
  const {
    data: tenants,
    isLoading: tenantsLoading,
    error: tenantsError,
  } = useQuery<Tenant[]>({
    queryKey: ["tenants"],
    queryFn: () => TenantService.listTenants(),
    enabled: isSuperAdmin,
  });
  const [selectedTenantId, setSelectedTenantId] = useState<string>(
    typedUser?.tenant_id ?? ""
  );
  useEffect(() => {
    if (isSuperAdmin && tenants && tenants.length > 0 && !selectedTenantId) {
      setSelectedTenantId(tenants[0].id);
    }
  }, [isSuperAdmin, tenants, selectedTenantId]);
  const tenantId = isSuperAdmin ? selectedTenantId : typedUser?.tenant_id ?? "";

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ApiKeyForm>({
    defaultValues: {
      provider: "openai",
      api_key: "",
    },
  });

  const { data: apiKeys, isLoading } = useQuery({
    queryKey: ["api-keys", tenantId],
    queryFn: () => ApiKeyService.listApiKeys(tenantId),
    enabled: !!tenantId,
  });

  const createMutation = useMutation({
    mutationFn: (data: ApiKeyCreateInput) =>
      ApiKeyService.createApiKey({ tenantId, data }),
    onSuccess: () => {
      showSuccessToast("API key added successfully");
      reset();
      setIsOpen(false);
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (keyId: string) =>
      ApiKeyService.deleteApiKey({ tenantId, keyId }),
    onSuccess: () => {
      showSuccessToast("API key deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["api-keys"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const onSubmit: SubmitHandler<ApiKeyForm> = (data) => {
    createMutation.mutate(data);
  };

  const handleDelete = (keyId: string) => {
    if (confirm("Are you sure you want to delete this API key?")) {
      deleteMutation.mutate(keyId);
    }
  };

  // If super-admin has no tenants, render global API key management
  if (isSuperAdmin && !tenantId && !tenantsLoading && tenants?.length === 0) {
    return <GlobalApiKeyManagement />;
  }
  if (!tenantId) {
    return (
      <Heading size="md">
        {isSuperAdmin
          ? "No tenant selected."
          : "No tenant associated with your account"}
      </Heading>
    );
  }

  if (isLoading) {
    return <SkeletonText noOfLines={10} gap="4" />;
  }

  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading size="md">
          API Key Management
          {isSuperAdmin && selectedTenantId && tenants
            ? ` for ${tenants.find((t) => t.id === selectedTenantId)?.name || ''}`
            : ''}
        </Heading>
        {isSuperAdmin && (
          <NativeSelectRoot>
            <NativeSelectField
              w="auto"
              value={selectedTenantId}
              onChange={(e) => setSelectedTenantId(e.target.value)}
              mr={4}
            >
              {tenants?.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </NativeSelectField>
          </NativeSelectRoot>
        )}
        <Button
          colorPalette="teal"
          onClick={() => {
            reset();
            setIsOpen(true);
          }}
        >
          <FiPlus />
          Add API Key
        </Button>
      </Flex>

      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Provider</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Created</Table.ColumnHeader>
            <Table.ColumnHeader>Last Used</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {apiKeys?.map((key: ApiKey) => (
            <Table.Row key={key.id}>
              <Table.Cell>{key.provider}</Table.Cell>
              <Table.Cell>
                <Badge colorPalette={key.is_active ? "green" : "red"}>
                  {key.is_active ? "Active" : "Inactive"}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                {new Date(key.created_at).toLocaleString()}
              </Table.Cell>
              <Table.Cell>
                {key.last_used
                  ? new Date(key.last_used).toLocaleString()
                  : "Never used"}
              </Table.Cell>
              <Table.Cell>
                {!isSuperAdmin && (
                  <IconButton
                    aria-label="Delete API key"
                    size="sm"
                    colorPalette="red"
                    onClick={() => handleDelete(key.id)}
                  >
                    <FiTrash2 />
                  </IconButton>
                )}
              </Table.Cell>
            </Table.Row>
          ))}
          {apiKeys?.length === 0 && (
            <Table.Row>
              <Table.Cell colSpan={5} textAlign="center">
                No API keys found. Add a key to get started.
              </Table.Cell>
            </Table.Row>
          )}
        </Table.Body>
      </Table.Root>

      <DialogRoot open={isOpen} onOpenChange={({ open }) => setIsOpen(open)}>
        <DialogContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>Add API Key</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <VStack gap={4}>
                <Field label="Provider">
                  <NativeSelectRoot>
                    <NativeSelectField {...register("provider")}>
                      <option value="openai">OpenAI</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="custom">Custom</option>
                    </NativeSelectField>
                  </NativeSelectRoot>
                </Field>

                <Field
                  label="API Key"
                  required
                  invalid={!!errors.api_key}
                  errorText={errors.api_key?.message}
                >
                  <Input
                    type="password"
                    {...register("api_key", {
                      required: "API key is required",
                    })}
                    placeholder="Enter your API key"
                  />
                </Field>
                <Text fontSize="sm" color="gray.500">
                  Your API key will be encrypted and stored securely. It will
                  only be used server-side to make API calls and will never be
                  exposed to clients.
                </Text>
              </VStack>
            </DialogBody>

            <DialogFooter gap={2}>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button type="submit" colorPalette="teal" loading={isSubmitting}>
                Save
              </Button>
            </DialogFooter>
          </form>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>
    </VStack>
  );
};

export default TenantApiKeyManagement;
