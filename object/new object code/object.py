
class Entity:
    def __init__(self):
        self.components = []

    def send_event(self, event):
        for component in self.components:
            component.receive_event(event)

    def add_component(self, component):
        self.components.append(component)


class Event:
    def __init__(self, name, event):
        self.id = None
        self.event = {name: event}


class Component:
    def __init__(self, owner=None):
        self.events = []
        self.owner = owner

    def receive_event(self, event):
        self.events.append(event)
        for event in self.events:
            self.process_events()

    def process_events(self):
        pass


class PhysicsComponent(Component):
    def __init__(self, owner):
        Component.__init__(self)
        self.components = []

'''
Physical Component (event)
    process incoming event
    if event is of type ()
        process event
        loop sub comp and send event array to each component
            if component does something with event
                send new event to owner (physical component) or modify current event and send back
                    pop events out of the event array and always send the modified one back
                    maybe only pop event if its one we can modify
                then continue looping through to the next component
    send final event(s) to do w/e


'''