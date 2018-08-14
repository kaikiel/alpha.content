# -*- coding: utf-8 -*-
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.contenttypes.browser.folder import FolderView
from alpha.content import _
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.utils import getToolByName
from zope.globalrequest import getRequest
from Acquisition import aq_inner
from email.mime.text import MIMEText
from plone.app.users.browser.register import RegistrationForm
from alpha.content.browser.configlet import IDict
from alpha.content.browser.base_inform_configlet import IInform
from alpha.content.browser.user_configlet import IUser
from email.mime.text import MIMEText
from sets import Set
import ast
import json
import datetime
from db.connect.browser.views import SqlObj
import xlsxwriter
from StringIO import StringIO


class GeneralMethod(BrowserView):
    def salePrice(self, obj):
        if api.user.is_anonymous():
            if (obj.getParentNode().id == 'promotions'):
                obj_timeLimit = obj.timeLimit or datetime.datetime(1,1,1,0,0)
                if not(obj_timeLimit and not obj_timeLimit >= datetime.datetime.today()):
                    return obj.salePrice
                else:
                    return obj.price
            return obj.price

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': 'l_a_price', 'level_B': 'l_b_price', 'level_C': 'l_c_price', 'level_D': 'salePrice'}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                if group == 'level_D':
                    if (obj.getParentNode().id == 'promotions'):
                        obj_timeLimit = obj.timeLimit or datetime.datetime(1,1,1,0,0)
                        if not(obj_timeLimit and not obj_timeLimit >= datetime.datetime.today()):
                            return obj.salePrice
                        else:
                            return obj.price
                return getattr(obj, groupDict[group]) or obj.salePrice

        if (obj.getParentNode().id == 'promotions'):
            obj_timeLimit = obj.timeLimit or datetime.datetime(1,1,1,0,0)
            if not(obj_timeLimit and not obj_timeLimit >= datetime.datetime.today()):
                return obj.salePrice
            else:
                return obj.price
        return obj.price

    def hasSale(self):
        if api.user.is_anonymous():
            return False

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': False, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return False

    def hasCheckOut(self):
        if api.user.is_anonymous():
            return True

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': True, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return True

    def hasPromoCode(self):
        if api.user.is_anonymous():
            return True

        groupList = ['level_A', 'level_B', 'level_C', 'level_D']
        groupDict = {'level_A': False, 'level_B': False, 'level_C': False, 'level_D': True}
        currentGroups = api.user.get_current().getProperty('group')
        for group in groupList:
            if group in currentGroups:
                return groupDict[group]
        return True


class GetProductData(GeneralMethod):
    def __call__(self):
        try:
            request = self.request
            uid = request.get('uid', '')
            if uid:
                content = api.content.get(UID=uid)
                title = content.title
                contentUrl = content.absolute_url()
                price = self.salePrice(content)
                img = contentUrl + '/@@images/cover/thumb'
                data = [str(title), contentUrl, price, img]
                return json.dumps(data)
            else:
                return 'error'
        except Exception as e:
            print 'restful getProductData error {}'.format(e)


class Companys(BrowserView):
    template = ViewPageTemplateFile('templates/companys.pt')
    def __call__(self):
        companyBrains = api.content.find(context=self.context, portal_type='Document', sort_on="getObjPositionInParent")
	self.companyBrains = companyBrains
	return self.template()


class UseCouponStatus(BrowserView):
    template = ViewPageTemplateFile('templates/use_coupon_status.pt')
    def __call__(self):
        username = api.user.get_current().id
        permissions = api.user.get_permissions(username=username)['Manage Site']
        if permissions:
            request = self.request
            execSql = SqlObj()
            execStr = """SELECT * FROM coupon_status  ORDER BY `coupon_status`.`id` DESC"""
            self.data = execSql.execSql(execStr)

            return self.template()
        else:
            self.request.response.redirect(self.context.portal_url)


class ReturnProduct(BrowserView):
    template = ViewPageTemplateFile('templates/return_product.pt')
    def __call__(self):
        self.viewTitle = _(u'Return')
	request = self.request
	first_name = request.get('first_name')
 	last_name = request.get('last_name')
        phone = request.get('phone')
        product_name = request.get('product_name')
        product_code = request.get('product_code')
        date = request.get('date')
        opened = request.get('opened')
        order_id = request.get('order_id')
        reason = request.get('reason')
        amount = request.get('amount')
        detail = request.get('detail')

	if first_name and last_name:
	    body_str = """fisrst_name:%s<br>last_name:%s<br>phone:%s<br>date:%s<br>order_id:%s<br>product_name:%s<br>product_code:%s<br>
			amount:%s<br>reason:%s<br>opened:%s<br>detail:%s<br>
                    """ %(first_name, last_name, phone, date, order_id, product_name, product_code, amount, reason, opened, detail)
            mime_text = MIMEText(body_str, 'html', 'utf-8')
            api.portal.send_email(
                recipient="ah13441673@gmail.com",
                sender="henry@mingtak.com.tw",
                subject="退貨申請" ,
               body=mime_text.as_string(),
            )
        return self.template()


