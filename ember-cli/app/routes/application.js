import Ember from 'ember';

export default Ember.Route.extend({
    actions: {
        openModal: function (templateName, model) {
            this.render(templateName, {
                into: 'application',
                outlet: 'modal',
                model: model
            });
        },

        closeModal: function() {
            this.disconnectOutlet({
                outlet: 'modal',
                parentView: 'application'
            });
        }
    }
});