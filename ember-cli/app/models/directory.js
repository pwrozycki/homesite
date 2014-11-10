import Subdirectory from "./subdirectory";
import DS from "ember-data";

export default Subdirectory.extend({
    images: DS.hasMany('image', { async: true}),
    subdirectories: DS.hasMany('subdirectory', { async: true})
});