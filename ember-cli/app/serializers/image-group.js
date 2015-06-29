import DS from 'ember-data';
import RESTSerializer from './default-serializer';

export default RESTSerializer.extend(DS.EmbeddedRecordsMixin, {
    attrs: {
        images: { serialize: 'ids', deserialize: 'records' }
    }
});