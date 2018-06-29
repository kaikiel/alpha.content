Vue.component(
    'product_gernal',
    {
    template:
    `<div class="single-product mb-30">
          <div class="single-img">
            <a v-bind:href="url">
              <img v-bind:src="image"  class="first" />
            </a>
          </div>
          <div class="product-content">
            <span>{{product_number}}</span>
            <h3><a v-bind:href="url">{{title}}</a></h3>
	  <template v-for="n in rating">
	      <i class="fa fa-star" style="color:yellow"></i>
	  </template>
          <template v-for="n in 5-rating">
              <i class="fa fa-star" style="color:#ccc"></i>
          </template>

            <div class="product-price">
              <ul>
		<template v-if="sale_price == null || sale_price == ''">
                  <li class="new-price" >{{price}}</li>
		</template>
		<template v-else>
                  <li class="new-price sale"> {{sale_price}}</li>
                  <li class="old-price">{{price}}</li>
		</template>
              </ul>
            </div>
            <div class="add-to-links mt-15">
              <ul>
                <li>
		  <a class="add_shop" v-if="stock" v-on:click="$emit('add_to_cart')"><i class="fa fa-shopping-cart"></i></a>
		  <a class="out_of_stock" v-else><i class="fa fa-shopping-cart"></i></a>
		</li>
                <li><a ><i class="fa fa-book" v-bind:data-uid="uid" v-on:click="$emit('add_to_compare')"></i></a></li>
                <li><a href="#"><i class="fa fa-heart-o"></i></a></li>
              </ul>
            </div>
          </div>
      </div>`,
    props: ['title','product_number','price', 'sale_price', 'url', 'image', 'uid', 'stock', 'rating']
})
Vue.component(
    'product_detail',
    {
        template:
        `<div class="shop-product bb-5">
           <div class="col-lg-5 col-md-5 col-sm-5 col-xs-12">
             <div class="product-wrapper-2">
  		<div class="single-img">
  			<a v-bind:href="url">
 			  <img v-bind:src="image" alt="product" class="first" />
  			</a>
  		</div>
             </div>
           </div>
          <div class="col-lg-7 col-md-7 col-sm-7 col-xs-12">
            <div class="product-details-2">
  		<h3><a v-bind:href="url">{{title}}</a></h3>
  		<div class="product-rating mb-10 color">
              <template v-for="n in rating">
                  <i class="fa fa-star" style="color:yellow"></i>
              </template>
              <template v-for="n in 5-rating">
        	      <i class="fa fa-star" style="color:#ccc"></i>
	      </template>

  		</div>
  		<div class="product-price">
  			<ul>
                <template v-if="sale_price == null || sale_price == ''">
                  <li class="new-price" >{{price}}</li>
                </template>
                <template v-else>
                  <li class="new-price sale"> {{sale_price}}</li>
                  <li class="old-price">{{price}}</li>
                </template>
  			</ul>
  		</div>
  		<p>{{description}}</p>
  		<div class="action-inner mt-20">
  			<div class="product-button-3">
  		          <a class="add_shop"  v-if="stock" v-on:click="$emit('add_to_cart')" >
			    <i class="fa fa-shopping-cart"></i>Add to cart</a>
			  <a class="out_of_stock" v-else ><i class="fa fa-shopping-cart"></i>Out of cart</a>
  			</div>
  			<div class="add-to-links">
  			  <ul>
  			    <li><a ><i class="fa fa-book" v-bind:data-uid="uid"  v-on:click="$emit('add_to_compare')"></i></a></li>
  			    <li><a href="#"><i class="fa fa-heart-o"></i></a></li>
  			  </ul>
  			</div>
  		</div>
  	</div>  
  	<div class="availability">
          <span v-if="!stock">Out of stock</span>
  	</div>
  	<!-- single-details-end -->
  </div>
</div>`,
        props: ['title','product_number','price', 'sale_price', 'url', 'image', 'uid', 'description', 'stock', 'rating']
    }
)
Vue.component('paginate', VuejsPaginate)


