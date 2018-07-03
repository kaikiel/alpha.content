# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.contenttypes.browser.folder import FolderView
from plone.app.users.browser.register import RegistrationForm
from zope.interface import alsoProvides
from Acquisition import aq_inner
from email.mime.text import MIMEText
import json
import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from zope.globalrequest import getRequest
from alpha.content.browser.configlet import IDict
from alpha.content.browser.currency_configlet import IExchange
from Products.CMFCore.utils import getToolByName
from sets import Set
import pdb


class ExchangeRate(BrowserView):
    def getRMBRate(self):
        rmbRate = api.portal.get_registry_record('exchange', interface=IExchange)
        return rmbRate


class NewsItemView(BrowserView):
    
    def getNewsMonth(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%B')

    def getNewsYear(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y')

    def getNewsDay(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%d')


class ProductView(ExchangeRate):
    def pdb(self):
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
	portal = api.portal.get()
        try:
            request = self.request
        except:
            request = getRequest()

	try:
	    lang = request.cookies.get('I18N_LANGUAGE')
	    if lang == 'zh-tw':
                productBrains = api.content.find(context=portal['zh-tw']['products'], portal_type="Product")
	    elif lang == 'en-us':
		productBrains = api.content.find(ccontext=portal['en-us']['products'], protal_type='Product')
        except:
            productBrains = []
        alsoProvides(request, IDisableCSRFProtection)
        # sortList[buggy] = [0,{'1/4': 0, '1/8': 5} ]
        # sortList[${cayegory}] = [${category_count}, { ${subject}: ${subject_count} }]
        sortList = {}
	brandList = {}
        try:
            for item in productBrains:
		obj = item.getObject()
                category = obj.category
                subject = obj.subcategory
		brand = obj.brand
		title = obj.title
		productNo = obj.productNo
		objAbsUrl = obj.absolute_url()
		salePrice = obj.salePrice
		price = obj.price
		availability = obj.availability
		description = obj.description

                if sortList.has_key(category):
                    sortList[category][0] += 1
                    if sortList[category][1].has_key(subject):
                        sortList[category][1][subject] += 1
                    else:
                        sortList[category][1][subject] = 1
                else:
                    sortList[category] = [1, {subject: 1}]

		if brandList.has_key(brand):
		    brandList[brand] += 1
		else:
		    brandList[brand] = 1
            sortList = json.dumps(sortList).decode('utf-8')
            api.portal.set_registry_record('sortList', sortList, interface=IDict)

	    brandList = json.dumps(brandList).decode('utf-8')
	    api.portal.set_registry_record('brandList', brandList, interface=IDict)

        except  Exception as e:
	    import pdb;pdb.set_trace()
            print e


class ProductListing(BrowserView):
    template = ViewPageTemplateFile("templates/product_listing.pt")
    def __call__(self):
	request = self.request
	productData = []
        sortList = {}
        brandList = {}

	productBrain = api.content.find(context=self.context, portal_type='Product')
	for item in productBrain:
	    obj = item.getObject()
	    title = obj.title
            category = obj.category
            subject = obj.subcategory
            brand = obj.brand
            productNo = obj.productNo
            objAbsUrl = obj.absolute_url()
            salePrice = obj.salePrice
            price = obj.price
            availability = obj.availability
            description = obj.description
            img = objAbsUrl + '/@@images/cover'
            uid = obj.UID()
	    rating = obj.rating
	    translationGroup = item.TranslationGroup
            if sortList.has_key(category):
                sortList[category][0] += 1
                if sortList[category][1].has_key(subject):
                    sortList[category][1][subject] += 1
                else:
                    sortList[category][1][subject] = 1
            else:
                sortList[category] = [1, {subject: 1}]
            if brandList.has_key(brand):
                brandList[brand] += 1
            else:
                brandList[brand] = 1

	    productData.append([title, category, subject, brand, price, salePrice, objAbsUrl, productNo, img, uid,
                                        availability, description, translationGroup, rating])

	self.productData = json.dumps(productData)
	self.sortList = sortList
	self.brandList = brandList
        self.pre_category = request.get('category', '')
        self.pre_subject = request.get('subject', '')
        self.pre_brand = request.get('brand', '')
	self.rmbRate = api.portal.get_registry_record('exchange', interface=IExchange)

        return self.template()


class ConfirmCart(BrowserView):
    template = ViewPageTemplateFile("templates/confirm_cart.pt")
    def __call__(self):
        request = self.request
	abs_url = api.portal.get().absolute_url()
	cookie_shop_cart = requesty.cookiesget('shop_cart')
	if not cookie_shop_cart or json.loads(cookie_shop_cart):
	    api.portal.show_message(message='Shop Cart Is Empty', request=request, type='warn')
	    request.response.redirect('%s/products' %abs_url)
	    return
	shop_cart = json.loads(request.cookies['shop_cart'])
	uidList = shop_cart.keys()
	productData = []
	totalNumber = 0
	for uid in uidList:
	    product = api.content.get(UID=uid)
	    amount = shop_cart[str(uid)][4]
	    title = product.title
            price = product.price
            salePrice = product.salePrice
            abs_url = product.absolute_url()
	    if salePrice:
		totalNumber += salePrice * amount
	    else:
		totalNumber += price * amount

	    productData.append( [title, price, salePrice, abs_url, amount, uid] )

	self.totalNumber = totalNumber
	self.productData = productData
	return self.template()


class ContactUs(BrowserView):
    template = ViewPageTemplateFile('templates/contact_us.pt')
    def __call__(self):
	return self.template()


class NewsFolderView(FolderView, NewsItemView):
    def results (self, **kwargs):
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'News Item')
        kwargs.setdefault('batch', True)
        kwargs.setdefault('b_size', self.b_size)
        kwargs.setdefault('b_start', self.b_start)

        listing = aq_inner(self.context).restrictedTraverse(
            '@@folderListing', None)
        if listing is None:
            return []
        results = listing(**kwargs)
        return results


class SocialButtonMacro(BrowserView):
    """"""


class SendMail(BrowserView):
    def __call__(self):
        request = self.request
	name = request.get('name')
	email = request.get('email')
	message = request.get('message')
        body_str = """Name:{}<br/>Email:{}<br/>Message:{}""".format(name, email, message)
        mime_text = MIMEText(body_str, 'html', 'utf-8')
        api.portal.send_email(
            recipient="ah13441673@gmail.com",
            sender="henry@mingtak.com.tw",
            subject="Contact Us",
            body=mime_text.as_string(),
        )
        api.portal.show_message(message='發送成功!'.decode('utf-8'), request=request)


class CompareList(BrowserView):
    template = ViewPageTemplateFile('templates/compare_list.pt')
    def __call__(self):
	request = self.request
	json_compare_list = request.cookies.get('compare_list')
	data = []
	if json_compare_list:
	    lang = request.cookies.get('I18N_LANGUAGE')
	    compare_list = json.loads(json_compare_list)
	    for item in compare_list:
	        contents = api.content.find(TranslationGroup = item)
 	        for brain in contents:
		    if brain.Language == lang:
		        data.append(brain)
	    self.data = data
	else:
	    self.data = False

	return self.template()


class LogOut(BrowserView):
    def __call__(self):
        mt = getToolByName(self.context, 'portal_membership')
        mt.logoutUser(self.request)
        current_url = self.context.portal_url() 
        self.request.response.redirect(current_url)


class Register(RegistrationForm):
    RegistrationForm.template = ViewPageTemplateFile('templates/register_form.pt')


class PersonalDetails(BrowserView):
    template = ViewPageTemplateFile('templates/personal_view.pt')
    def __call__(self):
        if not api.user.is_anonymous():
            formdata = self.request.form
            if formdata.has_key('email') and formdata.has_key('fName'):
                formNameList = ['fName'   , 'lName', 'email', 'phone'  , 'fax'  , 'company', 'address1', 
                                'address2', 'city' , 'zip'  , 'country', 'state', 'newsletter']
                self.setProperties(formNameList)
                current_url = self.request.URL
                self.request.response.redirect(current_url)

            return self.template()
        else:
            portal_url = self.context.portal_url()
            self.request.response.redirect(portal_url+'/login')

    def getCurrentUser(self):
        return api.user.get_current()

    def setProperties(self, formNameList):
        request = self.request
        alsoProvides(request, IDisableCSRFProtection)
        mappingDict = {}
        portal_memberdata = getToolByName(self.context, "portal_memberdata")
        formdata = self.request.form
        for name in formNameList:
            if portal_memberdata.hasProperty(name) and formdata.has_key(name):
                mappingDict.update({name: formdata[name]})
            if name == 'newsletter' and formdata.has_key('newsletter'):
                self.updateEmailList(formdata['email'], formdata['newsletter'])
        self.getCurrentUser().setMemberProperties(mapping=mappingDict) 

    def updateEmailList(self, email, action):
        newsletter = self.getNewsletter()
        emailList = Set()
        if newsletter != None:
            emailList = newsletter.getObject().description.split('\r\n')
            emailList = Set([e for e in emailList if e != ''])
            if action == 'true':
                emailList.add(email)
            elif action == 'false':
                emailList.discard(email)
            request = self.request
            alsoProvides(request, IDisableCSRFProtection)
            emailStr = ''
            for email in emailList:
                emailStr += email + '\r\n'
            newsletter.getObject().description = emailStr

    def getNewsletter(self):
        portal = api.portal.get()
        if portal.hasObject('resource'):
            emailPage = api.content.find(portal['resource'], portal_type='Document', id='newsletter' )
            return emailPage[0] if len(emailPage) != 0 else None
        else:
            return


