import mutagen

class TaggedFile:
    def __init__(self, path):
        self.path = path
        self.f = mutagen.File(path)


    # Getters

    def title(self):
        return [ self.f.tags[k] for k in self.f.keys() if 'TIT' in k ][0].text[0]

    def artist(self):
        return [ self.f.tags[k] for k in self.f.keys() if 'TPE' in k ][0].text[0]

    def album(self):
        return self.f.tags['TALB'].text[0] if 'TALB' in self.f.tags else None

    def art(self):
        art = [ self.f.tags[k] for k in self.f.keys() if 'APIC' in k ]
        return (art[0].mime, art[0].data) if len(art) != 0 else None

    def length(self):
        return self.f.info.length


    # Setters

    def set_title(self, value : str):
        self.f.tags.add(mutagen.id3.TIT1(text = value))
        self.f.tags.add(mutagen.id3.TIT2(text = value))

    def set_artist(self, value : str):
        self.f.tags.add(mutagen.id3.TPE1(text = value))
        self.f.tags.add(mutagen.id3.TPE2(text = value))

    def set_album(self, value : str):
        self.f.tags.add(mutagen.id3.TALB(text = value))

    def set_art(self, mime : str, data : bytes):
        self.f.tags.add(mutagen.id3.APIC(
        	desc = 'art',
        	mime = mime,
        	data = data,
    	))

    def save(self):
        self.f.save()

