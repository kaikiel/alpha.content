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


@implementer(IMapCategory)
@adapter(IDexterityContent)
class MapCategory(object):
    """"""
