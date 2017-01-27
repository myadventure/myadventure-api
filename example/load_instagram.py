
import urlparse
from instagram.client import InstagramAPI


def get_media(api, media=None, max_id=None):
    """Get media."""

    if media is None:
        media = []

    response, next = api.user_recent_media(max_id=max_id)

    for media_item in response:
        media.append(media_item)

    if next is not None:
        parsednext = urlparse.urlparse(next)
        max_id = urlparse.parse_qs(parsednext.query)['max_id'][0]
        media = get_media(api, media, max_id)

    return media


def import_media(access_token, client_secret):
    """Import media."""

    api = InstagramAPI( \
        access_token=access_token.encode('ascii', 'ignore'), \
        client_secret=client_secret.encode('ascii', 'ignore') \
    )

    media = get_media(api)

    points = []

    for item in media:
        title = None
        desc = None
        video = None
        if hasattr(item, 'caption'):
            if item.caption is not None:
                desc = item.caption.text
        if hasattr(item, 'location'):
            if item.location.name is not None:
                title = item.location.name
            if item.location.point is not None:
                latitude = item.location.point.latitude
                longitude = item.location.point.longitude
        timestamp = item.created_time
        thumb = item.images.get('thumbnail').url
        photo = item.images.get('standard_resolution').url
        if hasattr(item, 'videos'):
            video = item.videos.get('standard_resolution').url
        resource = item.link

        try:
            point = {
                'title':title,
                'latitude':latitude,
                'longitude':longitude,
                'point_type':'photo',
                'timestamp':timestamp,
                'instagram_id':item.id,
                'thumb':thumb,
                'photo':photo,
                'video':video,
                'resource':resource,
                'desc':desc
            }
        except AttributeError:
            pass
        points.append(point)

    return points
