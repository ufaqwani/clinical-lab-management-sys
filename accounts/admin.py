from django.contrib import admin
from .models import Lab, LabMembership

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'owner', 'created_at')
    search_fields = ('name', 'email')

@admin.register(LabMembership)
class LabMembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab', 'user', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('lab__name', 'user__username', 'user__email')
