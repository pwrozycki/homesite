from copy import copy

from rest_framework_ember.renderers import JSONRenderer
from rest_framework_ember.utils import get_resource_name


class MyJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context.get('view')
        resource_name = get_resource_name(view)
        data_copy = copy(data)

        result = {}
        if 'results' in data:
            result[resource_name] = data_copy.pop('results')
            result['meta'] = data_copy
        else:
            result[resource_name] = data_copy

        result.update(self.prepare_sideloaded_data(result[resource_name]))

        return super(JSONRenderer, self).render(
            result, accepted_media_type, renderer_context)

    def prepare_sideloaded_data(self, content):
        sideloaded_content_dict = {}

        # dig deep through objects and extract sideloaded data
        # replace every occurrence with list of identifiers (flatten deep structure)
        if isinstance(content, list):
            for entry in content:
                self.extract_sideloaded_content(entry, sideloaded_content_dict)
        else:
            self.extract_sideloaded_content(content, sideloaded_content_dict)

        for k in sideloaded_content_dict:
            sideloaded_content_dict[k] = list(sideloaded_content_dict[k].values())

        # return dictionary of data to be sideloaded
        return sideloaded_content_dict

    def extract_sideloaded_content(self, instance_dict, sideloaded_content_dict):
        for (property_name, property_value) in instance_dict.items():

            if isinstance(property_value, list):
                for (index, related_element) in enumerate(property_value):

                    if isinstance(related_element, dict) and 'id' in related_element:
                        self.extract_sideloaded_content(related_element, sideloaded_content_dict)
                        sideloaded_objects_dict = sideloaded_content_dict.setdefault(property_name, {})
                        sideloaded_objects_dict[related_element['id']] = related_element
                        property_value[index] = related_element['id']
