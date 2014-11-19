import Ember from 'ember';

export default Ember.ObjectController.extend({
    needs: ['session'],
    init: function() {
        // TODO: should be moved to initializer
        this.get('controllers.session').setupApplication();
    }
});