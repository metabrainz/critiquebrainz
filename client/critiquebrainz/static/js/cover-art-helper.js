/**
 * Replaces cover art image with a placeholder.
 * Meant to be used as a fallback for albums without cover art.
 * Example: <img src="//coverartarchive.org/release-group/d1850227-c7c7-42c8-b469-6e99023412de/front-250" onerror="coverArtMissing(this);">
 */
function coverArtMissing(image) {
    image.onerror = "";
    image.src = "/static/img/missing-art.png";
}