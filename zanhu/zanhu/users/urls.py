from django.urls import path
from zanhu.users import views

# from zanhu.users.views import (
#     user_redirect_view,
#     user_update_view,
#     user_detail_view,
# )

app_name = "users"
urlpatterns = [
    # path("~redirect/", views.UserRedirectView.as_view(), name="redirect"),
    path("update/", views.user_update_view, name="update"),
    path("<str:username>/", views.user_detail_view, name="detail"),
]
