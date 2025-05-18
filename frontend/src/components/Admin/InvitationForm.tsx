// frontend/src/components/Admin/InvitationForm.tsx
import { 
  DialogRoot, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogBody, 
  DialogFooter, 
  DialogActionTrigger, 
  DialogCloseTrigger 
} from "@/components/ui/dialog";
import { Button, Input, Select, VStack } from "@chakra-ui/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type SubmitHandler, useForm } from "react-hook-form";
import { Field } from "../ui/field";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import { emailPattern } from "@/utils";
import { TenantUserService } from '@/services/tenant-user-service';
import { InvitationCreateInput } from '@/types/tenant';

interface InvitationFormProps {
  isOpen: boolean;
  onClose: () => void;
  tenantId: string;
}

interface InvitationFormValues {
  email: string;
  role: string;
}

const InvitationForm = ({ isOpen, onClose, tenantId }: InvitationFormProps) => {
  const queryClient = useQueryClient();
  const { showSuccessToast } = useCustomToast();
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<InvitationFormValues>({
    defaultValues: {
      email: "",
      role: "user"
    }
  });

  const invitationMutation = useMutation({
    mutationFn: (data: InvitationCreateInput) => 
      TenantUserService.createInvitation({ tenantId, data }),
    onSuccess: () => {
      showSuccessToast("Invitation sent successfully");
      reset();
      onClose();
      queryClient.invalidateQueries({ queryKey: ["tenant-invitations"] });
    },
    onError: (err: any) => {
      handleError(err);
    }
  });

  const onSubmit: SubmitHandler<InvitationFormValues> = (data) => {
    invitationMutation.mutate(data);
  };

  return (
    <DialogRoot open={isOpen} onOpenChange={({ open }) => !open && onClose()}>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Invite User</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                label="Email"
                required
                invalid={!!errors.email}
                errorText={errors.email?.message}
              >
                <Input
                  id="email"
                  {...register("email", {
                    required: "Email is required",
                    pattern: emailPattern
                  })}
                  placeholder="Email"
                  type="email"
                />
              </Field>

              <Field
                label="Role"
                required
              >
                <Select.ItemGroup
                  id="role"
                  {...register("role", { required: "Role is required" })}
                >
                  <option value="user">User</option>
                  <option value="tenant_admin">Tenant Admin</option>
                </Select.ItemGroup>
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
              Send Invitation
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  );
};

export default InvitationForm;