import Ember from 'ember';

export default Ember.Component.extend({

    didInsertElement: function () {
        var self = this;

        Ember.$("#modal").dialog({
            width: 800,
            close: function () {
                Ember.$(this).dialog("destroy");
                self.sendAction("closeModal");
            }
        });
    }
});