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
        return searchableText

    @property
    def sort_on(self):
        sort_on = getattr(self.request, 'sort_on', 'sortable_title')
        return sort_on

    @property
    def sort_order(self):
        sort_order = getattr(self.request, 'sort_order', 'ascending')
        return sort_order

    @property
    def sort_by(self):
        sort_by = "sort_on:{},sort_order:{}".format(self.sort_on, self.sort_order) 
        return sort_by 

    @property
    def p_category(self):
        p_category = getattr(self.request, 'p_category', '')
        p_category = p_category if p_category != 'No Category' else None
        return p_category

    @property
    def p_subject(self):
        p_subject = getattr(self.request, 'p_subject', '')
        p_subject = p_subject if p_subject != 'No Subject' else None
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

    def getNewProduct(self):
        top3Product = api.content.find(portal_type='Product', sort_on='created', sort_order='descending', b_size='3')
        return top3Product
