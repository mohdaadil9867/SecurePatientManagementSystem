from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name="Doctor").exists()
        )


class IsReceptionist(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name="Receptionist").exists()
        )


class IsBillingStaff(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name="Billing Staff").exists()
        )


class IsInsuranceOfficer(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name="Insurance Officer").exists()
        )


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser