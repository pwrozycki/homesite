import DS from 'ember-data';

export default DS.RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
    attrs: {
        image: { serialize: 'ids', deserialize: 'records' },
        redundant: { serialize: 'ids', deserialize: 'records' }
    }
});