import random
from collections import defaultdict
import json
from decimal import Decimal

from django.contrib.auth import authenticate, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from requests.exceptions import ConnectionError

# Create your views here.
from django.views import View
from django.contrib.auth.decorators import login_required

from .Scrapper import Scrapper
from .models import *
from .forms import *
from .recommender import get_similar


class HomeView(View):
    templateName = "index.html"

    # @login_required
    def get(self, request):
        shops = Shop.objects.filter(status=True)

        product_names = []
        interests = ProductInterest.objects.filter(user_id=request.user.id)
        # print(interests)
        for interest in interests:
            if interest.category is not None:
                product_names.append(interest.category.name)
        # print(product_names)
        # print(product_names)
        ids = []
        if len(product_names):
            ids = get_similar(product_names)[:10]
        # print(ids)
        productList = []
        productIndex = 0
        for id in ids:
            category = Category.objects.get(id=id)
            try:
                scrapper = Scrapper(
                    category.searchQuery,
                    category.shop.productSelector,
                    category.shop.nameSelector,
                    category.shop.priceSelector,
                    category.shop.imageSelector,
                    category.shop.linkSelector,
                    category.shop.name,
                    category.shop.priceOffset
                )
                # print(scrapper.getResultsForMany())
                results = scrapper.getResultsForMany()

                if len(results) > 2:
                    rLength = random.randint(1, len(results))
                    rList = random.choices(results, k=rLength)

                    # print(rList)

                    for item in rList:
                        item['category'] = category
                        item['index'] = productIndex
                        productList.append(item)
                        productIndex += 1

            except ConnectionError:
                messages.add_message(request, messages.ERROR, "Failed because of internet connection")

        # print(productList)
        context = {
            'shops': shops,
            'products': productList
        }

        return render(request, "index.html", context=context)


class SearchView(View):
    def get(self, request):
        searchItem = request.GET.get('q', None)

        shops = Shop.objects.filter(status=True)
        results = []
        if searchItem:
            productIndex = 0
            for shop in shops:

                url = shop.searchQuery.replace("[$q]", searchItem)
                scrapper = Scrapper(url, shop.productSelector, shop.nameSelector, shop.priceSelector,
                                    shop.imageSelector,
                                    shop.linkSelector,
                                    shop.name,
                                    shop.priceOffset)
                '''
                print("-----Results For: "+ shop.name)
                print(scrapper.getResultsForMany())
                print("\n")
                '''
                try:
                    scrapped = scrapper.getResultsForMany()
                    for scrap in scrapped:
                        scrap['shop'] = shop
                        scrap['index'] = productIndex
                        results.append(scrap)
                        productIndex += 1

                except ConnectionError:
                    messages.add_message(request, messages.ERROR, "Failed because of internet connection")

        print(results)
        context = {
            'shops': shops,
            'results': results,
            'pageTitle': "Search Results For " + searchItem
        }

        return render(request, "search-view-page.html", context=context)


class shopsView(View):

    def get(self, request):
        shops = Shop.objects.filter(status=True)
        context = {
            'shops': shops
        }
        # messages.add_message(request, messages.ERROR, "Invalid Information")
        return render(request, "shops-view-page.html", context=context)


class ShopView(View):

    def get(self, request, id):
        productList = []
        shop = Shop.objects.get(pk=id)

        categoryId = request.GET.get('category', None)
        if categoryId is None:
            url = shop.website
            categoryHeading = shop.name + ": Featured Products"
            productSelector = shop.featuredProductSelector
            selectedCategory = None

        else:
            selectedCategory = Category.objects.get(pk=categoryId)
            url = selectedCategory.searchQuery
            productSelector = shop.productSelector
            if selectedCategory.category is not None:
                parent = selectedCategory.category.name
                categoryHeading = shop.name + ": " + parent + " - " + selectedCategory.name
            else:
                categoryHeading = shop.name + ": " + selectedCategory.name

        categories = Category \
            .objects \
            .values() \
            .filter(category__isnull=True, shop=id)

        categoryList = list(categories)
        for category in categoryList:
            subCategories = Category \
                .objects \
                .values() \
                .filter(category=category['id'])
            category['categories'] = list(subCategories)
        try:
            scrapper = Scrapper(url, productSelector, shop.nameSelector, shop.priceSelector,
                                shop.imageSelector, shop.linkSelector, shop.name,
                                shop.priceOffset)

            # print(scrapper.getResultsForMany())
            productIndex = 0
            productList = scrapper.getResultsForMany()
            for product in productList:
                product['index'] = productIndex
                productIndex += 1
        except ConnectionError:
            messages.add_message(request, messages.ERROR, "Failed because of internet connection")
        # print(categoryList)
        # print(productList)
        context = {
            'shop': shop,
            'pageTitle': shop.name,
            'categories': categoryList,
            'category': selectedCategory,
            'products': productList,
            'categoryHeading': categoryHeading
        }
        return render(request, "shop-view-page.html", context=context)


