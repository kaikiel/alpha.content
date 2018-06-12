# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from email.mime.text import MIMEText
import json
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zope.globalrequest import getRequest


class NewsItemView(BrowserView):
    template = ViewPageTemplateFile('templates/news_item_view.pt')
    def __call__(self):
        return self.template()


class ProductView(BrowserView):
    def pdb(self):
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)
        import pdb;pdb.set_trace()

    def getImg(self):
	request = self.request
	context = self.context
	imgBrain = api.content.find(context=context, portal_type='ProductImg', sort_limit=4)
	return imgBrain


class CoverView(BrowserView):
    template = ViewPageTemplateFile('templates/cover_view.pt')
    def __call__(self):
	return self.template()


class UpdateConfiglet():
    def __call__(self):
        productBrains = api.content.find(path="gct/products", portal_type="Product")
        data = {}
        try:
            request = self.request
        except:
            request = getRequest()

        alsoProvides(request, IDisableCSRFProtection)
        # data[buggy] = [0,{'1/4': 0, '1/8': 5} ]
        # data[${cayegory}] = [${category_count}, { ${subject}: ${subject_count} }]
        try:
            for item in productBrains:
                category = item.p_category
                subject = item.p_subject

                if data.has_key(category):
                    data[category][0] += 1
                    if data[category][1].has_key(subject):


                        data[category][1][subject] += 1
                    else:
                        data[category][1][subject] = 1
                else:
                    data[category] = [1, {subject: 1}]

            data = json.dumps(data).decode('utf-8')
            api.portal.set_registry_record('dict', data, interface=IDict)
            return "Successful"
        except  Exception as e:
            return e

