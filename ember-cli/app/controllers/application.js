import Ember from 'ember';

export default Ember.ObjectController.extend({
    needs: ['session'],
    session: Ember.computed.alias('controllers.session'),

    actions: {
        login: function () {
            this.get('session').login();
        },
        logout: function () {
            this.get('session').logout();
        }
    }
});