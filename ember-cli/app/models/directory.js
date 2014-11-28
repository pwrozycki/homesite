import Subdirectory from "./subdirectory";
import DS from "ember-data";

export default Subdirectory.extend({
    images: DS.hasMany('image'),
    subdirectories: DS.hasMany('subdirectory'),

    /**
     * signifies if cached object can be used or should be reloaded when entering gallery.directory route.
     */
    needsToBeReloaded: false
});