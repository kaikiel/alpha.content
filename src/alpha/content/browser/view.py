# -*- coding: utf-8 -*- 
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import json
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class ProductView(BrowserView):
    def pdb(self):
        import pdb;pdb.set_trace()
