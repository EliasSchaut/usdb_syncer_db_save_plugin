from usdb_syncer import hooks, usdb_song
from prisma import Prisma

# Initialize the Prisma client
prisma = Prisma()


async def save_song_metadata(song: usdb_song.UsdbSong) -> None:
    """Save relevant song metadata to the database."""
    # Connect to Prisma if not already connected
    if not prisma.is_connected():
        await prisma.connect()

    # Ensure the genre, artist, and language exist, or create them if not
    genre = await prisma.genre.upsert(
        where={"name": song.genre},
        update={},
        create={"name": song.genre}
    )

    artist = await prisma.artist.upsert(
        where={"name": song.artist},
        update={},
        create={"name": song.artist}
    )

    language = await prisma.language.upsert(
        where={"name": song.language},
        update={},
        create={"name": song.language}
    )

    # Create the new Track record with related foreign keys
    await prisma.track.create(
        data={
            'usdb_id': song.song_id,
            'title': song.title,
            'year': song.year,
            'cover_src': song.sync_meta.meta_tags.cover.source,
            'genre_id': genre.id,
            'artist_id': artist.id,
            'language_id': language.id,
        }
    )
    print(f"Song '{song.title}' by '{song.artist}' saved to database.")


def on_download_finished(song: usdb_song.UsdbSong) -> None:
    prisma.run(save_song_metadata(song))
    print(f"Download finished for: {song}")


# Subscribe to the download finished hook
hooks.SongLoaderDidFinish.subscribe(on_download_finished)
