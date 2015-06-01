export default {
    name: 'collection-info',
    after: 'store',

    /**
     * Inject CollectionInfo to every Image model.
     */
    initialize: function (container, application) {
        var store = container.lookup('store:main');

        application.deferReadiness();

        // find CollectionInfo and inject it to every Image model
        store.find('collection-info', 1).then(function(collectionInfo) {
            container.register('collectionInfo:main', collectionInfo, {instantiate: false});
            application.inject('model:image', 'collectionInfo', 'collectionInfo:main');
            application.inject('model:video', 'collectionInfo', 'collectionInfo:main');

            application.advanceReadiness();
        });
    }
};