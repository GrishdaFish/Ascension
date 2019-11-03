__author__ = 'Grishnak'


class Event:
    def __init__(self, id, payload=[]):
        self.id = id
        self.payload = payload

    def get_id(self):
        return self.id

    def get_payload(self):
        return self.payload