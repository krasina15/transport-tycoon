import sys

# c - port
# d - warehouse with cargo

delivery_count = 0
tick = 0

routes = {
    ('D', 'A'): [('D', 'C'), ('C', 'A')],
    ('D', 'B'): [('D', 'B')]
}

distance = {
    ('D', 'B'): 5,
    ('D', 'C'): 1,
    ('C', 'A'): 4
}

route_type = {
    ('D', 'B'): 'truck',
    ('D', 'C'): 'truck',
    ('C', 'A'): 'ferry'
}


class Cargo:
    def __init__(self, departure, arrival, id):
        self.shape = 'container'
        self.id = id
        self.departure = departure
        self.delivery_plan = None
        self.arrival = arrival
        self.transit = None


class Vehicle:
    def __init__(self, color, kind, location):
        self.color = color
        self.kind = kind  # truck\ferry
        self.departure_facility = None
        self.cargo = None
        self.loaded = False
        self.arrival_facility = None
        self.spawn_facility = location
        self.current_location = None
        self.on_facility = True
        self.arrival_time = 0
        self.arrival_timer = 0

    def make_turn(self):
        if all([self.arrival_facility is None, self.current_location is None]):
            self.arrival_facility = self.spawn_facility
            self.departure_facility = self.spawn_facility
            self.current_location = self.spawn_facility
            print("!!", self.color, self.kind, "spawn on", self.spawn_facility.title)

        if self.arrival_timer != 0:
            print(">>", self.color, self.kind, 'on the way from', self.departure_facility.title, 'to',
                  self.arrival_facility.title, ', arrival in ', self.arrival_timer)
            self.arrival_timer = self.arrival_timer - 1
            if self.arrival_timer != 0:
                return

        if self.arrival_timer == 0:
            if self.arrival_facility is not None:
                self.current_location = self.arrival_facility
            self.departure_facility = self.current_location
            self.arrival_facility = None
            self.on_facility = True

        # unload action:
        if all([self.on_facility is True, self.loaded is True]):
            self.cargo.transit += 1
            print("!", self.color, self.kind, "unload", self.cargo.shape, "on",
                  self.current_location.title)
            self.current_location.unload_cargo(self.cargo)
            self.loaded = False

        if all([self.on_facility is True, self.loaded is False, self.current_location != self.spawn_facility]):
            self.departure_facility = self.current_location
            self.arrival_facility = self.spawn_facility
            self.arrival_timer = self.arrival_time
            print(">>", self.color, self.kind, "going back to", self.arrival_facility.title)
            self.on_facility = False
            self.current_location = None

            return
        if all([self.on_facility is True, self.loaded is False, len(self.current_location.delivery_queue) == 0]):
            print(">>", self.color, self.kind, "waiting on", self.current_location.title, ", nothing to delivery")

        # load cargo:
        if all([self.on_facility is True, self.loaded is False, len(self.current_location.delivery_queue) != 0]):
            print(">>", self.color, self.kind, "loaded:", self.loaded, "on", self.current_location.title,
                  "trying to load something")
            if route_type[self.current_location.delivery_queue[0].delivery_plan[self.current_location.delivery_queue[0].transit]] is not self.kind:
                print('impossible')
                return
            else:
                self.cargo = self.current_location.delivery_queue[0]
                departure, arrival = self.cargo.delivery_plan[self.current_location.delivery_queue[0].transit]
                if self.current_location.title != departure:
                    print('no way', self.current_location.title, departure)
                    return
                self.arrival_facility = facilities[arrival]
                self.departure_facility = facilities[departure]
                self.arrival_timer = distance[departure, arrival]
                self.arrival_time = distance[departure, arrival]
                self.departure_facility.load_cargo()
                self.loaded = True
                self.on_facility = False
                print(">>", self.color, self.kind, "loaded:", self.loaded, "with", self.cargo.shape, "on",
                      self.departure_facility.title, "and going with", self.cargo.shape, "to",
                      self.arrival_facility.title)
                print(">>", self.color, self.kind, 'time in the way', self.arrival_timer)
                return


class Facility:
    title = str

    def __init__(self, title):
        self.title = title
        self.delivery_queue = []
        self.storage_fill = 0

    def add_cargo(self, cargo_item):
        cargo_item.delivery_plan = routes[cargo_item.departure, cargo_item.arrival]
        cargo_item.transit = 0
        self.delivery_queue.append(cargo_item)
        self.storage_fill += 1

    def load_cargo(self):
        self.delivery_queue.pop(0)
        self.storage_fill -= 1

    def unload_cargo(self, cargo_item):
        global delivery_count
        if cargo_item.arrival != self.title:
            self.delivery_queue.append(cargo_item)
        else:
            delivery_count += 1
        self.storage_fill += 1
        print('! cargo unloaded in facility', self.title)


## AB
#cargo_list = [Cargo('D', 'A', 'tomato'), Cargo('D', 'B', 'carrot')]

## ABB
#cargo_list = [Cargo('D', 'A', 'tomato'), Cargo('D', 'B', 'carrot'), Cargo('D', 'B', 'pepper')]

## AAB ABB AB
#cargo_list = [Cargo('D', 'A', '0'), Cargo('D', 'A', '1'), Cargo('D', 'B', '2'),
#          Cargo('D', 'A', '3'), Cargo('D', 'B', '4'), Cargo('D', 'B', '5'),
#          Cargo('D', 'A', '6'), Cargo('D', 'B', '7')]

# ABB BAB AAA BBB
cargo_list = [Cargo('D', 'A', '0'), Cargo('D', 'B', '1'), Cargo('D', 'B', '2'),
          Cargo('D', 'B', '3'), Cargo('D', 'A', '4'), Cargo('D', 'B', '5'),
          Cargo('D', 'A', '6'), Cargo('D', 'A', '7'), Cargo('D', 'A', '8'),
          Cargo('D', 'B', '9'), Cargo('D', 'B', '10'), Cargo('D', 'B', '11')]

facilities = {'A': Facility('A'), 'B': Facility('B'), 'C': Facility('C'), 'D': Facility('D')}

for cargo in cargo_list:
    facilities['D'].add_cargo(cargo)

vehicles = [Vehicle('green', 'truck', facilities['D']), Vehicle('red', 'truck', facilities['D']),
            Vehicle('grey', 'ferry', facilities['C'])]

while True:
    print('!!! tick:', tick)
    for vehicle in vehicles:
        vehicle.make_turn()
    tick = tick + 1
    if delivery_count == len(cargo_list):
        break
