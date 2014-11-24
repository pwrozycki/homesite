import Subdirectory from "./subdirectory";
import DS from "ember-data";

export default Subdirectory.extend({
    images: DS.hasMany('image'),
    subdirectories: DS.hasMany('subdirectory')
});