import { Box, Flex, Icon, Text } from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import { Link as RouterLink } from "@tanstack/react-router";
import {
  FiBriefcase,
  FiHome,
  FiSettings,
  FiUsers,
  FiDollarSign,
} from "react-icons/fi";
import type { IconType } from "react-icons/lib";

import type { UserPublic } from "@/client";
import { UserWithTenant } from "@/types/tenant";

const items = [
  { icon: FiHome, title: "Dashboard", path: "/" },
  { icon: FiBriefcase, title: "Items", path: "/items" },
  { icon: FiDollarSign, title: "Subscriptions", path: "/subscriptions" },
  { icon: FiSettings, title: "User Settings", path: "/settings" },
];

interface SidebarItemsProps {
  onClose?: () => void;
}

interface Item {
  icon: IconType;
  title: string;
  path: string;
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const queryClient = useQueryClient();
  const currentUser = queryClient.getQueryData<UserWithTenant>(["currentUser"]);
  const isSuperAdmin = currentUser?.is_superuser;
  const isTenantAdmin = currentUser?.role === "tenant_admin";
  const hasTenant = !!currentUser?.tenant_id;

  // Show admin link to both superadmins and tenant admins
  const showAdminLink = isSuperAdmin || isTenantAdmin;

  const finalItems: Item[] = showAdminLink
    ? [...items, { icon: FiUsers, title: "Admin", path: "/admin" }]
    : items;
// Add tenant user management for tenant admins
  if (isTenantAdmin && hasTenant) {
    finalItems.push({ icon: FiUsers, title: "Tenant Users", path: "/tenant-users" });
  }
  // Add admin dashboard for superadmins
  if (isSuperAdmin) {
    finalItems.push({ icon: FiUsers, title: "Admin", path: "/admin" });
  }
  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose}>
      <Flex
        gap={4}
        px={4}
        py={2}
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ));

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        Menu
      </Text>
      <Box>{listItems}</Box>
    </>
  );
};

export default SidebarItems;
