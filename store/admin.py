from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    extra = 0
    model = models.OrderItem


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
    list_per_page = 10
    list_select_related = ['customer']


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    autocomplete_fields = ['collection']
    search_fields = ['title__icontains']
    prepopulated_fields = {'slug': ['title']}
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        products_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"${products_count} products successfully updated",
            messages.SUCCESS
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page = 10
    list_select_related = ['user']

    @admin.display(ordering='orders')
    def orders(self, customer):
        url = (
                reverse('admin:store_order_changelist')
                + '?'
                + urlencode({'customer__id': str(customer.id)})
        )
        return format_html(f'<a href="{url}">{customer.orders} Orders</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders=Count('order')
        )


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title__icontains']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
                reverse('admin:store_product_changelist')
                + '?'
                + urlencode({'collection__id': str(collection.id)})
        )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )
