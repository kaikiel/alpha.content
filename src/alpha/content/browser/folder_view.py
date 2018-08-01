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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from alpha.content.browser.view import GeneralMethod
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
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)
        return IContentListing(results)


class CustomFolderView(FolderView):

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
    def path(self):
        portal = api.portal.get()
        context = self.context
        if portal.hasObject('products'):
            context = portal['products']
        path = getattr(self.request, 'context_path', context.absolute_url_path())
        return path

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
    def brands(self):
        brands = getattr(self.request, 'brands', '')
        return brands.decode("utf8")

    @property
    def p_category(self):
        p_category = getattr(self.request, 'p_category', '')
        return p_category.decode("utf8")

    @property
    def p_subject(self):
        p_subject = getattr(self.request, 'p_subject', '')
        return p_subject.decode("utf8")
    
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

    @property
    def price_min(self):
        price_min = getattr(self.request, 'price_min', 0)
        return int(price_min)

    @property
    def price_max(self):
        price_max = getattr(self.request, 'price_max', 20000)
        return int(price_max)

    @property
    def price(self):
        price = range(self.price_min, self.price_max+1)
        return price

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
        kwargs.setdefault('path', self.path)
        kwargs.setdefault('batch', True)
        kwargs.setdefault('sort_on', self.sort_on)
        kwargs.setdefault('sort_order', self.sort_order)
        
        if self.searchableText:
            kwargs['SearchableText'] = self.munge_search_term(self.searchableText)

        if self.brands:
            kwargs['brands'] = self.brands

        if self.p_category:
            kwargs['p_category'] = self.p_category

        if self.p_subject:
            kwargs['p_subject'] = self.p_subject

        listing = aq_inner(self.context).restrictedTraverse(
            '@@coverListing', None)
        if listing is None:
            return []
        results = listing(**kwargs)

        # in diff user price is different
        results = [item for item in results if self.salePrice(item.getObject()) in self.price]
        return results

    def batch(self):
        batch = Batch(
            self.results(),
            size=self.b_size,
            start=self.b_start,
            orphan=1
        )
        return batch

    def getObjectImg(self, obj):
        imgList = []
        imgNameList = ['img1', 'img2', 'img3', 'img4']
        for imgName in imgNameList:
            if getattr(obj, imgName):
                imgList.append('{}/@@images/{}'.format( obj.absolute_url(), imgName) )
        return imgList


class SearchView(CustomFolderView, GeneralMethod):

    @property
    def viewTitle(self):
        viewTitle = _(u'Search')
        return viewTitle

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


class ProductListing(CustomFolderView, GeneralMethod):
    test = 123
    template =  ViewPageTemplateFile('templates/product_listing.pt')
    def __call__(self):
        categoryList = self.getCategoryListAll()
        self.categoryList = categoryList.values()[0]
        self.max_price = categoryList.keys()[0]
        return self.template()

    @property
    def path(self):
        path = getattr(self.request, 'context_path', self.context.absolute_url_path())
        return path

    @property
    def price_max(self):
        price_max = getattr(self.request, 'price_max', self.max_price)
        return int(price_max)

    def getBrandList(self):
        brandList = {}
	productBrain = api.content.find(context=self.context, portal_type='Product')
	for item in productBrain:
	    obj = item.getObject()
            brand = obj.brand
            if brandList.has_key(brand):
                brandList[brand] += 1
            else:
                brandList[brand] = 1
	return brandList

    def getCategoryListAll(self):
        categoryList = {}
        price = 0
	productBrain = api.content.find(context=self.context, portal_type='Product')
	for item in productBrain:
	    obj = item.getObject()
            contentPrice = self.salePrice(obj)
            price =  contentPrice if contentPrice > price else price
            category = obj.category
            subject = obj.subcategory
            if categoryList.has_key(category):
                categoryList[category][0] += 1
                if categoryList[category][1].has_key(subject):
                    categoryList[category][1][subject] += 1
                else:
                    categoryList[category][1][subject] = 1
            else:
                categoryList[category] = [1, {subject: 1}]
	return {price:categoryList}

    def getProductAD(self):
        portal = api.portal.get()
        context = self.context
        if portal.hasObject('resource'):
            context = portal['resource']
        productAD = api.content.find(context=context, id="product-ad")
        return productAD

