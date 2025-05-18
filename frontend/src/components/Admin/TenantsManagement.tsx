// frontend/src/components/Admin/TenantsManagement.tsx
import { useState } from "react";
import {
  Button,
  Input,
  VStack,
  Table,
  Text,
  HStack,
  Badge,
  Heading,
  IconButton,
  Flex,
  Alert,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FiEdit, FiPlus, FiTrash2 } from "react-icons/fi";
import { type SubmitHandler, useForm } from "react-hook-form";

import { handleError } from "@/utils";
import useCustomToast from "@/hooks/useCustomToast";
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
import { Checkbox } from "@/components/ui/checkbox";
import { SkeletonText } from "../ui/skeleton";
import { TenantService } from '@/services/tenant-service';
import { Tenant, TenantCreateInput, TenantUpdateInput } from '@/types/tenant';
// Create a TenantService in your client
// This is a placeholder - you'll need to implement this service

interface TenantForm {
  name: string;
  description: string;
  is_active: boolean;
}
interface TenantsResponse {
  data: Tenant[];
  count?: number;
}
const TenantsManagement = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [editingTenant, setEditingTenant] = useState<Tenant | null>(null);
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<TenantForm>({
    defaultValues: {
      name: "",
      description: "",
      is_active: true,
    },
  });

  const {
    data: tenantsData,
    isLoading,
    error,
  } = useQuery<TenantsResponse | Tenant[]>({
    queryKey: ["tenants"],
    queryFn: () => TenantService.listTenants(),
    retry: 1, // Limit retries on failure
  });

  const createMutation = useMutation({
    mutationFn: (data: TenantCreateInput) => TenantService.createTenant(data),
    onSuccess: () => {
      showSuccessToast("Tenant created successfully");
      setIsOpen(false);
      reset();
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      tenantId,
      data,
    }: {
      tenantId: string;
      data: TenantUpdateInput;
    }) => TenantService.updateTenant({ tenantId, data }),
    onSuccess: () => {
      showSuccessToast("Tenant updated successfully");
      setIsOpen(false);
      reset();
      setEditingTenant(null);
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (tenantId: string) => TenantService.deleteTenant(tenantId),
    onSuccess: () => {
      showSuccessToast("Tenant deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const onSubmit: SubmitHandler<TenantForm> = (data) => {
    if (editingTenant) {
      updateMutation.mutate({ tenantId: editingTenant.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (tenant: Tenant) => {
    setEditingTenant(tenant);
    setValue("name", tenant.name);
    setValue("description", tenant.description || "");
    setValue("is_active", tenant.is_active);
    setIsOpen(true);
  };

  const handleDelete = (tenantId: string) => {
    if (confirm("Are you sure you want to delete this tenant?")) {
      deleteMutation.mutate(tenantId);
    }
  };

  if (isLoading) {
    return <SkeletonText noOfLines={10} gap="4" />;
  }
  if (error) {
    return (
      <Alert.Root status="error">
        <VStack align="start">
          <Text>Error loading tenants</Text>
          <Text fontSize="sm">{(error as Error).message}</Text>
          <Button
            onClick={() =>
              queryClient.invalidateQueries({ queryKey: ["tenants"] })
            }
          >
            Retry
          </Button>
        </VStack>
      </Alert.Root>
    );
  }

  // Extract the tenants array from the response
  // This handles different API response formats
  const tenants = Array.isArray(tenantsData)
    ? tenantsData
    : tenantsData?.data || [];
  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading size="md">Tenant Management</Heading>
        <Button
          colorPalette="teal"
          onClick={() => {
            setEditingTenant(null);
            reset();
            setIsOpen(true);
          }}
        >
          <FiPlus />
          Add Tenant
        </Button>
      </Flex>

      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Name</Table.ColumnHeader>
            <Table.ColumnHeader>Description</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Credit Balance</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {tenants?.map((tenant: Tenant) => (
            <Table.Row key={tenant.id}>
              <Table.Cell>{tenant.name}</Table.Cell>
              <Table.Cell>{tenant.description || "N/A"}</Table.Cell>
              <Table.Cell>
                <Badge colorPalette={tenant.is_active ? "green" : "red"}>
                  {tenant.is_active ? "Active" : "Inactive"}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                {tenant.credit_balance
                  ? `${tenant.credit_balance} credits`
                  : "0 credits"}
              </Table.Cell>
              <Table.Cell>
                <HStack gap={2}>
                  <IconButton
                    aria-label="Edit tenant"
                    size="sm"
                    onClick={() => handleEdit(tenant)}
                  >
                    <FiEdit />
                  </IconButton>
                  <IconButton
                    aria-label="Delete tenant"
                    size="sm"
                    colorPalette="red"
                    onClick={() => handleDelete(tenant.id)}
                  >
                    <FiTrash2 />
                  </IconButton>
                </HStack>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>

      <DialogRoot open={isOpen} onOpenChange={({ open }) => setIsOpen(open)}>
        <DialogContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>
                {editingTenant ? "Edit Tenant" : "Create New Tenant"}
              </DialogTitle>
            </DialogHeader>
            <DialogBody>
              <VStack gap={4}>
                <Field
                  label="Name"
                  required
                  invalid={!!errors.name}
                  errorText={errors.name?.message}
                >
                  <Input
                    {...register("name", { required: "Name is required" })}
                  />
                </Field>

                <Field label="Description">
                  <Input {...register("description")} />
                </Field>

                <Field>
                  <Checkbox {...register("is_active")}>Active</Checkbox>
                </Field>
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
                {editingTenant ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </form>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>
    </VStack>
  );
};

export default TenantsManagement;
