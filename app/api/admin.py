from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext

from .models import Post, Like, User


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (gettext('Personal Info'), {'fields': ('name', )}),
        (
            gettext('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (gettext('Important dates'), {'fields': ('last_login',
                                                 'last_activity')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


admin.site.site_header = 'Social Network STARNAVi Administration'
admin.site.site_title = 'Social Network STARNAVi Administration'

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Like)
