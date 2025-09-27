class TrafficLight:
  id_counter = 0

  def __init__(self, coords: tuple, duration = 10, isGreen = False):
    self.id = TrafficLight.id_counter
    TrafficLight.id_counter += 1

    self.coords = coords
    self.duration = duration
    self.timer = 0
    self.isGreen = isGreen

  def setIsGreen(self, state: bool):
    self.isGreen = state

  def update(self, dt):
    self.timer += dt
    if self.timer >= self.duration:
      self.timer = 0
      self.isGreen = not self.isGreen