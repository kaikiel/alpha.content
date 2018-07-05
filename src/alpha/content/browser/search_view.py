# -*- coding: utf-8 -*-
from plone import api
from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.contenttypes import _
from Products.CMFPlone.PloneBatch import Batch
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.contentlisting.interfaces import IContentListing
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import ast
import random
import json
import re


MULTISPACE = u'\u3000'.encode('utf-8')
def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s


class CoverListing(BrowserView):
    
    def __call__(self,**kw):
        query = {}
        query.update(**kw)
        query.setdefault('portal_type', 'Product')
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)
        return IContentListing(results)



class SearchView(FolderView):

    def pdb(self):
        import pdb;pdb.set_trace()

    @property
    def b_size(self):
        b_size = getattr(self.request, 'b_size', None)\
            or getattr(self.request, 'limit_display', None) or 12
        return int(b_size)

    @property
    def searchableText(self):
        searchableText = getattr(self.request, 'searchableText', '')
        if searchableText:
            searchableText = quote_chars(searchableText)
        return searchableText

    @property
    def sort_on(self):
        sort_on = filter(None, re.split('sort_on:(.*),sort_order:(.*)', self.sort_by))[0]
        return sort_on

    @property
    def sort_order(self):
        sort_order = filter(None, re.split('sort_on:(.*),sort_order:(.*)', self.sort_by))[1]
        return sort_order

    @property
    def sort_by(self):
        sort_by = getattr(self.request, 'sort_by', 'sort_on:sortable_title,sort_order:ascending') 
        return sort_by 

    @property
    def p_category(self):
        p_category = getattr(self.request, 'p_category', '')
        return p_category

    @property
    def p_subject(self):
        p_subject = getattr(self.request, 'p_subject', '')
        return p_subject
    
    def categoryDict(self):
        categoryDict = ast.literal_eval(api.portal.get_registry_record('dict', interface=IDict))
        return categoryDict

    def results(self, **kwargs):
        """Return a content listing based result set with contents of the
        folder.

        :param **kwargs: Any keyword argument, which can be used for catalog
                         queries.
        :type  **kwargs: keyword argument

        :returns: plone.app.contentlisting based result set.
        :rtype: ``plone.app.contentlisting.interfaces.IContentListing`` based
                sequence.
        """
        # Extra filter
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'Product')
        portal = api.portal.get()
        context = self.context
        if portal.hasObject('products'):
            context = portal['products']
        kwargs.setdefault('path', context.absolute_url_path())
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)
        kwargs.setdefault('sort_on', self.sort_on)
        kwargs.setdefault('sort_order', self.sort_order)
        kwargs.setdefault('SearchableText', self.searchableText)
        
        if self.p_subject != '':
            kwargs.setdefault('p_subject', self.p_subject)
        if self.p_category != '':
            kwargs.setdefault('p_category', self.p_category)

        listing = aq_inner(self.context).restrictedTraverse(
            '@@coverListing', None)
        if listing is None:
            return []
        results = listing(**kwargs)
        return results

    def batch(self):
        batch = Batch(
            self.results(),
            size=self.b_size,
            start=self.b_start,
            orphan=1
        )
        return batch

    def getRandProduct(self):
        portal = api.portal.get()
        context = self.context
        if portal.hasObject('products'):
            context = portal['products']
        randProduct = api.content.find(portal_type='Product', context=context)
        randProductLen = len(randProduct)
        randProductSet = set()
        while len(randProductSet) < 8:
            randnum = random.randint(0, randProductLen-1)
            randProductSet.add(randProduct[randnum])
        return randProductSet
