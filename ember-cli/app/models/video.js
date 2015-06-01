import File from "./file";

export default File.extend({
    fileType: 'video',

    ripped: function () {
        return [this.get('collectionInfo.videosRoot'), this.get('path')].join('/');
    }.property('collectionInfo.videosRoot', 'path')
});