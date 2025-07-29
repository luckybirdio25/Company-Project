from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect
from django.conf import settings

class PermissionRequiredMixin(UserPassesTestMixin):
    permission_required = None

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        # Superusers can access everything
        if self.request.user.is_superuser:
            return True
        # Check if user has the required permission
        if self.permission_required:
            return self.request.user.has_perm(self.permission_required)
        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return render(self.request, '403.html', status=403)

class SuperuserRequiredMixin(UserPassesTestMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return render(self.request, '403.html', status=403) 