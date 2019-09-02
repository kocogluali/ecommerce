// Anasayfa || Detay Sayfasında body değiştirme

var pageType = $("div#content div.container:eq(0)").attr("data-inline-type")
if (pageType) {
    $("body").removeAttr("class").attr("class", pageType)
}
$(document).ready(function () {
    if ($("input[name='oldAdres']:first").val() != "0" && $("input[name='oldAdres']:first").length > 0) {
        $("input[name='oldAdres']:first").click();
        $("#customer_details input,textarea,select").removeAttr("required");
    }
});

// Product Detail // Vote Stars
$("#yorum_ekle p.stars a").click(function () {
    $("input#votes").val($(this).index() + 1);
    $("#yorum_ekle p.stars a").removeAttr("style");
    for (var i = 0; i < $(this).index() + 1; i++) {
        $("#yorum_ekle p.stars a:eq(" + i + ")").css("background-color", "#fed700")
    }
});

// -------------ACCOUNT BASKET-------------
$("tr.cart_item td input[name*='qtyMinMax']").click(function () {
    var item = $(this).parent("div").children("input[type*='number']");
    if ($(this).hasClass("minus")) {
        if (item.val() > 1 && parseInt(item.attr("max")) > item.val())
            item.val(parseInt(item.val()) - 1);
    } else if (parseInt(item.attr("max")) > item.val())
        item.val(parseInt(item.val()) + 1);
});
//sepet Güncelleme
$("input[name*='update_cart']").click(function () {
    var qtyList = new Array(new Array(new Array()));
    $("#formBasket input[type='number'][name='basketItemQty']").each(function () {
        qtyList.push(new Array($(this).attr("data-model-name"), $(this).val()))
    });
    qtyList.splice(0, 1);
    // console.log(qtyList)
    $.ajax({
        url: '/kullanici/update_cart',
        dataType: 'json',
        data: {
            'qtyList[]': qtyList,
            'basketID': $("#basketID").val(),
            'cargoID': $("#calc_shipping_country").val(),
        },
        success: function (data) {
            $.each(JSON.parse(data.basket), function (index, element) {
                console.log(element)
                $("tr.cart_item:eq(" + index + ") span[data-model-name='basketItemTotalPrice']").text(element.fields.totalPrice)

            });
            var cartTotal = parseFloat(JSON.parse(data.cartTotal))
            $("span[id*='cartSubTotal']").text(cartTotal)
            var couponDiscPrice = parseFloat($("#cartCoupon").text())
            var cargoPrice = parseFloat($("#calc_shipping_country option:selected").attr("data-value"))
            if (isNaN(couponDiscPrice))
                couponDiscPrice = 0
            $("span[id*='cartTotal']").text(parseFloat(cartTotal + cargoPrice - couponDiscPrice))
            console.log(couponDiscPrice, cargoPrice)
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(xhr.responseText);
        }
    });
});
//  Sepet Item  Silme
$("#formBasket  td.product-remove a.remove").click(function () {
    var basketItemID = $(this).parent("td").children("input").val();
    var itemTrRows = $(this).parent("td").parent("tr");
    var itemTotalPrice = parseFloat(jQuery(itemTrRows).find($("span[data-model-name='basketItemTotalPrice']")).text()).toFixed(2);
    var cartsubTotal = parseFloat($("#formBasket table.shop_table.shop_table_responsive span#cartSubTotal").text());
    var cartTotal = parseInt($("#formBasket  #cartTotal").text());
    $.ajax({
            url: '/kullanici/remove_basket_item',
            data: {
                'basket_item_id': basketItemID,
            },
            success: function (data) {
                itemTrRows.hide(1000).remove();
                $("#formBasket #cartTotal").text((cartTotal - itemTotalPrice).toFixed(2));
                $("#formBasket #cartSubTotal").text((cartsubTotal - itemTotalPrice).toFixed(2));

            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.responseText)
            }
        }
    )
});
//  Sepet Item  Silme Header and HeaderAll
$("li.mini_cart_item a.remove").click(function () {
    var itemID = $(this).attr("name");
    var parentLi = $(this).parent("li")
    var cartSubTotal = parseFloat($("#cartSubTotal").text()).toFixed(2)
    var qty = parseFloat(jQuery(parentLi).find($("span[data-model-name='basketItemQty']")).text())
    var itemPrice = parseFloat(jQuery(parentLi).find($("span[data-model-name='basketItemPrice']")).text()).toFixed(2);

    $.ajax({
            url: '/kullanici/remove_basket_item',
            data: {
                'basket_item_id': itemID,
            },
            success: function (data) {
                parentLi.hide(1000).remove();
                $("#cartSubTotal").text(cartSubTotal - (qty * itemPrice));
                $("#cartSubTotal").text((cartSubTotal - (qty * itemPrice)).toFixed(2));
                var totalPrice = (cartSubTotal - (qty * itemPrice)).toFixed(2)
                if (!isNaN(totalPrice)) {
                    $("li.nav-item.dropdown span.amount").text(totalPrice);
                    $("span.cart-items-count.count").text(parseInt($("span.cart-items-count.count").text()) - 1);
                } else {
                    $("li.nav-item.dropdown span.amount").text("0");
                    $("span.cart-items-count.count").text("0");
                }

            },
            error: function (xhr, ajaxOptions, thrownError) {
                console.log(xhr.responseText)
            }
        }
    )
});
// -------------------WISHLIST ADD AND REMOVE ----------------------------
$("a.remove_from_wishlist").click(function () {
    var parameters = String($(this).attr("name")).split(",");
    var productID = parameters[0];
    var userID = parameters[1];
    var kendi = $(this).parent("div").parent("td").parent("tr")
    // alert(productID)
    $.ajax({
        url: '/kullanici/remove_fav_items',
        data: {
            'productID': productID,
            'userID': userID,
        },
        success: function (data) {
            kendi.remove()
        },
        error: function (xhr) {
            alert(xhr.responseText)
        }
    })
});
$("div").on('click', '.add_to_wishlist', function () {
    if ($("#curAddToWishID").val() != $(this).attr("name")) {
        $("#curAddToWishID").val($(this).attr("name"));
        var parameters = String($(this).attr("name"));
        var productID = parameters[0];
        $.ajax({
            url: '/kullanici/add_favorite_item',
            data: {
                'productID': productID,
            },
            success: function (data) {
                alert(data);
            },
            error: function (xhr) {
                alert(xhr.responseText)
            }
        })
    }
});
// -----------------./ wishlist ADD AND REMOVE ----------------------------
// -----------------Account => create new acoount ?----------------------
$("#createaccount").click(function () {
    if ($("#account_password").attr("required"))
        $("#account_password").removeAttr("required").parent("span").parent("p").parent("div").toggle();
    else
        $("#account_password").attr("required", "required").parent("span").parent("p").parent("div").toggle();
});
// -------OLD ADRES OR NEW ADRES ON CHANGE ----------
$("input[name='oldAdres']").change(function () {
    if ($(this).val() == "0") {
        $("#customer_details").css("display", "block");
        $("#customer_details input,textarea,select").attr("required", true);
        // $("#order_review input,textarea,select").removeAttr("required");
    } else {
        $("#customer_details input,textarea,select").removeAttr("required");
        // $("#order_review input,textarea,select").attr("required",true);
        $("#customer_details").css("display", "none");
    }
    $("#selected_adres").val($(this).val())
});
// -------------------------Apply Coupon-------------------------------
$("input[name='apply_coupon']").click(function () {
    var coupon_code = $("#coupon_code").val();
    if (coupon_code) {
        $.ajax({
            url: '/kullanici/apply_coupon',
            dataType: 'json',
            data: {
                'code': coupon_code,
                'basketID': $(this).attr("data-model-name"),
            },
            success: function (data) {
                if (JSON.parse(data.status == true)) {
                    // alert("Kupon Uygulandı")
                    var tableDiscTr = '<tr class="order-total">\n' +
                        '   <th>Kupon İndirimi</th>\n' +
                        '    <td data-title="couponDiscPrice"><strong><span class="amount">₺<span id="couponDiscPrice"> ' + data.discPrice + '</span> </span></strong></td>\n' +
                        '  </tr>'
                    $("#formBasket table:eq(1)").prepend(tableDiscTr);
                    $("#order_review table:eq(0) tr.shipping").after(tableDiscTr);
                    var cartTotal = parseFloat($("#cartTotal").text().replace(",", "."))
                    var coupPrice = parseFloat(data.discPrice)
                    $("#cartTotal").text(cartTotal - coupPrice);
                } else
                    alert((data.messages))
            },
            error: function (xhr) {
                alert(xhr.responseText)
            }
        })
    } else {
        alert("Lütfen Kod Giriniz")
    }

});
//------------------------ iyzico and payment method---------------------------------
// Taksit Getir
$("input#cardNumberCre").keyup(function () {
    uzunluk = $(this).val().length;
    if (uzunluk > 6) {
        cart_number = $(this).val();
        $.ajax({
            url: '/kullanici/taksit_getir',
            data: {
                'cart_number': cart_number,
            },
            success: function (data) {
                var $tr = '';
                response = $.parseJSON(data);
                $("#payment_banka_resim").text(response.installmentDetails[0].bankName)
                response = response.installmentDetails[0].installmentPrices
                console.log("-----")
                console.log(response)
                $("#iyzico_installment tbody").children('tr').remove()
                $.each(response, function (i, item) {
                    $tr = $('<tr>').append(
                        $('<td>').html('<span> <input type="radio" class="form-control secili_taksit" id="secilen_taksit" name="secilen_taksit" value=' + item.installmentNumber + '></span>'),
                        $('<td>').text("₺" + item.installmentPrice),
                        $('<td>').text(item.installmentNumber),
                        $('<td>').text("₺" + item.totalPrice),
                    );
                    $("#iyzico_installment").append($tr);
                });
                $("#iyzico_installment input[type='radio']").eq(0).click();
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert(xhr.responseText);
            }
        });
    } else
        console.log("deneme")
});

// open sozleşme tabs
function openSozTab() {
    $("#sozlesme").slideToggle();
}

// taksit sayisini güncelle input hidden

$('#iyzico_installment').on('click', 'input', function () {
    var taksit = $(this).val();
    $("input#taksit_sayisi").val($(this).val())
});

// check payment inputs
function checkPaymentInputs() {
    var durum = true
    var cardNumber = $("#cardNumberCre").val()
    var cardMonth = $("#cardMonth").val()
    var cardYear = $("#cardYear").val()
    var cardCVC = $("#cardCVC").val()
    var terms = $("input#terms").prop("checked")
    var taksit = $("input[name='secilen_taksit']:checked").val()
    if (!cardNumber || !cardMonth || !cardYear || !cardCVC) {
        durum = false
        alert("Lütfen Kredi Kartı Bilgilerini Eksiksiz Doldurunuz")
        // console.log(cardYear, cardMonth, cardCVC, cardNumber)
    }
    if (!terms) {
        durum = false;
        alert("Sözleşmeyi Kabul etmediniz !")
    }
    if (!taksit)
        alert("Lütfen Kaç Taksitle Ödemek İstediğinizi Seçiniz")
    return durum;
}
