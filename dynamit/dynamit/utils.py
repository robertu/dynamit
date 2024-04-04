from django.apps import apps
from django.contrib import admin
from ordered_set import OrderedSet

from tqdm import tqdm


def define_other_perms(sender, **kwargs):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType

    OPISY = {
        "add": "Dodaje",
        "view": "Podgląda",
        "change": "Zmienia",
        "delete": "Usuwa",
        "list": "Listuje",
        "viewown": "Podgląda własne",
        "listown": "Listuje własne",
        "deleteown": "Usuwa własne",
        "changeown": "Zmienia własne",
    }
    actions = OPISY.keys()
    app_label = sender.label
    models = apps.all_models[app_label]

    for model in tqdm(models, desc="Define other perms %10s" % app_label):
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            pass
        else:
            m = ct.model_class()
            all_fields = m._meta.get_fields()
            extraact = []
            for f in all_fields:
                pk = getattr(f, "primary_key", False)
                if not pk:
                    extraact.append(
                        (f"change_{f.name}_on_{model}", f"Can change field {f.name}")
                    )
                    extraact.append(
                        (f"view_{f.name}_on_{model}", f"Can view field {f.name}")
                    )
            owner_field = getattr(m._meta, "owner_field", None)
            for action in actions:
                if action in ["viewown", "deleteown", "changeown", "listown"]:
                    if not owner_field:
                        continue
                per, created = Permission.objects.get_or_create(
                    content_type=ct, codename=f"{action}_{model}"
                )
                per.name = f"Can {action}"
                per.save()
            for (codename, name) in extraact:
                per, created = Permission.objects.get_or_create(
                    content_type=ct, codename=codename
                )
                per.name = name
                per.save()



class DynamicModelAdmin(admin.ModelAdmin):

    def has_view_permission(self, request, obj=None):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        if user.has_perm(f"{app}.view_{m}") or user.has_perm(f"{app}.viewown_{m}"):
            return True
        return False

    def has_change_permission(self, request, obj=None):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        if user.has_perm(f"{app}.change_{m}"):
            return True
        if user.has_perm(f"{app}.changeown_{m}") and obj and obj.created_by == user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        if user.has_perm(f"{app}.delete_{m}"):
            return True
        if user.has_perm(f"{app}.deleteown_{m}") and obj and obj.created_by == user:
            return True
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        if user.has_perm(f"{app}.list_{m}"):
            return qs
        if user.has_perm(f"{app}.listown_{m}"):
            return qs.filter(created_by=user)
        return qs.none()

    def get_list_display(self, request):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        return list([f for f in self.list_display if user.has_perm(f"{app}.view_{f}_on_{m}")])

    def get_readonly_fields(self, request, obj=None):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name
        if not self.readonly_fields:
            return []
        return list([f for f in self.readonly_fields if user.has_perm(f"{app}.view_{f}_on_{m}") and not user.has_perm(f"{app}.change_{f}_on_{m}")])

    def get_fields(self, request, obj=None):
        user = request.user
        app = self.model._meta.app_label
        m = self.model._meta.model_name

        if self.fields:
            flds = self.fields
        else:
            form = self._get_form_for_get_fields(request, obj)
            flds = [*form.base_fields, *self.get_readonly_fields(request, obj)]
        return list([f for f in flds if user.has_perm(f"{app}.view_{f}_on_{m}") or user.has_perm(f"{app}.change_{f}_on_{m}")])


    def save_model(self, request, obj, form, change):
        if obj.id is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class DynamicTypedModelAdmin(DynamicModelAdmin):
    list_display = ("nazwa", "is_active",)
    list_filter = ("is_active", "created_by", "created_on")
    search_fields = ("nazwa",)
    readonly_fields = ("nazwa", "is_active", "created_by", "created_on",)
    visible_fields = ("nazwa", "is_active")
    type_definition = None

    def get_fields(self, request, obj=None):
        assert getattr(self, 'type_definition', None), "type_definition field is not defined on admin class"
        fields = super().get_fields(request, obj)
        if not obj:
            return self.visible_fields
        try:
            visible = getattr(obj, self.type_definition).attrs.filter(is_visible=True).values_list("field", flat=True)
        except AttributeError:
            return self.visible_fields
        fields = list(OrderedSet(visible) & OrderedSet(fields))
        return fields