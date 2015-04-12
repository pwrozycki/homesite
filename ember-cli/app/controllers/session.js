import Ember from 'ember';

var REST_SESSION_URL = '/gallery/api/session';

var $ = Ember.$;

export default Ember.Controller.extend({
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

    getActiveSessions: function () {
        var self = this;
        var ajaxJsonPromise = Ember.$.getJSON(REST_SESSION_URL);

        // embed jquery promise in RSVP promise
        // otherwise promise is resolved before user is fetched
        return Ember.RSVP.resolve(ajaxJsonPromise).then(function (response) {
            return self.fetchCurrentUser(response.sessionView.user_id);
        });
    },

    fetchCurrentUser: function (user_id) {
        var self = this;
        if (!Ember.isEmpty(user_id)) {
            return this.store.find('user', user_id).then(function (user) {
                self.set('model', user);
            });
        }

        // return fake promise that is resolved at once
        return Ember.RSVP.resolve(null);
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