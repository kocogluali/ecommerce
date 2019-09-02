$(document).ready(function () {
    if ($("#pageTrigger").val() == "False") {
        productFilterbyAttrBrands();
        $(this).val("True");
    }
    // PRODUCT DETAIL VARIANT
    $("#product_varyant select[id*='selvaryant']").change(function () {
        var product_id = $("#product_id").val()
        var secimler = new Array();
        var isNull = false;
        $("#product_varyant select[id*='selvaryant']").each(function (index) {
            // var secimler = (index + ": " + $(this).val());
            if ($(this).val() != "") {
                secimler.push($(this).val());
                isNull = false;
            } else {
                secimler.push(0)
                isNull = true;
            }
        });
        if (isNull == false) {
            $.ajax({
                url: '/urun_fiyat_getir',
                data: {
                    'product_id': product_id,
                    'secimler[]': secimler,
                },
                success: function (data) {
                    console.log(data)
                    var json = JSON.parse(data);
                    $("[id*='urun_fiyat']").text("₺ " + String(json["total"]).replace(".", ","))
                    $("[id*='normal_fiyat']").text("₺ " + String(json["normal_price"]).replace(".", ","))
                    $("#urun_stok").text(json["qty"])

                },
                error: function (xhr, ajaxOptions, thrownError) {
                    alert(xhr.responseText);
                }
            });
        }
    });
    // PRODUCT DETAIL VARIANT

    // PRODUCT LIST FILTER

    $("input[id*='varyant'],input[id*='brandF']").change(function () {
        productFilterbyAttrBrands($(this));
        var itemCheck = $(this).parent("label").children("span.cr").children("i");
        if (itemCheck.hasClass("fa-check"))
            itemCheck.removeClass("fa fa-check");
        else
            itemCheck.addClass("fa fa-check");
    });
    // END PRODUCT LIST FILTER

});

//PRODUCT LIST FILTER FUNCTIONS
function productFilterbyAttrBrands() {
    var slug = document.location.pathname.split("/")[1];
    var curPage = $("#curPage").val();
    var perPageItem = $("select[name='ppp']").val();
    var ordering = $("select[name='orderby']").val();
    $.ajax({
        url: '/product_filter',
        dataType: 'json',
        data: {
            'slug': slug,
            'secimler[]': getAttrList(),
            'price_min': $("#minPrice").val(),
            'price_max': $("#maxPrice").val(),
            'page': curPage,
            'brandss[]': getBrandList("brandF"),
            'orderBy': ordering,
            'perPageItem': perPageItem,
        },
        success: function (data) {
            $("#pageCount").val(JSON.parse(data.sayfa_sayisi));
            $(".spTotalPage").text(JSON.parse(data.sayfa_sayisi));
            $("#spTotalProduct").text(JSON.parse(data.p_count));
            var perPageItem = parseInt(JSON.parse(data.perPageItem))
            var curPage = parseInt($("#curPage").val());
            if (curPage == 1)
                $("span[id*='spShowingProduct']").text(curPage + "-" + ((perPageItem * curPage)));
            else
                $("span[id*='spShowingProduct']").text(((perPageItem * curPage) - 2) + "-" + ((perPageItem * curPage) + 1));
            bindFilterSideBar(JSON.parse(data.gelen_sublar), JSON.parse(data.filterSideBarAttr), getAttrList());
            urunleriListele(JSON.parse(data.products, slug))
        }
    })
}

// PRODUCT LIST FILTER FUNCTIONS
function bindFilterSideBar(subAttrs, filterSideBarAttr, selectedAttrList) {
    // PARENT ATTRIBUTE
    $("input[id*='varyant']").parent("label").parent("li").hide();
    $(subAttrs).each(function (index, element) {
        $("#varyant" + element.pk + "").parent("label").parent("li").show();
    });
}

//PAGINATION
function pagination(paginatonElement) {
    var slug = document.location.pathname.split("/")[1];
    var elementType = paginatonElement.getAttribute("type")
    var curPage = parseInt($("#curPage").val());
    var pageCount = parseInt($("#pageCount").val())
    if (elementType == "prev" && curPage > 1) {
        $("#curPage").val(curPage - 1);
        if (slug == "ara")
            searchPageFilter();
        else
            productFilterbyAttrBrands()
    } else if (elementType == "next" && curPage >= 1 && curPage < pageCount) {
        $("#curPage").val(curPage + 1);
        if (slug == "ara")
            searchPageFilter();
        else
            productFilterbyAttrBrands()
    }
    curPage = parseInt($("#curPage").val());
    var prevButton = $("nav.woocommerce-pagination a.page-numbers[type='prev']");
    var nextButton = $("nav.woocommerce-pagination a.page-numbers[type='next']");
    if (curPage < pageCount) {
        nextButton.show()
        prevButton.show()
    } else {
        nextButton.hide()
    }
    if (curPage == pageCount)
        prevButton.show()
    if (curPage == 1) {
        prevButton.hide()
    }
    $("#spCurPage").text(curPage);
    $(".spTotalPage").text(pageCount);
}

