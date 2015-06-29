import DS from 'ember-data';
import RESTSerializer from './default-serializer';

export default RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
    attrs: {
        files: { serialize: 'ids', deserialize: 'records' },
        subdirectories: { serialize: 'ids', deserialize: 'records' }
    }
});