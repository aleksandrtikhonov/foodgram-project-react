from django.urls import include, path

from api.views import CurrentUserSubscriptionsView, ManageSubscribeView

urlpatterns = [
    path("users/subscriptions/", CurrentUserSubscriptionsView.as_view()),
    path("users/<int:user_id>/", ManageSubscribeView.as_view()),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("users/<int:user_id>/subscribe/", ManageSubscribeView.as_view()),
]
