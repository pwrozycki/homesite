import Ember from 'ember';

export default Ember.TextField.extend({
    hasFocusBinding: Ember.computed.alias('hasFocus'),

    didInsertElement: function() {
        this.set('hasFocusBinding', false);
    },

    focusOut: function() {
        var self = this;

        // delay setting hasFocusBinding to false
        this.run = Ember.run.later(function() {
            self.set('hasFocusBinding', false);
        }, 200);
    },

    focusIn: function(event) {
        this.set('hasFocusBinding', true);

        Ember.run.later(function() {
            Ember.$(event.target).select();
        }, 50);

        // if focus was restored remove any pending focusOut run
        if (this.run != null) {
            Ember.run.cancel(this.run);
            this.run = null;
        }
    }
});