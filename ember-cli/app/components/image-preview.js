import Ember from 'ember';

export default Ember.Component.extend({
    actions: {
        up: function () {
            this.sendAction('upPressed');
        },
        left: function () {
            this.sendAction('leftPressed');
        },
        right: function () {
            this.sendAction('rightPressed');
        }
    }
});
