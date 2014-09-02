( function (G, U) {

  $.validator.addMethod('double', function(value, element, param) {
      return (value !== "") && (value == parseFloat(value, 10)) && (value >= 0);
  }, 'Please enter a numeric value!');

  $.validator.addMethod(
    "regex",
    function(value, element, regexp) {
        var re = new RegExp(regexp);
        return this.optional(element) || re.test(value);
    },
    "Please check your input."
  );

}(this, undefined))
