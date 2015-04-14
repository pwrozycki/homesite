import Ember from 'ember';

export default Ember.Component.extend({
    classNames: ['dirlisting'],

    actions: {
        toggleShared: function (directory) {
            var oldShared = directory.get('shared');
            directory.set('shared', !oldShared);
            directory.save().catch(function () {
                directory.set('shared', oldShared);
            });
        }
    }
});
