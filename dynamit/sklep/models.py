from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
# Create your models here.
models.options.DEFAULT_NAMES += ("owner_field","type_field")

from django.urls import reverse

User = get_user_model()

class TypProduktu(models.Model):

    class Meta:
        verbose_name = "typ produktu"
        verbose_name_plural = "typy produktów"

    nazwa = models.CharField(max_length=200)

    def __str__(self):
        return self.nazwa


class Rozmiar(models.Model):

    class Meta:
        verbose_name = "rozmiar"
        verbose_name_plural = "rozmiary"
        ordering = ("id",)

    nazwa = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nazwa

class Kolor(models.Model):

    class Meta:
        verbose_name = "kolor"
        verbose_name_plural = "kolory"
        ordering = ("nazwa",)

    nazwa = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.nazwa

class Produkt(models.Model):

    class Meta:
        owner_field = "created_by"
        type_field = "typ_produktu"
        verbose_name = "produkt"
        verbose_name_plural = "produkty"

    nazwa = models.CharField(max_length=200)
    typ_produktu = models.ForeignKey(TypProduktu, null=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField("aktywny", default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        editable=False,
    )
    created_on = models.DateTimeField("data utworzenia", auto_now_add=True)
    dlugosc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    szerokosc = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wysokosc = models.DecimalField("wysokość", max_digits=5, decimal_places=2, null=True, blank=True)
    waga = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cena = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rozmiar = models.ForeignKey(Rozmiar, null=True, blank=True, on_delete=models.SET_NULL)
    kolor = models.ForeignKey(Kolor, null=True, blank=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.nazwa


class AtrybutTypuProduktu(models.Model):

    class Meta:
        owner_field = "created_by"
        verbose_name = "typ produktu (atrybut)"
        verbose_name_plural = "typ produktu (atrybuty)"

    typ_produktu = models.ForeignKey(TypProduktu, editable=False, on_delete=models.CASCADE, related_name="attrs")
    nazwa = models.CharField(max_length=200, editable=False)
    field = models.CharField(max_length=200, editable=False)
    is_visible = models.BooleanField("widoczny", default=True)

    def __str__(self):
        return str(self.nazwa)

    def __repr__(self):
        return f"<AtrybutTypuProduktu({self.typ_produktu}): {self.field} '{self.nazwa}'>"


class Dostawa(models.Model):

    class Meta:
        owner_field = "created_by"
        verbose_name = "dostawa"
        verbose_name_plural = "dostawy"

    nazwa = models.CharField(max_length=200)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        editable=False,
    )
    created_on = models.DateTimeField("data dostawy")

    def to_fullcalendar(self):

        return {
            "id": self.pk,
            "title": self.nazwa,
            "start": self.created_on.isoformat(),
            "end": (self.created_on + timedelta(hours=1)).isoformat(),
            "url": reverse("admin:sklep_dostawa_change", args=[self.pk]),
        }

    def __str__(self):
        return self.nazwa

