# -*- coding: utf-8 -*-

from alpha.content import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from alpha.content.vocabularies.city_category import CityCategory, CityCategoryFactory

@provider(IFormFieldProvider)
class ICityCategory(model.Schema):
    cityCategory = schema.Choice(
        title=_(u'City Category'),
        vocabulary='alpha.content.CityCategory',
    )



@implementer(ICityCategory)
@adapter(IDexterityContent)
class CityCategory(object):
    def __init__(self, context):
        self.context = context

    @property
    def cityCategory(self):
        if hasattr(self.context, 'cityCategory'):
            return self.context.cityCategory
        return None

    @cityCategory.setter
    def cityCategory(self, value):
        self.context.cityCategory = value

