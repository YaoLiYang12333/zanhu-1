from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
import allauth.account.urls

urlpatterns = [
                  path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
                  path(
                      "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
                  ),
                  # Django Admin, use {% url 'admin:index' %}
                  # path(settings.ADMIN_URL, admin.site.urls),

                  # User management
                  path("users/", include("zanhu.users.urls", namespace="users")),
                  path("accounts/", include("allauth.urls")),

                  # 第三方模块
                  path('markdownx/', include('markdownx.urls')),
                  path('comments/', include('django_comments.urls')),
                  path("search/", include("haystack.urls")),

                  # 开发的应用
                  path('news/', include('zanhu.news.urls', namespace='news')),
                  path("articles/", include("zanhu.articles.urls", namespace="articles")),
                  path("qa/", include("zanhu.qa.urls", namespace="qa")),
                  path("messager/", include("zanhu.messager.urls", namespace="messager")),
                  path("notifications/", include("zanhu.notifications.urls", namespace="notifications")),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
