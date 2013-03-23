import os
import sys
def import_all(dir):
  library_list = []
  for f in os.listdir(os.path.abspath(dir)):
   module_name, ext = os.path.splitext(f) # Handles no-extension files, etc.
   if ext == '.py': # Important, ignore .pyc/other files.
     if os.path.abspath(dir) not in sys.path:
      modified = True
      sys.path.append(os.path.abspath(dir)) # stick the path on the end
     module = __import__(module_name)
     library_list.append(module)
  if modified:
   sys.path.pop() # return system path to normal

  return library_list
