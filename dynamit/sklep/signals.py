from django.forms.models import model_to_dict
from django.db.models.signals import post_save

from . models import Produkt, AtrybutTypuProduktu, TypProduktu

def do_it_well(Model, AtrybutTypu):
    def define_attribs(sender, instance=None, created=True, **kwargs):
        m = Model()
        values = model_to_dict(m)
        ks = values.keys()

        AtrybutTypu.objects.all().exclude(field__in=ks).delete() # usuwam starocie

        for f in ks:
            ff = getattr(Model, f)
            if ff.field.primary_key:
                continue
            dii = {
                "field": ff.field.name,
                "nazwa": ff.field.verbose_name,
                Model._meta.type_field: instance,
            }
            AtrybutTypu.objects.get_or_create(**dii)
    return define_attribs

post_save.connect(do_it_well(Produkt, AtrybutTypuProduktu), sender=TypProduktu)
