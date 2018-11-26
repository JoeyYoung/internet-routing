from generator import Generator

class game:
    def __init__(self):
        # settings of the game

        # Internet topology
        self.generator = Generator(1000, 4)
        self.generator.build_topology()

