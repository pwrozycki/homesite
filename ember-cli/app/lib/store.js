import Ember from 'ember';

export default {
    /**
     * Returns unique object of type 'type' either from store (if exists) or fetched by DS.Store.
     * findByQuery is used to find object in store
     * query is used in query parameters to DS.Store
     * query defaults to findByQuery (if not specified)
     */
    getUniqueFromCacheOrFetch: function (store, type, findByQuery, query) {
        // query defaults to findByQuery
        if (query === undefined) {
            query = findByQuery;
        }

        var findByQueryKey = Object.keys(findByQuery)[0];
        var findByQueryValue = findByQuery[findByQueryKey];

        // find object of type 'type' by findByQuery key and value
        var objectFromStore = store.all(type).findBy(findByQueryKey, findByQueryValue);
        if (!Ember.isEmpty(objectFromStore)) {
            // return promise instead of raw object (as expected)
            return Ember.RSVP.resolve(objectFromStore);
        }

        // fetch object from store
        return store.find(type, query).then(
            function (result) {
                return result.objectAt(0);
            }
        );
    }
};