$("select[name='ppp']").change(function () {
    var slug = document.location.pathname.split("/")[1];
    $("#curPage").val(1);
    var curPage = parseInt($("#curPage").val());
    var pageCount = parseInt($("#pageCount").val())
    $("#spCurPage").text(curPage);
    $(".spTotalPage").text(pageCount);
    pagination(document.getElementById("btnPrevPage"));
    if (slug == "ara")
        searchPageFilter();
    else
        productFilterbyAttrBrands();

});

function getBrandList(brandInputID) {
    var brandList = []
    $("input[id*=" + brandInputID + "]").each(function () {
        if ($(this).prop("checked") == true) {
            brandList.push($(this).val())
        }
    });
    if (!brandList)
        return 0;
    return brandList
}

function getAttrList() {
    var attrList = new Array();
    var index = 0;

    $($("ul[id*='attrFilterByID']")).each(function () {
        var itemList = [];
        jQuery(this).find("input").each(function () {
            if ($(this).prop("checked") == true)
                itemList.push(parseInt($(this).val()));
        });
        attrList[index] = new Array(itemList);
        index++;
    });
    return attrList;
}

function urunleriListele(product, mainSlug) {
    var mainSlug = $("#hdnCatSlug").val();
    var ulTabOne = $("div.tab-content div#grid:eq(0) ul");
    ulTabOne.html(" ");
    $(product).each(function (index, element) {
        var li = '<li class="product">\n' +
            '                    <div class="product-outer" style="height: 391px;">\n' +
            '                        <div class="product-inner">\n' +
            '                            <span class="loop-product-categories"><a href="/' + mainSlug + '/" rel="tag">' + $("#hdnCatName").val() + '</a></span>\n' +
            '                            <a href="/' + mainSlug + '/' + element.fields.slug + '/">\n' +
            '                                <h3>' + element.fields.title + '</h3>\n' +
            '                                <div class="product-thumbnail">\n' +
            '                                    \n' +
            '                                        <img src="/media/' + element.fields.image + '" alt="' + element.fields.title + '" width="240" height="220" style="width: 240px;height: 220px">\n' +
            '                                    \n' +
            '                                </div>\n' +
            '                            </a>\n' +
            '                            <div class="price-add-to-cart">\n' +
            '                                <span class="price">\n' +
            '                                    <span class="electro-price">\n' +
            '                                        <ins><span class="amount">₺ ' + element.fields.price + '</span></ins>\n' +
            '                                    </span>\n' +
            '                                </span>\n' +
            '                                <a rel="nofollow" href="/' + mainSlug + '/' + element.fields.slug + '/" class="button add_to_cart_button">Add\n' +
            '                                    to cart</a>\n' +
            '                            </div><!-- /.price-add-to-cart -->\n' +
            '\n' +
            '                            <div class="hover-area">\n' +
            '                                <div class="action-buttons">\n' +
            '                                    <a href="javascript:void();" rel="nofollow" class="add_to_wishlist" name="' + element.pk + '">Wishlist</a>\n' +
            '                                    <a href="#" class="add-to-compare-link">Compare</a>\n' +
            '                                </div>\n' +
            '                            </div>\n' +
            '                        </div>\n' +
            '                        <!-- /.product-inner -->\n' +
            '                    </div><!-- /.product-outer -->\n' +
            '                </li>';
        ulTabOne.append(li)
    });
    $("span[id*='spShowingProduct']").text($("div#grid ul li").length);
    // ul tab two
    var ulTabTwo = $("div.tab-content div#grid-extended ul");
    ulTabTwo.html(" ");
    $(product).each(function (index, element) {
        var li = '<li class="product">\n' +
            '                    <div class="product-outer" style="height: 583px;">\n' +
            '                        <div class="product-inner">\n' +
            '                            <span class="loop-product-categories"><a href="' + mainSlug + '" rel="tag">' + $("#hdnCatName").val() + '</a></span>\n' +
            '                            <a href="/' + mainSlug + '/' + element.fields.slug + '/">\n' +
            '                                <h3>' + element.fields.title + '</h3>\n' +
            '                                <div class="product-thumbnail">\n' +
            '                                    \n' +
            '                                        <img class="wp-post-image" src="/media/' + element.fields.image + '" alt="' + element.fields.title + '">\n' +
            '                                    \n' +
            '                                </div>\n' +
            '\n' +
            '                                <div class="product-rating">\n' +
            '                                    <div title="5 üzerinden ' + element.fields.voteAverage + '" class="star-rating"><span style="width:' + parseFloat(element.fields.voteAverage) * 20 + '%"><strong class="rating">5 üzerinden ' + element.fields.voteAverage + '</strong> </span>\n' +
            '                                    </div>\n' +
            '                                    (' + element.fields.voteAverage + ')\n' +
            '                                </div>\n' +
            '\n' +
            '                                <div class="product-short-description">\n' +
            '                                    <p>' + element.fields.info + '</p>..\n' +
            '                                </div>\n' +
            '\n' +
            '                                <div class="product-sku">Ürün Kodu : ' + element.fields.code + '</div>\n' +
            '                            </a>\n' +
            '                            <div class="price-add-to-cart">\n' +
            '                            <span class="price">\n' +
            '                                <span class="electro-price">\n' +
            '                                    <ins><span class="amount">₺ ' + element.fields.price + '</span></ins>\n' +
            '                                </span>\n' +
            '                            </span>\n' +
            '                                <a rel="nofollow" href="/kadin-pantolon/kadin-pantolon-notdetail/" class="button add_to_cart_button">\n' +
            '                                    Add to cart</a>\n' +
            '                            </div><!-- /.price-add-to-cart -->\n' +
            '                            <div class="hover-area">\n' +
            '                                <div class="action-buttons">\n' +
            '                                    <a href="#" rel="nofollow" class="add_to_wishlist" name="9,1">Wishlist</a>\n' +
            '                                    <a href="#" class="add-to-compare-link">Compare</a>\n' +
            '                                </div>\n' +
            '                            </div>\n' +
            '\n' +
            '                        </div><!-- /.product-inner -->\n' +
            '                    </div><!-- /.product-outer -->\n' +
            '                </li>'
        ulTabTwo.append(li)
    });


}

