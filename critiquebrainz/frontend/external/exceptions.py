class ExternalAPIException(Exception):
    """Base exception for this package"""
    pass

class SpotifyWebAPIException(ExternalAPIException):
    """Exception related to errors dealing with Spotify API."""
    pass
