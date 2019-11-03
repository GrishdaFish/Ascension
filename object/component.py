__author__ = 'Grishnak'


class Component:
    def __init__(self, owner=None, priority=100):
        self.events = []
        self.owner = owner
        self.priority = priority

    def receive_event(self, event):
        self.events.append(event)
        self.process_event()

    def process_event(self):  # usually will get over ridden, but there in case we only have attaching
        pass                  # behaviour only, so it'll do nothing on a process event call

    def clear(self):
        self.events = []