var slug = document.location.pathname.split("/")[1];

// SITE SEARCH
function searchPageFilter() {
    var minPrice = $("#minPrice").val()
    var maxPrice = $("#maxPrice").val()
    var query = getUrlParameter("q")
    var product_cat = getUrlParameter("product_cat")
    var postType = getUrlParameter("post_type")
    var curPage = $("#curPage").val();
    var ordering = $("select[name='orderby']").val();
    var perPageItem = $("select[name='ppp']").val();
    $.ajax({
        url: '/home/filterSearchProduct',
        dataType: 'json',
        data: {
            'query': query,
            'price_min': minPrice,
            'price_max': maxPrice,
            'post_type': postType,
            'product_cat': product_cat,
            'page': curPage,
            'brands[]': getBrandList("brandS"),
            'orderBy': ordering,
            'perPageItem': perPageItem,
        },
        success: function (data) {
            $("#pageCount").val(JSON.parse(data.sayfa_sayisi));
            $(".spTotalPage").text(JSON.parse(data.sayfa_sayisi));
            $("#spTotalProduct").text(JSON.parse(data.p_count));
            $("span[id*='spShowingProduct']").text(JSON.parse(data.perPageItem));
            urunleriListele(JSON.parse(data.products, slug));
        }
    })
}

function goToPage(pageNumber) {
    var slug = document.location.pathname.split("/")[1];
    var curPage = parseInt($("#curPage").val());
    var pageCount = parseInt($("#pageCount").val());
    if (pageNumber > pageCount)
        pageNumber = pageCount;
    else if (pageNumber < 1)
        pageNumber = 1;
    $("#curPage").val(pageNumber);
    $("#spCurPage").text(pageNumber);
    if (slug == "ara")
        searchPageFilter();
    else
        productFilterbyAttrBrands();
    curPage = parseInt($("#curPage").val());
    var prevButton = $("nav.woocommerce-pagination a.page-numbers[type='prev']");
    var nextButton = $("nav.woocommerce-pagination a.page-numbers[type='next']");
    if (curPage < pageCount) {
        nextButton.show()
        prevButton.show()
    } else {
        nextButton.hide()
    }
    if (curPage == pageCount)
        prevButton.show()
    if (curPage == 1) {
        prevButton.hide()
    }
    $("#spCurPage").text(curPage);
    $(".spTotalPage").text(pageCount);
}

// SITE SEARCH END
var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};
