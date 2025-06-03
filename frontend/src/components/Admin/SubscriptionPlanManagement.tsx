import { useState } from "react";
import {
  Button,
  Input,
  VStack,
  Table,
  Text,
  IconButton,
  Textarea,
  Badge,
  HStack,
  Heading,
  Flex,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FiEdit, FiTrash2, FiPlus } from "react-icons/fi";
import { type SubmitHandler, useForm, Controller } from "react-hook-form";
import { SubscriptionsService, type ApiError } from "@/client";
import useCustomToast from "@/hooks/useCustomToast";
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
import { Checkbox } from "@/components/ui/checkbox";
import { SkeletonText } from "../ui/skeleton";

interface PlanForm {
  name: string;
  description: string | null;
  price: number;
  duration_days: number;
  features: string;
  is_active: boolean;
  credit_limit: number;
}

const SubscriptionPlanManagement = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [editingPlan, setEditingPlan] = useState<any | null>(null);
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    control,
    formState: { errors, isSubmitting },
  } = useForm<PlanForm>({
  defaultValues: {
      name: "",
      description: "",
      price: 0,
      duration_days: 30,
      features: "",
      is_active: true,
      credit_limit: 0,
    },
  });

  const { data: plans, isLoading } = useQuery({
    queryKey: ["admin-subscription-plans"],
    queryFn: () =>
      SubscriptionsService.listSubscriptionPlans({ activeOnly: false }),
  });

  const createMutation = useMutation({
    mutationFn: (data: any) =>
      SubscriptionsService.createSubscriptionPlan({
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("Plan created successfully");
      queryClient.invalidateQueries({ queryKey: ["admin-subscription-plans"] });
      setIsOpen(false);
      reset();
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ planId, data }: { planId: string; data: any }) =>
      SubscriptionsService.updateSubscriptionPlan({
        planId,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("Plan updated successfully");
      queryClient.invalidateQueries({ queryKey: ["admin-subscription-plans"] });
      setIsOpen(false);
      reset();
      setEditingPlan(null);
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (planId: string) =>
      SubscriptionsService.deleteSubscriptionPlan({ planId }),
    onSuccess: () => {
      showSuccessToast("Plan deleted successfully");
      queryClient.invalidateQueries({ queryKey: ["admin-subscription-plans"] });
    },
    onError: (err: ApiError) => {
      handleError(err);
    },
  });

  const onSubmit: SubmitHandler<PlanForm> = (data) => {
    const formattedData = {
      ...data,
      description: data.description || null,
      features: data.features.split("\n").filter((f) => f.trim()),
    };

    if (editingPlan) {
      updateMutation.mutate({ planId: editingPlan.id, data: formattedData });
    } else {
      createMutation.mutate(formattedData);
    }
  };

  const handleEdit = (plan: any) => {
    setEditingPlan(plan);
    setValue("name", plan.name);
    setValue("description", plan.description || "");
    setValue("price", plan.price);
    setValue("duration_days", plan.duration_days);
    setValue("features", plan.features?.join("\n") || "");
    setValue("is_active", plan.is_active);
    setIsOpen(true);
  };

  if (isLoading) {
    return (
      <VStack align="stretch" gap={6}>
        <SkeletonText noOfLines={10} />
      </VStack>
    );
  }

  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading size="md">Subscription Plans Management</Heading>
        <Button
          colorPalette="teal"
          onClick={() => {
            setEditingPlan(null);
            reset();
            setIsOpen(true);
          }}
        >
          <FiPlus />
          Add Plan
        </Button>
      </Flex>

      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Name</Table.ColumnHeader>
            <Table.ColumnHeader>Price</Table.ColumnHeader>
            <Table.ColumnHeader>Duration</Table.ColumnHeader>
            <Table.ColumnHeader>Credits</Table.ColumnHeader>
            <Table.ColumnHeader>Status</Table.ColumnHeader>
            <Table.ColumnHeader>Actions</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {plans?.data.map((plan) => (
            <Table.Row key={plan.id}>
              <Table.Cell>{plan.name}</Table.Cell>
              <Table.Cell>${plan.price}</Table.Cell>
              <Table.Cell>{plan.duration_days} days</Table.Cell>
              <Table.Cell>{plan.credit_limit}</Table.Cell>
              <Table.Cell>
                <Badge colorPalette={plan.is_active ? "green" : "red"}>
                  {plan.is_active ? "Active" : "Inactive"}
                </Badge>
              </Table.Cell>
              <Table.Cell>
                <HStack gap={2}>
                  <IconButton
                    aria-label="Edit plan"
                    size="sm"
                    onClick={() => handleEdit(plan)}
                  >
                    <FiEdit />
                  </IconButton>
                  <IconButton
                    aria-label="Delete plan"
                    size="sm"
                    colorPalette="red"
                    onClick={() => deleteMutation.mutate(plan.id)}
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
                {editingPlan ? "Edit Plan" : "Create New Plan"}
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
                  <Textarea {...register("description")} />
                </Field>

                <Field
                  label="Price"
                  required
                  invalid={!!errors.price}
                  errorText={errors.price?.message}
                >
                  <Input
                    type="number"
                    step="0.01"
                    {...register("price", {
                      required: "Price is required",
                      min: { value: 0, message: "Price must be positive" },
                      valueAsNumber: true,
                    })}
                  />
                </Field>

                <Field
                  label="Duration (days)"
                  required
                  invalid={!!errors.duration_days}
                  errorText={errors.duration_days?.message}
                >
                  <Input
                    type="number"
                    {...register("duration_days", {
                      required: "Duration is required",
                      min: {
                        value: 1,
                        message: "Duration must be at least 1 day",
                      },
                      valueAsNumber: true,
                    })}
                  />
                </Field>

                <Field label="Features (one per line)">
                  <Textarea {...register("features")} rows={4} />
                </Field>
                <Field
                  label="Monthly Credit Limit (per user)"
                  invalid={!!errors.credit_limit}
                  errorText={errors.credit_limit?.message}
                >
                  <Input
                    type="number"
                    step="0.01"
                    {...register("credit_limit", {
                      min: { value: 0, message: "Credit must be non-negative" },
                      valueAsNumber: true,
                    })}
                  />
                </Field>

                <Controller
                  control={control}
                  name="is_active"
                  render={({ field }) => (
                    <Field>
                      <Checkbox
                        checked={field.value}
                        onCheckedChange={({ checked }) =>
                          field.onChange(checked)
                        }
                      >
                        Active
                      </Checkbox>
                    </Field>
                  )}
                />
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
                {editingPlan ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </form>
          <DialogCloseTrigger />
        </DialogContent>
      </DialogRoot>
    </VStack>
  );
};

export default SubscriptionPlanManagement;
