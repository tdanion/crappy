#coding: utf-8

import numpy as np

from .modifier import Modifier


class Moving_avg(Modifier):
  def __init__(self,npoints=100):
    Modifier.__init__(self)
    self.npoints = npoints

  def evaluate(self,data):
    if not hasattr(self,"last"):
      self.last = dict(data)
      for k in data:
        self.last[k] = [self.last[k]]
    r = {}
    for k in data:
      self.last[k].append(data[k])
      if len(self.last[k]) > self.npoints:
        self.last[k] = self.last[k][-self.npoints:]
      try:
        r[k] = np.mean(self.last[k])
      except TypeError:
        r[k] = self.last[k][-1]
    return r