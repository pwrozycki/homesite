import DS from 'ember-data';

export default DS.RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
    attrs: {
        images: { serialize: 'ids', deserialize: 'records' },
        subdirectories: { serialize: 'ids', deserialize: 'records' }
    }
});