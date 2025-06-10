from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),
    
    # Employee URLs
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/update/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    path('employees/upload/', views.employee_upload, name='employee_upload'),
    path('employees/download/template/', views.download_employee_template, name='download_employee_template'),
    path('employees/download/data/', views.download_employee_data, name='download_employee_data'),
    path('employees/<int:pk>/toggle-status/', views.employee_toggle_status, name='employee_toggle_status'),
    
    # Asset URLs
    path('assets/', views.ITAssetListView.as_view(), name='asset_list'),
    path('assets/<int:pk>/', views.ITAssetDetailView.as_view(), name='asset_detail'),
    path('assets/create/', views.ITAssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/update/', views.ITAssetUpdateView.as_view(), name='asset_update'),
    path('assets/<int:pk>/delete/', views.ITAssetDeleteView.as_view(), name='asset_delete'),
    path('assets/upload/', views.asset_upload, name='asset_upload'),
    path('assets/download/template/', views.download_asset_template, name='download_asset_template'),
    path('assets/download/data/', views.download_asset_data, name='download_asset_data'),
    path('assets/assign/', views.asset_assign, name='asset_assign'),
    
    # Asset Type URLs
    path('asset-types/', views.AssetTypeListView.as_view(), name='asset_type_list'),
    path('asset-types/create/', views.AssetTypeCreateView.as_view(), name='asset_type_create'),
    path('asset-types/<int:pk>/update/', views.AssetTypeUpdateView.as_view(), name='asset_type_update'),
    path('asset-types/<int:pk>/delete/', views.AssetTypeDeleteView.as_view(), name='asset_type_delete'),
    
    # Owner Company URLs
    path('companies/', views.OwnerCompanyListView.as_view(), name='owner_company_list'),
    path('companies/create/', views.OwnerCompanyCreateView.as_view(), name='owner_company_create'),
    path('companies/<int:pk>/update/', views.OwnerCompanyUpdateView.as_view(), name='owner_company_update'),
    path('companies/<int:pk>/delete/', views.OwnerCompanyDeleteView.as_view(), name='owner_company_delete'),
    
    # Department URLs
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Team URLs
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('teams/create/', views.TeamCreateView.as_view(), name='team_create'),
    path('teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('teams/<int:pk>/update/', views.TeamUpdateView.as_view(), name='team_update'),
    path('teams/<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
    path('teams/<int:team_id>/add-member/', views.add_team_member, name='add_team_member'),
    path('teams/<int:team_id>/remove-member/<int:employee_id>/', views.remove_team_member, name='remove_team_member'),
    path('my-teams/', views.my_teams, name='my_teams'),
    
    # User Management URLs
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    
    # Role Management URLs
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/create/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/update/', views.RoleUpdateView.as_view(), name='role_update'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    
    # Message URLs
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/sent/', views.SentMessageListView.as_view(), name='sent_message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<int:pk>/reply/', views.MessageReplyView.as_view(), name='message_reply'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('messages/notifications/', views.message_notifications, name='message_notifications'),
    path('messages/<int:pk>/check-replies/', views.check_replies, name='check_replies'),
    
    # Asset History URLs
    path('history/', views.AssetHistoryListView.as_view(), name='asset_history'),
    
    # Authentication URLs
    path('logout/', views.logout_view, name='logout'),
]
