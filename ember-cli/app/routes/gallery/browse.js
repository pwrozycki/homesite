import Ember from 'ember';

export default Ember.Route.extend({
    model: function (params) {
        return this.store.find('directory', { path: params.directory}).then(
            function (result) {
                return result.objectAt(0);
            }
        );
    }
});