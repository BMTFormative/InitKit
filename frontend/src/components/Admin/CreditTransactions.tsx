// frontend/src/components/Admin/CreditTransactions.tsx
import {
  VStack,
  Table,
  Heading,
  Flex,
  Button,
  Input,
  Text,
} from "@chakra-ui/react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import useAuth from "@/hooks/useAuth";
import { useState } from "react";
import { type SubmitHandler, useForm } from "react-hook-form";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { SkeletonText } from "../ui/skeleton";
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
import { CreditService } from "@/services/credit-service";
import { CreditTransaction, CreditAddInput } from "@/types/tenant";
import { UserPublic } from "@/client";
import { UserWithTenant } from "@/types/tenant";

interface AddCreditsForm {
  amount: number;
  description: string;
}

const CreditTransactions = () => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  const { user } = useAuth();

  // Add type assertion and default to empty string if null/undefined
  const typedUser = user as UserWithTenant | null;
  const tenantId = typedUser?.tenant_id ?? "";
  const isSuperAdmin = typedUser?.is_superuser ?? false;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<AddCreditsForm>({
    defaultValues: {
      amount: 100,
      description: "Manual credit addition",
    },
  });

  const { data: transactions, isLoading } = useQuery({
    queryKey: ["credit-transactions", tenantId],
    queryFn: () => CreditService.listTransactions(tenantId),
    enabled: !!tenantId, // Only run the query if tenantId exists
  });

  const addCreditsMutation = useMutation({
    mutationFn: (data: CreditAddInput) =>
      CreditService.addCredits({ tenantId, data }),
    onSuccess: () => {
      showSuccessToast("Credits added successfully");
      reset();
      setIsOpen(false);
      queryClient.invalidateQueries({ queryKey: ["credit-transactions"] });
      queryClient.invalidateQueries({ queryKey: ["tenants"] });
    },
    onError: (err: any) => {
      handleError(err);
    },
  });

  const onSubmit: SubmitHandler<AddCreditsForm> = (data) => {
    addCreditsMutation.mutate(data);
  };

  if (!tenantId) {
    return <Heading size="md">No tenant associated with your account</Heading>;
  }

  if (isLoading) {
    return <SkeletonText noOfLines={10} gap="4" />;
  }

  return (
    <VStack align="stretch" gap={6}>
      <Flex justify="space-between" align="center">
        <Heading size="md">Credit Transactions</Heading>
        {isSuperAdmin && (
          <Button
            colorPalette="teal"
            onClick={() => {
              reset();
              setIsOpen(true);
            }}
          >
            Add Credits
          </Button>
        )}
      </Flex>

      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeader>Date</Table.ColumnHeader>
            <Table.ColumnHeader>Type</Table.ColumnHeader>
            <Table.ColumnHeader>Amount</Table.ColumnHeader>
            <Table.ColumnHeader>Description</Table.ColumnHeader>
            <Table.ColumnHeader>User</Table.ColumnHeader>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {transactions?.map((transaction: CreditTransaction) => (
            <Table.Row key={transaction.id}>
              <Table.Cell>
                {new Date(transaction.created_at).toLocaleString()}
              </Table.Cell>
              <Table.Cell>{transaction.transaction_type}</Table.Cell>
              <Table.Cell
                color={transaction.amount > 0 ? "green.500" : "red.500"}
              >
                {transaction.amount > 0 ? "+" : ""}
                {transaction.amount}
              </Table.Cell>
              <Table.Cell>{transaction.description}</Table.Cell>
              <Table.Cell>{transaction.user_id || "System"}</Table.Cell>
            </Table.Row>
          ))}
          {transactions?.length === 0 && (
            <Table.Row>
              <Table.Cell colSpan={5} textAlign="center">
                No transactions found.
              </Table.Cell>
            </Table.Row>
          )}
        </Table.Body>
      </Table.Root>

      {isSuperAdmin && (
        <DialogRoot open={isOpen} onOpenChange={({ open }) => setIsOpen(open)}>
          <DialogContent>
            <form onSubmit={handleSubmit(onSubmit)}>
              <DialogHeader>
                <DialogTitle>Add Credits</DialogTitle>
              </DialogHeader>
              <DialogBody>
                <VStack gap={4}>
                  <Field
                    label="Amount"
                    required
                    invalid={!!errors.amount}
                    errorText={errors.amount?.message}
                  >
                    <Input
                      type="number"
                      {...register("amount", {
                        required: "Amount is required",
                        min: {
                          value: 1,
                          message: "Amount must be positive",
                        },
                      })}
                    />
                  </Field>

                  <Field
                    label="Description"
                    required
                    invalid={!!errors.description}
                    errorText={errors.description?.message}
                  >
                    <Input
                      {...register("description", {
                        required: "Description is required",
                      })}
                    />
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
                <Button
                  type="submit"
                  colorPalette="teal"
                  loading={isSubmitting}
                >
                  Add Credits
                </Button>
              </DialogFooter>
            </form>
            <DialogCloseTrigger />
          </DialogContent>
        </DialogRoot>
      )}
    </VStack>
  );
};

export default CreditTransactions;
