$(window).on('load', function () {
  /*
  fixes the height of the scrollable plots if the form height is less
   */
  $('.panel-body').css('max-height', $('#survey-main').height())
})

function reset_inputs() {
  /*
  function to reset all inputs on the page. It currently detects all radio buttons and then
  1. set the button as not checked
  2. remove the class 'checked' from the label so that it does apply the css
   */
  $('#survey-form').trigger('reset')
  $('.question ul li input').parent().removeClass("checked")
  $('.question ul li input:checked').parent().addClass("checked")

}

function check_inputs(submit_value) {
  /*
  checks inputs and shows error, if no error submits the form
   */

  var all_checked = true
  // get all the radio inputs
  var radio_groups = {}
  $(":radio").each(function () {
    radio_groups[this.name] = true
  })

  // checking each of the them for selection
  for (var radio_group in radio_groups) {
    var radio_checked = !!$(":radio[name='" + radio_group + "']:checked").length
    if (!radio_checked) {
      all_checked = false
      break
    }
  }

  // now checking the number of components drawn on figure
  if (all_checked) {
    $("div.lasso_select span").each(function () {
      if (this.textContent === 'None') {
        all_checked = false
      }
    })
  }

  // if not checked show the error message, otherwise submit the form with the submit value as input so that it can be
  // differentiated
  if (!all_checked) {
    $(".alert.error").addClass('visible')
  } else {
    $(".alert.error").removeClass('visible')
    // adding extra input to the form with submit value, it is used to detect which button has been clicked
    var input = $("<input />")
      .attr("type", "hidden")
      .attr("name", "action_type").val(submit_value)
    $('#survey-form').append($(input)).submit()
  }
}

$(document).ready(function () {
  /*
  initial function settings per button and removing any class for radio groups
   */
  $('#back-button').on('click', function () {
    $('#survey-form').submit()
  })

  $('#finish-button').on('click', function (e) {
    check_inputs(e.target.value)
  })

  $('#save_or_more-button').on('click', function (e) {
    check_inputs(e.target.value)
  })

  $('#reset-button').on('click', function () {
    reset_inputs()
  })

  // setting up the initially selected ones as green
  $('.question ul li input').parent().removeClass("checked")
  $('.question ul li input:checked').parent().addClass("checked")

  // setting up the selected ones as green
  $('.question ul li input').on('click', function (e) {
    var clicked = $('#' + e.target.id)
    // finding the common parent that holding all the answers
    var all_options_parent = clicked.parent().parent().parent()
    // removing checked class from the labels
    $('#' + all_options_parent.attr('id') + ' > li > label').removeClass("checked")
    // apply the checked class to the selected one.
    clicked.parent().addClass('checked')
  })

  $('.question-set .single input[type=button]').on('click', function (e) {
    var button_id = e.target.id
    var input_id = button_id.replace('_zero-button', '')
    $('#' + input_id + '_span').text('0')
    $('#' + button_id).removeClass('visible')
  })
})
