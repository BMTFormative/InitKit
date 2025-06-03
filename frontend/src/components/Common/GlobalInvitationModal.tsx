// frontend/src/components/Common/GlobalInvitationModal.tsx
import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { UserWithTenant } from "../../types/tenant";
import InvitationForm from "../Admin/InvitationForm";

const GlobalInvitationModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const queryClient = useQueryClient();
  const currentUser = queryClient.getQueryData<UserWithTenant>(["currentUser"]);
  const tenantId = currentUser?.tenant_id ?? "";
  const isTenantAdmin = currentUser?.role === "tenant_admin";
  const isSuperAdmin = currentUser?.is_superuser;

  // Only show for users who can manage a tenant
  const canManageTenant = (isTenantAdmin || isSuperAdmin) && !!tenantId;

  useEffect(() => {
    const handleOpenModal = () => {
      if (canManageTenant) {
        setIsOpen(true);
      }
    };

    window.addEventListener("open-invitation-modal", handleOpenModal);
    return () => {
      window.removeEventListener("open-invitation-modal", handleOpenModal);
    };
  }, [canManageTenant]);

  if (!canManageTenant) return null;

  return (
    <InvitationForm
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      tenantId={tenantId}
    />
  );
};

export default GlobalInvitationModal;
