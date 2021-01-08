from django.contrib import admin

from .models import *


class ImageInLineAdmin(admin.TabularInline):
    model = Image
    fields = ('image', )
    max_num = 5


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [ImageInLineAdmin, ]


admin.site.register(Category)