class IndexView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("HomeView")
        return redirect("/login")


class CompareView(View):

    def get(self, request):
        compareProducts = ProductCompare.objects.filter(user_id=request.user.id)
        count = int(compareProducts.count()) + 1
        context = {
            'compareProducts': compareProducts,
            'count': count
        }
        return render(request, "compare-view-page.html", context=context)


class FavouriteView(View):

    def get(self, request):
        favouriteProducts = FavouriteProduct.objects.filter(user_id=request.user.id)
        count = int(favouriteProducts.count()) + 1
        context = {
            'favouriteProducts': favouriteProducts,
            'count': count
        }
        return render(request, "favourite-view.html", context=context)


class RegisterView(View):
    def get(self, request):
        context = {
            'form': RegisterForm
        }
        return render(request, "register-view-page.html", context=context)

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(user)
            messages.add_message(request, messages.SUCCESS, 'User Registered Successfully.')
            return redirect("LoginView")

        # messages.add_message(request, messages.ERROR, "Encountered an error")
        context = {
            'form': form
        }
        return render(request, "register-view-page.html", context=context)


class LoginView(View):
    def get(self, request):
        context = {
            'form': LoginForm
        }
        return render(request, "login.html", context=context)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        has_next = request.GET.get('next', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            # Save session as cookie to login the user
            login(request, user)
            # Success, now let's login the user.
            if has_next:
                messages.add_message(request, messages.INFO, 'Welcome back')
                return redirect(has_next)

            return redirect("/home")
        else:
            messages.add_message(request, messages.ERROR, 'Incorrect username and or password.')

        form = LoginForm(request.POST, instance=user)
        return render(request, 'login.html', {'form': form})


class AddToInterest(View):
    def get(self, request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        res = {}
        if is_ajax:
            link = request.GET.get('link', None)
            image = request.GET.get('image', None)
            name = request.GET.get('name', None)
            categoryId = request.GET.get('categoryId', None)
            price = request.GET.get('price', None)
            shopId = request.GET.get('shopId', None)

            if shopId is None or link is None or image is None or name is None or categoryId is None or price is None:
                res['success'] = False
                res['detail'] = "Invalid data"
            else:
                interest = ProductInterest.objects.create(
                    link=link,
                    image=image,
                    name=name,
                    category_id=categoryId,
                    price=price,
                    shop_id=shopId,
                    user_id=request.user.id
                )
                if interest:
                    res['success'] = True
                else:
                    res['success'] = True
                    res['detail'] = "Failed to save"


        else:
            res['success'] = False
            res['detail'] = "Method not allowed"

        return HttpResponse(json.dumps(res), content_type='application/json')


class AddToCompare(View):
    def get(self, request):
        link = request.GET.get('link', None)
        image = request.GET.get('image', None)
        name = request.GET.get('name', None)
        categoryId = request.GET.get('categoryId', None)
        price = request.GET.get('price', None)
        shopId = request.GET.get('shopId', None)
        next = request.GET.get('next', '/')

        if shopId is None or link is None or image is None or name is None or price is None:
            messages.add_message(request, messages.ERROR, "Invalid Information")
            return HttpResponseRedirect(next)
        else:

            try:
                compare = ProductCompare.objects.get(name=name, shop_id=shopId,
                                                     user_id=request.user.id)
                compare.price = price
                compare.link = link
                compare.image = image
                compare.save()
                messages.add_message(request, messages.INFO, "Product added already")
            except ProductCompare.DoesNotExist:

                compare = ProductCompare.objects.create(
                    link=link,
                    image=image,
                    name=name,
                    category_id=categoryId,
                    price=price,
                    shop_id=shopId,
                    user_id=request.user.id
                )
                messages.add_message(request, messages.SUCCESS, "Product added to compare")
            if compare:

                return HttpResponseRedirect("/compare")
            else:
                messages.add_message(request, messages.ERROR, "Failed to save")
                return HttpResponseRedirect(next)


class AddToNewCompare(View):
    def post(self, request):
        link = request.POST.get('link', None)
        image = request.POST.get('image', None)
        name = request.POST.get('name', None)
        categoryId = request.POST.get('categoryId', None)
        price = request.POST.get('price', None)
        shopId = request.POST.get('shopId', None)
        next = request.POST.get('next', '/')

        if shopId is None or link is None or image is None or name is None or price is None:
            messages.add_message(request, messages.ERROR, "Invalid Information")
            return HttpResponseRedirect(next)
        else:

            try:
                compare = ProductCompare.objects.get(name=name, shop_id=shopId,
                                                     user_id=request.user.id)
                compare.price = price
                compare.link = link
                compare.image = image
                compare.save()
                messages.add_message(request, messages.INFO, "Product added already")
            except ProductCompare.DoesNotExist:

                compare = ProductCompare.objects.create(
                    link=link,
                    image=image,
                    name=name,
                    category_id=categoryId,
                    price=price,
                    shop_id=shopId,
                    user_id=request.user.id
                )
                messages.add_message(request, messages.SUCCESS, "Product added to compare")
            if compare:

                return redirect("CompareView")
            else:
                messages.add_message(request, messages.ERROR, "Failed to save")
                return HttpResponseRedirect(next)


class AddToFavourites(View):
    def post(self, request):
        link = request.POST.get('link', None)
        image = request.POST.get('image', None)
        name = request.POST.get('name', None)
        categoryId = request.POST.get('categoryId', None)
        price = request.POST.get('price', None)
        shopId = request.POST.get('shopId', None)
        next = request.POST.get('next', '/')

        if shopId is None or link is None or image is None or name is None or price is None:
            messages.add_message(request, messages.ERROR, "Invalid Information")
            return HttpResponseRedirect(next)
        else:

            try:
                compare = FavouriteProduct.objects.get(name=name, shop_id=shopId,
                                                       user_id=request.user.id)
                compare.price = price
                compare.link = link
                compare.image = image
                compare.save()
                messages.add_message(request, messages.INFO, "Product added already")
            except FavouriteProduct.DoesNotExist:

                compare = FavouriteProduct.objects.create(
                    link=link,
                    image=image,
                    name=name,
                    category_id=categoryId,
                    price=price,
                    shop_id=shopId,
                    user_id=request.user.id
                )
                messages.add_message(request, messages.SUCCESS, "Product added to favourites")
            if compare:

                return redirect("FavouriteView")
            else:
                messages.add_message(request, messages.ERROR, "Failed to save")
                return HttpResponseRedirect(next)


class DeleteCompareView(View):
    def get(self, request, id):

        try:
            compare = ProductCompare.objects.get(id=id, user_id=request.user.id)
            compare.delete()
            messages.add_message(request, messages.SUCCESS, "Product deleted successfully")
            return redirect("CompareView")
        except ProductCompare.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Failed to delete")
            return redirect("CompareView")
class DeleteFavouriteView(View):
    def get(self, request, id):

        try:
            compare = FavouriteProduct.objects.get(id=id, user_id=request.user.id)
            compare.delete()
            messages.add_message(request, messages.SUCCESS, "Product deleted successfully")
            return redirect("FavouriteView")
        except ProductCompare.DoesNotExist:
            messages.add_message(request, messages.ERROR, "Failed to delete")
            return redirect("FavouriteView")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("LoginView")
