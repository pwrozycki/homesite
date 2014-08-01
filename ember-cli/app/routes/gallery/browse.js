import Ember from 'ember';

export default Ember.Route.extend({
    model: function (params) {
        var promise = null;
        if(! params.directory) {
            promise = this.store.find('directory', { root: true });
        } else {
            promise = this.store.find('directory', { path: params.directory});
        }

        return promise.then(
            function (result) {
                return result.objectAt(0);
            }
        );
    }
});