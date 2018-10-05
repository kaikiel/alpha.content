# -*- coding: utf-8 -*-

# from plone import api
from alpha.content import _
from plone.dexterity.interfaces import IDexterityContent
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class VocabItem(object):
    def __init__(self, token, value):
        self.token = token
        self.value = value

@implementer(IVocabularyFactory)
class CityCategory(object):
    """
    """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        items = [
            VocabItem(u'01', _(u'Taipei')),
            VocabItem(u'02', _(u'New Taipei')),
            VocabItem(u'03', _(u'Taoyuan')),
            VocabItem(u'04', _(u'Hsinchu')),
            VocabItem(u'05', _(u'Miaoli')),
            VocabItem(u'06', _(u'Taichung')),
            VocabItem(u'07', _(u'Changhua')),
            VocabItem(u'08', _(u'Yunlin')),
            VocabItem(u'09', _(u'Chiayi')),
            VocabItem(u'10', _(u'Nantou')),
            VocabItem(u'11', _(u'Tainan')),
            VocabItem(u'12', _(u'Kaohsiung')),
            VocabItem(u'13', _(u'Pingtung')),
            VocabItem(u'14', _(u'Yilan')),
            VocabItem(u'15', _(u'Hualien')),
            VocabItem(u'16', _(u'Taitung')),
            VocabItem(u'17', _(u'Penghu')),
            VocabItem(u'18', _(u'Kinmen')),
            VocabItem(u'19', _(u'Lienchiang')),
        ]

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        # create a list of SimpleTerm items:
        terms = []
        for item in items:
            terms.append(
                SimpleTerm(
                    value=item.token,
                    token=str(item.token),
                    title=item.value,
                )
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


CityCategoryFactory = CityCategory()

