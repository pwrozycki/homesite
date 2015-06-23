import File from "./file";

export default File.extend({
    fileType: 'video',
    isVideo: true,

    rippedSuffix: function() {
        return [this.get('collectionInfo.videosRoot'), this.get('path')].join('/');
    }.property('collectionInfo.videosRoot', 'path'),

    ripped: function () {
         return this.get('rippedSuffix') + '.mp4';
    }.property('rippedSuffix'),

    firstFrameJpeg: function() {
        return this.get('rippedSuffix') + '.jpg';
    }.property('rippedSuffix')
});