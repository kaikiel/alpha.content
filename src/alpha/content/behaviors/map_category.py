# -*- coding: utf-8 -*-

from alpha.content import _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from alpha.content.vocabularies.map_category import MapCategory, MapCategoryFactory

@provider(IFormFieldProvider)
class IMapCategory(model.Schema):
    """
    """

    mapCategory = schema.Choice(
        title=_(u'Map Category'),
        vocabulary='alpha.content.MapCategory',
    )


@implementer(IMapCategory)
@adapter(IDexterityContent)
class MapCategory(object):
    def __init__(self, context):
        self.context = context

    @property
    def mapCategory(self):
        if hasattr(self.context, 'mapCategory'):
            return self.context.mapCategory
        return None

    @mapCategory.setter
    def mapCategory(self, value):
        self.context.mapCategory = value