class Brands(BrowserView):
    template = ViewPageTemplateFile('templates/brands.pt')
    def __call__(self):
        self.viewTitle = _('Brands')
	brandList = {}
	productBrains = api.content.find(context=api.portal.get()['products'], portal_type='Product')
	for item in productBrains:
            obj = item.getObject()
            brand = obj.brand
	    firstLetter = brand[0]
	    if brandList.has_key(firstLetter):
                if brand not in brandList[firstLetter]:
                    brandList[firstLetter].append(brand)
	    else:
	        brandList[firstLetter] = [brand]
	self.brandList = brandList
	return self.template()


class SiteMap(BrowserView):
    template = ViewPageTemplateFile('templates/site_map.pt')
    def __call__(self):
        self.viewTitle = _(u'Site Map')
	site_map = api.content.find(context=api.portal.get(), depth=1)
	self.site_map = site_map
        return self.template()


class NewsItemView(BrowserView):
    def getNewsMonth(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%B')

    def getNewsYear(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y')

    def getNewsDay(self, obj):
        return datetime.datetime.strptime(obj.CreationDate(), '%Y-%m-%dT%H:%M:%S+00:00').strftime('%d')


class ProductView(GeneralMethod):
    def getImg(self):
        imgList = []
        imgNameList = ['img1', 'img2', 'img3', 'img4']
        for imgName in imgNameList:
            if getattr(self.context, imgName):
                imgList.append('{}/@@images/{}'.format( self.context.absolute_url(), imgName) )
	return imgList


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
            print e


class ConfirmCart(GeneralMethod):
    template = ViewPageTemplateFile("templates/confirm_cart.pt")
    def __call__(self):
        self.viewTitle = _(u'Confirm Cart')
        request = self.request
	abs_url = api.portal.get().absolute_url()
	cookie_shop_cart = request.cookies.get('shop_cart')
	if not cookie_shop_cart or not json.loads(cookie_shop_cart):
	    api.portal.show_message(message='Shop Cart Is Empty', request=request, type='warn')
	    request.response.redirect('%s/products' %abs_url)
	    return

	shop_cart = json.loads(request.cookies['shop_cart'])
	uidList = shop_cart.keys()
	productData = []
	totalNumber = 0
	for uid in uidList:
	    product = api.content.get(UID=uid)
            if product:
	        amount = int(shop_cart[str(uid)])
	        title = product.title
                price = product.price
                salePrice = product.salePrice
                abs_url = product.absolute_url()
                totalNumber += self.salePrice(product) * amount

	        productData.append( [title, price, salePrice, abs_url, amount, uid, product] )
	self.totalNumber = totalNumber
	self.productData = productData
	return self.template()

    def getUserProperties(self):
        user = api.user.get_current()
        propertyList = ['city', 'fax', 'group', 'zip', 'address2', 'address1', 'company', 'promoCode', 'telephone', 'lName', 'state', 'fName', 'country', 'fullname', 'newsletter', 'email']
        propertyDict = {}
        for p_name in propertyList:
            propertyDict.update({p_name: user.getProperty(p_name)})
        return propertyDict


class DownloadExcel(GeneralMethod):

    def __call__(self):
        output = StringIO()
        request = self.request
        productData = self.request.cookies.get('shop_cart', '')
        if productData:
            productData = json.loads(productData)
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('Sheet1')

            worksheet.write('A1', '商品名稱')
            worksheet.write('B1', '料號')
            worksheet.write('C1', '價格')
            worksheet.write('D1', '數量')
            worksheet.write('E1', '總價')

            count = 2
            totalPrice = 0
            for k,v in productData.items():
                obj = api.content.get(UID=k)
                price = self.salePrice(obj)
                worksheet.write('A%s' %count, obj.title)
                worksheet.write('B%s' %count, obj.productNo)
                worksheet.write('C%s' %count, price)
                worksheet.write('D%s' %count, int(v))
                worksheet.write('E%s' %count, price * int(v))
                totalPrice += price * int(v)
                count += 1
            worksheet.write('A%s' %count, '總金額')
            worksheet.write('B%s' %count, totalPrice)

            workbook.close()

            response = request.response
            response.setHeader('Content-Type', 'application/xls')
            response.setHeader('Content-Disposition', 'attachment; filename="shopping_list.xls"' )
            request.response.setCookie('shop_cart', '')
            #api.portal.show_message(message='訂單已成立，之後會用email聯絡'.encode('utf-8'), request=request)
            response.appendBody(output.getvalue())
            response.outputBody()
        return 


class UseCoupon(BrowserView):
    def __call__(self):
        request = self.request
        execSql = SqlObj()
	currency = request.get('currency')
	total = request.get('total')
        product_detail = request.get('product_detail')
        discount = request.get('discount') or 'Null'
        discount_detail = request.get('discount_detail')
        username = api.user.get_current().getUserName()
        recipient_name = request.get('recipient_name', '')
        address = request.get('address', '')
        billing_no = request.get('billing_no', '')
	coupon_code = request.get('coupon_code') or 'Null'
	create_time = request.get('create_time')
        coupon_owner = ''
        if coupon_code:
            existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode')
            coupon_owner = ', '.join([key for key, value in existCode.items() if value == coupon_code]) 

        execStr = "INSERT INTO `coupon_status`(`billing_no`, `coupon_code`, `user`, `recipient_name`, `address`, `product_detail`, `currency`, `total`, `discount`, `coupon_owner`,  `discount_detail`, `time`) \
                   VALUES ('%s', %s, '%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s')" \
                   %(billing_no, coupon_code, username, recipient_name, address, product_detail, currency, total, discount, coupon_owner, discount_detail, create_time)
        execSql.execSql(execStr)


class ContactUs(BrowserView):
    template = ViewPageTemplateFile('templates/contact_us.pt')
    def __call__(self):
        self.viewTitle = _(u'Contact Us')
	self.address = api.portal.get_registry_record('address', interface=IInform)
	self.cellphone = api.portal.get_registry_record('cellphone', interface=IInform)

	return self.template()


class NewsFolderView(FolderView, NewsItemView):
    def results (self, **kwargs):
        kwargs.update(self.request.get('contentFilter', {}))
        if 'object_provides' not in kwargs:  # object_provides is more specific
            kwargs.setdefault('portal_type', 'News Item')
        kwargs.setdefault('batch', True)

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


class CompareList(GeneralMethod):
    template = ViewPageTemplateFile('templates/compare_list.pt')
    def __call__(self):
        self.viewTitle = _(u'Compare List')
	request = self.request
	json_compare_list = request.cookies.get('compare_list')
	data = []
	if json_compare_list:
	    compare_list = json.loads(json_compare_list)
	    for item in compare_list:
	        contents = api.content.find(UID = item)
 	        for brain in contents:
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
    RegistrationForm.viewTitle = _(u'Register')


class PersonalDetails(BrowserView):
    template = ViewPageTemplateFile('templates/personal_view.pt')
    def __call__(self):
        self.viewTitle = _(u'Personal Details')
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


class WishListView(GeneralMethod):
    @property
    def viewTitle(self):
        viewTitle = _(u'Wish List')
        return viewTitle

    def getUserProperty_wishList(self):
        user = api.user.get_current()
        if user:
            wishList = user.getProperty('wishList')
            if wishList:
                return wishList.split(', ')
            else:
                return []
        else:
            self.request.response.redirect(portal_url+'/login')

    def getWishList(self):
        wishUIDList = self.getUserProperty_wishList()
        wishList = []
        for uid in wishUIDList:
            wishList.append(api.content.get(UID=uid))
        return wishList

class AddWishList(BrowserView):
    def setWishList(self, wishItemUID):
        user  = api.user.get_current()
        wishList = user.getProperty('wishList')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                if wishItemUID not in wishList:
                    wishList = wishList.split(', ')
                    wishList.append(wishItemUID)
                    wishList = ', '.join(wishList) 
                else:
                    msg = _(u'Add WishList Repeat!!')
                    trans_msg = api.portal.translate(msg, lang=self.context.Language())
                    return json.dumps({'error': trans_msg})
            else: 
                wishList = str(wishItemUID)
            alsoProvides(self.request, IDisableCSRFProtection)
            user.setMemberProperties(mapping={'wishList': wishList})

            msg = _(u'Add WishList Success!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'success': trans_msg})
        else:
            msg = _(u'wishItemUID is not valid!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})

    def __call__(self):
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('wishItemUID'):
                wishItemUID  = query['wishItemUID']
                return self.setWishList(wishItemUID)
            else:
                msg = _(u'Query string supplied is not valid')
                trans_msg = api.portal.translate(msg, lang=self.context.Language())
                return json.dumps({'error': trans_msg})
        else: 
            msg = _(u'Add WishList Must Be Login!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})


class DelWishList(BrowserView):
    def delWishList(self, wishItemUID):
        user  = api.user.get_current()
        wishList = user.getProperty('wishList').split(', ')
        checkUID = api.content.find(portal_type='Product', UID=wishItemUID)
        if len(checkUID) > 0:
            if wishList:
                if wishItemUID in wishList:
                    wishList.remove(wishItemUID)
                    wishList = ', '.join(wishList) 
                    alsoProvides(self.request, IDisableCSRFProtection)
                    user.setMemberProperties(mapping={'wishList': wishList})

                    msg = _(u'Delete WishList Success!!')
                    trans_msg = api.portal.translate(msg, lang=self.context.Language())
                    return json.dumps({'success': trans_msg})

        msg = _(u'wishItemUID is not valid!!')
        trans_msg = api.portal.translate(msg, lang=self.context.Language())
        return json.dumps({'error': trans_msg})

    def __call__(self):
        query = self.request.form.copy()
        if not api.user.is_anonymous():
            if query.has_key('wishItemUID'):
                wishItemUID  = query['wishItemUID']
                return self.delWishList(wishItemUID)
            else:
                msg = _(u'Query string supplied is not valid')
                trans_msg = api.portal.translate(msg, lang=self.context.Language())
                return json.dumps({'error': trans_msg})
        else: 
            msg = _(u'Add WishList Must Be Login!!')
            trans_msg = api.portal.translate(msg, lang=self.context.Language())
            return json.dumps({'error': trans_msg})


class CheckPromoCode(BrowserView):
    def __call__(self):
        promoCode = getattr(self.request, 'promoCode', '')
        existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
        if str(promoCode) in existCode.values():
            return '1'
        else:
            return '0'

class UserAdd(BrowserView):
    def __call__(self):
        request  = self.request
        if request.get('BODY'):
            data = json.loads(self.request.get('BODY', '{}'))
            if data.has_key('username') and data.has_key('email') and data.has_key('password') and data.has_key('fullname'):
                if not api.user.get(username=data['username']):
                    # Disable CSRF protection
                    alsoProvides(self.request, IDisableCSRFProtection)
                    try:
                        properties = {'fullname':data['fullname']}
                        user = api.user.create(username=data['username'], email=data['email'], password=data['password'], properties=properties)
                        return '{"success": "username":"user: '+ user.id +' is created"}'
                    except Exception as ex:
                        return '{"error": "username can not created"}'
                return '{"error": "username can not created"}'
            return '{"error": "Required username, email, password, fullname field is missing"}'
        return '{"error": "json data is missing"}'

class UserProperty(BrowserView):
    def __call__(self):
        request  = self.request
        propertyList = ['city', 'fax', 'group', 'zip', 'address2', 'address1', 'company', 'promoCode', 'telephone', 'lName', 'state', 'fName', 'country', 'fullname', 'newsletter', 'email']
        if request.get('BODY'):
            body = json.loads(self.request.get('BODY', '{}'))
            if body.has_key('username'):
                username = body['username']
                user = api.user.get(username=username)
                if user:
                    userProperty = {}
                    for p in propertyList:
                        userProperty.update({p : user.getProperty(p)})
                    data = json.dumps(userProperty)
                    return data
                return '{"error": "username is not exist"}'
            return '{"error": "Required username field is missing"}'
        return '{"error": "json data is missing"}'

class UpdateUserConfiglet(BrowserView):
    def __call__(self):
        request = self.request
        if request.get('BODY'):
            promoCode = json.loads(request.get('BODY'))['promoCode']
            username = json.loads(request.get('BODY'))['username']
            if promoCode:
                # Disable CSRF protection
                alsoProvides(self.request, IDisableCSRFProtection)

                existCode = api.portal.get_registry_record('alpha.content.browser.user_configlet.IUser.promoCode') or {}
                existCode.update({str(username): str(promoCode)})
                api.portal.set_registry_record('alpha.content.browser.user_configlet.IUser.promoCode', existCode)
                return '{"success": "UserConfiglet is updated"}'
            return '{"error": "json data is missing"}'


class OrderHistoryView(BrowserView):
    @property
    def viewTitle(self):
        viewTitle = _(u'Order History')
        return viewTitle

    def checkAnonymous(self):
        if api.user.is_anonymous():
            self.request.response.redirect(self.context.portal_url()+'/login')

    def getMyOrder(self):
        username = api.user.get_current().id
        execSql = SqlObj()
        execStr = """SELECT * FROM coupon_status WHERE `user` LIKE '%s' ORDER BY `time` DESC""" %username
        results = execSql.execSql(execStr)
        
	return results 



