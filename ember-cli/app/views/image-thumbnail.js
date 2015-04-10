import Ember from 'ember';

export default Ember.View.extend({
    templateName: 'views/image-thumbnail',
    classNames: ['thumbnail-container'],
    classNameBindings: ['image.selected:selected'],

    click: function(event) {
        if ($(event.target).is('img')) {
            if (event['ctrlKey']) {
                this.toggleProperty('image.selected');
            } else {
                this.get('controller').send('showPreview', this.get('image'));
            }
        }
    }
});