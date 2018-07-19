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
BAD_CHARS = ('?', '-', '+', '*', MULTISPACE)

def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s

def quote(term):
    # The terms and, or and not must be wrapped in quotes to avoid
    # being parsed as logical query atoms.
    if term.lower() in ('and', 'or', 'not'):
        term = '"%s"' % term
    return term

class CoverListing(BrowserView):
    
    def __call__(self,**kw):
        query = {}
        query.update(**kw)
        query.setdefault('portal_type', 'Product')
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)
        return IContentListing(results)



class SearchView(FolderView):

    @property
    def viewTitle(self):
        viewTitle = _(u'Search')
        return viewTitle

    def pdb(self):
        import pdb;pdb.set_trace()

    def munge_search_term(self, q):
        for char in BAD_CHARS:
            q = q.replace(char, ' ')
        r = map(quote, q.split())
        r = " AND ".join(r)
        r = quote_chars(r) + '*'
        return r

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
    
    def categoryList(self):
        portal = api.portal.get()
        context = self.context
        if portal.hasObject('Products'):
            context = portal['Products']
        files = api.content.find(context=context, portal_type="Product")
        categoryList = []
        for item in files:
            category = item.p_category
            if category and category not in categoryList:
                categoryList.append(category)
        return sorted(categoryList)

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
        
        if self.searchableText:
            kwargs['SearchableText'] = self.munge_search_term(self.searchableText)

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

    def getObjectImg(self, obj):
        imgList = []
        imgNameList = ['img1', 'img2', 'img3', 'img4']
        for imgName in imgNameList:
            if getattr(obj, imgName):
                imgList.append('{}/@@images/{}'.format( obj.absolute_url(), imgName) )
        return imgList