var product_listing = new Vue({
    el: '#product-listing',
    data: {
	now_template: 'product_gernal',
        product_data: [],
	none_limit_data: [],
	origin_data: [],
        pages: 0,
        now_page: 0,
	numbers: 12,
	sort: 'a-z',
    },
    created: function(){
	this.origin_data = JSON.parse(document.getElementById('productData').innerText)
	origin_data = this.origin_data
	product_data = this.product_data
	this.none_limit_data = origin_data
	numbers = this.numbers
	count = 0
	while (product_data.length < numbers){
	    if(product_data.length == this.none_limit_data.length){
		break
	    }else{
	        product_data.push(origin_data[count])
	        count ++
	    }
	}
	total_number = origin_data.length
	if (total_number % numbers != 0){
	    this.pages = Math.floor(total_number / numbers) +1
	}
	else{
	    this.pages = total_number / numbers
	}
    },
    methods: {
	add_to_compare: function(uid){
	    json_compare_list = $.cookie('compare_list')
	    if(json_compare_list){
		compare_list = JSON.parse(json_compare_list)
	    }else{
		compare_list = []
	    }
	    if(compare_list.indexOf(uid) == -1){
	        if(compare_list.length < 4){
	  	    compare_list.push(uid)
		    $.cookie('compare_list', JSON.stringify(compare_list))
		    $.notify('Add Compare Success!!',  {globalPosition: 'bottom right',className:'success'})
	        }else{
		    $.notify('Compare List is Full', {globalPosition: 'bottom right',className:'error'})
	        }
	    }else{
		$.notify('Product Already In Compare List', {globalPosition: 'bottom right',className:'error'})
	    }
	},
	add_to_cart: function(translationGroup, amount){
	    shop_cart.add_shop(translationGroup, amount)
	},
        change_page: function(page){
	    product_data = this.product_data
	    none_limit_data = this.none_limit_data
	    numbers = this.numbers
	    start = (page - 1) * numbers
	    this.product_data = []
	    while(this.product_data.length < numbers){
                if(start == this.none_limit_data.length){
                    break
                }else{
	            this.product_data.push(this.none_limit_data[start])
		    start ++
                }
	    }
        },
	change_numbers: function(){
            numbers = this.numbers
	    count = 1
            start = 0
            this.product_data = []
            while(this.product_data.length < numbers){
		if(this.product_data.length == this.none_limit_data.length){
                    break
            	}else{
                    this.product_data.push(this.none_limit_data[start])
                    start ++
		}
            }
	    total_number = this.none_limit_data.length
            if (total_number % numbers != 0){
                this.pages = Math.floor(total_number / numbers) +1
            }
            else{
                this.pages = total_number / numbers
            }
	},
	change_sort: function(){
            sort = this.sort
            origin_data = this.origin_data
            if(sort == 'highest'){
                origin_data.sort(function(a,b){
                    a_price = product_listing.judge_price(a)
                    b_price = product_listing.judge_price(b)
                    return b_price - a_price
                })
            }else if(sort == 'lowest'){
                origin_data.sort(function(a,b){
                    a_price = product_listing.judge_price(a)
                    b_price = product_listing.judge_price(b)
                    return a_price - b_price
                })
            }else if(sort == 'a-z'){
                origin_data.sort(function(a,b){
                    a_title = a[0].toUpperCase()
                    b_title = b[0].toUpperCase()
                    if(a_title > b_title){
                        return 1
                    }
                    if(a_title < b_title){
                        return -1
                    }
                    return 0
                })
            }else if(sort == 'z-a'){
                origin_data.sort(function(a,b){
                    a_title = a[0].toUpperCase()
                    b_title = b[0].toUpperCase()
                    if(a_title > b_title){ 
                        return -1
                    }
                    if(a_title < b_title){ 
                        return 1
                    }
                    return 0

                })
            }
            activity = $('.activity')
            if(activity.length == 0){
		product_listing.no_activity()
            }else{
                mode = activity.data('mode')
                if(mode == 'brand'){
                    brand = activity.data('brand')
                    product_listing.change_brand(brand)
                }else if(mode == 'category'){
                    category = activity.data('category')
                    subject = activity.data('subject')
                    product_listing.change_category(category, subject)
                }
            }
	},
        judge_price: function(product){
            if(product[5]){
                return parseInt(product[5])
            }else{
                return parseInt(product[4])
            }
        },
	change_category: function(category, subject){
	   origin_data = this.origin_data
	    numbers = this.numbers
	    count  = 1
	    none_limit_count = 1

            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
	    this.product_data = origin_data.filter(function(value){
		price = product_listing.judge_price(value)
		if(value[1] == category && value[2] == subject && price >= low && price <= height){
		    none_limit_count ++
		    product_listing.none_limit_data.push(value)
		    if(count <= numbers){
		         count ++
		         return value
		    }
		}
	    })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
	},
	change_brand: function(brand){
            origin_data = this.origin_data
            numbers = this.numbers
	    count = 1
	    none_limit_count = 1
            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
            this.product_data = origin_data.filter(function(value){
		price = product_listing.judge_price(value)
		if(value[3] == brand && price >= low && price <= height){
		    none_limit_count ++
                    product_listing.none_limit_data.push(value)
	            if(count <= numbers){
                        count ++
                        return value
		    }
		}
            })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
	    $('.page_list:nth-child(2)').addClass('active')
	},
        change_price_range: function(low, height){
            this.none_limit_data = []
            this.product_data = []
            product_data = this.product_data
            numbers = this.numbers
            none_limit_count = 1
	    activity = $('.activity')
	    mode = activity.data('mode')
	    if(activity.length == 0){
		product_listing.no_activity()
	    }
            else if(mode == 'brand'){
                brand = activity.data('brand')
                product_listing.change_brand(brand)
            }else if(mode == 'category'){
                category = activity.data('category')
                subject = activity.data('subject')
                product_listing.change_category(category, subject)
            }
        },
	no_activity: function(){
            origin_data = this.origin_data
            numbers = this.numbers
            count = 1
            none_limit_count = 1
            this.none_limit_data = []
            low = parseInt($('#amount1').val().split('-')[0].trim())
            height = parseInt($('#amount1').val().split('-')[1].trim())
	    this.product_data = this.origin_data.filter(function(value){
   	        price = product_listing.judge_price(value)
		if(price >= low && price <= height){
		    product_listing.none_limit_data.push(value)
		    none_limit_count ++
		    if(count <= numbers){
			count ++
			return value
		    }
		}
	    })
            if (none_limit_count % numbers != 0){
                this.pages = Math.floor(none_limit_count / numbers) +1
            }
            else{
                this.pages = none_limit_count / numbers
            }
            $('.page_list:nth-child(2)').addClass('active')
	}
    }
});


