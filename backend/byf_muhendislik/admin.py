# Admin Site Customization
from django.contrib import admin

# Customize admin site headers - Turkish interface
admin.site.site_header = 'BYF Mühendislik Yönetim Paneli'
admin.site.site_title = 'BYF Mühendislik Yönetimi'
admin.site.index_title = 'Site Yönetimi'

# Override default Django admin texts
admin.site.empty_value_display = '-'

