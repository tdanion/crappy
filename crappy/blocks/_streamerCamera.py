# coding: utf-8
##  @addtogroup blocks
# @{

##  @defgroup StreamerCamera StreamerCamera
# @{

## @file _streamerCamera.py
# @brief Streams pictures.
# @author V1ctor Couty, Robin Siemiatkowski
# @version 0.2
# @date 10/01/2017
from __future__ import print_function

from _masterblock import MasterBlock
import os
import time
import sys
from crappy.technical import TechnicalCamera as tc
from ..links._link import TimeoutError
import SimpleITK as sitk

class StreamerCamera(MasterBlock):
  """
  Streams pictures.
  """
  def __init__(self,**kwargs):
    """
    This block fetch images from a camera object, can save and/or transmit them to another block.
    No need to create the technical, this block will take care of it.

    It can be triggered by an other block, internally,
    or run as fast as possible

    kwargs:
        camera : {"Ximea","Jai","Webcam",...}
          See crappy.sensor._meta.MasterCam.classes for a full list
        numdevice : int, default = 0
            If you have several camera plugged, choose the right one.
        save_folder : directory, default = None
            directory to save the images. If inexistant, will be created.
            If None, will not save the images
        label : string, default="cycle"
            If using external trigger, the name of the saved images will 
            include the data from this label. (Useful to keep track of the
            differents stages of an experiment).
        See below for default values
    """
    MasterBlock.__init__(self)
    for arg,default in [("camera","ximea"),
                        ("numdevice",0),
                        ("save_folder",None),
                        ("label","cycle"),
                        ("show_fps",False)]:
      setattr(self,arg,kwargs.get(arg,default)) #Assign these attributes
      try: 
        del kwargs[arg] # And remove them (if any) to 
                        # keep the parameters for the technical
      except KeyError:
        pass
    self.camera_name = self.camera
    self.tc_kwargs = kwargs

  def prepare(self):
    if self.save_folder and not os.path.exists(self.save_folder):
      os.makedirs(self.save_folder)
    self.camera = tc(self.camera_name, self.numdevice,**self.tc_kwargs)
    self.trigger = "internal" if len(self.inputs) == 0 else "external"

  def main(self):
    timer = time.time()
    fps_timer = timer
    data = {}
    last_index = 0
    loops = 0
    while True:
      if self.show_fps and timer - fps_timer > 2:
        sys.stdout.write("\r[StreamerCamera] FPS: %2.2f" % (
                        (loops - last_index) / (timer - fps_timer)))
        sys.stdout.flush()
        fps_timer = timer
        last_index = loops
      if self.trigger == "internal":
        img = self.camera.sensor.read_image()
      elif self.trigger == "external":
        data = self.inputs[0].recv()  # wait for a signal
        if data is None:
          continue
        img = self.camera.sensor.get_image()
        t = time.time() - self.t0
      timer = time.time()
      if self.save_folder:
        image = sitk.GetImageFromArray(img)
        try:
          cycle = data[self.label] # If we received a data to add in the name
          sitk.WriteImage(image,
                 self.save_folder + "img_%.6d_cycle%09.1f_%.5f.tiff" % (
                 loops, cycle, timer - self.t0))
        except KeyError: # If we did not
          sitk.WriteImage(image,
                 self.save_folder + "img_%.6d_%.5f.tiff" % (
                 loops, timer - self.t0))
      loops += 1
      self.send(img)

    def __repr__(self):
      return "Streamer Camera (%s)"%self.camera_name
