from abc import ABC, abstractmethod

class Agent(ABC):
    def __init__(self, name, database):
        self.name = name
        self.db = database
        self.memory = []
    
    @abstractmethod
    def process(self, message):
        pass
    
    @abstractmethod
    def act(self):
        pass
    
    def remember(self, information):
        self.memory.append(information)