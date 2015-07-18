import File from "./file";

export default File.extend({
    fileType: 'video',
    isVideo: true,

    rippedSuffix: function() {
        return [this.get('collectionInfo.videosRoot'), this.get('path_with_timestamp')].join('/');
    }.property('collectionInfo.videosRoot', 'path_with_timestamp'),

    ripped: function () {
         return this.get('rippedSuffix') + '.mp4';
    }.property('rippedSuffix'),

    firstFrameJpeg: function() {
        return this.get('rippedSuffix') + '.jpg';
    }.property('rippedSuffix')
});