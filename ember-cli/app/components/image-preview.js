import Ember from 'ember';

export default Ember.Component.extend({
    actions: {
        up: function () {
            this.sendAction('up');
        },
        left: function () {
            this.sendAction('left');
        },
        right: function () {
            this.sendAction('right');
        }
    }
});
