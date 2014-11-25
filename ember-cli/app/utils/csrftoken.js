import Ember from 'ember';

var $ = Ember.$;

export default {
    getCookie: function (name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = $.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    csrfSafeMethod: function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    },

    setupAjaxForCSRF: function () {
        var self = this;
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                var csrftoken = self.getCookie('csrftoken');
                if (!self.csrfSafeMethod(settings.type) && !this.crossDomain && !Ember.isEmpty(csrftoken)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
};