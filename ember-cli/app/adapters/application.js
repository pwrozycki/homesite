import DS from 'ember-data';
import Ember from 'ember';

var BATCH_SIZE = 100;

export default DS.RESTAdapter.extend({
    namespace: 'gallery/api',
    coalesceFindRequests: true,

    /*
     Split findMany requests so that maximally BATCH_SIZE elements are fetched at once.
     */
    groupRecordsForFindMany: function (store, records) {
        // get original groups from super
        var groups = this._super(store, records);

        // split groups in subarrays with length not exceeding BATCH_SIZE
        var newGroups = [];
        groups.forEach(function (group) {
            var numberOfBatches = parseInt((group.length - 1) / BATCH_SIZE + 1);

            for (var i = 0; i < numberOfBatches; i++) {
                var begin = i * BATCH_SIZE;
                var end = (i + 1) * BATCH_SIZE;
                newGroups.push(group.slice(begin, end));
            }
        });

        return newGroups;
    }
});

