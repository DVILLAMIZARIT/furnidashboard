( function (G, U) {

  var FormHelper = G.FurnFormHelper || {};

  var init = function(form_container) {

    form_container.find("div.items-form:not(.processed)").each(function(index, f) {
        
      var $form = $(f);
      var $special_fields = $form.find(".item-special-fields");
      var $general_fields = $form.find(".item-general-fields");            
      var $in_stock = $general_fields.find('input.order-item-in-stock');
      var $status = $general_fields.find('select.order-item-status');
      var $po_num = $form.find("input.order-item-po");
      var $ack_num = $form.find("input.order-item-ack-num");
      var date = $.datepicker.formatDate('yy-mm-dd', new Date());

      $form.addClass('processed');

      if ($in_stock.length && $in_stock.prop('checked')) {
        $special_fields.find("input").val("");          // clear special order related values
        $status.val("S");                               // select "In Stock"
        $special_fields.hide();                         // hide special order related fields
        
      } else {  
        $status.val("P");                               // select "Pending"
        $special_fields.show();
      }

      $in_stock.change(function() {
        if (this.checked) {
          $special_fields.find("input").val("");        // clear special order related values
          $status.val("S");                             // select "In Stock"
          $special_fields.hide();                       // hide special order related fields
        } else {
          $status.val("P");                             // select "Pending"
          $special_fields.show();
        }
      });
      
      //processing of dependent fields once item status is changed
      $status.change(function() {
        if ($(this).val() == "S") {
          $special_fields.find("input").val("");        // clear special order related values
          $in_stock.prop("checked", "checked");
          $special_fields.hide();      // hide special order related fields
        } else {
          $in_stock.removeAttr("checked");
          $special_fields.show();
        }
      });
      
      //default PO date to current date if PO number is entered
      $po_num.change(function() {
        if ($(this).val().trim() != "") {
          $special_fields.find("input.order-item-po-date").val(date);
        } else { 
          $special_fields.find("input.order-item-po-date").val("");
        }
      });
      
      //default ack. date to current date if ack. number is entered
      $ack_num.change(function() {
        if ($(this).val().trim() != "") {
          $special_fields.find("input.order-item-ack-date").val(date);
        } else { 
          $special_fields.find("input.order-item-ack-date").val("");
        }
      });            
    });
  }

  //calc order total and balance due
  var recalcOrderTotals =  function() {
    var $total = $("#order-total");
    var $balance_due = $("#balance-due");

    var subtotal = $("#id_subtotal_after_discount").val();
    subtotal = parseFloat(subtotal.replace(',', ''));
    if (isNaN(subtotal)) {
      subtotal = 0.0;
    }

    var tax = $("#id_tax").val();
    tax = parseFloat(tax.replace(',', ''));
    if (isNaN(tax)) {
      tax = 0.0;
    }

    var shipping = $("#id_shipping").val();
    shipping = parseFloat(shipping.replace(',', ''));
    if (isNaN(shipping)) {
      shipping = 0.0;
    }

    var deposit_balance = $("#id_deposit_balance").val();
    deposit_balance = parseFloat(deposit_balance.replace(',', ''));
    if (isNaN(deposit_balance)) {
      deposit_balance = 0.0;
    }

    var total_amount = subtotal + tax + shipping;
    var due = total_amount - deposit_balance;
    
    $total.text("$" + total_amount.toFixed(2));
    $balance_due.text("$" + due.toFixed(2));
  }

  // routine that runs once new formset is added to the form
  var initFormset = function($form, prefix, caption) {
    var accordions = $form.parent().find('div.accordion-group');
    var form_ind = accordions.length - 1;
    $form.find("div.accordion-heading a.accordion-toggle").attr("href", "#collapse" + prefix + "-" + form_ind).text(caption + " " + (form_ind + 1));
    $form.find("div.accordion-body").attr("id", "collapse" + prefix + "-" + form_ind);
    $form.parents('fieldset.accordion').find("div.accordion-body").removeClass("in");
    $form.find("div.accordion-heading a").click();
  }

  FormHelper.applyItemFormRules = init;
  FormHelper.recalcOrderTotals = recalcOrderTotals;
  FormHelper.initFormset = initFormset;
  G.FurnFormHelper = FormHelper;

}(this, undefined))
