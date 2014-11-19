import Ember from 'ember';
import csrfutil from '../tools/csrftoken';

var REST_SESSION_URL = '/gallery/api/session';

var $ = Ember.$;

export default Ember.ObjectController.extend({
    username: null,
    password: null,
    error: null,

    reset: function () {
        this.setProperties({
            username: null,
            password: null,
            error: null,
            model: null
        });
    },

    isAuthenticated: function () {
        return !Ember.isEmpty(this.get('model'));
    }.property('model'),

    setupApplication: function () {
        var self = this;
        Ember.$.getJSON(REST_SESSION_URL).then(function (response) {
            self.fetchCurrentUser(response.sessionView.user_id);
        });

        csrfutil.setupCsrf();
    },

    fetchCurrentUser: function (user_id) {
        var self = this;
        if (!Ember.isEmpty(user_id)) {
            this.store.find('user', user_id).then(function (user) {
                self.set('model', user);
            });
        }
    },

    login: function () {
        var self = this, data = this.getProperties('username', 'password');
        $.post(REST_SESSION_URL, data).then(
            function (response) {
                var success = response.sessionView.success;
                if (!success) {
                    self.set('error', !success);
                } else {
                    self.fetchCurrentUser(response.sessionView.user_id);
                }
            }
        );
    },

    logout: function () {
        $.ajax({url: REST_SESSION_URL, type: 'delete'});
        this.reset();
    }
});