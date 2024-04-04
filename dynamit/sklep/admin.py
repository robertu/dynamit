import json
from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from dynamit.utils import DynamicTypedModelAdmin, DynamicModelAdmin
from . models import TypProduktu, Produkt, AtrybutTypuProduktu, Rozmiar, Kolor, Dostawa


@admin.register(Produkt)
class ProduktAdmin(DynamicTypedModelAdmin):
    list_filter = ("typ_produktu", "kolor", "rozmiar")
    autocomplete_fields = ("typ_produktu",)
    search_fields = ("nazwa", "typ_produktu__nazwa")
    visible_fields = ("nazwa", "typ_produktu", "is_active")
    type_definition = 'typ_produktu'

    list_display = [
        "nazwa",
        "typ_produktu",
        "cena",
        "rozmiar",
        "waga",
        "wysokosc",
        "szerokosc",
        "dlugosc",
        "is_active",
    ]
    readonly_fields = [
        "nazwa",
        "typ_produktu",
        "cena",
        "rozmiar",
        "waga",
        "wysokosc",
        "szerokosc",
        "dlugosc",
        "is_active",
    ]




class AtrybutTypuProduktuInline(admin.TabularInline):
    model = AtrybutTypuProduktu
    extra = 0
    has_delete_permission = lambda self, request, obj=None: False
    has_add_permission = lambda self, request, obj=None: False


@admin.register(TypProduktu)
class TypProduktuAdmin(admin.ModelAdmin):
    inlines = (AtrybutTypuProduktuInline,)
    list_display = ("nazwa", )
    search_fields = ("nazwa",)
    list_filter = ("nazwa",)

@admin.register(Dostawa)
class DostawaAdmin(DynamicModelAdmin):
    list_display = ("nazwa", "created_on", )
    search_fields = ("nazwa",)
    list_filter = ("created_on",)

    def changelist_view(self, request, extra_context=None):
        changelist = self.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        events = [w.to_fullcalendar() for w in queryset.all()]
        extra = extra_context or {}
        extra.update({"events": json.dumps(events, cls=DjangoJSONEncoder)})
        return super().changelist_view(request, extra_context=extra)

admin.site.register(Rozmiar, admin.ModelAdmin)
admin.site.register(Kolor, admin.ModelAdmin)
