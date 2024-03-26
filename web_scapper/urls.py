"""web_scapper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app.views import *
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from web_scapper import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="IndexView"),
    path('login', LoginView.as_view(), name="LoginView"),
    path('register', RegisterView.as_view(), name="RegisterView"),
    path('logout', login_required(LogoutView.as_view()), name="LogoutView"),
    path('home', login_required(HomeView.as_view()), name="HomeView"),
    path('shops/<int:id>', login_required(ShopView.as_view()), name="ShopView"),
    path('shops', login_required(shopsView.as_view()), name="shopsView"),
    path('search', login_required(SearchView.as_view()), name="SearchView"),
    path('compare', login_required(CompareView.as_view()), name="CompareView"),
    path('add-interests', login_required(AddToInterest.as_view()), name="AddToInterest"),
    #path('add-compare', login_required(AddToCompare.as_view()), name="AddToCompare"),
    path('favourites', login_required(FavouriteView.as_view()), name="FavouriteView"),
    path('add-compare-new', login_required(AddToNewCompare.as_view()), name="AddToNewCompare"),
    path('add-favourite', login_required(AddToFavourites.as_view()), name="AddToFavourites"),
    path('delete-compare/<int:id>', login_required(DeleteCompareView.as_view()), name="DeleteCompareView"),
    path('delete-favourite/<int:id>', login_required(DeleteFavouriteView.as_view()), name="DeleteFavouriteView")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
