import Ember from 'ember';

export default Ember.Route.extend({
    actions: {
        openModal: function (modalName, content) {
            this.controller.set('modalContent', content);
            this.render(modalName, {
                into: 'application',
                outlet: 'modal'
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